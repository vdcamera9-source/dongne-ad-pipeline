"""
Skill 02 — 스토리보드 + 클립 플랜 생성
입력: analysis dict, store_info dict
출력: storyboard dict → workspace/03_storyboard.json

클립 구조 (render_clips.py와 1:1 대응):
  clip_01  — Hook  (3초)
  clip_02a — Value A (2.5초, 대표 메뉴)
  clip_02b — Value B (2.5초, 부메뉴 or 실내)
  clip_03  — Mood  (4초)
  clip_04  — CTA   (3초)
"""
from __future__ import annotations
import json
from pathlib import Path
from google.genai import types
from .client import get_client
from .models import gemini_flash

PROMPT = """아래 분석 결과와 가게 정보를 바탕으로 15초 광고 스토리보드를 생성하세요.

=== 가게 정보 ===
{store_info_json}

=== 이미지 분석 결과 ===
{analysis_json}

=== 클립 구성 규칙 ===
render_clips.py가 아래 5개 클립을 순서대로 합성합니다:
- clip_01  : Hook 씬 (0~3초) — 음식 클로즈업, 강렬한 첫인상
- clip_02a : Value A 씬 (3~5.5초) — 대표 메뉴 전체 샷 + 가격 배지
- clip_02b : Value B 씬 (5.5~8초) — 부메뉴 or 매장 세부
- clip_03  : Mood 씬 (8~12초) — 인테리어/분위기
- clip_04  : CTA 씬 (12~15초) — 외관/간판

=== 카피 작성 원칙 ===
- main_copy: Hook 씬 대형 카피 (5~10자, 업종 감성)
- price_badge_main: 원형 배지 텍스트 (메뉴명\\n가격 형식, \\n은 실제 줄바꿈)
- price_badge_sub: 배지 아래 서브 텍스트 (예: "1인분 기준" or "매일 11:00")
- review_text: Mood 씬 리뷰 (따옴표 포함, 예: "소고기는 우판등심이 최고!")
- cta_info: CTA 바 하단 텍스트 (주소 | 영업시간 형식)

=== 클립별 source 규칙 ===
- analysis의 scene_assignment에서 source가 "real_photo"이면 해당 파일 사용
- source가 "generate"이면 Nano Banana로 이미지 생성 필요
- clip_02b는 scene_assignment의 Value 이미지가 있으면 다른 사진(Mood나 Hook 재활용), 없으면 generate

=== 비디오 프롬프트 원칙 ===
영어로 작성. [피사체 묘사] + [카메라 무브 동사] + [조명/분위기] + [초 단위]
예: "Sizzling Korean BBQ beef on iron grill, camera slowly pushes in, warm cinematic lighting, 4 seconds"

반드시 아래 JSON 형식만 반환 (마크다운 코드블록 없이 순수 JSON):
{{
  "store_info": {{
    "name": "가게명",
    "category": "업종",
    "address": "주소",
    "hours": "영업시간",
    "phone": "전화번호",
    "qr_url": "URL"
  }},
  "template": "warm",
  "ad_copy": {{
    "main_copy": "진짜 맛을 아는 사람들",
    "price_badge_main": "한우 생등심\\n37,500원",
    "price_badge_sub": "1인분 기준",
    "review_text": "\\"소고기는 우판등심이 최고!\\"",
    "cta_info": "수원 영통구  |  매일 11:00-22:00"
  }},
  "clip_plan": [
    {{
      "id": "01",
      "role": "Hook",
      "duration": 3,
      "source": "real_photo",
      "source_file": "photo_01.jpg",
      "generate_image": false,
      "image_prompt": null,
      "video_prompt": "..."
    }},
    {{
      "id": "02a",
      "role": "Value_A",
      "duration": 3,
      "source": "generate",
      "source_file": null,
      "generate_image": true,
      "image_prompt": "Elegant Korean BBQ beef spread on dark wooden table...",
      "video_prompt": "..."
    }},
    {{
      "id": "02b",
      "role": "Value_B",
      "duration": 3,
      "source": "real_photo",
      "source_file": "photo_02.jpg",
      "generate_image": false,
      "image_prompt": null,
      "video_prompt": "..."
    }},
    {{
      "id": "03",
      "role": "Mood",
      "duration": 4,
      "source": "real_photo",
      "source_file": "photo_03.jpg",
      "generate_image": false,
      "image_prompt": null,
      "video_prompt": "..."
    }},
    {{
      "id": "04",
      "role": "CTA",
      "duration": 3,
      "source": "real_photo",
      "source_file": "photo_04.jpg",
      "generate_image": false,
      "image_prompt": null,
      "video_prompt": "..."
    }}
  ]
}}
"""


def build_storyboard(
    analysis: dict,
    store_info: dict,
    workspace: Path,
) -> dict:
    client = get_client()

    response = client.models.generate_content(
        model=gemini_flash(),
        contents=[types.Content(role="user", parts=[
            types.Part.from_text(text=PROMPT.format(
                store_info_json=json.dumps(store_info, ensure_ascii=False, indent=2),
                analysis_json=json.dumps(analysis, ensure_ascii=False, indent=2),
            ))
        ])],
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    storyboard = json.loads(raw)

    out = workspace / "03_storyboard.json"
    out.write_text(json.dumps(storyboard, ensure_ascii=False, indent=2), encoding="utf-8")
    return storyboard
