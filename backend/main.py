from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import httpx
import shutil
import base64

app = FastAPI(
    title="Internship Project API",
    description="Backend API for AI Anomaly Detection",
    version="1.1.0"
)

# 이미지가 저장될 디렉토리 설정
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 정적 파일(이미지) 서빙 설정
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# AI Model 서비스 URL
AI_MODEL_URL = "http://ai-model:5000/predict"

class PredictRequest(BaseModel):
    filename: str
    model_name: str

class PredictResponse(BaseModel):
    is_defect: bool
    anomaly_score: float
    heatmap_url: str
    message: str
    filename: str

class UploadResponse(BaseModel):
    filename: str
    message: str

@app.post("/api/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_image(image: UploadFile = File(...)):
    """
    1. 파일을 서버에 업로드만 수행합니다.
    """
    content = await image.read()
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    return {
        "filename": image.filename,
        "message": "파일 업로드 완료"
    }

@app.post("/api/predict", response_model=PredictResponse, tags=["AI"])
async def predict_image(request: PredictRequest):
    """
    2. 업로드된 파일명을 바탕으로 AI 분석을 수행합니다.
    """
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    
    if not os.path.exists(file_path):
        return {"error": "파일을 찾을 수 없습니다."}

    # AI Model 컨테이너로 추론 요청
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            files = {"file": (request.filename, f)}
            response = await client.post(AI_MODEL_URL, files=files)
            ai_results = response.json()

    # AI 결과 추출
    is_defect = ai_results.get("is_defect", False)
    anomaly_score = ai_results.get("anomaly_score", 0.0)
    heatmap_data = ai_results.get("heatmap_data", "")

    # 히트맵 파일 생성 (ai-model에서 받은 base64 데이터를 이미지로 저장)
    heatmap_filename = f"heatmap_{request.filename}"
    heatmap_path = os.path.join(UPLOAD_DIR, heatmap_filename)

    if heatmap_data:
        heatmap_bytes = base64.b64decode(heatmap_data)
        with open(heatmap_path, "wb") as f:
            f.write(heatmap_bytes)
    else:
        shutil.copy(file_path, heatmap_path)

    # 응답 데이터 구성
    return {
        "is_defect": is_defect,
        "anomaly_score": anomaly_score,
        "heatmap_url": f"/uploads/{heatmap_filename}",
        "message": f"{request.model_name} 모델 분석 완료",
        "filename": request.filename
    }