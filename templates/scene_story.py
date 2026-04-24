from moviepy import ImageClip, TextClip, CompositeVideoClip, vfx
from config import Theme

def apply_ken_burns(clip: ImageClip, duration: float, zoom_start=1.0, zoom_end=1.15, target_size=(1920, 1080)):
    # 동적 줌 (간단한 구현: 시작/끝 크기를 다르게 하여 리사이즈 - moviepy v1 기준 resize 안될 수 있으므로 기본 리사이즈 후 crop 사용하거나 fx 활용)
    # MoviePy의 resize 기능은 함수를 허용함
    def resize_func(t):
        progress = t / duration
        # 선형 줌
        return zoom_start + (zoom_end - zoom_start) * progress

    # MoviePy v1.0.3에서는 clip.resized(resize_func)가 올바르게 작동하지 않을 수 있으므로 crop을 사용하거나 margin을 쓸 수 있습니다.
    # 안전하고 간단하게: clip.resize(lambda t: 1 + 0.15*t/duration) 
    # moviepy v1 의 리사이즈 함수
    try:
        zoomed = clip.resized(resize_func)
    except Exception:
        # v2나 속성이 다를 경우 대비 안전 폴백 (줌 안함)
        zoomed = clip.resized(width=target_size[0])
    
    # 1920x1080에서 벗어나는 부분을 잘라내고 중앙 정렬 (CompositeVideoClip이 잘라줌)
    return zoomed.with_position("center")

def create_story_scene(image_path: str, text: str, theme: Theme, duration: float, text_color: str = "white", target_size=(1920, 1080)) -> CompositeVideoClip:
    """단일 스토리 씬 (디졸브로 연결될 파트) 생성"""
    
    # 해상도를 맞춘 이미지
    bg = ImageClip(image_path).with_duration(duration)
    
    # Ken Burns 효과 (간단 줌인)
    max_side = max(target_size[0]*1.2, bg.w) # 원본 비율 유지하면서 크게
    bg = bg.resized(height=target_size[1]*1.2)
    
    def move_zoom(t):
        # 1.0 -> 1.1 scale over duration
        scale = 1.0 + (0.1 * (t / duration))
        return scale
        
    bg = bg.resized(move_zoom)
    # 이미지 중앙 맞추기 (CompositeVideoClip이 잘라줌)
    bg = bg.with_position("center")
    
    layers = [bg]
    
    if text:
        # 하단 자막
        # 폰트는 백제갈비처럼 명조나 부드러운 고딕 사용 (여기서는 Pretendard 가정)
        shadow_color = "white" if text_color.lower() in ("black", "#000000", "#000") else "black"
        
        txt = (
            TextClip(
                font=theme.font_family,
                text=text,
                font_size=60,
                color=text_color,
                method="caption",
                size=(1800, 250),
                horizontal_align="center",
            )
            .with_duration(duration - 1)  # 전체 길이에서 앞뒤 0.5초 여백을 위해
            .with_position(("center", target_size[1] - 250))
        )
        # Drop shadow (가독성을 위해 배경 없는 TextClip 복제)
        txt_shadow = (
            TextClip(
                font=theme.font_family,
                text=text,
                font_size=60,
                color=shadow_color,
                method="caption",
                size=(1800, 250),
                horizontal_align="center",
            )
            .with_duration(duration - 1)
            .with_position(("center", target_size[1] - 246))
        )

        
        # 0.5초 대기 후 자막 등장, 0.5초 전 사라짐
        txt_shadow = txt_shadow.with_start(0.5).with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])
        txt = txt.with_start(0.5).with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])
        
        layers.append(txt_shadow)
        layers.append(txt)

    return CompositeVideoClip(layers, size=target_size).with_duration(duration)
