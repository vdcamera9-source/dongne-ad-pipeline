"""Scene 1: Hook (0~3초) – 대표 이미지 + 메인 카피 spring 등장."""
import numpy as np
from moviepy import VideoClip

from config import Theme, WIDTH, HEIGHT, FPS
from effects.ken_burns import apply_ken_burns
from effects.text_overlay import draw_text_on_frame


def _ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)


def create_hook_scene(
    image_path: str,
    main_copy: str,
    theme: Theme,
    duration: float = 3.0,
) -> VideoClip:
    kb_clip = apply_ken_burns(
        image_path,
        duration=duration,
        zoom_start=1.0,
        zoom_end=theme.ken_burns_zoom_end,
        target_size=(WIDTH, HEIGHT),
    )

    # 그라데이션 오버레이 (하단 50%) – PIL로 생성
    from PIL import Image
    grad_h = HEIGHT // 2
    bg_r, bg_g, bg_b = theme.bg_color
    gradient = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    for i in range(grad_h):
        alpha = int(theme.overlay_alpha * (i / grad_h))
        gradient[HEIGHT - grad_h + i, :] = [bg_r, bg_g, bg_b, alpha]

    def make_frame(t: float) -> np.ndarray:
        base = kb_clip.get_frame(t)

        # 그라데이션 합성
        from PIL import Image as PILImage
        img = PILImage.fromarray(base).convert("RGBA")
        overlay = PILImage.fromarray(gradient, "RGBA")
        img = PILImage.alpha_composite(img, overlay).convert("RGB")
        frame = np.array(img)

        # 텍스트 spring 등장: 0.3초 딜레이 후 등장
        delay = 0.3
        if t < delay:
            text_alpha = 0.0
            text_y_offset = 60
        else:
            progress = min((t - delay) / (duration - delay), 1.0)
            eased = _ease_in_out(progress)
            text_alpha = eased
            text_y_offset = int(60 * (1 - eased))

        if text_alpha > 0.01:
            frame = draw_text_on_frame(
                frame,
                main_copy,
                position=(WIDTH // 2, HEIGHT - 160 + text_y_offset),
                font_size=theme.font_size_main,
                color=theme.text_color,
                alpha=text_alpha,
                align="center",
                max_width=WIDTH - 240,
                shadow=True,
            )

        return frame

    return VideoClip(make_frame, duration=duration)
