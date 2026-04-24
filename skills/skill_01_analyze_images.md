# Skill 01 — 가게 실사진 분석
> 입력: `workspace/01_store_photos/` 폴더의 이미지들  
> 출력: `workspace/02_analysis.json`

---

## 역할

사용자가 넣어둔 가게 실사진을 보고 **각 이미지가 어떤 씬에 적합한지**,  
**품질이 시작 프레임으로 쓸 수 있는지** 판단한다.

---

## 실행 절차

### 1단계 — 이미지 목록 확인

`workspace/01_store_photos/` 폴더의 이미지 파일을 전부 나열한다.  
지원 형식: `.jpg` `.jpeg` `.png` `.webp`

이미지가 없으면 아래 메시지를 출력하고 중단한다.
```
⚠️ workspace/01_store_photos/ 폴더에 이미지가 없습니다.
가게 사진을 넣은 뒤 다시 실행해주세요.
```

---

### 2단계 — 이미지별 분석

각 이미지에 대해 아래 항목을 판단한다.

#### 피사체 분류 (하나만 선택)
| 코드 | 설명 | 예시 |
|------|------|------|
| `food_closeup` | 음식 클로즈업 | 치킨 확대, 커피 클로즈업 |
| `food_fullshot` | 음식 전체 샷 | 메뉴 세트, 플레이팅 전체 |
| `interior` | 매장 내부 | 테이블, 인테리어, 손님 |
| `exterior` | 매장 외관 | 간판, 건물 전경 |
| `menu_board` | 메뉴판 | 벽 메뉴판, 테이블 메뉴 |
| `staff` | 직원/요리 과정 | 조리 장면, 서빙 |
| `other` | 기타 | |

#### 분위기 판단 (하나만 선택)
| 코드 | 설명 |
|------|------|
| `warm` | 따뜻함, 아늑함, 감성적 |
| `lively` | 활기참, 밝음, 식욕 자극 |
| `premium` | 세련됨, 고급스러움, 차분함 |

#### 씬 적합도 판단 (하나만 선택)
| 코드 | 설명 | 이런 이미지면 |
|------|------|-------------|
| `Hook` | 0~3초, 시선 사로잡기 | 음식 클로즈업, 강렬한 첫인상 |
| `Value` | 3~8초, 가격·메뉴 정보 | 음식 전체 샷, 메뉴판 |
| `Mood` | 8~12초, 분위기·신뢰 | 인테리어, 손님, 조리 과정 |
| `CTA` | 12~15초, 행동 유도 | 외관, 간판, 지도 |

#### 품질 점수 (0~10)
| 점수 | 기준 |
|------|------|
| 9~10 | 선명, 적절한 조명, 구도 좋음 → 즉시 사용 가능 |
| 7~8 | 약간의 노이즈나 역광 있지만 사용 가능 |
| 5~6 | 흐림, 어두움, 잘린 구도 → 주의해서 사용 |
| 4 이하 | 사용 불가 → Nano Banana 생성으로 대체 필요 |

#### 문제점 목록 (해당하는 것 모두)
- `역광` — 피사체보다 배경이 밝음
- `흐림` — 초점이 맞지 않음
- `어두움` — 전체적으로 노출 부족
- `구도_불량` — 중요한 피사체가 잘리거나 치우침
- `배경_복잡` — 배경이 너무 복잡해서 피사체가 묻힘
- `해상도_낮음` — 확대 시 픽셀이 보임

---

### 3단계 — 전체 판단

모든 이미지 분석이 끝나면 아래를 판단한다.

**테마 추천**:
- 이미지 대부분이 따뜻한 톤 → `warm`
- 음식이 선명하고 채도 높음 → `lively`
- 어둡고 세련된 분위기 → `premium`

**부족한 씬 파악**:
- Hook 역할 이미지 없거나 품질 5 이하 → `Hook 씬 생성 필요`
- Value 역할 이미지 없거나 품질 5 이하 → `Value 씬 생성 필요`
- Mood 역할 이미지 없거나 품질 5 이하 → `Mood 씬 생성 필요`
- CTA 역할 이미지 없거나 품질 5 이하 → `CTA 씬 생성 필요`

---

## 출력 형식 (`workspace/02_analysis.json`)

```json
{
  "analyzed_at": "2026-04-24",
  "store_name": "황금치킨",
  "detected_category": "치킨",
  "theme_recommendation": "lively",
  "scenes_to_generate": ["Value"],
  "images": [
    {
      "file": "photo_01.jpg",
      "subject": "food_closeup",
      "mood": "lively",
      "recommended_scene": "Hook",
      "quality_score": 8.5,
      "usable": true,
      "issues": []
    },
    {
      "file": "photo_02.jpg",
      "subject": "exterior",
      "mood": "warm",
      "recommended_scene": "CTA",
      "quality_score": 7.0,
      "usable": true,
      "issues": ["역광"]
    },
    {
      "file": "photo_03.jpg",
      "subject": "interior",
      "mood": "warm",
      "recommended_scene": "Mood",
      "quality_score": 8.0,
      "usable": true,
      "issues": []
    }
  ],
  "scene_assignment": {
    "Hook":  {"file": "photo_01.jpg", "source": "real_photo"},
    "Value": {"file": null,           "source": "generate"},
    "Mood":  {"file": "photo_03.jpg", "source": "real_photo"},
    "CTA":   {"file": "photo_02.jpg", "source": "real_photo"}
  }
}
```

---

## 완료 후 출력 메시지 예시

```
✅ 이미지 분석 완료

총 3장 분석:
  Hook  ← photo_01.jpg (품질 8.5) ✅ 사용
  Value ← 이미지 없음 ⚠️ Nano Banana 생성 필요
  Mood  ← photo_03.jpg (품질 8.0) ✅ 사용
  CTA   ← photo_02.jpg (품질 7.0, 역광 있음) ✅ 사용

추천 테마: lively
다음 단계: skill_02_storyboard.md 실행
```
