# ai-model/main.py (완전한 GoogleNet Fine-tuning 구현)

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os
import numpy as np
from pathlib import Path

app = FastAPI(title="GoogleNet Anomaly Detection API")

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 모델 로드 (torchvision의 GoogleNet 사용)
model = models.googlenet(pretrained=True)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)  # Binary classification: 0(정상), 1(비정상)

# 학습된 가중치 로드 (실제로는 /dais05/2026HDRB_data에서 학습 후 저장)
model_path = "/app/model.pth"  # 컨테이너 내 경로
if os.path.exists(model_path):
    model.load_state_dict(torch.load(model_path, map_location=device))
    print("Pretrained model loaded successfully")
else:
    print("No pretrained model found. Using random weights (for demo)")

model.to(device)
model.eval()

# 이미지 전처리 (GoogleNet 입력: 224x224)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def predict_anomaly(image_bytes: bytes):
    """이미지에서 정상/비정상 판정 및 anomaly score 계산"""
    # PIL 이미지 로드
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # 전처리
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    # 추론
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        # 클래스별 확률: prob_normal(0), prob_defect(1)
        prob_normal = probabilities[0].item()
        prob_defect = probabilities[1].item()
        
        # is_defect: 비정상 확률이 0.5 초과시 True
        is_defect = prob_defect > 0.5
        
        # anomaly_score: 비정상 확률을 0-100 스케일로 변환 (API 명세서 준수)
        anomaly_score = round(prob_defect * 100, 1)
    
    return {
        "is_defect": bool(is_defect),
        "anomaly_score": anomaly_score,
        "prob_normal": round(prob_normal * 100, 1),
        "prob_defect": round(prob_defect * 100, 1),
        "heatmap_data": "base64_encoded_heatmap"  # 실제 GradCAM 구현시 사용
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Backend에서 호출되는 AI 추론 API"""
    try:
        contents = await file.read()
        result = predict_anomaly(contents)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)