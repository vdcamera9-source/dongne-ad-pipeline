# Skill 06 — MoviePy 최종 렌더링
> 입력: `workspace/07_clips/` (Higgsfield 생성 클립 4개) + `workspace/03_storyboard.json`  
> 출력: `workspace/08_output/final_ad.mp4`

---

## 역할

Higgsfield가 생성한 4개의 동영상 클립 위에  
**텍스트 · 그래픽 · 색보정 레이어**를 합성해  
최종 15초 광고 MP4를 출력한다.

---

## 실행 전 체크리스트

```
□ workspace/07_clips/clip_01.mp4 존재 확인
□ workspace/07_clips/clip_02.mp4 존재 확인
□ workspace/07_clips/clip_03.mp4 존재 확인
□ workspace/07_clips/clip_04.mp4 존재 확인
□ workspace/03_storyboard.json 존재 확인
□ assets/fonts/Pretendard-Bold.ttf 존재 확인
```

클립이 없으면:
```
⚠️ clip_0X.mp4 파일이 없습니다.
Higgsfield에서 클립을 생성 후 workspace/07_clips/에 저장해주세요.
```

---

## 합성 레이어 순서 (아래에서 위로)

```
Layer 1  Higgsfield 클립          ← 베이스 동영상
Layer 2  컬러 그레이딩             ← 채도·색온도 보정
Layer 3  비네팅                    ← 가장자리 어둡게
Layer 4  White Flash 전환          ← 씬 전환 효과
Layer 5  Lower Third 바            ← 하단 주소 바 (씬 4만)
Layer 6  가격 배지                 ← 원형 스탬프 (씬 2만)
Layer 7  메인 텍스트 오버레이       ← 씬별 카피
Layer 8  QR 코드                   ← 씬 4 마지막에 fade-in
```

---

## Layer별 처리 방법

### Layer 2 — 컬러 그레이딩

테마별 보정값:

| 테마 | R 채널 | G 채널 | B 채널 | 채도 | 밝기 |
|------|--------|--------|--------|------|------|
| **warm** | +15 | +5 | -10 | ×1.35 | +5 |
| **lively** | +10 | +5 | -5 | ×1.45 | +8 |
| **premium** | -5 | -5 | +10 | ×1.20 | -5 |

numpy로 처리:
```python
frame = frame.astype(np.float32)
frame[:,:,0] = np.clip(frame[:,:,0] + R보정, 0, 255)  # R
frame[:,:,1] = np.clip(frame[:,:,1] + G보정, 0, 255)  # G
frame[:,:,2] = np.clip(frame[:,:,2] + B보정, 0, 255)  # B
# 채도: HSV 변환 후 S 채널 × 배율
frame = np.clip(frame, 0, 255).astype(np.uint8)
```

---

### Layer 3 — 비네팅

화면 가장자리를 어둡게 처리해 중앙 집중 효과:

```python
# 중앙에서 멀어질수록 어두워지는 마스크 생성
# 강도: 가장자리 20~30% 어둡게
# 적용: 모든 씬에 항상 켜짐
vignette_strength = 0.7  # 0.0 = 효과 없음, 1.0 = 완전 검정
```

---

### Layer 4 — White Flash 씬 전환

씬과 씬 사이 0.15초(4~5프레임) 화이트 프레임 삽입:

```
[씬 1 마지막 5프레임] → [화이트 5프레임] → [씬 2 첫 프레임]
```

- 화이트 프레임: RGB (255, 255, 255)
- 총 0.15초 (30fps 기준 4프레임)
- warm 테마: fade (부드럽게)
- lively 테마: hard cut (강하게)
- premium 테마: fade to black (블랙 플래시)

---

### Layer 5 — Lower Third 바 (씬 4 전용)

화면 하단에 브랜드 색상 띠:

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│ [브랜드 강조색 배경 바 — 화면 하단 18% 높이]            │
│  가게명                    주소 | 영업시간              │
└────────────────────────────────────────────────────────┘
```

- 씬 4 시작 후 0.4초에 아래에서 슬라이드업
- 배경색: 테마 accent_color (반투명 90%)
- 텍스트: 화이트, Pretendard-Bold

---

### Layer 6 — 가격 배지 (씬 2 전용)

원형 배지가 바운스로 등장:

```
      ┌─────────┐
      │ 황금 후 │
      │ 라이드  │
      │17,000원 │
      └─────────┘
   → 씬2 시작 1.5초 후 팡! 등장
   → 빨간 원형 배경 + 흰 텍스트
   → 바운스: 1.3배 → 1.0배 (0.3초)
```

---

### Layer 7 — 텍스트 오버레이

씬별 카피를 스토리보드의 `text_animation` 값으로 등장:

| 애니메이션 | 효과 | 적용 씬 |
|-----------|------|---------|
| `spring_bounce` | 아래에서 튀어오름 | Hook |
| `slide_in_left` | 왼쪽에서 슬라이드 | Value |
| `fade_in` | 서서히 등장 | Mood, CTA |

폰트:
- warm: Pretendard-Bold, 텍스트색 `#3D2B1F`
- lively: Pretendard-Bold, 텍스트색 `#2D2D2D`  
- premium: Pretendard-Bold, 텍스트색 `#FFFFFF`

---

### Layer 8 — QR 코드 (씬 4 전용)

- 씬 4 시작 0.5초 후 우하단에 fade-in
- 흰 배경 패딩 박스 (16px)
- 크기: 200×200px
- "QR 스캔하기" 텍스트 (작은 폰트) 아래 표시

---

## 렌더링 실행 명령

```bash
cd C:\00_DEV\13_addd\video_pipeline
uv run python render.py --mode clips --input workspace/07_clips/ --storyboard workspace/03_storyboard.json --output workspace/08_output/final_ad.mp4
```

또는 기존 render.py가 지원하지 않으면 아래 스크립트 작성 후 실행:

```bash
uv run python skills/run_render.py
```

---

## 렌더링 사양

```
해상도: 1920 × 1080 (Full HD)
FPS: 30
코덱: H.264 (libx264)
오디오: AAC 128kbps
총 길이: 15초 (씬1 3초 + 씬2 5초 + 씬3 4초 + 씬4 3초)
예상 파일 크기: 10~30MB (클립 품질에 따라)
예상 렌더링 시간: 2~5분 (RTX 4090 기준)
```

---

## 품질 검증 체크리스트

```
□ 영상 길이 정확히 15초인가?  (ffprobe로 확인)
□ 해상도 1920×1080인가?
□ 씬 전환이 매끄러운가? (White Flash 정상 동작)
□ 텍스트가 선명하게 읽히는가?
□ 가격 배지가 씬 2에 나타나는가?
□ QR 코드가 씬 4 후반에 나타나는가?
□ Lower Third 바가 씬 4에 슬라이드업 되는가?
□ 비네팅이 자연스러운가?
□ 컬러 그레이딩이 너무 과하지 않은가?
```

---

## 완료 후 출력 메시지

```
✅ 최종 렌더링 완료

출력 파일: workspace/08_output/final_ad.mp4
길이: 15.0초
해상도: 1920×1080
파일 크기: XX.X MB

재생해서 최종 확인해주세요.
수정 필요 시 어느 씬, 어떤 요소인지 알려주세요.
```
