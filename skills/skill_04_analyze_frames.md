# Skill 04 — 시작 프레임 이미지 분석
> 입력: `workspace/05_start_frames/` + `workspace/01_store_photos/` (실사진)  
> 출력: `workspace/05_frame_analysis.json`

---

## 역할

Nano Banana로 생성한 이미지와 실사진을 **동영상 생성 관점**에서 분석한다.  
"이 이미지에서 어떤 움직임이 자연스러운가"를 판단하고  
Higgsfield 동영상 프롬프트 작성에 필요한 정보를 추출한다.

---

## 실행 전 확인

`workspace/05_start_frames/` 폴더에 이미지가 있는지 확인한다.  
실사진을 그대로 쓰는 씬은 `workspace/01_store_photos/`에서 가져온다.

---

## 분석 항목 (씬별)

각 씬 이미지에 대해 아래를 판단한다.

### A. 피사체 위치와 구도
```
- 주 피사체가 화면 어디에 있는가?
  → 중앙 / 좌측 / 우측 / 하단 / 상단

- 여백(빈 공간)이 어느 방향에 있는가?
  → 텍스트 오버레이 배치와 카메라 무브 방향 결정에 사용

- 피사체와 배경의 비율은?
  → 피사체 70%+ : 클로즈업 움직임 추천
  → 피사체 40% 이하: 와이드 무브 추천
```

### B. 조명 방향
```
- 빛이 어디서 오는가?
  → 정면광: 카메라 직선 이동 가능
  → 측면광(좌/우): 빛 방향으로 팬 이동 자연스러움
  → 역광: 천천히 당기는 움직임 (Dolly Out) 권장
  → 위에서 아래: Tilt Down 자연스러움
```

### C. 움직임 포인트
```
이미지에서 "움직임이 생겨날 수 있는 요소"를 찾는다:

- 연기/증기: 위쪽으로 피어오름 → 카메라 천천히 올라가기
- 액체/소스: 흘러내림 → 슬로우 모션 + Tilt Down
- 음식 질감: 바삭함/윤기 → 미세한 줌인으로 강조
- 인물/손: 동작 방향으로 카메라 따라가기
- 배경 공간: 깊이감 → Dolly In으로 공간 탐색
- 창문/조명: 빛의 방향으로 팬
```

### D. 텍스트 오버레이 적합 구역
```
이미지에서 텍스트를 올렸을 때 가장 자연스러운 위치:

- 하단 1/3: 피사체가 중앙이나 상단에 있을 때
- 좌측: 피사체가 우측에 있을 때
- 우측: 피사체가 좌측에 있을 때
- 중앙: 피사체 주변 공간이 충분할 때
```

### E. 컬러 그레이딩 방향
```
이미지 색조를 보고 후처리 방향 결정:
- 이미 따뜻한 톤: 채도 ×1.2 정도만 (과보정 금지)
- 차가운 톤: R+20, B-15로 따뜻하게 보정 필요
- 어두운 이미지: 밝기 +15, 대비 +10
- 이미 선명한 이미지: 채도 ×1.3 정도
```

---

## 씬별 카메라 무브 결정 로직

```
피사체 = 음식 클로즈업?
  → 여백 없음 → Dolly In (극단적 클로즈업 강조)
  → 여백 있음 → Slow Push-In (안정적 접근)

피사체 = 음식 전체 샷?
  → 좌우 공간 있음 → Pan Right (메뉴 리빌)
  → 위에서 촬영 → Static (안정적 유지, 텍스트 강조)

피사체 = 인테리어/공간?
  → 깊이 있음 → Dolly In (공간 탐색)
  → 넓은 공간 → Slow Pan Right/Left

피사체 = 외관/간판?
  → CTA 씬 → Dolly Out (전체 노출, 웅장함)
  → 좁은 골목 → Static + Tilt Up
```

---

## 출력 형식 (`workspace/05_frame_analysis.json`)

```json
{
  "analyzed_at": "2026-04-24",
  "scenes": [
    {
      "scene_id": 1,
      "role": "Hook",
      "source_file": "01_store_photos/photo_01.jpg",
      "subject_position": "center",
      "empty_space": "bottom",
      "light_direction": "top-left",
      "motion_points": ["steam_rising", "texture_glistening"],
      "text_zone": "bottom_third",
      "recommended_camera": "Dolly In (slow)",
      "higgsfield_preset": "dolly_in",
      "color_notes": "already warm, saturation ×1.3 only",
      "animation_anchor": "steam area upper center"
    },
    {
      "scene_id": 2,
      "role": "Value",
      "source_file": "05_start_frames/scene_02.png",
      "subject_position": "right-center",
      "empty_space": "left",
      "light_direction": "top-center studio",
      "motion_points": ["crispy_texture", "plate_reflection"],
      "text_zone": "left_third",
      "recommended_camera": "Pan Right",
      "higgsfield_preset": "pan_right",
      "color_notes": "add saturation ×1.4, R+10",
      "animation_anchor": "left empty space to right subject"
    },
    {
      "scene_id": 3,
      "role": "Mood",
      "source_file": "01_store_photos/photo_03.jpg",
      "subject_position": "center-wide",
      "empty_space": "right",
      "light_direction": "left window",
      "motion_points": ["dust_particles", "ambient_light"],
      "text_zone": "center_bottom",
      "recommended_camera": "Slow Pan Right",
      "higgsfield_preset": "pan_right",
      "color_notes": "warm up, R+15, saturation ×1.2",
      "animation_anchor": "window light direction"
    },
    {
      "scene_id": 4,
      "role": "CTA",
      "source_file": "01_store_photos/photo_02.jpg",
      "subject_position": "center",
      "empty_space": "sides",
      "light_direction": "natural outdoor",
      "motion_points": ["signage", "street_environment"],
      "text_zone": "bottom_third",
      "recommended_camera": "Dolly Out",
      "higgsfield_preset": "dolly_out",
      "color_notes": "slight brightness +10, neutral",
      "animation_anchor": "store entrance center"
    }
  ]
}
```

---

## 완료 후 출력 메시지

```
✅ 시작 프레임 분석 완료

Scene 1 Hook  → Dolly In  | 텍스트: 하단
Scene 2 Value → Pan Right | 텍스트: 좌측
Scene 3 Mood  → Slow Pan  | 텍스트: 중앙 하단
Scene 4 CTA   → Dolly Out | 텍스트: 하단

다음 단계: skill_05_video_prompts.md 실행
```
