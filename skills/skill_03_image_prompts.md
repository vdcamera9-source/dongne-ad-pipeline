# Skill 03 — Nano Banana 시작 프레임 생성 프롬프트
> 입력: `workspace/03_storyboard.json`  
> 출력: `workspace/04_image_prompts.md` (복사해서 바로 쓸 수 있는 프롬프트)

---

## 역할

스토리보드에서 `generate_new_frame: true`인 씬에 대해  
**Nano Banana (Gemini 3.1 Flash Image)** 에 그대로 붙여넣을 수 있는  
고품질 이미지 생성 프롬프트를 만든다.

---

## Nano Banana 사용 방법

1. **DeeVid** 접속 → [deevid.ai/model/nano-banana](https://deevid.ai/model/nano-banana)  
2. 모델: **Nano Banana 2** (Gemini 3.1 Flash Image) 선택
3. 종횡비: **16:9** (1920×1080)
4. 아래 프롬프트를 복사해서 붙여넣기
5. 생성된 이미지를 `workspace/05_start_frames/scene_XX.png`로 저장

---

## 프롬프트 설계 원칙

> AI동영상.md 핵심: "시작 프레임 품질 = 결과 영상의 80%"

**구조**: `[피사체] + [구도/샷 크기] + [조명] + [분위기] + [기술 사양]`

**필수 포함 요소**:
- 렌즈 정보: `shot on 85mm lens` / `50mm lens` / `35mm wide angle`
- 심도: `shallow depth of field` / `deep focus`
- 조명: `warm golden light` / `studio soft box` / `dramatic side light`
- 스타일: `commercial food photography` / `advertising photography`
- 해상도: `4K photorealistic` / `ultra detailed`

**절대 쓰지 않기**:
- `beautiful` `amazing` `stunning` (너무 추상적)
- 두 가지 이상의 주제를 한 프롬프트에 (AI동영상.md 실수 ⑤)

---

## 업종별 프롬프트 템플릿

### 카페 / 베이커리 (warm 테마)

**Hook 씬 — 음식 클로즈업**
```
Close-up of a steaming hot coffee in a white ceramic mug,
placed on a rustic wooden table near a sunlit window,
steam rising in soft curls catching warm morning light,
shot on 85mm lens, very shallow depth of field,
warm amber tones, creamy bokeh background,
commercial food photography, cozy cafe atmosphere,
4K photorealistic, no text, no watermark
```

**Value 씬 — 메뉴 전체 샷**
```
Top-down flat lay of cafe menu items: latte, croissant, and small dessert
arranged neatly on a white marble surface,
soft natural daylight from the left, clean and minimal styling,
shot on 50mm lens, moderate depth of field,
warm neutral tones, Instagram-worthy food styling,
Korean cafe advertisement photography, ultra detailed, 4K
```

---

### 치킨 / 분식 / 패스트푸드 (lively 테마)

**Hook 씬 — 음식 클로즈업**
```
Extreme close-up of golden crispy fried chicken piece,
glistening oil on the skin, steam rising dramatically,
shot on 100mm macro lens, ultra shallow depth of field,
warm studio lighting from above and slight left,
rich amber and orange tones, high saturation,
Korean fried chicken food commercial photography,
appetizing and mouthwatering, 4K photorealistic, no text
```

**Value 씬 — 메뉴 전체 + 가격 공간 확보**
```
Full shot of golden fried chicken set on a clean white plate,
placed on a bright yellow and white striped paper background,
studio lighting, sharp focus on entire dish,
shot on 50mm lens, everything in focus,
vivid warm colors, high contrast, clean edges,
Korean restaurant menu photography style,
space on left side for text overlay, 4K, no text, no watermark
```

**Mood 씬 — 매장 분위기**
```
Interior of a cozy Korean fried chicken restaurant,
wooden tables and warm hanging lights,
a family or friends group blurred softly in background,
shot on 35mm lens, medium depth of field,
warm golden hour lighting from windows,
inviting and lively atmosphere, editorial photography,
4K photorealistic, no people in sharp focus
```

---

### 한식 / 고기집 (warm 또는 lively 테마)

**Hook 씬**
```
Close-up of sizzling Korean BBQ meat on a hot iron grill,
smoke and steam rising, meat glistening with marinade,
shot on 85mm lens, shallow depth of field,
dramatic warm lighting, dark background with glowing embers,
commercial food photography, appetizing Korean BBQ style,
4K ultra detailed, no text
```

**Value 씬**
```
Elegant spread of Korean BBQ dishes: marinated meat, side dishes (banchan),
lettuce wraps, and dipping sauces arranged on dark wooden table,
soft studio lighting, top-down 45-degree angle,
shot on 50mm, all items in focus,
rich warm colors, traditional Korean dining atmosphere,
restaurant menu photography, ultra detailed, 4K
```

---

### 레스토랑 / 바 (premium 테마)

**Hook 씬**
```
Elegant close-up of a gourmet dish on a dark slate plate,
single garnish visible, dramatic side lighting creating deep shadows,
shot on 100mm macro lens, extremely shallow depth of field,
cool dark tones with golden highlights, moody and sophisticated,
fine dining food photography, Michelin-star plating style,
4K photorealistic, no text, no watermark
```

**Value 씬**
```
Premium dinner course spread on dark marble table,
wine glass, plated appetizer and main, subtle candlelight,
shot on 50mm lens, shallow depth of field,
deep navy and gold color palette, luxurious atmosphere,
upscale restaurant advertising photography,
space on right for text overlay, 4K, no text
```

---

## 출력 형식 (`workspace/04_image_prompts.md`)

스토리보드의 `generate_new_frame: true` 씬마다 아래 형식으로 출력한다.

````markdown
# Nano Banana 이미지 생성 프롬프트

**가게**: 황금치킨 본점  
**테마**: lively  
**생성 플랫폼**: DeeVid → Nano Banana 2  
**종횡비**: 16:9 (1920×1080)

---

## Scene 2 — Value 씬

**목적**: 황금 후라이드 치킨 전체 샷, 가격 텍스트 공간 확보  
**저장 위치**: `workspace/05_start_frames/scene_02.png`

```
Full shot of golden fried chicken set on a clean white plate,
placed on a bright yellow and white striped paper background,
studio lighting, sharp focus on entire dish,
shot on 50mm lens, everything in focus,
vivid warm colors, high contrast, clean edges,
Korean restaurant menu photography style,
space on left side for text overlay, 4K, no text, no watermark
```

**생성 팁**:
- 텍스트가 들어갈 왼쪽 공간이 충분한지 확인
- 배경이 너무 복잡하면 재생성
- 치킨이 화면의 60~70% 차지하는 구도 선택

---

## (추가 씬 있을 경우 동일 형식 반복)
````

---

## 완료 후 출력 메시지

```
✅ Nano Banana 프롬프트 생성 완료
workspace/04_image_prompts.md 저장됨

📌 다음 액션 (사용자):
1. workspace/04_image_prompts.md 열기
2. 각 씬의 프롬프트를 Nano Banana에 붙여넣기
   → https://deevid.ai/model/nano-banana
3. 생성된 이미지를 아래 이름으로 저장:
   → workspace/05_start_frames/scene_02.png

저장 완료 후 → skill_04_analyze_frames.md 실행
```
