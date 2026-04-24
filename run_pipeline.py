"""
CLI: 로컬에서 파이프라인 직접 실행

사용법:
  uv run python run_pipeline.py --md store_sample.md --photos workspace/01_store_photos/

선택사항:
  --job-id abc123   (지정 안 하면 자동 생성)
"""
import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="동네방네 광고 자동 생성")
    parser.add_argument("--md", required=True, help="업체 정보 YAML 파일 경로")
    parser.add_argument("--photos", required=True, help="가게 사진 폴더 경로")
    parser.add_argument("--job-id", default=None, help="작업 ID (선택)")
    args = parser.parse_args()

    md_path = Path(args.md)
    photos_dir = Path(args.photos)

    if not md_path.exists():
        print(f"오류: MD 파일 없음: {md_path}")
        sys.exit(1)
    if not photos_dir.exists():
        print(f"오류: 사진 폴더 없음: {photos_dir}")
        sys.exit(1)

    from pipeline.orchestrator import run_pipeline

    def on_progress(event: dict):
        step = event.get("step", "?")
        total = event.get("total", "?")
        msg = event.get("msg", "")
        done = event.get("done", False)
        prefix = f"[{step}/{total}]"
        mark = "✅" if done else "  "
        print(f"{mark} {prefix} {msg}")

    print(f"파이프라인 시작: {md_path.name} + {photos_dir}")
    result = asyncio.run(run_pipeline(
        store_md_path=md_path,
        photos_dir=photos_dir,
        on_progress=on_progress,
        job_id=args.job_id,
    ))
    print(f"\n완료: {result}")
    size_mb = result.stat().st_size / 1024 / 1024
    print(f"파일 크기: {size_mb:.1f}MB")


if __name__ == "__main__":
    main()
