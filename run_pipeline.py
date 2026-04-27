"""
CLI: 로컬에서 파이프라인 직접 실행 (실시간 진행 상황 + 중간 결과물 표시)

사용법:
  uv run python run_pipeline.py --md store_sample.md --photos workspace/01_store_photos/

선택사항:
  --job-id abc123   (지정 안 하면 자동 생성)
  --sample          (API 없이 기존 샘플 파일로 렌더링만 테스트)
"""
import argparse
import asyncio
import json
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

# 출력 버퍼링 비활성화 (실시간 출력)
sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# -- ANSI 컬러 ----------------------------------------------------------------
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
RED     = "\033[91m"
BLUE    = "\033[94m"
WHITE   = "\033[97m"

STEP_LABELS = {
    1: "[1] 가게 사진 분석    (Ollama Vision)",
    2: "[2] 스토리보드 생성   (SuperGemma)",
    3: "[3] AI 이미지 생성    (ComfyUI FLUX)",
    4: "[4] 프레임 분석       (Ollama Vision)",
    5: "[5] 비디오 클립 생성  (ComfyUI LTXV)",
    6: "[6] 최종 광고 렌더링  (MoviePy)",
}

_step_start: dict[int, float] = {}
_current_step = {"v": 0}


# -- 출력 헬퍼 ----------------------------------------------------------------

def ts() -> str:
    return f"{DIM}[{datetime.now().strftime('%H:%M:%S')}]{RESET}"

def p(*args, **kwargs):
    print(*args, **kwargs, flush=True)

def print_header(job_id: str, md_path: Path, photos_dir: Path):
    p()
    p(f"{BOLD}{CYAN}{'='*62}{RESET}")
    p(f"{BOLD}{WHITE}     동네방네 광고 자동 생성 파이프라인{RESET}")
    p(f"{BOLD}{CYAN}{'='*62}{RESET}")
    p(f"  Job ID   : {YELLOW}{job_id}{RESET}")
    p(f"  업체 정보: {md_path}")
    p(f"  사진 폴더: {photos_dir}")
    p(f"{BOLD}{CYAN}{'='*62}{RESET}")
    p()

def print_step_start(step: int, total: int):
    _step_start[step] = time.time()
    label = STEP_LABELS.get(step, f"[{step}] 처리 중")
    p(f"\n{ts()} {BOLD}{BLUE}{label}{RESET}")
    p(f"{ts()} {DIM}{'─'*50}{RESET}")

def print_step_done(step: int):
    elapsed = time.time() - _step_start.get(step, time.time())
    label = STEP_LABELS.get(step, "").split("(")[0].strip()
    p(f"{ts()} {GREEN}>>> {label} 완료  ({elapsed:.1f}s){RESET}")

def print_info(msg: str):
    p(f"{ts()}  {WHITE}{msg}{RESET}")

def print_save(path: Path):
    p(f"{ts()}  {DIM}[저장] {path}{RESET}")

def print_detail(msg: str):
    p(f"{ts()}   {DIM}{msg}{RESET}")

def print_warn(msg: str):
    p(f"{ts()}  {YELLOW}[주의] {msg}{RESET}")

def print_error(msg: str):
    p(f"{ts()}  {RED}[오류] {msg}{RESET}")


# -- 중간 결과물 출력 ----------------------------------------------------------

def show_analysis(workspace: Path):
    path = workspace / "02_analysis.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    print_save(path)
    print_detail(f"테마: {data.get('theme_recommendation','?')} | "
                 f"사진 {len(data.get('photo_files',[]))}장")
    for scene, info in data.get("scene_assignment", {}).items():
        src  = info.get("source", "?")
        file = info.get("file", "없음")
        tag  = "[실사진]" if src == "real_photo" else "[AI생성]"
        print_detail(f"  {tag} {scene:6s} -> {file}")

def show_storyboard(workspace: Path):
    path = workspace / "03_storyboard.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    print_save(path)
    copy_ = data.get("ad_copy", {})
    print_detail(f"메인 카피  : {copy_.get('main_copy','')}")
    print_detail(f"가격 배지  : {copy_.get('price_badge_main','').replace(chr(10), ' / ')}")
    print_detail(f"리뷰       : {copy_.get('review_text','')}")
    p(f"{ts()}   {DIM}클립 계획:{RESET}")
    for c in data.get("clip_plan", []):
        gen  = "[AI생성]" if c.get("generate_image") else f"[{c.get('source_file','?')}]"
        vp   = (c.get("video_prompt") or "")[:58]
        print_detail(f"  clip_{c['id']} ({c['role']:8s} {c['duration']}s) {gen}")
        print_detail(f"    prompt: {vp}...")

def show_generated_images(workspace: Path):
    frames_dir = workspace / "05_start_frames"
    if not frames_dir.exists():
        return
    imgs = sorted(list(frames_dir.glob("*.png")) + list(frames_dir.glob("*.jpg")))
    if imgs:
        print_detail(f"생성된 이미지 {len(imgs)}장:")
        for img in imgs:
            print_save(img)

def show_clips(workspace: Path):
    clips_dir = workspace / "07_clips"
    if not clips_dir.exists():
        return
    clips = sorted(clips_dir.glob("clip_*.mp4"))
    if clips:
        print_detail(f"생성된 클립 {len(clips)}개:")
        for clip in clips:
            size_mb = clip.stat().st_size / 1024 / 1024
            print_save(clip)
            print_detail(f"  {clip.name}  {size_mb:.1f}MB")


# -- on_progress 콜백 ---------------------------------------------------------

def make_progress_handler(workspace: Path):

    def on_progress(event: dict):
        step = event.get("step", 0)
        msg  = event.get("msg", "")
        done = event.get("done", False)

        if step != _current_step["v"]:
            if _current_step["v"] > 0:
                print_step_done(_current_step["v"])
                _show_step_result(_current_step["v"], workspace)
            _current_step["v"] = step
            total = event.get("total", 6)
            print_step_start(step, total)

        if msg:
            if "[SKIP]" in msg:
                print_detail(f"(건너뜀) {msg}")
            else:
                print_info(msg)

        if done:
            print_step_done(step)

    return on_progress


def _show_step_result(step: int, workspace: Path):
    if step == 1:
        show_analysis(workspace)
    elif step == 2:
        show_storyboard(workspace)
    elif step == 3:
        show_generated_images(workspace)
    elif step == 4:
        path = workspace / "05_frame_analysis.json"
        if path.exists():
            print_save(path)
    elif step == 5:
        show_clips(workspace)


# -- 메인 ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="동네방네 광고 자동 생성")
    parser.add_argument("--md",      required=False)
    parser.add_argument("--photos",  required=False)
    parser.add_argument("--job-id",  default=None)
    parser.add_argument("--sample",  action="store_true")
    parser.add_argument("--backend", choices=["local", "api"], default="local", help="백엔드 선택 (local: Ollama/ComfyUI, api: Google Gemini/Veo)")
    args = parser.parse_args()

    if not args.sample:
        if not args.md or not args.photos:
            parser.error("--sample 없으면 --md, --photos 필수")
        md_path    = Path(args.md)
        photos_dir = Path(args.photos)
        if not md_path.exists():
            print_error(f"MD 파일 없음: {md_path}"); sys.exit(1)
        if not photos_dir.exists():
            print_error(f"사진 폴더 없음: {photos_dir}"); sys.exit(1)
    else:
        md_path    = Path("dummy.md")
        photos_dir = Path("dummy_dir")

    job_id = args.job_id or uuid.uuid4().hex[:8]

    from pipeline.orchestrator import WORKSPACE_ROOT
    workspace = WORKSPACE_ROOT / job_id

    print_header(job_id, md_path, photos_dir)
    print_info(f"선택된 백엔드: {BOLD}{args.backend.upper()}{RESET}")
    print_info(f"결과물 폴더:   {BOLD}{workspace}{RESET}")

    on_progress = make_progress_handler(workspace)
    start_total = time.time()

    from pipeline.orchestrator import run_pipeline

    try:
        result = asyncio.run(run_pipeline(
            store_md_path=md_path,
            photos_dir=photos_dir,
            on_progress=on_progress,
            job_id=job_id,
            use_sample=args.sample,
            backend=args.backend,
        ))
    except Exception as e:
        print_error(f"파이프라인 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    total_elapsed = time.time() - start_total

    p()
    p(f"{BOLD}{CYAN}{'='*62}{RESET}")
    p(f"{BOLD}{GREEN}  파이프라인 완료!{RESET}")
    p(f"{BOLD}{CYAN}{'='*62}{RESET}")
    p(f"  총 소요 시간 : {YELLOW}{total_elapsed/60:.1f}분{RESET}")
    p(f"  최종 결과물  : {BOLD}{result}{RESET}")
    size_mb = result.stat().st_size / 1024 / 1024
    p(f"  파일 크기    : {size_mb:.1f}MB")
    p(f"{BOLD}{CYAN}{'='*62}{RESET}")
    p()


if __name__ == "__main__":
    main()
