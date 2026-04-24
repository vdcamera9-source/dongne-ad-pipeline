# 동네방네 광고 영상 생성 에이전트
> 버전: 1.0 | 작성일: 2026-04-24  
> **역할**: 가게 실사진 → 15초 TV 광고 MP4 자동 생성 오케스트레이터

---

## 에이전트 소개

이 에이전트는 소상공인 가게의 실사진과 기본 정보를 입력받아  
아래 6개 스킬을 순서대로 실행하면서 최종 광고 영상을 만든다.

**각 스킬은 `skills/` 폴더의 마크다운 파일이다.**  
에이전트(Claude)가 해당 마크다운을 읽고 그 지시에 따라 작업한다.

---

## 전체 워크플로우

```
사용자: 가게 사진을 workspace/01_store_photos/ 에 넣고 시작
         ↓
STEP 1  skill_01_analyze_images.md
         가게 사진 분석 → 씬 배정 · 품질 평가
         출력: workspace/02_analysis.json
         ↓
STEP 2  skill_02_storyboard.md
         4씬 스토리보드 설계 + 카피 작성
         출력: workspace/03_storyboard.json
         ↓
STEP 3  skill_03_image_prompts.md      ← 생성 필요 씬이 있을 때만
         Nano Banana 이미지 프롬프트 생성
         출력: workspace/04_image_prompts.md
         ↓
[USER]  Nano Banana에서 이미지 생성 → workspace/05_start_frames/ 저장
         ↓
STEP 4  skill_04_analyze_frames.md
         시작 프레임 분석 → 카메라 무브 결정
         출력: workspace/05_frame_analysis.json
         ↓
STEP 5  skill_05_video_prompts.md
         Higgsfield 동영상 프롬프트 생성
         출력: workspace/06_video_prompts.md
         ↓
[USER]  Higgsfield에서 클립 생성 → workspace/07_clips/ 저장
         ↓
STEP 6  skill_06_render.md
         MoviePy로 최종 합성 렌더링
         출력: workspace/08_output/final_ad.mp4
```

---

## 워크스페이스 구조

```
video_pipeline/
├── AGENT.md                          ← 지금 이 파일
├── skills/
│   ├── skill_01_analyze_images.md
│   ├── skill_02_storyboard.md
│   ├── skill_03_image_prompts.md
│   ├── skill_04_analyze_frames.md
│   ├── skill_05_video_prompts.md
│   └── skill_06_render.md
└── workspace/
    ├── 01_store_photos/     ← [USER] 가게 실사진 여기에
    ├── 02_analysis.json     ← skill_01 출력
    ├── 03_storyboard.json   ← skill_02 출력
    ├── 04_image_prompts.md  ← skill_03 출력
    ├── 05_start_frames/     ← [USER] Nano Banana 생성 이미지
    ├── 05_frame_analysis.json ← skill_04 출력
    ├── 06_video_prompts.md  ← skill_05 출력
    ├── 07_clips/            ← [USER] Higgsfield 생성 클립
    └── 08_output/           ← skill_06 출력 (최종 MP4)
```

---

## 에이전트 실행 방법

### 전체 자동 실행 (처음부터)

```
"AGENT.md를 읽고 전체 광고 제작 프로세스를 시작해줘"
```

### 특정 스킬만 실행

```
"skill_03을 실행해줘"
"스토리보드가 완성됐어, 이미지 프롬프트 만들어줘"
"클립 다 만들었어, 렌더링해줘"
```

### 현재 상태 확인

```
"지금 어느 단계까지 완료됐어?"
"workspace 폴더 상태 확인해줘"
```

---

## 각 스텝 상세

### STEP 1 — 이미지 분석

**파일**: `skills/skill_01_analyze_images.md`  
**실행 조건**: `workspace/01_store_photos/`에 이미지 있을 때  
**주요 판단**:
- 각 이미지의 씬 역할 (Hook/Value/Mood/CTA)
- 품질 점수 (7 미만이면 생성 권장)
- 부족한 씬 파악

**에이전트 행동**:
1. `workspace/01_store_photos/` 폴더 확인
2. 이미지 하나씩 분석
3. `02_analysis.json` 작성
4. 결과 요약 출력 후 STEP 2 진행 여부 확인

---

### STEP 2 — 스토리보드 설계

**파일**: `skills/skill_02_storyboard.md`  
**실행 조건**: `02_analysis.json` 존재  
**주요 결정**:
- 씬별 카피 문구 (자동 생성 또는 사용자 제공)
- 이미지 소스 (실사진 vs Nano Banana)
- 카메라 무브 방향

**에이전트 행동**:
1. 가게 정보 수집 (이름, 메뉴, 가격, 주소, 영업시간)
2. 스토리보드 초안 작성
3. 사용자에게 표 형식으로 보여주고 확인 요청
4. 확인 후 `03_storyboard.json` 저장

> ⚠️ **확인 없이 넘어가지 않는다** — 스토리보드는 반드시 사용자 승인 후 진행

---

### STEP 3 — Nano Banana 프롬프트 (조건부)

**파일**: `skills/skill_03_image_prompts.md`  
**실행 조건**: `03_storyboard.json`에 `generate_new_frame: true`인 씬 존재  
**건너뜀 조건**: 모든 씬이 실사진으로 커버될 때

**에이전트 행동**:
1. 생성 필요 씬 파악
2. 업종·테마에 맞는 프롬프트 작성
3. `04_image_prompts.md` 저장
4. 사용 방법 안내 출력

**사용자 액션 필요**:
```
📌 [사용자 액션 필요]
workspace/04_image_prompts.md의 프롬프트로 Nano Banana에서 이미지 생성 후
workspace/05_start_frames/ 폴더에 저장해주세요.

완료되면: "이미지 생성 완료, 다음 진행해줘"
```

---

### STEP 4 — 시작 프레임 분석

**파일**: `skills/skill_04_analyze_frames.md`  
**실행 조건**: `workspace/05_start_frames/`에 이미지 존재 (또는 모두 실사진)

**에이전트 행동**:
1. 생성된 이미지 + 실사진 순서대로 분석
2. 카메라 무브, 텍스트 구역, 색보정 방향 결정
3. `05_frame_analysis.json` 저장

---

### STEP 5 — Higgsfield 프롬프트

**파일**: `skills/skill_05_video_prompts.md`  
**실행 조건**: `05_frame_analysis.json` 존재

**에이전트 행동**:
1. 씬별 최적 모델 선택 (Seedance 2.0 / WAN 2.1)
2. 씬별 프롬프트 작성
3. `06_video_prompts.md` 저장
4. 사용 방법 + 클립 저장 안내 출력

**사용자 액션 필요**:
```
📌 [사용자 액션 필요]
workspace/06_video_prompts.md의 프롬프트로 Higgsfield에서 클립 생성 후
workspace/07_clips/ 폴더에 저장해주세요.

파일명: clip_01.mp4 / clip_02.mp4 / clip_03.mp4 / clip_04.mp4
완료되면: "클립 생성 완료, 렌더링해줘"
```

---

### STEP 6 — 최종 렌더링

**파일**: `skills/skill_06_render.md`  
**실행 조건**: `workspace/07_clips/`에 clip_01~04.mp4 존재

**에이전트 행동**:
1. 클립 파일 존재 확인
2. `render.py` 실행 (클립 모드)
3. 합성 레이어 순서대로 처리
4. `workspace/08_output/final_ad.mp4` 출력
5. 품질 검증 후 완료 보고

---

## 에러 처리 매뉴얼

| 상황 | 대응 |
|------|------|
| 이미지 없음 | 사용자에게 폴더 안내 후 중단 |
| 품질 낮은 이미지만 있음 | Nano Banana 생성 권장 안내 |
| 스토리보드 수정 요청 | 해당 씬만 수정 후 재확인 |
| Nano Banana 이미지 불만족 | 프롬프트 개선안 제시 |
| Higgsfield 클립 불만족 | 프롬프트 수정 + 재시도 가이드 |
| 렌더링 오류 | 오류 메시지 분석 후 해결책 제시 |
| 클립 길이 불일치 | trim/pad 처리 후 재렌더링 |

---

## 외부 도구 빠른 링크

| 도구 | 용도 | URL |
|------|------|-----|
| DeeVid Nano Banana | 시작 프레임 이미지 생성 | https://deevid.ai/model/nano-banana |
| Higgsfield I2V | 이미지 → 동영상 클립 | https://higgsfield.ai/ai-video |
| Higgsfield 카메라 가이드 | 프롬프트 작성 참고 | https://higgsfield.ai/blog/WAN-AI-Camera-Control-Your-Guide-to-Cinematic-Motion |
| Google Veo 3.1 | 대안 I2V (무료 10회/월) | https://aistudio.google.com/models/veo-3 |

---

## 시작하기

```
가게 사진을 workspace/01_store_photos/ 폴더에 넣으세요.
준비되면 이렇게 말해주세요:

"동네방네 광고 시작해줘"
```
