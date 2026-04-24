import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"
FALLBACK_FONT = None  # PIL default


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        FONT_DIR / "Pretendard-Bold.ttf",
        FONT_DIR / "NotoSansKR-Bold.ttf",
        FONT_DIR / "NotoSerifKR-Bold.otf",
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except Exception:
                continue
    # PIL 기본 폰트 fallback (한글 깨질 수 있음)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def draw_text_on_frame(
    frame: np.ndarray,
    text: str,
    position: tuple[int, int],
    font_size: int,
    color: tuple[int, int, int],
    alpha: float = 1.0,
    align: str = "center",
    max_width: int | None = None,
    shadow: bool = True,
) -> np.ndarray:
    """frame numpy array 위에 텍스트를 그려 반환."""
    img = Image.fromarray(frame).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = _load_font(font_size)
    lines = _wrap_text(text, font, draw, max_width or img.width - 120)

    x, y = position
    line_height = font_size + 8

    # 전체 텍스트 블록 높이 계산 후 중앙 정렬 오프셋
    total_h = line_height * len(lines)
    y -= total_h // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]

        if align == "center":
            lx = x - line_w // 2
        elif align == "right":
            lx = x - line_w
        else:
            lx = x

        # 그림자
        if shadow:
            a = int(alpha * 180)
            draw.text((lx + 3, y + 3), line, font=font, fill=(0, 0, 0, a))

        a = int(alpha * 255)
        draw.text((lx, y), line, font=font, fill=(*color, a))
        y += line_height

    composited = Image.alpha_composite(img, overlay).convert("RGB")
    return np.array(composited)


def _wrap_text(text: str, font, draw: ImageDraw.ImageDraw, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]
