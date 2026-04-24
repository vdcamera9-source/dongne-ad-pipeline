"""렌더링 파이프라인 테스트 – 3종 템플릿 각각 MP4 생성 후 검증."""
from __future__ import annotations

import subprocess
import json
from pathlib import Path

from render import render_ad_video

DEMO_DIR = Path("assets/demo")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

BASE_AD_DATA = {
    "store_name": "성수 커피랩",
    "category": "카페",
    "address": "성수동 2-5-8",
    "hours": "매일 9AM-9PM",
    "phone": "02-1234-5678",
    "main_copy": "오늘 하루, 한잔의 여유",
    "sub_copy": "핸드드립으로 내리는 동네 카페",
    "cta": "성수동 2-5-8 | 매일 9AM-9PM",
    "storyboard": [
        {"scene": 1, "duration": 3, "visual_desc": "커피 내리는 클로즈업", "text": "오늘 하루, 한잔의 여유"},
        {"scene": 2, "duration": 5, "visual_desc": "카페 내부 전경 + 메뉴판", "text": "핸드드립 아메리카노 4,500원"},
        {"scene": 3, "duration": 4, "visual_desc": "창가 자리 분위기", "text": "단골 리뷰: '분위기가 너무 좋아요'"},
        {"scene": 4, "duration": 3, "visual_desc": "가게 외관 + QR코드", "text": "성수동 2-5-8 | 지금 방문하세요"},
    ],
    "images": [
        str(DEMO_DIR / "scene1_hero.png"),
        str(DEMO_DIR / "scene2_menu.png"),
        str(DEMO_DIR / "scene3_interior.png"),
        str(DEMO_DIR / "scene4_exterior.png"),
    ],
    "qr_url": "https://dongne.app/r?ad_id=123&store_id=456",
    "bgm_path": "",
}

TEMPLATES = ["warm", "lively", "premium"]


def check_video(path: str) -> dict:
    """ffprobe로 영상 메타데이터 검증."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return {"error": "ffprobe failed"}
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        streams = data.get("streams", [])
        video_stream = next((s for s in streams if s["codec_type"] == "video"), {})
        return {
            "duration": round(duration, 2),
            "width": video_stream.get("width"),
            "height": video_stream.get("height"),
            "codec": video_stream.get("codec_name"),
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    print("=" * 60)
    print("동네방네 렌더링 파이프라인 테스트")
    print("=" * 60)

    results = []
    for template in TEMPLATES:
        print(f"\n[{template.upper()}] 렌더링 중...")
        ad_data = {**BASE_AD_DATA, "template": template}
        output_path = str(OUTPUT_DIR / f"test_{template}.mp4")

        try:
            render_ad_video(ad_data, output_path)
            meta = check_video(output_path)
            size_mb = Path(output_path).stat().st_size / 1024 / 1024

            ok = (
                meta.get("duration", 0) >= 14.5
                and meta.get("width") == 1920
                and meta.get("height") == 1080
            )
            status = "✅ PASS" if ok else "⚠️  WARN"
            print(f"  {status} | 길이: {meta.get('duration')}s | {meta.get('width')}x{meta.get('height')} | {size_mb:.1f}MB")
            results.append((template, ok, meta))
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            results.append((template, False, {}))

    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    all_pass = all(r[1] for r in results)
    for template, ok, meta in results:
        mark = "✅" if ok else "❌"
        print(f"  {mark} {template}: {meta}")
    print(f"\n최종: {'ALL PASS' if all_pass else 'SOME FAILED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
