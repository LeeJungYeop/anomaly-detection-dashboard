# 개발 필요 API 목록 (API To-Do List)

본 문서는 프로젝트의 각 단계에서 백엔드 및 AI 파트가 구현해야 할 API의 우선순위와 목록을 관리합니다.

---

## 1단계: 핵심 기능 (Core)

### 1.1 이미지 분석 API (`POST /api/analyze`)
- **목적**: 업로드된 이미지를 AI 모델로 분석하고 결과를 반환함.
- **상세 규격**: [API 규격서(api_contract.md)](file:///C:/Users/goal_/.gemini/antigravity/brain/a493a939-6dda-4057-8200-9c2bda57443c/api_contract.md) 참고

---

## 2단계: 편의 기능 (Enhancement)

### 2.1 분석 이력 조회 API (`GET /api/history`)
- **목적**: 과거의 분석 기록들을 리스트로 가져와 사이드바 또는 대시보드에 표시함.
- **데이터 구조**:
| 필드명 | 타입 | 설명 | 예시 |
| :--- | :--- | :--- | :--- |
| `id` | `String` | 기록 고유 ID | `log_20260206_001` |
| `timestamp` | `String` | 분석 시간 | `2026-02-06 08:30` |
| `result` | `String` | 분석 결과 요약 | `Normal` / `Defect` |

---

## 3단계: 관리 기능 (Management)

### 3.1 이력 삭제 API (`DELETE /api/history/:id`)
- **목적**: 특정 분석 기록을 삭제함.

### 3.2 모델 정보 조회 API (`GET /api/models`)
- **목적**: 현재 사용 가능한 AI 모델 리스트 및 정보를 가져옴.