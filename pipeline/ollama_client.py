"""
Ollama 로컬 API 클라이언트 (http://localhost:11434)

모델 분리:
- TEXT_MODEL  : SuperGemma4-26b (Q4) — /api/generate raw 모드 (텍스트 스토리보드)
- VISION_MODEL: gemma4:e4b — /api/chat 멀티모달 (이미지 분석)

SuperGemma는 TEMPLATE {{ .Prompt }} 포맷이라 /api/chat 500 오류 → /api/generate 사용
"""
from __future__ import annotations
import base64
import json
import os
from pathlib import Path

import requests

OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# 텍스트 생성 (스토리보드, 씬 배정) — SuperGemma4 raw generate 모드
TEXT_MODEL = os.environ.get(
    "OLLAMA_TEXT_MODEL",
    "iaprofesseur/SuperGemma4-26b-uncensored-Q4:latest"
)

# 비전 (이미지 분석) — gemma4:e4b /api/chat 멀티모달
VISION_MODEL = os.environ.get(
    "OLLAMA_VISION_MODEL",
    "gemma4:e4b"
)

# 하위 호환용 (기존 코드가 DEFAULT_MODEL 참조하는 경우)
DEFAULT_MODEL = TEXT_MODEL

TIMEOUT = 600  # 최대 10분


def chat(prompt: str, model: str | None = None) -> str:
    """
    텍스트 전용 생성.
    SuperGemma (TEMPLATE {{ .Prompt }}) → /api/generate
    기타 chat 지원 모델 → /api/chat
    """
    if model is None:
        model = TEXT_MODEL

    # SuperGemma는 raw generate 모드
    if "SuperGemma" in model or "supergemma" in model.lower():
        return _generate(prompt, model)

    url = f"{OLLAMA_BASE}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.3},
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _generate(prompt: str, model: str) -> str:
    """Ollama /api/generate — TEMPLATE {{ .Prompt }} 형식 모델용."""
    url = f"{OLLAMA_BASE}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["response"]


def chat_vision(prompt: str, image_path: Path, model: str | None = None) -> str:
    """이미지 + 텍스트 멀티모달 생성 — gemma4:e4b /api/chat."""
    if model is None:
        model = VISION_MODEL
    img_b64 = base64.b64encode(image_path.read_bytes()).decode()
    url = f"{OLLAMA_BASE}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [img_b64],
            }
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def parse_json(raw: str) -> dict | list:
    """LLM 응답에서 JSON 추출 (```json 코드블록 처리)."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


def is_available() -> bool:
    """Ollama 서버 실행 여부 확인."""
    try:
        requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return True
    except Exception:
        return False
