from moviepy import ImageClip, TextClip, ColorClip, CompositeVideoClip

def apply_global_overlay(video_clip, logo_path: str, phone: str, address: str, font_family: str):
    """전체 비디오 위에 로고와 정보창을 오버레이"""
    layers = [video_clip]
    duration = video_clip.duration
    target_size = video_clip.size

    # 좌상단 로고
    if logo_path:
        logo = (
            ImageClip(logo_path)
            .resized(width=200)  # 로고 사이즈
            .with_position((50, 50))
            .with_duration(duration)
        )
        layers.append(logo)
        
    # 우상단 인포 박스 (전화번호 & 주소)
    if phone or address:
        info_text = f"예약/문의: {phone}\n{address}"
        
        txt = (
            TextClip(
                font=font_family,
                text=info_text,
                font_size=30,
                color="white",
            )
        )
        
        # 반투명 배경 박스
        bg_box = (
            ColorClip(size=(txt.w + 40, txt.h + 40), color=(0, 0, 0))
            .with_opacity(0.5)
            .with_position((target_size[0] - txt.w - 90, 40))
            .with_duration(duration)
        )
        
        txt = txt.with_position((target_size[0] - txt.w - 70, 60)).with_duration(duration)
        
        layers.append(bg_box)
        layers.append(txt)

    return CompositeVideoClip(layers, size=target_size).with_duration(duration)
