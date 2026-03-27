# 2026 Q1 Internship Project

## 프로젝트 개요
웹에서 용접 이미지를 업로드하면 AI 모델이 해당 이미지의 정상 여부를 판별합니다.
판별 결과로 `Anomaly Score`와 `Heatmap`을 제공하여 이상 징후와 위치를 직관적으로 확인할 수 있습니다.

## 아키텍처

<img width="681" height="260" alt="Image" src="https://github.com/user-attachments/assets/d2727fad-7fc5-4ef5-a776-a31785e8af98" />

```
Browser
  │
  ▼
nginx (80)
  ├─ /api/      → backend (8000)
  └─ /          → frontend (80)
                      │
                      ▼
                  ai-model (5000)
```


## 기술 스택

| 구분 | 기술 |
|------|------|
| AI | PyTorch, GoogLeNet, Grad-CAM |
| Backend | FastAPI, httpx |
| Frontend | HTML, JavaScript |
| Infra | Docker, nginx |

## 서비스 동작 예시

### 메인 화면
<img width="1917" height="902" alt="Main Screen" src="https://github.com/user-attachments/assets/81a6c467-b7f2-4677-adef-871ad6ed8e6b" />

### 분석 결과 화면 - 정상
<img width="1895" height="902" alt="Normal Result" src="https://github.com/user-attachments/assets/32549e97-be1e-45df-abc5-1bbea4d46f8b" />

### 분석 결과 화면 - 이상
<img width="1897" height="905" alt="Abnormal Result" src="https://github.com/user-attachments/assets/ae6c6f84-b03f-41e2-b6d9-89e4d11722f9" />

## 주요 기능
- 용접 이미지 업로드
- 정상 / 이상 여부 판별
- `Anomaly Score` 제공
- `Heatmap` 시각화 제공

## 시스템 구성

### Frontend
- 사용자 인터페이스 제공
- 이미지 업로드 및 분석 결과 시각화

### Backend
- 업로드된 이미지 수신
- AI 모델에 추론 요청
- Heatmap 이미지 저장

### AI Model
- GoogLeNet 기반 모델 사용
- Grad-CAM으로 불량 위치 히트맵 생성
- 추론 결과 반환
  - `is_defect` — 정상/이상 여부
  - `anomaly_score` — 이상 점수 (0~100)
  - `heatmap_data` — Grad-CAM 히트맵 (base64)

### Nginx
- 요청 경로에 따라 Frontend와 Backend로 트래픽 분기

## 동작 흐름
1. 사용자가 브라우저를 통해 서비스에 접속합니다.
2. Nginx가 요청 경로에 따라 Frontend 또는 Backend로 트래픽을 전달합니다.
3. 사용자가 Frontend에서 용접 이미지를 업로드합니다.
4. Frontend가 Backend에 분석 요청을 전송합니다.
5. Backend가 AI Model 서비스에 이미지를 전달하고 추론을 요청합니다.
6. AI Model이 `is_defect`, `anomaly_score`, `heatmap_data`를 반환합니다.
7. Backend가 `heatmap_data`를 이미지로 저장하고 `heatmap_url`을 생성합니다.
8. Backend가 최종 결과를 Frontend에 응답합니다.
9. Frontend가 정상/이상 여부, 점수, Heatmap을 사용자에게 시각화합니다.

## API

### 이미지 업로드
```
POST /api/upload
Content-Type: multipart/form-data
```
```json
{
  "filename": "test.jpg",
  "message": "파일 업로드 완료"
}
```

### 이상 탐지
```
POST /api/predict
Content-Type: application/json
```
```json
{
  "is_defect": true,
  "anomaly_score": 87.3,
  "heatmap_url": "/uploads/heatmap_test.jpg",
  "message": "GoogleNet 모델 분석 완료",
  "filename": "test.jpg"
}
```

## 기대 효과
- 용접 품질 이상 여부를 빠르게 판별할 수 있습니다.
- Heatmap을 통해 이상 위치를 직관적으로 확인할 수 있습니다.
- 현장 검사 효율과 정확도를 높일 수 있습니다.

