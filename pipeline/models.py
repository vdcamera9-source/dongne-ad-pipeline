"""
AI Studio vs Vertex AI 모델 ID 매핑.

Vertex AI는 일부 preview 모델명이 다르고,
이미지 생성은 Imagen 3 모델을 사용한다.
"""
from .client import is_vertex

def gemini_flash() -> str:
    return "gemini-2.5-flash"

def image_gen_model() -> str:
    if is_vertex():
        return "imagen-3.0-generate-002"
    return "gemini-3-pro-image-preview"

def video_gen_model() -> str:
    return "veo-3.1-lite-generate-preview"
