"""
Skill 06 — 최종 광고 렌더링
render_clips.py의 씬 빌더를 가져와 job별 경로로 실행.
출력: workspace/08_output/final_ad.mp4
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# video_pipeline/ 루트를 import 경로에 추가
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import render_clips  # noqa: E402 (root-level module)
from moviepy import AudioFileClip, concatenate_videoclips
from config import FPS  # noqa: E402


def render_final(
    storyboard: dict,
    clips_dir: Path,
    workspace: Path,
) -> Path:
    """5개 클립 + 스토리보드 → final_ad.mp4"""
    theme = storyboard.get("template", "warm")

    required = {
        "01":  clips_dir / "clip_01.mp4",
        "02a": clips_dir / "clip_02a.mp4",
        "02b": clips_dir / "clip_02b.mp4",
        "03":  clips_dir / "clip_03.mp4",
        "04":  clips_dir / "clip_04.mp4",
    }

    missing = [k for k, p in required.items() if not p.exists()]
    if missing:
        raise FileNotFoundError(f"클립 없음: {missing}")

    s1 = render_clips.build_scene1(required["01"], storyboard, theme)
    s2 = render_clips.build_scene2(required["02a"], required["02b"], storyboard, theme)
    s3 = render_clips.build_scene3(required["03"], storyboard, theme)
    s4 = render_clips.build_scene4(required["04"], storyboard, theme)

    f12 = render_clips.white_flash(0.15)
    f23 = render_clips.white_flash(0.15)
    f34 = render_clips.white_flash(0.15)

    final = concatenate_videoclips([s1, f12, s2, f23, s3, f34, s4])

    bgm_path = storyboard.get("bgm_path", "")
    if bgm_path and Path(bgm_path).exists():
        bgm = AudioFileClip(bgm_path).subclipped(0, final.duration).with_volume_scaled(0.3)
        final = final.with_audio(bgm)

    output_dir = workspace / "08_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "final_ad.mp4"

    final.write_videofile(
        str(out),
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        logger="bar",
    )

    return out
