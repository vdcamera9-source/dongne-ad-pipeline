"""
Skill 03 — 16:9 이미지 생성 (ComfyUI FLUX.1-schnell fp8)
입력: clip["image_prompt"]
출력: workspace/05_start_frames/{clip_id}.png
"""
from __future__ import annotations
import copy
import json
import random
from pathlib import Path

from .comfyui_client import queue_prompt, wait_for_result, download_output

_WORKFLOW_PATH = Path(__file__).parent / "workflows" / "flux_t2i_api.json"
_WORKFLOW: dict | None = None


def _get_workflow() -> dict:
    global _WORKFLOW
    if _WORKFLOW is None:
        _WORKFLOW = json.loads(_WORKFLOW_PATH.read_text(encoding="utf-8"))
    return _WORKFLOW


def generate_frame_image(
    clip: dict,
    workspace: Path,
    backend: str = "local",
) -> Path:
    prompt = clip.get("image_prompt")
    if not prompt:
        raise ValueError(f"clip {clip['id']}: image_prompt가 없습니다.")

    frames_dir = workspace / "05_start_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    out_path = frames_dir / f"{clip['id']}.jpg" if backend == "api" else frames_dir / f"{clip['id']}.png"

    if backend == "api":
        print(f"  Gemini Flash Image 이미지 생성: {clip['id']} / {prompt[:60]}...")
        from .google_client import generate_image as g_gen_image
        # API는 jpg로 반환 (google_client 기본)
        return g_gen_image(prompt, out_path)

    wf = copy.deepcopy(_get_workflow())

    # 프롬프트 삽입 (노드 2: CLIPTextEncode)
    wf["2"]["inputs"]["text"] = prompt

    # 랜덤 시드
    wf["4"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)

    print(f"  FLUX 이미지 생성: {clip['id']} / {prompt[:60]}...")
    pid = queue_prompt(wf)
    outputs = wait_for_result(pid, timeout=300)

    if not outputs:
        raise RuntimeError(f"FLUX 출력 없음: clip {clip['id']}")

    download_output(outputs[0], out_path)
    print(f"  이미지 저장 완료: {out_path}")
    return out_path
