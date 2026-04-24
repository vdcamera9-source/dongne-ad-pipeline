import os
from pathlib import Path
from render_story import render_story_ad

def run_test():
    base_dir = Path(r"C:\Users\SEC\.gemini\antigravity\brain\a8ed483a-e080-4d51-b892-335a3ff6fa2d")
    
    ad_data = {
        "store_name": "우판등심",
        "phone": "02-987-6543",
        "address": "프리미엄 한우 전문점",
        "logo_image": str(base_dir / "upan_logo_1776916568780.png"),
        "template": "story",
        "images": [
            str(base_dir / "upan_raw_meat_1776916582728.png"),
            str(base_dir / "upan_raw_meat_1776916582728.png"), # 첫 씬과 두 번째 씬은 생고기 강조
            str(base_dir / "upan_grill_1776916597161.png"),
            str(base_dir / "upan_interior_1776916611156.png")
        ],
        "storyboard": [
            {"text": "우판등심은 당신에게 오는\n과정부터 다릅니다."},
            {"text": "고기 관리부터 숙성까지\n차곡차곡 쌓인 경험을 대접합니다."},
            {"text": "누군가에게 귀한 음식을 대접하고픈\n당신의 마음을 헤아리는 갈비 전문점."},
            {"text": "모든 고객을 VIP로\n생각하겠습니다."}
        ],
        "bgm_path": ""  # BGM 없이 렌더링
    }

    output_file = "output/upan_story_30s.mp4"
    if os.path.exists(output_file):
        os.remove(output_file)

    print("렌더링 시작...")
    try:
        render_story_ad(ad_data, output_file)
        print("[SUCCESS] 우판등심 스토리 템플릿 렌더링 완료:", output_file)
    except Exception as e:
        print("[ERROR] 우판등심 스토리 템플릿 렌더링 중 오류:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
