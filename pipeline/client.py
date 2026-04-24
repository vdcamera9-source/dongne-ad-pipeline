"""
인증 우선순위:
  1. GOOGLE_CLOUD_PROJECT 환경변수 있음 → Vertex AI (ADC, GCP 환경)
  2. GEMINI_API_KEY 환경변수 있음       → Google AI Studio (로컬 개발)
  3. 둘 다 없음                         → RuntimeError
"""
import os
from google import genai

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if project:
            location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            _client = genai.Client(
                vertexai=True,
                project=project,
                location=location,
            )
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "인증 정보 없음.\n"
                    "  GCP 환경: GOOGLE_CLOUD_PROJECT 설정 후 `gcloud auth application-default login`\n"
                    "  로컬 개발: GEMINI_API_KEY 설정"
                )
            _client = genai.Client(api_key=api_key)
    return _client


def is_vertex() -> bool:
    return bool(os.environ.get("GOOGLE_CLOUD_PROJECT"))
