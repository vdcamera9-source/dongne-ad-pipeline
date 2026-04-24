"""데모용 placeholder 이미지 4장 + fallback 이미지 생성."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path("assets")
DEMO_DIR = ASSETS / "demo"
FALLBACK_DIR = ASSETS / "fallback"
DEMO_DIR.mkdir(parents=True, exist_ok=True)
FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    ("scene1_hero.png",     (180, 120, 80),  "Scene 1\n커피 내리는 클로즈업"),
    ("scene2_menu.png",     (200, 160, 100), "Scene 2\n카페 내부 + 메뉴판"),
    ("scene3_interior.png", (160, 140, 120), "Scene 3\n창가 자리 분위기"),
    ("scene4_exterior.png", (120, 100, 80),  "Scene 4\n가게 외관"),
]


def make_placeholder(path: Path, bg: tuple, label: str, size=(1920, 1080)):
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)

    # 그리드 선
    for x in range(0, size[0], 100):
        draw.line([(x, 0), (x, size[1])], fill=(min(bg[0]+30,255), min(bg[1]+30,255), min(bg[2]+30,255)), width=1)
    for y in range(0, size[1], 100):
        draw.line([(0, y), (size[0], y)], fill=(min(bg[0]+30,255), min(bg[1]+30,255), min(bg[2]+30,255)), width=1)

    # 중앙 텍스트
    try:
        font = ImageFont.load_default(size=60)
    except TypeError:
        font = ImageFont.load_default()

    for i, line in enumerate(label.split("\n")):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (size[0] - w) // 2
        y = size[1] // 2 - 60 + i * 80
        draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 100), font=font)
        draw.text((x, y), line, fill=(255, 255, 255), font=font)

    img.save(str(path))
    print(f"  생성: {path}")


print("데모 이미지 생성 중...")
for filename, bg_color, label in SCENES:
    make_placeholder(DEMO_DIR / filename, bg_color, label)

make_placeholder(FALLBACK_DIR / "default.png", (80, 80, 80), "Fallback\nImage")
print("완료!")
