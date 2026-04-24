"""스토리형 30초 프리미엄 메인 렌더링 엔트리포인트."""
from __future__ import annotations

import os
import logging
from pathlib import Path

from moviepy import AudioFileClip, concatenate_videoclips, CompositeVideoClip, vfx

from config import get_theme, FPS, STORY_DURATION
from templates.scene_story import create_story_scene
from effects.overlay import apply_global_overlay

FALLBACK_IMAGE = str(Path(__file__).parent / "assets" / "fallback" / "default.png")
logger = logging.getLogger(__name__)

def _resolve_image(path: str) -> str:
    """이미지 경로가 없으면 fallback 이미지 반환."""
    if path and Path(path).exists():
        return path
    logger.warning("Image not found: %s — using fallback", path)
    return FALLBACK_IMAGE

def render_story_ad(ad_data: dict, output_path: str) -> str:
    """
    30초 스토리형 광고 렌더링.
    """
    theme = get_theme(ad_data.get("template", "story"))
    images = ad_data.get("images", [])
    storyboard = ad_data.get("storyboard", []) # [{'text': ...}, ...] 으로 기대함
    
    logo_path = ad_data.get("logo_image", "")
    phone_number = ad_data.get("phone", "")
    address_str = ad_data.get("address", "")
    
    logo_path = _resolve_image(logo_path) if logo_path else ""

    logger.info("스토리형 렌더링 시작: %s / 테마: %s", ad_data.get("store_name"), theme.name)

    # 30초 내에 이미지를 고르게 분배. 기본적으로 5장(장당 6초) 혹은 6장(장당 5초).
    num_scenes = len(images) if images else 1
    duration_per_scene = STORY_DURATION / num_scenes

    scenes = []
    
    for i in range(num_scenes):
        img_path = _resolve_image(images[i])
        text = storyboard[i].get("text", "") if i < len(storyboard) else ""
        text_color = storyboard[i].get("color", "white") if i < len(storyboard) else "white"
        
        scene = create_story_scene(
            image_path=img_path,
            text=text,
            theme=theme,
            duration=duration_per_scene,
            text_color=text_color
        )
        
        # 디졸브 전환 효과 (첫 씬 제외)
        if i > 0:
            scene = scene.with_effects([vfx.CrossFadeIn(1.0)])
            
        scenes.append(scene)

    # 장면 이어붙이기 (Crossfade 적용을 위해 compose 필요하지만 일단 겹침 렌더 구성)
    # concatenate_videoclips에서 method="compose"를 사용해야 CrossFade가 적용됨
    final = concatenate_videoclips(scenes, method="compose")

    # Global Overlay 적용
    final = apply_global_overlay(
        final, 
        logo_path=logo_path, 
        phone=phone_number, 
        address=address_str, 
        font_family=theme.font_family
    )

    # BGM 합성 (길이가 짧을 수 있으므로 loop 적용 혹은 자르기)
    # moviepy v2 에서는 audio 속성을 with_audio나 직접 수정.
    bgm_path = ad_data.get("bgm_path", "")
    if bgm_path and Path(bgm_path).exists():
        bgm = AudioFileClip(bgm_path)
        # BGM이 30초보다 짧으면 반복, 길면 자름
        from moviepy.audio.fx.audio_loop import audio_loop
        bgm = audio_loop(bgm, duration=STORY_DURATION).with_volume_scaled(0.3)
        final = final.with_audio(bgm)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        logger="bar",
    )

    logger.info("스토리형 렌더링 완료: %s", output_path)
    return output_path
