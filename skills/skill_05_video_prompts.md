# Skill 05 — Higgsfield 동영상 생성 프롬프트
> 입력: `workspace/05_frame_analysis.json` + `workspace/03_storyboard.json`  
> 출력: `workspace/06_video_prompts.md` (복사해서 바로 쓸 수 있는 프롬프트)

---

## 역할

이미지 분석 결과를 바탕으로  
**Higgsfield에 그대로 붙여넣을 수 있는** 동영상 생성 프롬프트를 만든다.  
씬별로 모델 선택, 카메라 프리셋, 상세 프롬프트를 제공한다.

---

## Higgsfield 사용 방법

1. [higgsfield.ai/ai-video](https://higgsfield.ai/ai-video) 접속
2. **Image to Video** 탭 선택
3. 시작 프레임 이미지 업로드 (`workspace/05_start_frames/` 또는 실사진)
4. 모델 선택 (씬별 권장 모델 명시)
5. 아래 프롬프트 붙여넣기
6. Camera Movement 프리셋 선택
7. Duration 설정 (씬 길이 + 0.5초 여유)
8. 생성 후 `workspace/07_clips/clip_0X.mp4`로 저장

---

## Higgsfield 프롬프트 구조

```
[현재 장면 묘사] + [움직임 묘사] + [카메라 움직임] + [분위기/조명] + [스타일]
```

**핵심 원칙** (AI동영상.md 기반):
- **씬당 주요 움직임 1개만** — 복잡한 움직임 금지
- **카메라 움직임을 동사로 명시** — `camera slowly pushes in` `camera pans right`
- **모호한 형용사 금지** — `beautiful` `amazing` 대신 구체적 묘사
- **길이를 초로 명시** — `smooth motion, 4 seconds`

---

## 카메라 무브 프롬프트 표현 사전

| 무브 | Higgsfield 프리셋 | 프롬프트 표현 |
|------|-----------------|------------|
| 천천히 밀기 | `Dolly In` | `camera slowly and smoothly pushes forward` |
| 당기기 | `Dolly Out` | `camera gradually pulls back, revealing more of the scene` |
| 오른쪽 팬 | `Pan Right` | `camera smoothly pans from left to right` |
| 왼쪽 팬 | `Pan Left` | `camera smoothly pans from right to left` |
| 충격 줌 | `Crash Zoom` | `camera suddenly crash zooms into the subject` |
| 위에서 아래 틸트 | `Tilt Down` | `camera slowly tilts downward` |
| 정적 | `Static` | `camera remains completely still, no movement` |
| 핸드헬드 | `Handheld` | `slight handheld camera shake, natural documentary feel` |

---

## 업종별 씬 프롬프트 예시

### 치킨 — Hook 씬 (Dolly In, 3~4초)

```
Extreme close-up of golden crispy fried chicken, 
oil glistening on the crunchy skin, wisps of steam rising gently upward,
camera slowly and smoothly pushes in revealing more texture detail,
warm amber studio lighting from above, dark background with subtle depth,
ultra shallow depth of field, bokeh background,
cinematic food commercial style, appetizing and rich,
smooth motion, no cuts, 4 seconds
```

**모델**: Seedance 2.0 (빠른 움직임 대응)  
**프리셋**: Dolly In  
**Duration**: 4초  

---

### 치킨 — Value 씬 (Pan Right, 5~6초)

```
Full shot of golden fried chicken set on white ceramic plate,
camera smoothly pans from left to right, starting from empty space then revealing the full dish,
bright studio lighting, clean white/yellow background,
everything in sharp focus, vivid colors, high saturation,
Korean food commercial style, professional food photography aesthetic,
smooth pan motion, no cuts, 5 seconds
```

**모델**: WAN 2.1 (선명한 디테일)  
**프리셋**: Pan Right  
**Duration**: 5.5초  

---

### 치킨 — Mood 씬 (Slow Pan, 4~5초)

```
Interior of warm Korean fried chicken restaurant,
wooden tables with checkered tablecloths, warm hanging pendant lights,
camera slowly pans right, revealing more of the cozy dining space,
golden hour light streaming through left windows,
soft bokeh on background patrons, inviting and lively atmosphere,
cinematic, smooth motion, no cuts, 4 seconds
```

**모델**: WAN 2.1 또는 Kling 2.0  
**프리셋**: Pan Right (Slow)  
**Duration**: 4.5초  

---

### 치킨 — CTA 씬 (Dolly Out, 3~4초)

```
Exterior of Korean fried chicken restaurant on a quiet street,
illuminated hanging sign clearly visible, warm interior light glowing through windows,
camera gradually pulls back revealing the full storefront and street context,
dusk lighting, inviting atmosphere, signage in sharp focus,
cinematic, smooth dolly-out motion, no cuts, 3 seconds
```

**모델**: Seedance 2.0 또는 Kling 2.0  
**프리셋**: Dolly Out  
**Duration**: 3.5초  

---

## 카페 씬 프롬프트 예시

### 카페 — Hook 씬

```
Close-up of hot coffee in white ceramic mug,
steam rising in soft delicate curls catching warm morning light,
camera gently and slowly pushes in from medium to close-up,
warm amber tones, golden bokeh background, shallow depth of field,
cozy cafe morning atmosphere, cinematic food commercial style,
smooth camera motion, no cuts, 3 seconds
```

**모델**: Seedance 2.0  
**프리셋**: Dolly In (Slow)  

---

### 카페 — Value 씬

```
Barista hands gracefully placing a latte art coffee cup onto a wooden counter,
camera smoothly slides from right to left following the movement,
warm natural light from left window, soft steam visible,
medium depth of field, cozy cafe background slightly blurred,
professional food commercial aesthetic, smooth motion, 5 seconds
```

**모델**: WAN 2.1  
**프리셋**: Pan Left  

---

## 레스토랑/바 씬 프롬프트 예시

### 프리미엄 — Hook 씬

```
Elegant gourmet dish on dark slate plate,
single garnish catching dramatic side light, deep atmospheric shadows,
camera slowly and precisely pushes in, magnifying the fine textures,
cool dark tones with golden rim light, extremely shallow depth of field,
fine dining cinematic style, sophisticated and moody,
smooth motion, no cuts, 3 seconds
```

**모델**: Seedance 2.0  
**프리셋**: Dolly In  

---

## 출력 형식 (`workspace/06_video_prompts.md`)

````markdown
# Higgsfield 동영상 생성 프롬프트

**가게**: 황금치킨 본점  
**테마**: lively  
**플랫폼**: [higgsfield.ai/ai-video](https://higgsfield.ai/ai-video)

---

## Scene 1 — Hook (3초)

**시작 프레임**: `01_store_photos/photo_01.jpg` 업로드  
**모델**: Seedance 2.0  
**카메라 프리셋**: Dolly In  
**Duration**: 3.5초 (편집 시 3초 사용)  
**저장**: `workspace/07_clips/clip_01.mp4`

```
[프롬프트 내용]
```

---

## Scene 2 — Value (5초)

**시작 프레임**: `05_start_frames/scene_02.png` 업로드  
**모델**: WAN 2.1  
**카메라 프리셋**: Pan Right  
**Duration**: 5.5초  
**저장**: `workspace/07_clips/clip_02.mp4`

```
[프롬프트 내용]
```

---

## Scene 3 — Mood (4초)

...

## Scene 4 — CTA (3초)

...
````

---

## 완료 후 출력 메시지

```
✅ Higgsfield 동영상 프롬프트 생성 완료
workspace/06_video_prompts.md 저장됨

📌 다음 액션 (사용자):
1. workspace/06_video_prompts.md 열기
2. 각 씬별 프롬프트를 Higgsfield에서 실행
   → https://higgsfield.ai/ai-video
3. 생성된 클립을 아래 이름으로 저장:
   clip_01.mp4 / clip_02.mp4 / clip_03.mp4 / clip_04.mp4
   → workspace/07_clips/

📌 클립 품질 체크리스트:
  □ 카메라가 의도한 방향으로 움직이는가?
  □ 피사체 형태가 뭉개지지 않는가?
  □ 움직임이 자연스럽고 너무 빠르지 않은가?
  □ 조명이 일관성 있는가?

만족스러운 클립이 준비되면 → skill_06_render.md 실행
```
