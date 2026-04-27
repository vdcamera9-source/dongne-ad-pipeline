"""
Phase 1 렌더링 단독 테스트
API 없이 기존 샘플 클립 + 스토리보드로 final_ad.mp4 생성

사용법:
  uv run python test_render_only.py
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
WORKSPACE   = ROOT / "workspace"
CLIPS_DIR   = WORKSPACE / "07_clips"
STORYBOARD  = WORKSPACE / "03_storyboard.json"
OUTPUT_DIR  = WORKSPACE / "08_output"

REQUIRED_CLIPS = ["clip_01.mp4", "clip_02a.mp4", "clip_02b.mp4", "clip_03.mp4", "clip_04.mp4"]


def check_files():
    errors = []
    if not STORYBOARD.exists():
        errors.append(f"없음: {STORYBOARD}")
    for name in REQUIRED_CLIPS:
        p = CLIPS_DIR / name
        if not p.exists():
            errors.append(f"없음: {p}")
    if errors:
        print("파일 확인 실패:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print("파일 확인 완료")
    for name in REQUIRED_CLIPS:
        size = (CLIPS_DIR / name).stat().st_size / 1024 / 1024
        print(f"  {name}  {size:.1f} MB")


def main():
    print("=" * 50)
    print("렌더링 단독 테스트 (API 없음)")
    print("=" * 50)

    check_files()

    storyboard = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    print(f"\n스토리보드 로드: {storyboard['store_info']['name']} / {storyboard['template']} 테마")

    from pipeline.skill_06_render import render_final

    print("\n렌더링 시작...")
    t0 = time.time()
    out = render_final(storyboard, CLIPS_DIR, WORKSPACE)
    elapsed = time.time() - t0

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"\n완료: {out}")
    print(f"크기: {size_mb:.1f} MB  |  소요: {elapsed:.0f}초")


if __name__ == "__main__":
    main()
