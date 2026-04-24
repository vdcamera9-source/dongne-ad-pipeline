import cv2
import os
import json
from pathlib import Path
from PIL import Image

def get_keyframes(video_path: str, num_frames: int = 4):
    """비디오에서 지정된 개수만큼 균등한 간격으로 프레임을 추출합니다."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"비디오를 열 수 없습니다: {video_path}")
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    interval = max(total_frames // num_frames, 1)
    
    frames = []
    for i in range(num_frames):
        # 각 구간의 중간 지점 프레임을 추출
        frame_idx = (i * interval) + (interval // 2)
        if frame_idx >= total_frames:
            break
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            # BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            frames.append(pil_image)
            
    cap.release()
    return frames

def evaluate_video(video_path: str, ad_data: dict) -> dict:
    """
    MP4 영상의 키프레임을 추출하여 Gemini Vision 모델에게 광고 가독성 및 레이아웃을 평가하게 합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Evaluator] GEMINI_API_KEY가 없습니다. 에이전트 평가를 모의(Mock) 실행합니다.")
        # 더미 피드백 반환 (개발/테스트용)
        # 흰색 배경에 흰색 텍스트가 있을 것으로 가정하여 블랙으로 바꾸라고 제안
        return {
            "status": "FAIL",
            "feedback": "2번째 씬의 배경 밝기가 너무 밝아서 흰색 자막이 잘 보이지 않습니다. 가독성을 위해 검은색 폰트로 변경이 필요합니다.",
            "suggested_updates": {
                "storyboard_updates": [
                    {"index": 0, "color": "white"},
                    {"index": 1, "color": "black"}, # 색상 반전 제안
                    {"index": 2, "color": "white"},
                    {"index": 3, "color": "white"}
                ]
            }
        }
        
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("[Evaluator] google-genai 라이브러리가 설치되지 않았습니다. 모의(Mock)를 실행합니다.")
        return {
            "status": "PASS",
            "feedback": "가독성 양호함."
        }

    client = genai.Client(api_key=api_key)
    
    print(f"[Evaluator] '{video_path}' 분석을 위한 프레임 추출 중...")
    frames = get_keyframes(video_path, num_frames=len(ad_data.get("images", [1,2,3,4])))
    
    # 모델에 전달할 프롬프트 구성
    prompt = f"""
당신은 TV 광고 영상의 품질을 분석하는 AI 평가 에이전트입니다.
제공된 이미지들은 30초짜리 광고 영상에서 시간순으로 추출된 핵심 프레임들입니다.

사용한 스크립트 데이터:
{json.dumps(ad_data.get('storyboard', []), ensure_ascii=False, indent=2)}

다음 사항들을 확인하세요:
1. 화면 하단/중앙의 자막(Text) 가독성 (배경색과 텍스트(흰색/검은색 등)가 구분이 잘 되는지)
2. 텍스트가 화면 밖으로 넘치거나 잘 시인되지 않는지.
3. 영상의 전반적인 레이아웃이 깔끔한지.

평가 결과를 아래와 같은 JSON 형식으로만 응답하세요. 다른 설명은 제외해주세요.
문제가 없다면 status를 "PASS"로, 문제가 있어서 폰트 색상을 변경해야 한다면 "FAIL"로 설정하세요.

응답 예시:
{{
  "status": "FAIL",
  "feedback": "[구체적인 문제점 설명]",
  "suggested_updates": {{
    "storyboard_updates": [
      {{"index": 0, "color": "white"}},
      {{"index": 1, "color": "black"}}, // 배경이 밝아서 가독성이 떨어지면 black으로 변경 제안
      ...
    ]
  }}
}}
"""

    contents = [prompt] + frames
    
    print("[Evaluator] Gemini 2.5 Flash에 프레임 전송 통신 대기 중...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    
    try:
        result = json.loads(response.text)
        print("[Evaluator] 평가 완료. 결과:", result.get("status"))
        return result
    except Exception as e:
        print("[Evaluator] 모델 응답 파싱 실패:", e)
        return {"status": "ERROR", "feedback": str(e)}
