"""
Skill 05 — LTXV 0.9.8 I2V 비디오 클립 생성 (ComfyUI)
입력: 시작 프레임 이미지 + video_prompt
출력: workspace/07_clips/clip_{id}.mp4

- ComfyUI /upload/image → LoadImage 노드로 시작 프레임 전달
- 25fps 기준 프레임 수 = duration * 25 (8n+1 규칙 자동 보정)
- VRAM 공유 충돌 방지: 순차 처리 (max_workers=1)
"""
from __future__ import annotations
import copy
import json
import math
import random
from pathlib import Path

from .comfyui_client import queue_prompt, wait_for_result, download_output, upload_image

_WORKFLOW_PATH = Path(__file__).parent / "workflows" / "ltxv_i2v_api.json"
_WORKFLOW: dict | None = None

FPS = 25

# clip role별 strength (높을수록 원본 이미지 변형 허용, 낮을수록 충실)
_ROLE_STRENGTH = {
    "Hook":    0.9,   # 첫 장면: 살짝 동적
    "Value_A": 0.85,  # 메뉴샷: 가급적 원본 유지
    "Value_B": 0.80,  # 부메뉴: 원본 최대한 유지 (볶음 장면 방지)
    "Mood":    0.75,  # 분위기: 가장 정적
    "CTA":     0.85,  # 외관: 정적
}


def _get_workflow() -> dict:
    global _WORKFLOW
    if _WORKFLOW is None:
        _WORKFLOW = json.loads(_WORKFLOW_PATH.read_text(encoding="utf-8"))
    return _WORKFLOW


def _ltxv_frame_count(duration_seconds: int) -> int:
    """LTXV 규칙: 프레임 수 = 8n + 1 (최소 9). 25fps 기준."""
    raw = max(duration_seconds * FPS, 9)
    # 8n+1 에 가장 가까운 값으로 올림
    n = math.ceil((raw - 1) / 8)
    return 8 * n + 1


def generate_video_clip(
    image_path: Path,
    video_prompt: str,
    duration_seconds: int,
    output_path: Path,
    clip_role: str = "Mood",
    backend: str = "local",
) -> Path:
    """단일 클립 생성 (ComfyUI LTXV I2V 또는 Google Veo)."""
    if backend == "api":
        print(f"  Veo 3.1 비디오 생성: {duration_seconds}s / {video_prompt[:60]}...")
        from .google_client import generate_video as g_gen_video
        return g_gen_video(video_prompt, output_path, image_path)

    clip_role_strength = _ROLE_STRENGTH.get(clip_role, 0.85)
    # 1. 이미지 업로드
    print(f"  이미지 업로드: {image_path.name}")
    uploaded_name = upload_image(image_path)

    # 2. 워크플로우 복사 및 파라미터 주입
    wf = copy.deepcopy(_get_workflow())
    frame_count = _ltxv_frame_count(duration_seconds)

    # 프롬프트에 정적 카메라 보조 지시어 추가
    static_suffix = ", static camera, minimal motion, cinematic hold"
    wf["3"]["inputs"]["text"] = video_prompt + static_suffix  # positive
    wf["5"]["inputs"]["image"] = uploaded_name               # LoadImage
    wf["6"]["inputs"]["length"] = frame_count                # LTXVImgToVideo
    wf["6"]["inputs"]["strength"] = clip_role_strength       # 이미지 충실도
    wf["8"]["inputs"]["seed"] = random.randint(0, 2**32 - 1) # KSampler

    print(f"  LTXV 비디오 생성: {duration_seconds}s → {frame_count}프레임 / {video_prompt[:60]}...")

    # 3. 큐 제출 및 완료 대기
    pid = queue_prompt(wf)
    outputs = wait_for_result(pid, timeout=600)

    if not outputs:
        raise RuntimeError(f"LTXV 출력 없음: {output_path.name}")

    # 4. 다운로드
    output_path.parent.mkdir(parents=True, exist_ok=True)
    download_output(outputs[0], output_path)
    print(f"  비디오 저장 완료: {output_path}")
    return output_path


def generate_all_clips(
    clip_plan: list[dict],
    photos_dir: Path,
    workspace: Path,
    on_progress: callable | None = None,
    backend: str = "local",
) -> dict[str, Path]:
    """5개 클립 순차 생성 (GPU 1개 = max_workers=1) → {clip_id: Path} 반환."""
    frames_dir = workspace / "05_start_frames"
    clips_dir = workspace / "07_clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, Path] = {}

    for i, clip in enumerate(clip_plan, 1):
        image_path = _resolve_image_path(clip, photos_dir, frames_dir)
        if not image_path or not image_path.exists():
            raise FileNotFoundError(f"클립 {clip['id']} 시작 프레임 없음: {image_path}")

        clip_id = clip["id"]
        output_path = clips_dir / f"clip_{clip_id}.mp4"

        print(f"\n    [{i}/{len(clip_plan)}] 클립 생성 시작: clip_{clip_id} "
              f"({clip.get('role','?')}, {clip['duration']}s)", flush=True)

        try:
            path = generate_video_clip(
                image_path=image_path,
                video_prompt=clip["video_prompt"],
                duration_seconds=clip["duration"],
                output_path=output_path,
                clip_role=clip.get("role", "Mood"),
                backend=backend,
            )
            results[clip_id] = path
            if on_progress:
                on_progress(f"clip_{clip_id} 생성 완료")
        except Exception as e:
            raise RuntimeError(f"clip_{clip_id} 생성 실패: {e}") from e

    return results


def _resolve_image_path(clip: dict, photos_dir: Path, frames_dir: Path) -> Path | None:
    if clip.get("generate_image"):
        png_path = frames_dir / f"{clip['id']}.png"
        jpg_path = frames_dir / f"{clip['id']}.jpg"
        if jpg_path.exists():
            return jpg_path
        return png_path
    source_file = clip.get("source_file")
    if source_file:
        return photos_dir / source_file
    return None
