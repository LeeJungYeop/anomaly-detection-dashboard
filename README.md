# Anomaly Detection Dashboard

> 용접 이미지를 업로드하면 AI가 결함 여부와 위치를 즉시 판별합니다

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

## Demo

### 메인 화면
<img width="1917" height="902" alt="Main Screen" src="https://github.com/user-attachments/assets/81a6c467-b7f2-4677-adef-871ad6ed8e6b" />

### 정상 판정
<img width="1895" height="902" alt="Normal Result" src="https://github.com/user-attachments/assets/32549e97-be1e-45df-abc5-1bbea4d46f8b" />

### 이상 판정 — Grad-CAM 히트맵으로 결함 위치 시각화
<img width="1897" height="905" alt="Abnormal Result" src="https://github.com/user-attachments/assets/ae6c6f84-b03f-41e2-b6d9-89e4d11722f9" />

---

## How It Works

```
이미지 업로드
    │
    ▼
Backend (FastAPI)  ──────────────────────────────────────────────────
    │                                                                │
    ▼                                                                │
AI Model (FastAPI)                                                   │
    ├─ GoogLeNet        →  정상 / 이상 분류                           │
    ├─ Anomaly Score    →  이상 점수 (0 ~ 100)                       │
    └─ Grad-CAM         →  결함 위치 히트맵 (base64)                  │
                                                                     │
    ─────────────────────────────────────────────────────────────────┘
    │
    ▼
Frontend — 결과 시각화 (점수 + 히트맵)
```

---

## Architecture

```
Browser
  │
  ▼
nginx (8000)
  ├─ /api/  →  backend  (8000)  →  ai-model (5000)
  └─ /      →  frontend (80)
```

4개의 Docker 컨테이너가 `docker-compose`로 구성됩니다.

---

## Quick Start

```bash
docker-compose up --build
```

브라우저에서 `http://localhost:8000` 접속

---

## Tech Stack

| 분류 | 기술 |
|------|------|
| AI | GoogLeNet (PyTorch), Grad-CAM |
| Backend | FastAPI, httpx |
| Frontend | HTML, JavaScript |
| Infra | Docker, nginx |
