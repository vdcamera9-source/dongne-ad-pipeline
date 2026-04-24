"""
파이프라인 오케스트레이터
MD 업체정보 + 사진 폴더 → final_ad.mp4

진행상황은 on_progress 콜백으로 전달:
  on_progress({"step": N, "total": 6, "msg": "...", "done": False/True})
"""
from __future__ import annotations
import asyncio
import json
import uuid
import yaml
from pathlib import Path
from typing import Callable

from .skill_01_analyze import analyze_store_photos
from .skill_02_storyboard import build_storyboard
from .skill_03_gen_image import generate_frame_image
from .skill_04_analyze_frame import analyze_all_frames
from .skill_05_gen_video import generate_all_clips
from .skill_06_render import render_final

WORKSPACE_ROOT = Path(__file__).parent.parent / "workspace"


def parse_store_md(md_path: Path) -> dict:
    """YAML 업체 정보 파일 파싱."""
    text = md_path.read_text(encoding="utf-8")
    return yaml.safe_load(text)


def _emit(on_progress: Callable | None, step: int, total: int, msg: str, done: bool = False):
    if on_progress:
        on_progress({"step": step, "total": total, "msg": msg, "done": done})


async def run_pipeline(
    store_md_path: str | Path,
    photos_dir: str | Path,
    on_progress: Callable | None = None,
    job_id: str | None = None,
) -> Path:
    """
    전체 파이프라인 실행.
    Returns: final_ad.mp4 경로
    """
    store_md_path = Path(store_md_path)
    photos_dir = Path(photos_dir)
    job_id = job_id or uuid.uuid4().hex[:8]
    workspace = WORKSPACE_ROOT / job_id
    workspace.mkdir(parents=True, exist_ok=True)

    loop = asyncio.get_event_loop()
    TOTAL = 6

    # ── Step 1: 업체 MD 파싱 + 이미지 분석 ───────────────────
    _emit(on_progress, 1, TOTAL, "가게 사진 분석 중...")
    store_info = parse_store_md(store_md_path)
    analysis = await loop.run_in_executor(
        None, analyze_store_photos, photos_dir, store_info, workspace
    )
    _emit(on_progress, 1, TOTAL, f"이미지 {len(analysis['photo_files'])}장 분석 완료")

    # ── Step 2: 스토리보드 생성 ───────────────────────────────
    _emit(on_progress, 2, TOTAL, "스토리보드 설계 중...")
    storyboard = await loop.run_in_executor(
        None, build_storyboard, analysis, store_info, workspace
    )
    clip_plan = storyboard["clip_plan"]
    _emit(on_progress, 2, TOTAL, f"스토리보드 완료: {storyboard['template']} 테마")

    # ── Step 3: Nano Banana 이미지 생성 ──────────────────────
    gen_clips = [c for c in clip_plan if c.get("generate_image")]
    if gen_clips:
        _emit(on_progress, 3, TOTAL, f"이미지 생성 중 ({len(gen_clips)}장)...")
        for clip in gen_clips:
            await loop.run_in_executor(None, generate_frame_image, clip, workspace)
            _emit(on_progress, 3, TOTAL, f"이미지 생성 완료: {clip['id']}")
    else:
        _emit(on_progress, 3, TOTAL, "이미지 생성 없음 (실사진만 사용)")

    # ── Step 4: 시작 프레임 분석 ─────────────────────────────
    _emit(on_progress, 4, TOTAL, "시작 프레임 분석 중...")
    await loop.run_in_executor(
        None, analyze_all_frames, clip_plan, photos_dir, workspace
    )
    _emit(on_progress, 4, TOTAL, "프레임 분석 완료")

    # ── Step 5: Veo 3.1 Lite 영상 생성 (병렬) ────────────────
    _emit(on_progress, 5, TOTAL, f"영상 생성 중 ({len(clip_plan)}클립, 병렬)...")

    def _progress_cb(msg: str):
        _emit(on_progress, 5, TOTAL, msg)

    await loop.run_in_executor(
        None,
        _run_generate_clips,
        clip_plan,
        photos_dir,
        workspace,
        _progress_cb,
    )
    _emit(on_progress, 5, TOTAL, "전체 영상 클립 생성 완료")

    # ── Step 6: 최종 렌더링 ───────────────────────────────────
    _emit(on_progress, 6, TOTAL, "최종 광고 렌더링 중...")
    clips_dir = workspace / "07_clips"
    out = await loop.run_in_executor(None, render_final, storyboard, clips_dir, workspace)
    _emit(on_progress, 6, TOTAL, f"렌더링 완료: {out}", done=True)

    return out


def _run_generate_clips(clip_plan, photos_dir, workspace, on_progress):
    """ThreadPool 내 동기 래퍼 (run_in_executor는 코루틴 불가)."""
    generate_all_clips(clip_plan, photos_dir, workspace, on_progress=on_progress)
