"""
ComfyUI HTTP/WebSocket API 클라이언트

사용 흐름:
  1. queue_prompt(workflow)  → prompt_id
  2. wait_for_result(prompt_id) → 완료된 출력 파일 경로 목록 (서버 기준)
  3. download_output(remote_filename, local_path) → 로컬 Path

ComfyUI API 주소: http://127.0.0.1:8188 (기본값, COMFYUI_URL 환경변수로 재정의)
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path

import requests


COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
WS_URL = COMFYUI_URL.replace("http://", "ws://").replace("https://", "wss://")
POLL_INTERVAL = 2   # seconds
MAX_WAIT = 600       # 10 minutes


# ── 기본 API 호출 ─────────────────────────────────────────────────────────────

def queue_prompt(workflow: dict, client_id: str | None = None) -> str:
    """워크플로우를 대기열에 추가하고 prompt_id 반환."""
    client_id = client_id or uuid.uuid4().hex
    payload = {"prompt": workflow, "client_id": client_id}
    resp = requests.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"ComfyUI 큐 오류: {data['error']}\n{data.get('node_errors', '')}")
    return data["prompt_id"]


def get_history(prompt_id: str) -> dict:
    """prompt_id의 실행 히스토리 반환."""
    resp = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def wait_for_result(prompt_id: str, timeout: int = MAX_WAIT) -> list[dict]:
    """
    prompt_id가 완료될 때까지 polling.
    반환: [{"filename": "...", "subfolder": "...", "type": "output"}, ...]
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = get_history(prompt_id)
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                msgs = status.get("messages", [])
                raise RuntimeError(f"ComfyUI 실행 오류: {msgs}")
            # 출력 파일 수집
            outputs = []
            for node_out in entry.get("outputs", {}).values():
                for key in ("images", "gifs", "videos"):
                    outputs.extend(node_out.get(key, []))
            if outputs:
                return outputs
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"ComfyUI 타임아웃 ({timeout}s): prompt_id={prompt_id}")


def download_output(file_info: dict, local_path: Path) -> Path:
    """
    ComfyUI /view 엔드포인트에서 파일 다운로드.
    file_info: {"filename": "...", "subfolder": "...", "type": "output"}
    """
    params = {
        "filename": file_info["filename"],
        "subfolder": file_info.get("subfolder", ""),
        "type": file_info.get("type", "output"),
    }
    resp = requests.get(f"{COMFYUI_URL}/view", params=params, timeout=120, stream=True)
    resp.raise_for_status()
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_path


def upload_image(image_path: Path, subfolder: str = "") -> str:
    """
    이미지를 ComfyUI 서버에 업로드하고 filename 반환.
    (I2V 워크플로우에서 LoadImage 노드에 전달할 때 사용)
    """
    with open(image_path, "rb") as f:
        files = {"image": (image_path.name, f, "image/png")}
        data = {"overwrite": "true", "subfolder": subfolder}
        resp = requests.post(f"{COMFYUI_URL}/upload/image", files=files, data=data, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    name = result["name"]
    sub = result.get("subfolder", "")
    return f"{sub}/{name}" if sub else name


def is_available() -> bool:
    """ComfyUI 서버 실행 여부 확인."""
    try:
        requests.get(f"{COMFYUI_URL}/system_stats", timeout=3)
        return True
    except Exception:
        return False
