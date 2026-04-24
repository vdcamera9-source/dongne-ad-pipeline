"""FastAPI 렌더링 API"""
from __future__ import annotations

import uuid
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from render import render_ad_video
from pipeline.api import router as pipeline_router

load_dotenv()  # .env 파일에서 GEMINI_API_KEY 로드

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="동네방네 영상 렌더링 API", version="0.2.0")

# 자동화 파이프라인 라우터 등록
app.include_router(pipeline_router)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


class Storyboard(BaseModel):
    scene: int
    duration: int
    visual_desc: str = ""
    text: str = ""


class AdData(BaseModel):
    store_name: str
    category: str = ""
    address: str = ""
    hours: str = ""
    phone: str = ""
    main_copy: str
    sub_copy: str = ""
    cta: str = ""
    storyboard: list[Storyboard] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    template: str = "warm"  # warm | lively | premium
    qr_url: str = ""
    bgm_path: str = ""


@app.post("/api/render-video")
async def render_video(ad_data: AdData) -> dict:
    output_path = str(OUTPUT_DIR / f"{uuid.uuid4()}.mp4")
    try:
        result_path = render_ad_video(ad_data.model_dump(), output_path)
        return {"video_url": f"/video/{Path(result_path).name}", "path": result_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/video/{filename}")
async def get_video(filename: str) -> FileResponse:
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(str(path), media_type="video/mp4")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
