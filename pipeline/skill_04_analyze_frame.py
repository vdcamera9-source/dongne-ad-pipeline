"""
Skill 04 — 시작 프레임 이미지 분석 (Gemini Vision)
입력: 각 clip의 시작 프레임 이미지
출력: clip_plan에 camera_move 정보 추가 → workspace/05_frame_analysis.json
"""
from __future__ import annotations
import json
from pathlib import Path
from google.genai import types
from .client import get_client
from .models import gemini_flash

PROMPT = """이 광고 영상의 시작 프레임 이미지를 분석해서 최적의 카메라 무브를 추천하세요.

씬 정보:
- 역할: {role}
- 영상 길이: {duration}초

분석 기준:
- 피사체 위치 (center/left/right/bottom/top)
- 여백 방향 (텍스트 오버레이 배치에 사용)
- 조명 방향
- 움직임 포인트 (연기, 액체, 질감 등)

카메라 무브 선택:
- Hook 씬: Dolly In (클로즈업 → 더 클로즈업)
- Value 씬: Pan Right (왼쪽 여백 → 오른쪽 메뉴)
- Mood 씬: Slow Pan Right (공간 탐색)
- CTA 씬: Dolly Out (전체 노출)

반드시 아래 JSON만 반환 (마크다운 없이):
{{
  "subject_position": "center",
  "empty_space": "bottom",
  "light_direction": "top-left",
  "motion_points": ["steam_rising", "texture"],
  "text_zone": "bottom_third",
  "recommended_camera": "Dolly In (slow)",
  "color_notes": "already warm, saturation x1.3 only"
}}
"""


def analyze_frame(image_path: Path, clip: dict) -> dict:
    """단일 프레임 이미지 분석 → 카메라 무브 dict 반환."""
    data = image_path.read_bytes()
    suffix = image_path.suffix.lower()
    mime = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"

    client = get_client()

    response = client.models.generate_content(
        model=gemini_flash(),
        contents=[types.Content(role="user", parts=[
            types.Part.from_bytes(data=data, mime_type=mime),
            types.Part.from_text(text=PROMPT.format(
                role=clip.get("role", ""),
                duration=clip.get("duration", 3),
            )),
        ])],
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    return json.loads(raw)


def analyze_all_frames(
    clip_plan: list[dict],
    photos_dir: Path,
    workspace: Path,
) -> list[dict]:
    """모든 클립의 시작 프레임 분석 → workspace/05_frame_analysis.json 저장."""
    frames_dir = workspace / "05_start_frames"
    results = []

    for clip in clip_plan:
        image_path = _resolve_image_path(clip, photos_dir, frames_dir)
        if not image_path or not image_path.exists():
            results.append({"clip_id": clip["id"], "error": "이미지 없음"})
            continue
        frame_info = analyze_frame(image_path, clip)
        frame_info["clip_id"] = clip["id"]
        frame_info["image_path"] = str(image_path)
        results.append(frame_info)

    out = workspace / "05_frame_analysis.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return results


def _resolve_image_path(clip: dict, photos_dir: Path, frames_dir: Path) -> Path | None:
    if clip.get("generate_image"):
        return frames_dir / f"{clip['id']}.png"
    source_file = clip.get("source_file")
    if source_file:
        return photos_dir / source_file
    return None
