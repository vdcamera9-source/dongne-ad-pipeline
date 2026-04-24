"""
render_clips.py
Higgsfield Static 클립 → Ken Burns + 광고 효과 합성 → 최종 MP4

입력: workspace/07_clips/clip_01~04.mp4
출력: workspace/08_output/final_ad.mp4
"""
from __future__ import annotations
import json, os
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from moviepy import VideoFileClip, VideoClip, concatenate_videoclips, AudioFileClip
import qrcode

from config import get_theme, FPS
from effects.text_overlay import draw_text_on_frame, _load_font

# ── 경로 설정 ─────────────────────────────────────────────
CLIPS_DIR  = Path("workspace/07_clips")
OUTPUT_DIR = Path("workspace/08_output")
STORYBOARD = Path("workspace/03_storyboard.json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080


# ── 유틸: 프레임 처리 함수들 ──────────────────────────────

def apply_color_grade(frame: np.ndarray, theme_name: str) -> np.ndarray:
    """채도·색온도 보정."""
    grades = {
        "warm":    dict(r=+15, g=+5,  b=-10, sat=1.38),
        "lively":  dict(r=+10, g=+5,  b=-5,  sat=1.45),
        "premium": dict(r=-5,  g=-5,  b=+10, sat=1.20),
    }
    g = grades.get(theme_name, grades["warm"])
    f = frame.astype(np.float32)
    f[..., 0] = np.clip(f[..., 0] + g["r"], 0, 255)
    f[..., 1] = np.clip(f[..., 1] + g["g"], 0, 255)
    f[..., 2] = np.clip(f[..., 2] + g["b"], 0, 255)
    # 채도 (HSV)
    img = Image.fromarray(f.astype(np.uint8)).convert("HSV")
    h_arr, s_arr, v_arr = np.array(img).transpose(2, 0, 1)
    s_arr = np.clip(s_arr.astype(np.float32) * g["sat"], 0, 255).astype(np.uint8)
    img2 = Image.fromarray(np.stack([h_arr, s_arr, v_arr], axis=2), "HSV").convert("RGB")
    return np.array(img2)


def apply_vignette(frame: np.ndarray, strength: float = 0.55) -> np.ndarray:
    """가장자리 어둡게."""
    if not hasattr(apply_vignette, "_mask"):
        ys = np.linspace(-1, 1, H)
        xs = np.linspace(-1, 1, W)
        xx, yy = np.meshgrid(xs, ys)
        dist = np.sqrt(xx**2 + yy**2)
        mask = np.clip(1 - dist * strength, 0, 1)
        apply_vignette._mask = mask[:, :, np.newaxis]
    return np.clip(frame * apply_vignette._mask, 0, 255).astype(np.uint8)


def white_flash(duration: float = 0.15) -> VideoClip:
    """씬 전환 화이트 플래시."""
    frames = max(1, int(duration * FPS))
    def make(t):
        alpha = 1.0 - t / duration
        v = int(255 * alpha)
        return np.full((H, W, 3), v, dtype=np.uint8)
    return VideoClip(make, duration=duration)


def apply_ken_burns(
    clip: VideoFileClip,
    zoom_start: float = 1.0,
    zoom_end: float = 1.10,
) -> VideoClip:
    """Static 클립 위에 Ken Burns 줌인 적용."""
    dur = clip.duration

    def make_frame(t: float) -> np.ndarray:
        base = clip.get_frame(t)
        progress = t / dur if dur > 0 else 1.0
        scale = zoom_start + (zoom_end - zoom_start) * progress

        crop_w = int(W / scale)
        crop_h = int(H / scale)
        x0 = (W - crop_w) // 2
        y0 = (H - crop_h) // 2
        cropped = base[y0:y0 + crop_h, x0:x0 + crop_w]
        return np.array(Image.fromarray(cropped).resize((W, H), Image.LANCZOS))

    return VideoClip(make_frame, duration=dur)


def draw_price_badge(
    frame: np.ndarray, text: str, t: float, appear_at: float = 1.5
) -> np.ndarray:
    """원형 가격 배지 바운스 등장."""
    if t < appear_at:
        return frame
    elapsed = t - appear_at
    bounce_dur = 0.35
    if elapsed < bounce_dur:
        scale = 1.0 + 0.35 * np.sin(np.pi * elapsed / bounce_dur)
    else:
        scale = 1.0

    size = int(260 * scale)
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.ellipse([0, 0, size - 1, size - 1], fill=(200, 30, 30, 230))

    font_size = max(20, int(36 * scale))
    font = _load_font(font_size)
    lines = text.split("\n")
    total_h = font_size * len(lines) + 6 * (len(lines) - 1)
    cy = (size - total_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        draw.text(((size - lw) // 2, cy), line, font=font, fill=(255, 255, 255, 255))
        cy += font_size + 6

    bx = W - size - 60
    by = H - size - 60
    base = Image.fromarray(frame).convert("RGBA")
    base.paste(badge, (bx, by), badge)
    return np.array(base.convert("RGB"))


def draw_lower_third(frame: np.ndarray, store: str, info: str, t: float, theme_name: str) -> np.ndarray:
    """하단 브랜드 바 슬라이드업."""
    BAR_H = 130
    slide_dur = 0.5
    if t < 0:
        return frame
    progress = min(t / slide_dur, 1.0)
    offset = int(BAR_H * (1 - progress))

    themes = {
        "warm":    (212, 149, 106),
        "lively":  (255, 107, 53),
        "premium": (232, 213, 183),
    }
    color = themes.get(theme_name, themes["warm"])

    img = Image.fromarray(frame).convert("RGBA")
    bar = Image.new("RGBA", (W, BAR_H), (*color, 220))
    img.paste(bar, (0, H - BAR_H + offset), bar)
    result = np.array(img.convert("RGB"))

    if progress > 0.3:
        text_alpha = min((progress - 0.3) / 0.4, 1.0)
        result = draw_text_on_frame(result, store, (W // 2, H - BAR_H + offset + 38),
                                    52, (255, 255, 255), text_alpha, "center", W - 200)
        result = draw_text_on_frame(result, info, (W // 2, H - BAR_H + offset + 95),
                                    34, (255, 255, 255), text_alpha * 0.9, "center", W - 200)
    return result


def draw_qr(frame: np.ndarray, url: str, t: float, appear_at: float = 0.5) -> np.ndarray:
    """우하단 QR 코드 fade-in."""
    if not url or t < appear_at:
        return frame
    alpha = min((t - appear_at) / 0.5, 1.0)
    size = 200
    qr_img = qrcode.make(url).resize((size, size))
    pad = 14
    box_size = size + pad * 2
    box = Image.new("RGBA", (box_size, box_size), (255, 255, 255, int(240 * alpha)))
    box.paste(qr_img, (pad, pad))
    base = Image.fromarray(frame).convert("RGBA")
    bx = W - box_size - 70
    by = H - box_size - 140
    r, g, b, a = box.split()
    a = a.point(lambda p: int(p * alpha))
    box = Image.merge("RGBA", (r, g, b, a))
    base.paste(box, (bx, by), box)
    return np.array(base.convert("RGB"))


def draw_tv_badge(frame: np.ndarray, t: float) -> np.ndarray:
    """생방송투데이 출연 배지 (좌상단)."""
    if t < 0.6:
        return frame
    alpha = min((t - 0.6) / 0.4, 1.0)
    return draw_text_on_frame(
        frame, "★ 생방송투데이 출연",
        (W // 2, 80), 36, (255, 220, 50), alpha, "center", W - 200, shadow=True
    )


# ── 씬별 클립 빌더 ────────────────────────────────────────

def build_scene1(clip_path: Path, sb: dict, theme: str) -> VideoClip:
    """Hook: 고기 굽기 — Ken Burns 1.0→1.12 + 메인 카피."""
    raw = VideoFileClip(str(clip_path)).subclipped(0, 3.0)
    kb  = apply_ken_burns(raw, 1.0, 1.12)
    copy = sb["ad_copy"]["main_copy"]

    def make(t):
        frame = kb.get_frame(t)
        frame = apply_color_grade(frame, theme)
        frame = apply_vignette(frame)
        text_alpha = min(t / 0.4, 1.0)
        frame = draw_text_on_frame(frame, copy,
            (W // 2, H - 180), 100, (255, 255, 255), text_alpha,
            "center", W - 300, shadow=True)
        return frame

    return VideoClip(make, duration=3.0)


def build_scene2(clip_a: Path, clip_b: Path, sb: dict, theme: str) -> VideoClip:
    """Value: 생등심 → 볶음밥 슬라이드 (각 2.5초, White Flash로 연결)."""
    price_main = sb["ad_copy"]["price_badge_main"]
    price_sub  = sb["ad_copy"]["price_badge_sub"]

    raw_a = VideoFileClip(str(clip_a)).subclipped(0, 2.5)
    kb_a  = apply_ken_burns(raw_a, 1.0, 1.07)

    def make_a(t):
        frame = kb_a.get_frame(t)
        frame = apply_color_grade(frame, theme)
        frame = apply_vignette(frame)
        frame = draw_price_badge(frame, price_main, t, appear_at=0.8)
        alpha = min(t / 0.4, 1.0)
        frame = draw_text_on_frame(frame, price_sub,
            (W // 2, H - 80), 38, (255, 255, 255), alpha * 0.85,
            "center", W - 300, shadow=True)
        return frame

    part_a = VideoClip(make_a, duration=2.5)
    flash  = white_flash(0.12)

    raw_b = VideoFileClip(str(clip_b)).subclipped(0, 2.5)
    kb_b  = apply_ken_burns(raw_b, 1.0, 1.06)

    def make_b(t):
        frame = kb_b.get_frame(t)
        frame = apply_color_grade(frame, theme)
        frame = apply_vignette(frame)
        alpha = min(t / 0.4, 1.0)
        frame = draw_text_on_frame(frame, "볶음밥 4,000원",
            (W // 2, H - 100), 52, (255, 255, 255), alpha,
            "center", W - 300, shadow=True)
        return frame

    part_b = VideoClip(make_b, duration=2.5)
    return concatenate_videoclips([part_a, flash, part_b])


def build_scene3(clip_path: Path, sb: dict, theme: str) -> VideoClip:
    """Mood: 매장 내부 — Ken Burns 1.0→1.08 + 리뷰 + TV 배지."""
    raw  = VideoFileClip(str(clip_path)).subclipped(0, 4.0)
    kb   = apply_ken_burns(raw, 1.0, 1.08)
    review = sb["ad_copy"]["review_text"]

    def make(t):
        frame = kb.get_frame(t)
        frame = apply_color_grade(frame, theme)
        frame = apply_vignette(frame)
        frame = draw_tv_badge(frame, t)
        alpha = min(max(t - 0.5, 0) / 0.5, 1.0)
        # 리뷰 반투명 박스
        if alpha > 0:
            box_w, box_h = W - 400, 120
            img = Image.fromarray(frame).convert("RGBA")
            bx, by = 200, H // 2 - 60
            box = Image.new("RGBA", (box_w, box_h),
                            (20, 20, 20, int(180 * alpha)))
            img.paste(box, (bx, by), box)
            frame = np.array(img.convert("RGB"))
            frame = draw_text_on_frame(frame, review,
                (W // 2, H // 2), 54, (255, 255, 255), alpha,
                "center", W - 450, shadow=False)
        return frame

    return VideoClip(make, duration=4.0)


def build_scene4(clip_path: Path, sb: dict, theme: str) -> VideoClip:
    """CTA: 외관 — Ken Burns 1.0→1.05 + Lower Third + QR."""
    raw   = VideoFileClip(str(clip_path)).subclipped(0, 3.0)
    kb    = apply_ken_burns(raw, 1.0, 1.05)
    store = sb["store_info"]["name"]
    info  = sb["ad_copy"]["cta_info"]
    qr_url = sb["store_info"].get("qr_url", "")

    def make(t):
        frame = kb.get_frame(t)
        frame = apply_color_grade(frame, theme)
        frame = apply_vignette(frame)
        frame = draw_lower_third(frame, store, info, t, theme)
        frame = draw_qr(frame, qr_url, t, appear_at=0.8)
        return frame

    return VideoClip(make, duration=3.0)


# ── 메인 ──────────────────────────────────────────────────

def main():
    sb = json.loads(STORYBOARD.read_text(encoding="utf-8"))
    theme = sb.get("template", "warm")

    clips = {
        "01":  CLIPS_DIR / "clip_01.mp4",
        "02a": CLIPS_DIR / "clip_02a.mp4",
        "02b": CLIPS_DIR / "clip_02b.mp4",
        "03":  CLIPS_DIR / "clip_03.mp4",
        "04":  CLIPS_DIR / "clip_04.mp4",
    }

    missing = [k for k, v in clips.items() if not v.exists()]
    if missing:
        print("아직 없는 클립:", missing)
        print("workspace/07_clips/ 에 저장 후 다시 실행하세요.")
        return

    print("렌더링 시작...")
    s1 = build_scene1(clips["01"],  sb, theme);  print("Scene 1 Hook  완료")
    s2 = build_scene2(clips["02a"], clips["02b"], sb, theme); print("Scene 2 Value 완료")
    s3 = build_scene3(clips["03"],  sb, theme);  print("Scene 3 Mood  완료")
    s4 = build_scene4(clips["04"],  sb, theme);  print("Scene 4 CTA   완료")

    f12 = white_flash(0.15)
    f23 = white_flash(0.15)
    f34 = white_flash(0.15)

    final = concatenate_videoclips([s1, f12, s2, f23, s3, f34, s4])

    bgm_path = sb.get("bgm_path", "")
    if bgm_path and Path(bgm_path).exists():
        bgm = AudioFileClip(bgm_path).subclipped(0, final.duration).with_volume_scaled(0.3)
        final = final.with_audio(bgm)

    out = str(OUTPUT_DIR / "final_ad.mp4")
    final.write_videofile(out, codec="libx264", audio_codec="aac", fps=FPS, logger=None)

    size_mb = Path(out).stat().st_size / 1024 / 1024
    dur = final.duration
    print(f"\n완료: {out}")
    print(f"길이: {dur:.1f}초  크기: {size_mb:.1f}MB")


if __name__ == "__main__":
    main()
