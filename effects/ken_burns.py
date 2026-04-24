import numpy as np
from moviepy import VideoClip
from PIL import Image


def apply_ken_burns(
    image_path: str,
    duration: float,
    zoom_start: float = 1.0,
    zoom_end: float = 1.15,
    target_size: tuple[int, int] = (1920, 1080),
) -> VideoClip:
    """이미지에 Ken Burns 줌인 효과 적용."""
    w, h = target_size

    # 원본 이미지를 target보다 크게 로드 (zoom 여유분)
    img = Image.open(image_path).convert("RGB")
    max_scale = zoom_end * 1.05
    base_w = int(w * max_scale)
    base_h = int(h * max_scale)
    img = img.resize((base_w, base_h), Image.LANCZOS)
    img_array = np.array(img)

    def make_frame(t: float) -> np.ndarray:
        progress = t / duration if duration > 0 else 1.0
        scale = zoom_start + (zoom_end - zoom_start) * progress

        cur_w = int(w * scale)
        cur_h = int(h * scale)

        x_off = (base_w - cur_w) // 2
        y_off = (base_h - cur_h) // 2
        cropped = img_array[y_off:y_off + cur_h, x_off:x_off + cur_w]

        frame_img = Image.fromarray(cropped).resize((w, h), Image.LANCZOS)
        return np.array(frame_img)

    return VideoClip(make_frame, duration=duration)
