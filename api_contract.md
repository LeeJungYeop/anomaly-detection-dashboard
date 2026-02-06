# API 상세 규격서 (Contract)

본 문서는 프론트엔드-백엔드-AI 모델 간의 효율적인 협업을 위해 정의된 API 명세입니다.

---

## 1. 이미지 분석 API (`POST /api/analyze`)

사용자가 업로드한 이미지를 AI 모델로 분석하여 결과를 반환합니다.

### A. 요청 (Request)
**Content-Type**: `multipart/form-data`

| 파라미터명 | 타입 | 필수 여부 | 설명 | 예시 |
| :--- | :--- | :---: | :--- | :--- |
| `image` | `File` | 필수 | 분석할 이미지 파일 (binary) | `image.jpg` |
| `model_id` | `String` | 필수 | 분석에 사용할 AI 모델 ID | `model-a`, `model-b` |

### B. 응답 (Response)
**Content-Type**: `application/json`

| 필드명 | 타입 | 설명 | 예시 |
| :--- | :--- | :--- | :--- |
| `status` | `String` | 요청 처리 상태 (`success` / `error`) | `success` |
| `data.anomaly_score` | `Number` | 탐지된 이상의 확률/점수 (0~100) | `87.5` |
| `data.prediction` | `String` | 최종 판정 결과 (`Normal` / `Defect`) | `Defect` |
| `data.heatmap_image` | `String` | 히트맵 오버레이 이미지 (Base64 형식 또는 URL) | `"data:image/png;base64,..."` |

### C. 에러 코드 (Error Codes)

| 상태 코드 | 메시지 | 원인 |
| :--- | :--- | :--- |
| `400` | `INVALID_FILE_TYPE` | 지원하지 않는 파일 형식 (PNG/JPG만 가능) |
| `413` | `FILE_TOO_LARGE` | 파일 용량 제한 초과 (최대 10MB) |
| `500` | `AI_INFERENCE_FAILED` | AI 모델 추론 중 내부 서버 오류 발생 |