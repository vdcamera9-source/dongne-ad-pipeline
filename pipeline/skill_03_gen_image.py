"""
Skill 03 — 16:9 이미지 생성
- Vertex AI: Imagen 3 (imagen-3.0-generate-002)
- AI Studio: Nano Banana Pro (gemini-3-pro-image-preview)
출력: workspace/05_start_frames/{clip_id}.png
"""
from __future__ import annotations
from pathlib import Path
from google.genai import types
from .client import get_client, is_vertex
from .models import image_gen_model


def generate_frame_image(
    clip: dict,
    workspace: Path,
) -> Path:
    prompt = clip.get("image_prompt")
    if not prompt:
        raise ValueError(f"clip {clip['id']}: image_prompt가 없습니다.")

    client = get_client()
    model = image_gen_model()

    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
        ),
    )

    # Vertex AI(Imagen 3)와 AI Studio 모두 동일한 응답 구조 사용
    image_bytes = response.generated_images[0].image.image_bytes

    frames_dir = workspace / "05_start_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    out = frames_dir / f"{clip['id']}.png"
    out.write_bytes(image_bytes)
    return out
