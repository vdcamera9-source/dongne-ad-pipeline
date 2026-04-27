"""
파이프라인 오케스트레이터
MD 업체정보 + 사진 폴더 → final_ad.mp4

진행상황은 on_progress 콜백으로 전달:
  on_progress({"step": N, "total": 6, "msg": "...", "done": False/True})

--sample 모드 (use_sample=True):
  API 없이 기존 샘플 파일로 렌더링만 실행
  sample_dir = workspace/ 루트 (기본값)
    - sample_dir/03_storyboard.json → 스토리보드
    - sample_dir/07_clips/          → 영상 클립 5개
    - 출력: sample_dir/08_output/final_ad.mp4
"""
from __future__ import annotations
import asyncio
import json
import shutil
import uuid
import yaml
from pathlib import Path
from typing import Callable

from .skill_01_analyze import analyze_store_photos
from .skill_02_storyboard import build_storyboard
from .skill_03_gen_image import generate_frame_image
from .skill_04_analyze_frame import analyze_all_frames
from .skill_05_gen_video import generate_all_clips
from .skill_06_render import render_final

WORKSPACE_ROOT = Path(__file__).parent.parent / "workspace"
SAMPLE_DIR     = WORKSPACE_ROOT  # 기본 샘플: workspace/ 루트


def parse_store_md(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    return yaml.safe_load(text)


def _emit(on_progress: Callable | None, step: int, total: int, msg: str, done: bool = False):
    if on_progress:
        on_progress({"step": step, "total": total, "msg": msg, "done": done})


# ── 샘플 모드 ─────────────────────────────────────────────────────────────────

async def run_pipeline_sample(
    on_progress: Callable | None = None,
    sample_dir: Path | None = None,
) -> Path:
    """
    API 없이 샘플 파일로 렌더링만 실행.
    sample_dir: 스토리보드와 클립이 있는 workspace 경로 (기본: workspace/ 루트)
    """
    sample_dir = Path(sample_dir) if sample_dir else SAMPLE_DIR
    TOTAL = 6

    _emit(on_progress, 1, TOTAL, "[SKIP] 사진 분석 - 샘플 모드")
    _emit(on_progress, 2, TOTAL, "[SKIP] 스토리보드 - 기존 파일 사용")

    storyboard_path = sample_dir / "03_storyboard.json"
    if not storyboard_path.exists():
        raise FileNotFoundError(f"스토리보드 없음: {storyboard_path}")
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    _emit(on_progress, 2, TOTAL,
          f"스토리보드 로드: {storyboard['store_info']['name']} / {storyboard['template']} 테마")

    _emit(on_progress, 3, TOTAL, "[SKIP] 이미지 생성 - 샘플 모드")
    _emit(on_progress, 4, TOTAL, "[SKIP] 프레임 분석 - 샘플 모드")
    _emit(on_progress, 5, TOTAL, "[SKIP] 영상 생성 - 기존 클립 사용")

    clips_dir = sample_dir / "07_clips"
    missing = [f for f in ["clip_01.mp4","clip_02a.mp4","clip_02b.mp4","clip_03.mp4","clip_04.mp4"]
               if not (clips_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"클립 없음: {missing}")
    _emit(on_progress, 5, TOTAL, f"클립 5개 확인 완료 ({clips_dir})")

    _emit(on_progress, 6, TOTAL, "최종 광고 렌더링 중...")
    loop = asyncio.get_event_loop()
    out = await loop.run_in_executor(None, render_final, storyboard, clips_dir, sample_dir)
    _emit(on_progress, 6, TOTAL, f"렌더링 완료: {out}", done=True)

    return out


# ── 풀 파이프라인 ──────────────────────────────────────────────────────────────

async def run_pipeline(
    store_md_path: str | Path,
    photos_dir: str | Path,
    on_progress: Callable | None = None,
    job_id: str | None = None,
    use_sample: bool = False,
    sample_dir: Path | None = None,
    backend: str = "local",
) -> Path:
    """
    전체 파이프라인 실행.
    use_sample=True 이면 API 단계를 건너뛰고 샘플 파일로 렌더링만 실행.
    Returns: final_ad.mp4 경로
    """
    if use_sample:
        return await run_pipeline_sample(on_progress=on_progress, sample_dir=sample_dir)

    store_md_path = Path(store_md_path)
    photos_dir    = Path(photos_dir)
    job_id        = job_id or uuid.uuid4().hex[:8]
    workspace     = WORKSPACE_ROOT / job_id
    workspace.mkdir(parents=True, exist_ok=True)

    loop  = asyncio.get_event_loop()
    TOTAL = 6

    # ── Step 1: 업체 MD 파싱 + 이미지 분석 ─────────────────────
    _emit(on_progress, 1, TOTAL, f"가게 사진 분석 중... (백엔드: {backend.upper()})")
    store_info = parse_store_md(store_md_path)
    analysis = await loop.run_in_executor(
        None, analyze_store_photos, photos_dir, store_info, workspace, backend
    )
    _emit(on_progress, 1, TOTAL, f"이미지 {len(analysis['photo_files'])}장 분석 완료")

    # ── Step 2: 스토리보드 생성 ──────────────────────────────────
    _emit(on_progress, 2, TOTAL, "스토리보드 설계 중...")
    storyboard = await loop.run_in_executor(
        None, build_storyboard, analysis, store_info, workspace, backend
    )
    clip_plan = storyboard["clip_plan"]
    _emit(on_progress, 2, TOTAL, f"스토리보드 완료: {storyboard['template']} 테마")

    # ── Step 3: 이미지 생성 ──────────────────────────────────────
    gen_clips = [c for c in clip_plan if c.get("generate_image")]
    if gen_clips:
        _emit(on_progress, 3, TOTAL, f"이미지 생성 중 ({len(gen_clips)}장)...")
        for clip in gen_clips:
            await loop.run_in_executor(None, generate_frame_image, clip, workspace, backend)
            _emit(on_progress, 3, TOTAL, f"이미지 생성 완료: {clip['id']}")
    else:
        _emit(on_progress, 3, TOTAL, "이미지 생성 없음 (실사진만 사용)")

    # ── Step 4: 시작 프레임 분석 ────────────────────────────────
    _emit(on_progress, 4, TOTAL, "시작 프레임 분석 중...")
    await loop.run_in_executor(
        None, analyze_all_frames, clip_plan, photos_dir, workspace, backend
    )
    _emit(on_progress, 4, TOTAL, "프레임 분석 완료")

    # ── Step 5: 영상 생성 (병렬) ────────────────────────────────
    _emit(on_progress, 5, TOTAL, f"영상 생성 중 ({len(clip_plan)}클립, 병렬)...")

    def _progress_cb(msg: str):
        _emit(on_progress, 5, TOTAL, msg)

    await loop.run_in_executor(
        None, _run_generate_clips, clip_plan, photos_dir, workspace, _progress_cb, backend
    )
    _emit(on_progress, 5, TOTAL, "전체 영상 클립 생성 완료")

    # ── Step 6: 최종 렌더링 ──────────────────────────────────────
    _emit(on_progress, 6, TOTAL, "최종 광고 렌더링 중...")
    clips_dir = workspace / "07_clips"
    out = await loop.run_in_executor(None, render_final, storyboard, clips_dir, workspace)
    _emit(on_progress, 6, TOTAL, f"렌더링 완료: {out}", done=True)

    return out


def _run_generate_clips(clip_plan, photos_dir, workspace, on_progress, backend):
    generate_all_clips(clip_plan, photos_dir, workspace, on_progress=on_progress, backend=backend)
