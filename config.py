from dataclasses import dataclass

@dataclass
class Theme:
    name: str
    bg_color: tuple[int, int, int]       # RGB
    accent_color: tuple[int, int, int]
    text_color: tuple[int, int, int]
    font_size_main: int
    font_size_sub: int
    font_size_cta: int
    transition_duration: float           # seconds
    ken_burns_zoom_end: float
    overlay_alpha: int                   # 0-255
    font_family: str = "NanumSquare"     # 기본 고딕 폰트 fallback

THEMES: dict[str, Theme] = {
    "warm": Theme(
        name="warm",
        bg_color=(255, 248, 240),        # #FFF8F0 크림화이트
        accent_color=(212, 149, 106),    # #D4956A 코랄
        text_color=(61, 43, 31),         # #3D2B1F 다크브라운
        font_size_main=90,
        font_size_sub=52,
        font_size_cta=44,
        transition_duration=0.8,
        ken_burns_zoom_end=1.15,
        overlay_alpha=180,
    ),
    "lively": Theme(
        name="lively",
        bg_color=(255, 245, 230),        # #FFF5E6 밝은 오렌지톤
        accent_color=(255, 107, 53),     # #FF6B35 오렌지
        text_color=(45, 45, 45),         # #2D2D2D 차콜
        font_size_main=96,
        font_size_sub=56,
        font_size_cta=46,
        transition_duration=0.3,
        ken_burns_zoom_end=1.30,
        overlay_alpha=160,
    ),
    "premium": Theme(
        name="premium",
        bg_color=(26, 26, 46),           # #1A1A2E 다크네이비
        accent_color=(232, 213, 183),    # #E8D5B7 골드
        text_color=(255, 255, 255),      # #FFFFFF 화이트
        font_size_main=88,
        font_size_sub=50,
        font_size_cta=42,
        transition_duration=0.5,
        ken_burns_zoom_end=1.10,
        overlay_alpha=200,
    ),
    "story": Theme(
        name="story",
        bg_color=(20, 15, 15),           # 어두운 브라운/블랙톤
        accent_color=(245, 215, 160),    # 골드 톤 포인트
        text_color=(255, 255, 255),      # 텍스트는 화이트
        font_size_main=60,
        font_size_sub=50,
        font_size_cta=40,
        transition_duration=1.0,         # 더 길고 부드러운 디졸브
        ken_burns_zoom_end=1.10,         # 매우 부드러운 줌인
        overlay_alpha=200,
        font_family="malgun.ttf",             # 윈도우 기본 폰트로 안전하게
    ),
}

def get_theme(name: str) -> Theme:
    return THEMES.get(name, THEMES["warm"])

WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 15  # seconds (default)
STORY_DURATION = 30 # seconds (for premium storytelling ad)

SCENE_TIMINGS = [
    (0, 3),    # Scene Hook
    (3, 8),    # Scene Value
    (8, 12),   # Scene Mood
    (12, 15),  # Scene CTA
]
