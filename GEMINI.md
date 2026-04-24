# 동네방네 광고 자동화 파이프라인

소상공인 가게 실사진 + YAML 업체정보 → 15초 TV 광고 MP4 자동 생성 시스템.

## 환경

- Python 3.11, uv 패키지 관리자
- GCP Vertex AI (ADC 인증) 또는 Google AI Studio API 키
- MoviePy 2.x 기반 렌더링 (로컬 CPU/GPU)

## 인증 설정

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

## 핵심 명령어

```bash
# 파이프라인 전체 실행 (CLI)
uv run python run_pipeline.py --md store_sample.md --photos workspace/01_store_photos/

# API 서버 실행
uv run python main.py

# API 서버 실행 (uvicorn 직접)
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 프로젝트 구조

```
video_pipeline/
├── pipeline/               ← 자동화 파이프라인 (핵심)
│   ├── client.py           ← Vertex AI / AI Studio 인증 (자동 전환)
│   ├── models.py           ← 환경별 모델 ID 매핑
│   ├── skill_01_analyze.py ← Gemini Vision 사진 분석
│   ├── skill_02_storyboard.py ← 스토리보드 JSON 생성
│   ├── skill_03_gen_image.py  ← Imagen 3 / Nano Banana 16:9 생성
│   ├── skill_04_analyze_frame.py ← 카메라 무브 결정
│   ├── skill_05_gen_video.py  ← Veo 3.1 Lite I2V (병렬)
│   ├── skill_06_render.py     ← MoviePy 최종 합성
│   ├── orchestrator.py        ← 순차 파이프라인 + SSE 콜백
│   └── api.py                 ← FastAPI 라우터
├── skills/                 ← 수동 가이드 마크다운 (수정 금지)
├── render_clips.py         ← 렌더링 엔진 (수정 금지)
├── config.py               ← 테마 설정 warm/lively/premium
├── store_sample.md         ← 샘플 업체 정보 YAML
├── run_pipeline.py         ← CLI 진입점
└── main.py                 ← FastAPI 앱
```

## 파이프라인 흐름

```
store_info.md + 사진 폴더
  → [1] 사진 분석       (Gemini Flash Vision)
  → [2] 스토리보드 설계  (Gemini Flash)
  → [3] 이미지 생성     (Imagen 3, 16:9, generate_image=true 씬만)
  → [4] 프레임 분석     (Gemini Flash Vision)
  → [5] 영상 생성       (Veo 3.1 Lite, 5클립 병렬, ~2~4분/클립)
  → [6] 최종 렌더링     (render_clips.py, 로컬)
  → workspace/{job_id}/08_output/final_ad.mp4
```

## 모델 ID (환경별 자동 선택)

| 용도 | Vertex AI | AI Studio |
|------|-----------|-----------|
| 텍스트/Vision | gemini-2.5-flash | gemini-2.5-flash |
| 이미지 생성 | imagen-3.0-generate-002 | gemini-3-pro-image-preview |
| 영상 생성 | veo-3.1-lite-generate-preview | veo-3.1-lite-generate-preview |

## 업체 정보 YAML 스키마

```yaml
store_name: 우판등심 수원점
category: 소고기구이
address: 경기 수원시 영통구 권선로908번길 10
hours: 매일 11:00 - 22:00
phone: 0507-1475-0230
website: http://www.woopan.co.kr
menus:
  - name: 한우 생등심 1인분
    price: 37500
    tag: 대표
usp:
  - 500시간 진공 저온숙성
reviews:
  - 소고기는 우판등심이 최고!
template: warm          # warm | lively | premium
qr_url: http://www.woopan.co.kr
```

## API 엔드포인트

```
POST /api/generate-ad
  Body: multipart/form-data
    store_md: (YAML 파일)
    photos:   (사진 파일들)
  Response: {"job_id": "abc12345", "stream_url": "/api/jobs/abc12345/stream"}

GET /api/jobs/{job_id}/stream   ← SSE 진행상황
GET /api/jobs/{job_id}/result   ← MP4 다운로드
```

## 주의사항

- `skills/*.md`, `render.py`, `render_clips.py` 절대 수정 금지
- Veo 생성은 클립당 2~4분, 5클립 병렬이므로 총 4~8분 소요
- Vertex AI Veo/Imagen은 `us-central1` 리전에서만 지원
- 비용: 광고 1편당 약 $2.56 (Veo $2.00 + Imagen $0.54 + Gemini $0.02)
