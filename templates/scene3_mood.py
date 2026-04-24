"""Scene 3: Mood (8~12초) – 내부 사진 Ken Burns + 리뷰 인용."""
import numpy as np
from PIL import Image
from moviepy import VideoClip

from config import Theme, WIDTH, HEIGHT
from effects.ken_burns import apply_ken_burns
from effects.text_overlay import draw_text_on_frame


def create_mood_scene(
    image_path: str,
    review_text: str,
    theme: Theme,
    duration: float = 4.0,
) -> VideoClip:
    kb_clip = apply_ken_burns(
        image_path,
        duration=duration,
        zoom_start=1.0,
        zoom_end=theme.ken_burns_zoom_end,
        target_size=(WIDTH, HEIGHT),
    )

    # 리뷰 박스 배경 (반투명)
    def make_frame(t: float) -> np.ndarray:
        base = kb_clip.get_frame(t)

        # 다크 오버레이 (상단 40%)
        img_pil = Image.fromarray(base).convert("RGBA")
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        ov_h = HEIGHT * 2 // 5
        r, g, b = theme.bg_color
        for i in range(ov_h):
            alpha = int(120 * (1 - i / ov_h))
            ov.paste(Image.new("RGBA", (WIDTH, 1), (r, g, b, alpha)), (0, i))
        frame = np.array(Image.alpha_composite(img_pil, ov).convert("RGB"))

        # 리뷰 텍스트 – fade in
        text_alpha = min(t / 0.6, 1.0)
        # 리뷰 박스 반투명 배경
        box_w, box_h = WIDTH - 400, 160
        box_x = 200
        box_y = HEIGHT // 2 - box_h // 2
        img2 = Image.fromarray(frame).convert("RGBA")
        box_img = Image.new("RGBA", (box_w, box_h), (*theme.bg_color, int(200 * text_alpha)))
        img2.paste(box_img, (box_x, box_y), box_img)
        frame = np.array(img2.convert("RGB"))

        frame = draw_text_on_frame(
            frame,
            review_text,
            position=(WIDTH // 2, HEIGHT // 2),
            font_size=theme.font_size_sub,
            color=theme.text_color,
            alpha=text_alpha,
            align="center",
            max_width=WIDTH - 480,
            shadow=False,
        )
        return frame

    return VideoClip(make_frame, duration=duration)
