import os
from pathlib import Path
from render_story import render_story_ad

def run_test():
    base_dir = Path(r"C:\Users\SEC\.gemini\antigravity\brain\a8ed483a-e080-4d51-b892-335a3ff6fa2d")
    
    ad_data = {
        "store_name": "나노 바나나",
        "phone": "02-123-4567",
        "address": "서울 프리미엄 라운지",
        "logo_image": str(base_dir / "nanobanana_logo_1776913157143.png"),
        "template": "story",
        "images": [
            str(base_dir / "nanobanana_product_1776913178089.png"),
            str(base_dir / "nanobanana_interior_1776913192857.png"),
            str(base_dir / "nanobanana_exterior_1776913208864.png"),
            str(base_dir / "nanobanana_product_1776913178089.png") # 마지막은 제품을 다시
        ],
        "storyboard": [
            {"text": "바나나의 정점\n나노 바나나입니다."},
            {"text": "최고의 숙성 과정으로\n프리미엄을 선사합니다."},
            {"text": "도심 속 럭셔리 라운지에서\n경험해보세요."},
            {"text": "가장 소중한 분을 모시는\n마음으로 준비했습니다."}
        ],
        "bgm_path": ""  # BGM 없이 렌더링 (빠름)
    }

    output_file = "output/nanobanana_story_30s.mp4"
    if os.path.exists(output_file):
        os.remove(output_file)

    print("렌더링 시작...")
    try:
        render_story_ad(ad_data, output_file)
        print("[SUCCESS] 스토리 템플릿 렌더링 완료:", output_file)
    except Exception as e:
        print("[ERROR] 스토리 템플릿 렌더링 중 오류:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
