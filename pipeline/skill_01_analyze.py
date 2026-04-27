"""
Skill 01 — 가게 실사진 분석 (Ollama 멀티모달)
입력: photos_dir (가게 사진 폴더), store_info (업체 정보 dict)
출력: analysis dict → workspace/02_analysis.json
"""
from __future__ import annotations
import json
from pathlib import Path

from .ollama_client import chat_vision, parse_json

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}

PROMPT = """아래 가게 사진을 분석해서 JSON으로 반환하세요.

가게 정보:
{store_info_json}

파일명: {filename}

각 이미지에 대해 판단하세요:
- subject: food_closeup | food_fullshot | interior | exterior | menu_board | staff | other
- mood: warm | lively | premium
- recommended_scene: Hook | Value | Mood | CTA
- quality_score: 0~10 (9~10=즉시사용, 7~8=사용가능, 5~6=주의, 4이하=생성필요)
- usable: quality_score >= 5
- issues: 역광/흐림/어두움/구도_불량/배경_복잡/해상도_낮음 중 해당하는 것

반드시 아래 JSON만 반환 (마크다운 코드블록 없이 순수 JSON):
{{
  "file": "{filename}",
  "subject": "food_closeup",
  "mood": "warm",
  "recommended_scene": "Hook",
  "quality_score": 8.5,
  "usable": true,
  "issues": []
}}
"""

SUMMARY_PROMPT = """아래 이미지 분석 결과를 바탕으로 광고 씬 배정 summary를 생성하세요.

가게 정보:
{store_info_json}

이미지 분석 결과:
{images_json}

규칙:
- 각 씬(Hook/Value/Mood/CTA)에 가장 적합한 이미지 파일 하나씩 배정
- quality_score 5 미만이거나 적합한 이미지 없으면 source를 "generate"로
- 있으면 source를 "real_photo"로

반드시 아래 JSON만 반환 (마크다운 코드블록 없이 순수 JSON):
{{
  "theme_recommendation": "warm",
  "scenes_to_generate": ["Value"],
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
    backend: str = "local",
) -> dict:
    photos_dir = Path(photos_dir)
    photos = sorted(
        [p for p in photos_dir.iterdir() if p.suffix.lower() in SUPPORTED]
    )
    if not photos:
        raise ValueError(f"사진 없음: {photos_dir}")

    store_json = json.dumps(store_info, ensure_ascii=False)

    # 각 이미지 개별 분석 (멀티모달)
    images: list[dict] = []
    for i, photo in enumerate(photos, 1):
        print(f"    [{i}/{len(photos)}] 분석 중: {photo.name} ...", flush=True)
        prompt = PROMPT.format(
            store_info_json=store_json,
            filename=photo.name,
        )
        if backend == "api":
            from .google_client import chat_vision as g_chat_vision
            raw = g_chat_vision(prompt, photo)
        else:
            raw = chat_vision(prompt, photo)
            
        try:
            info = parse_json(raw)
        except Exception:
            info = {
                "file": photo.name,
                "subject": "other",
                "mood": "warm",
                "recommended_scene": "Mood",
                "quality_score": 6,
                "usable": True,
                "issues": ["파싱실패"],
            }
        images.append(info)
        print(f"    [{i}/{len(photos)}] ✓ {photo.name} → "
              f"{info.get('recommended_scene')} (점수: {info.get('quality_score')})", flush=True)

    # 씬 배정 (텍스트)
    out_prompt = SUMMARY_PROMPT.format(
        store_info_json=store_json,
        images_json=json.dumps(images, ensure_ascii=False, indent=2),
    )
    if backend == "api":
        from .google_client import chat as g_chat
        summary_raw = g_chat(out_prompt)
    else:
        from .ollama_client import chat
        summary_raw = chat(out_prompt)
        
    try:
        summary = parse_json(summary_raw)
    except Exception:
        # 파싱 실패 시 기본값
        summary = {
            "theme_recommendation": "warm",
            "scenes_to_generate": [],
            "scene_assignment": {
                "Hook":  {"file": photos[0].name if len(photos) > 0 else None, "source": "real_photo"},
                "Value": {"file": photos[1].name if len(photos) > 1 else None, "source": "real_photo"},
                "Mood":  {"file": photos[2].name if len(photos) > 2 else None, "source": "real_photo"},
                "CTA":   {"file": photos[3].name if len(photos) > 3 else None, "source": "real_photo"},
            },
        }

    analysis = {
        **summary,
        "images": images,
        "store_name": store_info.get("store_name", ""),
        "photo_files": [p.name for p in photos],
    }

    out = workspace / "02_analysis.json"
    out.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    return analysis
