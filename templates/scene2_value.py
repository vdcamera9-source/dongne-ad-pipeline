"""Scene 2: Value (3~8초) – 메뉴/가격 슬라이드 (이미지 2장 순환)."""
import numpy as np
from PIL import Image
from moviepy import VideoClip

from config import Theme, WIDTH, HEIGHT
from effects.text_overlay import draw_text_on_frame


def _slide_progress(t: float, total: float) -> float:
    return min(t / total, 1.0)


def create_value_scene(
    images: list[str],
    text: str,
    theme: Theme,
    duration: float = 5.0,
) -> VideoClip:
    # 이미지 최대 2장
    imgs = images[:2]
    if not imgs:
        imgs = []

    loaded: list[np.ndarray] = []
    for p in imgs:
        try:
            img = Image.open(p).convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
            loaded.append(np.array(img))
        except Exception:
            loaded.append(np.full((HEIGHT, WIDTH, 3), theme.bg_color, dtype=np.uint8))

    if not loaded:
        loaded.append(np.full((HEIGHT, WIDTH, 3), theme.bg_color, dtype=np.uint8))

    slide_dur = duration / len(loaded)  # 각 이미지 표시 시간
    transition = min(theme.transition_duration, slide_dur * 0.4)

    def make_frame(t: float) -> np.ndarray:
        idx = min(int(t / slide_dur), len(loaded) - 1)
        local_t = t - idx * slide_dur

        current = loaded[idx].copy()
        next_img = loaded[idx + 1] if idx + 1 < len(loaded) else None

        # 슬라이드 전환
        if next_img is not None and local_t > slide_dur - transition:
            progress = (local_t - (slide_dur - transition)) / transition
            progress = max(0.0, min(1.0, progress))
            # 좌→우 슬라이드: current가 왼쪽으로 나가고 next가 오른쪽에서 들어옴
            offset = int(WIDTH * progress)
            frame = np.full((HEIGHT, WIDTH, 3), theme.bg_color, dtype=np.uint8)
            frame[:, :WIDTH - offset] = current[:, offset:]
            frame[:, WIDTH - offset:] = next_img[:, :offset]
        else:
            frame = current

        # 배경 오버레이 (하단 영역)
        overlay_h = 220
        img_pil = Image.fromarray(frame).convert("RGBA")
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        r, g, b = theme.bg_color
        for i in range(overlay_h):
            alpha = int(theme.overlay_alpha * (i / overlay_h))
            ov.paste(
                Image.new("RGBA", (WIDTH, 1), (r, g, b, alpha)),
                (0, HEIGHT - overlay_h + i),
            )
        frame = np.array(Image.alpha_composite(img_pil, ov).convert("RGB"))

        # 텍스트
        frame = draw_text_on_frame(
            frame,
            text,
            position=(WIDTH // 2, HEIGHT - 100),
            font_size=theme.font_size_sub,
            color=theme.text_color,
            alpha=min(local_t / 0.4, 1.0),
            align="center",
            max_width=WIDTH - 240,
            shadow=True,
        )
        return frame

    return VideoClip(make_frame, duration=duration)
