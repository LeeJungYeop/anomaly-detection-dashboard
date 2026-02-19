FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# 학습 (호스트 데이터셋 마운트 필요)
# CMD ["python", "train.py"]  # 필요시 주석 해제

# 추론 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
