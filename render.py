"""메인 렌더링 엔트리포인트 – JSON 입력 → MP4 출력."""
from __future__ import annotations

import os
import logging
from pathlib import Path

from moviepy import AudioFileClip, concatenate_videoclips

from config import get_theme, FPS, DURATION
from templates.scene1_hook import create_hook_scene
from templates.scene2_value import create_value_scene
from templates.scene3_mood import create_mood_scene
from templates.scene4_cta import create_cta_scene

FALLBACK_IMAGE = str(Path(__file__).parent / "assets" / "fallback" / "default.png")
logger = logging.getLogger(__name__)


def _resolve_image(path: str) -> str:
    """이미지 경로가 없으면 fallback 이미지 반환."""
    if path and Path(path).exists():
        return path
    logger.warning("Image not found: %s — using fallback", path)
    return FALLBACK_IMAGE


def render_ad_video(ad_data: dict, output_path: str) -> str:
    """
    ad_data: JSON 스키마 (20260422_동네방네_구현.md 섹션 1 참고)
    output_path: 저장할 MP4 경로
    returns: output_path
    """
    theme = get_theme(ad_data.get("template", "warm"))
    images = ad_data.get("images", [])
    storyboard = ad_data.get("storyboard", [])

    def img(idx: int) -> str:
        return _resolve_image(images[idx]) if idx < len(images) else FALLBACK_IMAGE

    def sb_text(idx: int) -> str:
        if idx < len(storyboard):
            return storyboard[idx].get("text", "")
        return ""

    logger.info("렌더링 시작: %s / 테마: %s", ad_data.get("store_name"), theme.name)

    scene1 = create_hook_scene(
        image_path=img(0),
        main_copy=ad_data.get("main_copy", ""),
        theme=theme,
        duration=3.0,
    )

    scene2 = create_value_scene(
        images=[img(1), img(2)],
        text=sb_text(1),
        theme=theme,
        duration=5.0,
    )

    scene3 = create_mood_scene(
        image_path=img(2),
        review_text=sb_text(2),
        theme=theme,
        duration=4.0,
    )

    scene4 = create_cta_scene(
        image_path=img(3),
        store_name=ad_data.get("store_name", ""),
        cta=ad_data.get("cta", ""),
        qr_url=ad_data.get("qr_url", ""),
        theme=theme,
        duration=3.0,
    )

    final = concatenate_videoclips([scene1, scene2, scene3, scene4])

    # BGM 합성
    bgm_path = ad_data.get("bgm_path", "")
    if bgm_path and Path(bgm_path).exists():
        bgm = AudioFileClip(bgm_path).subclipped(0, DURATION).with_volume_scaled(0.3)
        final = final.with_audio(bgm)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        logger=None,  # moviepy 로그 억제
    )

    logger.info("렌더링 완료: %s", output_path)
    return output_path
