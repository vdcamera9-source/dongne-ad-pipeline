"""
Google Cloud / AI Studio 통합 클라이언트
- Text/Vision 분할 (Gemini 2.5 Flash, 3.1 Pro 등)
- Image Generation (Gemini 3.1 Flash Image)
- Video Generation (Veo 3.1)
"""
import io
import os
import time
from pathlib import Path
from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception

# 타임아웃/설정
POLL_INTERVAL = 10


def _is_retryable(exc) -> bool:
    """429(quota) 및 400(bad request)은 재시도 의미 없음 → 즉시 실패."""
    if hasattr(exc, 'status_code') and exc.status_code in (400, 429):
        return False
    return True


def _get_client():
    if not genai:
        raise ImportError("google-genai 패키지가 설치되지 않았습니다. (uv add google-genai)")
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    return genai.Client()


@retry(wait=wait_exponential(multiplier=2, max=30), stop=stop_after_attempt(8),
       retry=retry_if_exception(_is_retryable))
def chat(prompt: str, model: str = "gemini-3.1-pro-preview") -> str:
    """텍스트 생성 (스토리보드 등)"""
    client = _get_client()
    # Gemini 3.1 Pro는 스토리보싱에 아주 강력함
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text


@retry(wait=wait_exponential(multiplier=2, max=30), stop=stop_after_attempt(8),
       retry=retry_if_exception(_is_retryable))
def chat_vision(prompt: str, image_path: Path, model: str = "gemini-2.5-flash") -> str:
    """이미지 포함 멀티모달 분석"""
    client = _get_client()
    img = Image.open(image_path)
    # Gemini 2.5 Flash는 영상/이미지 분석 속도와 가성비가 모두 뛰어남
    response = client.models.generate_content(
        model=model,
        contents=[img, prompt],
    )
    return response.text


@retry(wait=wait_exponential(multiplier=2, max=30), stop=stop_after_attempt(8),
       retry=retry_if_exception(_is_retryable))
def generate_image(prompt: str, output_path: Path, model: str = "gemini-3.1-flash-image-preview"):
    """
    이미지 생성 (Gemini 3.1 Flash Image 또는 Imagen 3)
    기본 해상도를 16:9 1280x720 류로 통일
    """
    client = _get_client()
    result = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/jpeg",
            aspect_ratio="16:9",
        )
    )
    
    if not result.generated_images:
        raise RuntimeError("이미지 생성에 실패했습니다.")
        
    generated_image = result.generated_images[0]
    image_bytes = generated_image.image.image_bytes
    
    with open(output_path, "wb") as f:
        f.write(image_bytes)
        
    return output_path


@retry(wait=wait_exponential(multiplier=2, max=60), stop=stop_after_attempt(3),
       retry=retry_if_exception(_is_retryable))
def generate_video(prompt: str, output_path: Path, image_path: Path = None, model: str = "veo-3.1-lite-generate-preview"):
    """
    비디오 클립 생성 (Veo 3.1)
    - 비동기 처리 후 폴링 대기
    """
    client = _get_client()
    
    # Veo API가 이미지-투-비디오를 어떻게 받는지 (contents 배열 혹은 image parameter)
    # google-genai SDK 0.5+ 기준으로 generate_videos를 사용합니다.
    # 시작 이미지가 있다면 프롬프트 텍스트 안에 같이 넣거나, kwargs로 넘겨야 할 수 있습니다. (현재 텍스트 기반 우선)
    # 만약 Veo가 입력 이미지를 받을 경우를 대비해, 로직 유연성 확보
    
    kwargs = {
        "model": model,
        "prompt": prompt,
    }
    
    # [TO-DO] Veo I2V(Google AI Studio) 파라미터가 명확해지면 아래를 활성화
    # if image_path:
    #    img = Image.open(image_path)
    #    kwargs["video_source"] = img # 임의 파라미터 가정
        
    operation = client.models.generate_videos(**kwargs)
    
    while not getattr(operation, 'done', False):
        time.sleep(POLL_INTERVAL)
        operation = client.operations.get(operation=operation)
        
    if getattr(operation, 'error', None):
        raise RuntimeError(f"비디오 생성 에러: {operation.error}")

    # operation.response 내부에 결과가 담깁니다 (버전에 따라 result()가 있거나 response 필드가 있음)
    result = getattr(operation, 'response', None)
    if not result and hasattr(operation, 'result'):
        result = operation.result()
        
    if not result or not getattr(result, 'generated_videos', None):
        raise RuntimeError(f"비디오 클립 생성에 실패하거나 응답이 없습니다.")
    
    video_obj = result.generated_videos[0].video
    if video_obj.video_bytes:
        video_bytes = video_obj.video_bytes
    else:
        # uri로 넘어온 경우 download() 호출 (Google GenAI SDK)
        video_bytes = client.files.download(file=video_obj)

    with open(output_path, "wb") as f:
        f.write(video_bytes)
        
    return output_path
