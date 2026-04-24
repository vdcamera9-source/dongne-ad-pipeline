import os
import shutil
from pathlib import Path
from render_story import render_story_ad
from agents.evaluator import evaluate_video
from agents.refiner import refine_ad_data

def run_auto_iterative_pipeline(initial_ad_data: dict, output_dir: str, max_iterations: int = 2) -> str:
    """
    AI 에이전트를 이용해 비디오를 렌더링하고, 평가 후 실패 시 재렌더링하는 루프를 실행합니다.
    """
    os.makedirs(output_dir, exist_ok=True)
    current_data = initial_ad_data
    
    # Iteration loop
    for iteration in range(1, max_iterations + 1):
        print(f"\n==============================================")
        print(f"[LOOP] [Iteration {iteration}/{max_iterations}] 파이프라인 시작")
        print(f"==============================================")
        
        # 1. 렌더링
        video_filename = f"auto_ad_v{iteration}.mp4"
        video_path = os.path.join(output_dir, video_filename)
        
        print(f"[AutoRender] 비디오 렌더링 중... (대상: {video_path})")
        # 실패하지 않는다고 가정하고 렌더링
        render_story_ad(current_data, video_path)
        
        # 2. VLM 에이전트 평가
        print(f"[AutoRender] Evaluator Agent 호출 중...")
        eval_result = evaluate_video(video_path, current_data)
        
        status = eval_result.get("status", "ERROR")
        
        if status == "PASS":
            print(f"[AutoRender] [SUCCESS] 평가 통과! 이 비디오가 최종본으로 승인되었습니다.")
            final_path = os.path.join(output_dir, "auto_ad_final.mp4")
            shutil.copy(video_path, final_path)
            return final_path
            
        elif status == "FAIL":
            feedback = eval_result.get("feedback", "")
            print(f"[AutoRender] [WARNING] 평가 실패: {feedback}")
            print(f"[AutoRender] 개선 사항을 적용하기 위해 Refiner Agent를 호출합니다.")
            
            if "suggested_updates" in eval_result:
                current_data = refine_ad_data(current_data, eval_result["suggested_updates"])
            else:
                print("[AutoRender] 수정 제안 내역이 없어 더 이상 반복할 수 없습니다.")
                return video_path
        else:
            print("[AutoRender] [ERROR] 평가 중 오류가 발생했습니다. 루프를 종료합니다.")
            return video_path

    print(f"\n[AutoRender] [END] 최대 반복 횟수({max_iterations})에 도달했습니다.")
    return video_path

if __name__ == "__main__":
    # 간단한 더미 데이터로 실행
    base_dir = Path(r"C:\Users\SEC\.gemini\antigravity\brain\a8ed483a-e080-4d51-b892-335a3ff6fa2d")
    
    # 일부러 하얀 배경의 로고나 화사한 인테리어를 넣어 흰색 글씨 가독성이 떨어지는 상황 세팅
    ad_data = {
        "store_name": "나노 바나나 자동화 테스트",
        "phone": "02-123-4567",
        "address": "에이전트 개선 테스트",
        "logo_image": str(base_dir / "nanobanana_logo_1776913157143.png"),
        "template": "story",
        "images": [
            str(base_dir / "nanobanana_exterior_1776913208864.png"),
            str(base_dir / "nanobanana_product_1776913178089.png") # 짧게 2컷만 (빠른 테스트)
        ],
        "storyboard": [
            {"text": "배경이 밝으면 텍스트가\n잘 보이지 않을 수 있습니다.", "color": "white"},
            {"text": "에이전트가 이를 감지하고\n수정해야 합니다.", "color": "white"}
        ],
        "bgm_path": ""  
    }
    
    final_video = run_auto_iterative_pipeline(ad_data, "output/agent_test")
    print(f"최종 비디오가 저장되었습니다: {final_video}")
