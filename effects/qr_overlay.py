import numpy as np
import qrcode
from PIL import Image


def generate_qr_image(url: str, size: int = 200) -> Image.Image:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size, size), Image.LANCZOS)


def apply_qr_to_frame(
    frame: np.ndarray,
    url: str,
    size: int = 200,
    margin: int = 80,
    fade_progress: float = 1.0,  # 0.0~1.0
) -> np.ndarray:
    """frame 우하단에 QR 코드를 fade-in하며 합성."""
    qr_img = generate_qr_image(url, size)

    # 흰 배경 + 패딩 박스
    pad = 16
    box_size = size + pad * 2
    box = Image.new("RGBA", (box_size, box_size), (255, 255, 255, int(255 * fade_progress)))
    box.paste(qr_img, (pad, pad))

    base = Image.fromarray(frame).convert("RGBA")
    h, w = frame.shape[:2]
    x = w - box_size - margin
    y = h - box_size - margin

    box_faded = box.copy()
    # alpha 채널 전체에 fade_progress 적용
    r, g, b, a = box_faded.split()
    a = a.point(lambda p: int(p * fade_progress))
    box_faded = Image.merge("RGBA", (r, g, b, a))

    base.paste(box_faded, (x, y), box_faded)
    return np.array(base.convert("RGB"))
