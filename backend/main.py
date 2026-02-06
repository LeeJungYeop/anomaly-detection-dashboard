from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import os
import random

app = FastAPI(
    title="Internship Project API",
    description="Backend API for AI Anomaly Detection",
    version="1.0.0"
)

# 이미지가 저장될 디렉토리 설정
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class UploadResponse(BaseModel):
    is_defect: bool
    anomaly_score: float
    heatmap_url: str
    message: str
    filename: str



@app.post("/api/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_image(
    image: UploadFile = File(...),
    model_name: str = Form(...)
):
    """
    이미지를 업로드하고 AI 분석 결과를 반환합니다.
    - **image**: 업로드할 이미지 파일
    - **model_name**: 프론트엔드에서 선택한 AI 모델 이름
    """
    # 파일 내용 읽기
    content = await image.read()
    
    # 서버 로컬에 파일 저장
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # 분석결과 시뮬레이션 (실제 구현 시에는 AI 모델 추론 로직이 들어감)
    is_defect = random.random() > 0.5
    anomaly_score = round(random.uniform(80.0, 99.9), 1) if is_defect else round(random.uniform(1.0, 20.0), 1)
    
    # 응답 데이터 구성
    return {
        "is_defect": is_defect,
        "anomaly_score": anomaly_score,
        "heatmap_url": f"/uploads/heatmap_{image.filename}",
        "message": f"{model_name} 모델을 이용한 분석이 완료되었습니다.",
        "filename": image.filename
    }