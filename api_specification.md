# API 명세서

## 1. 이미지 업로드
- 엔드포인트: `POST /api/upload`
- 데이터 형식: `multipart/form-data`

### 요청 본문 (Request Body)
| 항목 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| image | 파일 (이진 데이터) | 필수 | 분석 대상 이미지 파일 |
| model_name | 문자열 | 필수 | UI에서 선택한 AI 모델 이름 |

### 응답 본문 (Success 200)
| 항목 | 타입 | 설명 |
| :--- | :--- | :--- |
| filename | 문자열 | 서버에 저장된 또는 분석된 파일의 이름 |
| is_defect | 불리언 (Boolean) | 불량 감지 시 True, 정상이면 False |
| anomaly_score | 실수 (Float) | 0.0 - 100.0 |
| heatmap_url | 문자열 | 생성된 히트맵 이미지의 공개 URL |
| message | 문자열 | 분석 결과 또는 오류에 대한 요약 메시지 |


