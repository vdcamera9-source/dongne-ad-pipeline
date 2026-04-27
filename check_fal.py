"""
fal.ai API 키 유효성 확인 스크립트
사용법: uv run python check_fal.py
.env 파일에 FAL_KEY=your_key 설정 후 실행
"""
import os
from dotenv import load_dotenv

load_dotenv()

fal_key = os.environ.get("FAL_KEY")
if not fal_key:
    print("오류: .env 파일에 FAL_KEY가 설정되지 않았습니다.")
    print("  FAL_KEY=your_key_here  (.env에 추가)")
    raise SystemExit(1)

import fal_client

try:
    print("fal.ai 키 유효성 확인 중...")
    result = fal_client.subscribe(
        "fal-ai/flux/schnell",
        arguments={"prompt": "test", "num_images": 1}
    )
    print("키 유효 + 크레딧 정상")
except Exception as e:
    print(f"오류: {e}")
