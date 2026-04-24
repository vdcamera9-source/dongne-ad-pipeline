"""
Skill 05 — Veo 3.1 Lite I2V 비디오 클립 생성
입력: 시작 프레임 이미지 + video_prompt
출력: workspace/07_clips/clip_{id}.mp4

- 비동기 polling (15초 간격)
- 5클립 병렬 생성 지원
"""
from __future__ import annotations
import time
from pathlib import Path
from google.genai import types
from .client import get_client
from .models import video_gen_model
POLL_INTERVAL = 15  # seconds
MAX_WAIT = 600       # 10분


def generate_video_clip(
    image_path: Path,
    video_prompt: str,
    duration_seconds: int,
    output_path: Path,
) -> Path:
    """단일 클립 생성 (동기 블로킹). 병렬 처리는 orchestrator에서 ThreadPool로."""
    data = image_path.read_bytes()
    suffix = image_path.suffix.lower()
    mime = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"

    client = get_client()

    operation = client.models.generate_videos(
        model=video_gen_model(),
        prompt=video_prompt,
        config=types.GenerateVideosConfig(
            image=types.Image(image_bytes=data, mime_type=mime),
            aspect_ratio="16:9",
            resolution="1080p",
            duration_seconds=min(duration_seconds + 1, 8),  # 여유 1초
            number_of_videos=1,
        ),
    )

    elapsed = 0
    while not operation.done:
        if elapsed >= MAX_WAIT:
            raise TimeoutError(f"Veo 응답 초과: {output_path.name}")
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        operation = client.operations.get(operation)

    video_bytes = operation.result.generated_videos[0].video.video_bytes
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(video_bytes)
    return output_path


def generate_all_clips(
    clip_plan: list[dict],
    photos_dir: Path,
    workspace: Path,
    on_progress: callable | None = None,
) -> dict[str, Path]:
    """5개 클립을 ThreadPool로 병렬 생성 → {clip_id: Path} 반환."""
    import concurrent.futures

    frames_dir = workspace / "05_start_frames"
    clips_dir = workspace / "07_clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    tasks: dict[str, tuple[Path, str, int]] = {}
    for clip in clip_plan:
        image_path = _resolve_image_path(clip, photos_dir, frames_dir)
        if not image_path or not image_path.exists():
            raise FileNotFoundError(f"클립 {clip['id']} 시작 프레임 없음: {image_path}")
        clip_id = clip["id"]
        # render_clips.py 매핑: 02a → clip_02a.mp4
        output_path = clips_dir / f"clip_{clip_id}.mp4"
        tasks[clip_id] = (image_path, clip["video_prompt"], clip["duration"], output_path)

    results: dict[str, Path] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = {
            pool.submit(generate_video_clip, img, prompt, dur, out): clip_id
            for clip_id, (img, prompt, dur, out) in tasks.items()
        }
        for future in concurrent.futures.as_completed(futures):
            clip_id = futures[future]
            try:
                path = future.result()
                results[clip_id] = path
                if on_progress:
                    on_progress(f"clip_{clip_id} 생성 완료")
            except Exception as e:
                raise RuntimeError(f"clip_{clip_id} 생성 실패: {e}") from e

    return results


def _resolve_image_path(clip: dict, photos_dir: Path, frames_dir: Path) -> Path | None:
    if clip.get("generate_image"):
        return frames_dir / f"{clip['id']}.png"
    source_file = clip.get("source_file")
    if source_file:
        return photos_dir / source_file
    return None
