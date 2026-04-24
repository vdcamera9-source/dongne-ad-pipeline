"""3개 광고 세트 렌더링 – 콘셉트별 문구 + 이미지 매칭."""
from __future__ import annotations
from pathlib import Path
from render import render_ad_video
import time

SETS_DIR = Path("assets/sets")
OUTPUT_DIR = Path("output/sets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Set 1. 성수 커피랩  (따뜻한 / warm)
#   카페·베이커리 업종, 감성적 문구, 코랄 강조색
# ──────────────────────────────────────────────
CAFE = {
    "store_name": "성수 커피랩",
    "category": "카페",
    "address": "성동구 성수동 2가 5-8",
    "hours": "매일 09:00 – 21:00",
    "phone": "02-1234-5678",

    "main_copy": "오늘 하루, 한잔의 여유",
    "sub_copy": "직접 로스팅한 원두로 내리는 핸드드립",
    "cta": "성수동 2가 5-8  |  매일 09-21시",

    "storyboard": [
        {"scene": 1, "duration": 3, "visual_desc": "커피 내리는 클로즈업", "text": "오늘 하루,\n한잔의 여유"},
        {"scene": 2, "duration": 5, "visual_desc": "메뉴판 + 컵 슬라이드", "text": "핸드드립 아메리카노\n4,500원"},
        {"scene": 3, "duration": 4, "visual_desc": "창가 자리 분위기", "text": "\"여기 오면 하루가 좋아져요\""},
        {"scene": 4, "duration": 3, "visual_desc": "가게 외관 + QR", "text": "성수동 2가 5-8  |  지금 방문하세요"},
    ],
    "images": [
        str(SETS_DIR / "cafe/img_01.jpg"),   # hook: 커피/음료 클로즈업
        str(SETS_DIR / "cafe/img_03.jpg"),   # value: 메뉴 슬라이드 1
        str(SETS_DIR / "cafe/img_02.jpg"),   # value: 메뉴 슬라이드 2 / mood
        str(SETS_DIR / "cafe/img_05.jpg"),   # cta: 외관
    ],
    "template": "warm",
    "qr_url": "https://dongne.app/r?store=cafe_sungsu",
    "bgm_path": "",
}

# ──────────────────────────────────────────────
# Set 2. 황금치킨  (경쾌한 / lively)
#   치킨·분식 업종, 직관적 가격 강조, 오렌지 강조색
# ──────────────────────────────────────────────
CHICKEN = {
    "store_name": "황금치킨 본점",
    "category": "치킨",
    "address": "마포구 망원동 12-3",
    "hours": "매일 16:00 – 01:00",
    "phone": "02-9876-5432",

    "main_copy": "바삭함이 다르다!",
    "sub_copy": "33년 비법 양념, 황금 후라이드",
    "cta": "망원동 12-3  |  오후 4시 – 새벽 1시",

    "storyboard": [
        {"scene": 1, "duration": 3, "visual_desc": "치킨 클로즈업 + 김 모락모락", "text": "바삭함이 다르다!"},
        {"scene": 2, "duration": 5, "visual_desc": "후라이드·양념 비교 슬라이드", "text": "황금 후라이드\n17,000원"},
        {"scene": 3, "duration": 4, "visual_desc": "가족·친구 함께 먹는 장면", "text": "\"치킨은 역시 황금치킨!\""},
        {"scene": 4, "duration": 3, "visual_desc": "매장 외관 + 배달 앱 QR", "text": "망원동 12-3  |  지금 주문하세요"},
    ],
    "images": [
        str(SETS_DIR / "chicken/img_01.jpg"),
        str(SETS_DIR / "chicken/img_02.jpg"),
        str(SETS_DIR / "chicken/img_03.jpg"),
        str(SETS_DIR / "chicken/img_04.jpg"),
    ],
    "template": "lively",
    "qr_url": "https://dongne.app/r?store=golden_chicken",
    "bgm_path": "",
}

# ──────────────────────────────────────────────
# Set 3. 노을 라운지  (세련된 / premium)
#   바·레스토랑 업종, 감성 카피, 골드 강조색
# ──────────────────────────────────────────────
LOUNGE = {
    "store_name": "노을 라운지",
    "category": "레스토랑·바",
    "address": "용산구 이태원동 77-2  5F",
    "hours": "화–일  18:00 – 02:00",
    "phone": "02-5555-7777",

    "main_copy": "오늘 밤, 특별한 순간",
    "sub_copy": "서울 야경과 함께하는 루프탑 다이닝",
    "cta": "이태원동 77-2  5F  |  화~일 18시–",

    "storyboard": [
        {"scene": 1, "duration": 3, "visual_desc": "야경 + 와인잔 실루엣", "text": "오늘 밤,\n특별한 순간"},
        {"scene": 2, "duration": 5, "visual_desc": "코스 요리 플레이팅 슬라이드", "text": "디너 코스\n65,000원~"},
        {"scene": 3, "duration": 4, "visual_desc": "루프탑 테이블 분위기", "text": "\"서울에서 가장 아름다운 저녁\""},
        {"scene": 4, "duration": 3, "visual_desc": "입구 + 예약 QR", "text": "이태원동 77-2  5F  |  예약 권장"},
    ],
    "images": [
        str(SETS_DIR / "lounge/img_01.jpg"),
        str(SETS_DIR / "lounge/img_02.jpg"),
        str(SETS_DIR / "lounge/img_03.jpg"),
        str(SETS_DIR / "lounge/img_04.jpg"),
    ],
    "template": "premium",
    "qr_url": "https://dongne.app/r?store=noeul_lounge",
    "bgm_path": "",
}

AD_SETS = [
    ("cafe",    CAFE),
    ("chicken", CHICKEN),
    ("lounge",  LOUNGE),
]

if __name__ == "__main__":
    print("=" * 55)
    print("동네방네 광고 세트 렌더링 (3종)")
    print("=" * 55)
    for name, ad_data in AD_SETS:
        out = str(OUTPUT_DIR / f"{name}.mp4")
        print(f"\n[{name.upper()}]  {ad_data['store_name']} / {ad_data['template']}")
        start = time.time()
        render_ad_video(ad_data, out)
        elapsed = time.time() - start
        size_mb = Path(out).stat().st_size / 1024 / 1024
        print(f"  완료: {elapsed:.1f}s  {size_mb:.1f}MB  →  {out}")
    print("\n전체 완료!")
