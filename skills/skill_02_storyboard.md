# Skill 02 — 스토리보드 설계
> 입력: `workspace/02_analysis.json` + 사용자가 제공한 가게 정보  
> 출력: `workspace/03_storyboard.json`

---

## 역할

이미지 분석 결과와 가게 기본 정보를 합쳐  
**4씬 15초 광고 스토리보드**를 완성한다.  
각 씬의 카피, 카메라 움직임, 이미지 소스를 확정한다.

---

## 실행 전 — 가게 정보 수집

분석 결과에서 자동 파악되지 않은 정보를 사용자에게 확인한다.

```
다음 정보를 입력해주세요 (없으면 Enter로 건너뜀):

1. 가게 이름: 
2. 대표 메뉴 + 가격 (예: 황금 후라이드 17,000원): 
3. 주소: 
4. 영업시간: 
5. 전화번호: 
6. 리뷰 한 줄 (없으면 자동 생성): 
7. QR 연결 URL (없으면 생략): 
```

---

## 카피 자동 생성 원칙

### 메인 카피 (Hook 씬, 대형 타이포)
업종별 감성 + 핵심 가치를 담은 **5~10자** 내외 문구

| 업종 | 카피 방향 | 예시 |
|------|----------|------|
| 카페·베이커리 | 감성, 여유, 일상의 소확행 | "오늘 하루, 한잔의 여유" |
| 치킨·분식·패스트푸드 | 맛, 바삭함, 가성비 직관 | "바삭함이 다르다!" |
| 한식·고기집 | 정직한 맛, 가족, 특별한 날 | "진짜 맛을 아는 사람들" |
| 레스토랑·파인다이닝 | 특별함, 감각, 경험 | "오늘 밤, 특별한 순간" |
| 분식·떡볶이 | 추억, 편안함, 합리적 | "언제나 그 자리에" |

### 리뷰 문구 (Mood 씬)
- 실제 리뷰가 있으면 그대로 사용
- 없으면 업종별 전형적인 긍정 리뷰 생성
  - 카페: `"여기 오면 하루가 좋아져요"`
  - 치킨: `"치킨은 역시 여기!"`
  - 고기집: `"분위기도 맛도 최고예요"`

---

## 씬별 설계 기준

### Scene 1 — Hook (0~3초)
```
목적: 0.5초 안에 시선 사로잡기
이미지: 음식 클로즈업 or 임팩트 강한 사진
카피: main_copy (대형, 화면 하단 1/3)
카메라: Dolly In (느린 푸시인) — 몰입감
텍스트 등장: 1초 후 spring 바운스 등장
```

### Scene 2 — Value (3~8초)
```
목적: 핵심 정보 전달 — 메뉴명 + 가격
이미지: 음식 전체 샷 or Nano Banana 생성
카피: "메뉴명\n가격" (서브 사이즈)
특수 요소: 가격 원형 배지 (바운스 팝업, 1.5초 후 등장)
카메라: Pan Right or Overhead Tilt
텍스트 등장: 슬라이드 인 (왼쪽에서)
```

### Scene 3 — Mood (8~12초)
```
목적: 분위기·신뢰 구축 — 리뷰 인용
이미지: 인테리어 or 조리 과정 or 손님
카피: 리뷰 문구 (따옴표 포함)
특수 요소: 반투명 박스 배경 위 텍스트
카메라: Slow Pan or Ken Burns
텍스트 등장: 0.6초 fade-in
```

### Scene 4 — CTA (12~15초)
```
목적: 행동 유도 — 방문·주문 촉구
이미지: 매장 외관
카피: 가게명 (강조색) + 주소·영업시간
특수 요소: QR 코드 (0.5초 후 fade-in) + Lower Third 바
카메라: Dolly Out (와이드 노출)
텍스트 등장: 전체 fade-in
```

---

## 출력 형식 (`workspace/03_storyboard.json`)

```json
{
  "store_name": "황금치킨 본점",
  "category": "치킨",
  "template": "lively",
  "total_duration": 15,
  "ad_copy": {
    "main_copy": "바삭함이 다르다!",
    "review_text": "\"치킨은 역시 황금치킨!\"",
    "cta_text": "망원동 12-3  |  오후 4시 – 새벽 1시",
    "price_badge": "황금 후라이드\n17,000원"
  },
  "store_info": {
    "name": "황금치킨 본점",
    "address": "마포구 망원동 12-3",
    "hours": "매일 16:00 – 01:00",
    "phone": "02-9876-5432",
    "qr_url": "https://dongne.app/r?store=golden_chicken"
  },
  "scenes": [
    {
      "id": 1,
      "role": "Hook",
      "duration": 3,
      "source_file": "photo_01.jpg",
      "source_type": "real_photo",
      "generate_new_frame": false,
      "copy": "바삭함이 다르다!",
      "visual_goal": "황금빛 치킨 클로즈업, 김 모락모락, 식욕 자극",
      "camera_move": "Dolly In (slow)",
      "text_animation": "spring_bounce",
      "special_effects": []
    },
    {
      "id": 2,
      "role": "Value",
      "duration": 5,
      "source_file": null,
      "source_type": "generate",
      "generate_new_frame": true,
      "copy": "황금 후라이드\n17,000원",
      "visual_goal": "치킨 세트 전체 샷, 깔끔한 배경, 메뉴 정보 강조",
      "camera_move": "Pan Right",
      "text_animation": "slide_in_left",
      "special_effects": ["price_badge"]
    },
    {
      "id": 3,
      "role": "Mood",
      "duration": 4,
      "source_file": "photo_03.jpg",
      "source_type": "real_photo",
      "generate_new_frame": false,
      "copy": "\"치킨은 역시 황금치킨!\"",
      "visual_goal": "매장 내부, 테이블, 손님 분위기",
      "camera_move": "Slow Pan Right",
      "text_animation": "fade_in",
      "special_effects": ["review_box"]
    },
    {
      "id": 4,
      "role": "CTA",
      "duration": 3,
      "source_file": "photo_02.jpg",
      "source_type": "real_photo",
      "generate_new_frame": false,
      "copy": "황금치킨 본점",
      "visual_goal": "매장 외관 와이드샷, 간판 선명",
      "camera_move": "Dolly Out",
      "text_animation": "fade_in",
      "special_effects": ["lower_third", "qr_code"]
    }
  ]
}
```

---

## 완료 후 사용자에게 보여줄 스토리보드 요약

```
📋 스토리보드 확정

┌─────────────────────────────────────────────────────┐
│ Scene 1 Hook   0~3초  │ photo_01.jpg (실사진)       │
│ "바삭함이 다르다!"      │ 카메라: 천천히 밀기          │
├─────────────────────────────────────────────────────┤
│ Scene 2 Value  3~8초  │ ⚡ Nano Banana 생성 필요     │
│ "황금 후라이드 17,000원"│ 가격 배지 팝업 포함          │
├─────────────────────────────────────────────────────┤
│ Scene 3 Mood   8~12초 │ photo_03.jpg (실사진)       │
│ "치킨은 역시 황금치킨!" │ 리뷰 박스 오버레이           │
├─────────────────────────────────────────────────────┤
│ Scene 4 CTA    12~15초│ photo_02.jpg (실사진)       │
│ 주소 + 전화 + QR       │ Lower Third 바 + QR 코드   │
└─────────────────────────────────────────────────────┘

수정이 필요하면 말씀해주세요.
확인되면 → skill_03_image_prompts.md 실행
```
