"""Scene 4: CTA (12~15초) – 가게 외관 + QR 코드 fade-in + CTA 텍스트."""
import numpy as np
from PIL import Image
from moviepy import VideoClip

from config import Theme, WIDTH, HEIGHT
from effects.ken_burns import apply_ken_burns
from effects.text_overlay import draw_text_on_frame
from effects.qr_overlay import apply_qr_to_frame


def create_cta_scene(
    image_path: str,
    store_name: str,
    cta: str,
    qr_url: str,
    theme: Theme,
    duration: float = 3.0,
) -> VideoClip:
    kb_clip = apply_ken_burns(
        image_path,
        duration=duration,
        zoom_start=1.0,
        zoom_end=1.05,
        target_size=(WIDTH, HEIGHT),
    )

    def make_frame(t: float) -> np.ndarray:
        base = kb_clip.get_frame(t)

        # 하단 그라데이션
        img_pil = Image.fromarray(base).convert("RGBA")
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        ov_h = HEIGHT // 2
        r, g, b = theme.bg_color
        for i in range(ov_h):
            alpha = int(theme.overlay_alpha * (i / ov_h))
            ov.paste(Image.new("RGBA", (WIDTH, 1), (r, g, b, alpha)), (0, HEIGHT - ov_h + i))
        frame = np.array(Image.alpha_composite(img_pil, ov).convert("RGB"))

        fade = min(t / 0.4, 1.0)

        # 가게명
        frame = draw_text_on_frame(
            frame,
            store_name,
            position=(WIDTH // 2, HEIGHT - 280),
            font_size=theme.font_size_main,
            color=theme.accent_color,
            alpha=fade,
            align="center",
            max_width=WIDTH - 400,
            shadow=True,
        )

        # CTA 텍스트 (주소 + 영업시간)
        frame = draw_text_on_frame(
            frame,
            cta,
            position=(WIDTH // 2, HEIGHT - 160),
            font_size=theme.font_size_cta,
            color=theme.text_color,
            alpha=fade,
            align="center",
            max_width=WIDTH - 400,
            shadow=True,
        )

        # QR 코드 – 0.5초 후 fade-in
        qr_fade = max(0.0, min((t - 0.5) / 0.5, 1.0))
        if qr_url and qr_fade > 0:
            frame = apply_qr_to_frame(frame, qr_url, size=200, margin=80, fade_progress=qr_fade)

        return frame

    return VideoClip(make_frame, duration=duration)
