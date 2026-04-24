"""
Skill 01 — 가게 실사진 분석
입력: photos_dir (가게 사진 폴더), store_info (업체 정보 dict)
출력: analysis dict → workspace/02_analysis.json
"""
from __future__ import annotations
import json
from pathlib import Path
from google.genai import types
from .client import get_client
from .models import gemini_flash

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

PROMPT = """아래 가게 사진들을 분석해서 JSON으로 반환하세요.

가게 정보:
{store_info_json}

각 이미지에 대해 판단하세요:
- subject: food_closeup | food_fullshot | interior | exterior | menu_board | staff | other
- mood: warm | lively | premium
- recommended_scene: Hook | Value | Mood | CTA
- quality_score: 0~10 (9~10=즉시사용, 7~8=사용가능, 5~6=주의, 4이하=생성필요)
- usable: quality_score >= 5
- issues: 역광/흐림/어두움/구도_불량/배경_복잡/해상도_낮음 중 해당하는 것

전체 판단:
- theme_recommendation: warm | lively | premium
- scene_assignment: Hook/Value/Mood/CTA 각 씬에 가장 적합한 이미지 파일명 배정
  (품질 5 미만이거나 없으면 source를 "generate"로, 있으면 "real_photo"로)

반드시 아래 JSON 형식만 반환 (마크다운 코드블록 없이 순수 JSON):
{{
  "theme_recommendation": "warm",
  "scenes_to_generate": ["Value"],
  "images": [
    {{
      "file": "파일명.jpg",
      "subject": "food_closeup",
      "mood": "warm",
      "recommended_scene": "Hook",
      "quality_score": 8.5,
      "usable": true,
      "issues": []
    }}
  ],
  "scene_assignment": {{
    "Hook":  {{"file": "photo_01.jpg", "source": "real_photo"}},
    "Value": {{"file": null,           "source": "generate"}},
    "Mood":  {{"file": "photo_03.jpg", "source": "real_photo"}},
    "CTA":   {{"file": "photo_02.jpg", "source": "real_photo"}}
  }}
}}
"""


def analyze_store_photos(
    photos_dir: Path,
    store_info: dict,
    workspace: Path,
) -> dict:
    photos_dir = Path(photos_dir)
    photos = sorted(
        [p for p in photos_dir.iterdir() if p.suffix.lower() in SUPPORTED]
    )
    if not photos:
        raise ValueError(f"사진 없음: {photos_dir}")

    client = get_client()

    parts: list = []
    for photo in photos:
        data = photo.read_bytes()
        mime = "image/jpeg" if photo.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
        parts.append(types.Part.from_text(text=f"[파일명: {photo.name}]"))

    parts.append(types.Part.from_text(
        text=PROMPT.format(store_info_json=json.dumps(store_info, ensure_ascii=False))
    ))

    response = client.models.generate_content(
        model=gemini_flash(),
        contents=[types.Content(role="user", parts=parts)],
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    analysis = json.loads(raw)
    analysis["store_name"] = store_info.get("store_name", "")
    analysis["photo_files"] = [p.name for p in photos]

    out = workspace / "02_analysis.json"
    out.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    return analysis
