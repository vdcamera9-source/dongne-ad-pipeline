"""
FastAPI 엔드포인트
POST /api/generate-ad  — 업체 MD + 사진 → MP4 URL
GET  /api/jobs/{job_id}/stream — SSE 진행상황 스트림
GET  /api/jobs/{job_id}/result — 완료 결과 (MP4 URL)
"""
from __future__ import annotations
import asyncio
import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import AsyncGenerator

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from .orchestrator import run_pipeline

router = APIRouter(prefix="/api")

# 진행 상황: {job_id: asyncio.Queue}
_job_queues: dict[str, asyncio.Queue] = {}
# 결과: {job_id: str (파일 경로) | Exception}
_job_results: dict[str, Path | Exception] = {}


@router.post("/generate-ad")
async def generate_ad(
    store_md: UploadFile = File(..., description="업체 정보 YAML 파일"),
    photos: list[UploadFile] = File(..., description="가게 사진 (여러 장)"),
):
    """광고 생성 작업 시작 → job_id 즉시 반환."""
    job_id = uuid.uuid4().hex[:8]
    queue: asyncio.Queue = asyncio.Queue()
    _job_queues[job_id] = queue

    # 임시 폴더에 업로드 파일 저장
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"adgen_{job_id}_"))
    md_path = tmp_dir / "store_info.md"
    md_path.write_bytes(await store_md.read())

    photos_dir = tmp_dir / "photos"
    photos_dir.mkdir()
    for photo in photos:
        dest = photos_dir / photo.filename
        dest.write_bytes(await photo.read())

    # 백그라운드 파이프라인 실행
    asyncio.create_task(_run_job(job_id, md_path, photos_dir, queue, tmp_dir))

    return {"job_id": job_id, "stream_url": f"/api/jobs/{job_id}/stream"}


@router.get("/jobs/{job_id}/stream")
async def stream_progress(job_id: str):
    """SSE로 진행상황 스트리밍."""
    if job_id not in _job_queues:
        raise HTTPException(404, "job_id를 찾을 수 없습니다.")

    async def event_generator() -> AsyncGenerator[str, None]:
        queue = _job_queues[job_id]
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=60)
                data = json.dumps(event, ensure_ascii=False)
                yield f"data: {data}\n\n"
                if event.get("done"):
                    break
                if event.get("error"):
                    break
            except asyncio.TimeoutError:
                yield "data: {\"ping\": true}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/jobs/{job_id}/result")
async def get_result(job_id: str):
    """완료된 MP4 파일 다운로드."""
    result = _job_results.get(job_id)
    if result is None:
        raise HTTPException(202, "아직 처리 중입니다.")
    if isinstance(result, Exception):
        raise HTTPException(500, str(result))
    if not Path(result).exists():
        raise HTTPException(404, "파일을 찾을 수 없습니다.")
    return FileResponse(
        path=str(result),
        media_type="video/mp4",
        filename=f"ad_{job_id}.mp4",
    )


async def _run_job(
    job_id: str,
    md_path: Path,
    photos_dir: Path,
    queue: asyncio.Queue,
    tmp_dir: Path,
):
    """백그라운드 파이프라인 실행 태스크."""
    def on_progress(event: dict):
        asyncio.get_event_loop().call_soon_threadsafe(queue.put_nowait, event)

    try:
        result = await run_pipeline(
            store_md_path=md_path,
            photos_dir=photos_dir,
            on_progress=on_progress,
            job_id=job_id,
        )
        _job_results[job_id] = result
        await queue.put({"done": True, "result_url": f"/api/jobs/{job_id}/result"})
    except Exception as e:
        _job_results[job_id] = e
        await queue.put({"error": str(e), "done": True})
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        _job_queues.pop(job_id, None)
