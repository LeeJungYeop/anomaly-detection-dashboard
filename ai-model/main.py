# ai-model/main.py (완전한 GoogleNet Fine-tuning 구현 + Grad-CAM Heatmap)
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
import base64

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

# ============================================================
# Grad-CAM 히트맵 생성 관련
# ============================================================

# Feature map과 gradient를 저장할 변수
feature_maps = {}
gradients = {}


def forward_hook(module, input, output):
    """Forward pass에서 feature map 저장"""
    feature_maps['value'] = output


def backward_hook(module, grad_input, grad_output):
    """Backward pass에서 gradient 저장"""
    gradients['value'] = grad_output[0]


# GoogleNet의 마지막 Inception 블록에 hook 등록
model.inception5b.register_forward_hook(forward_hook)
model.inception5b.register_full_backward_hook(backward_hook)


def apply_jet_colormap(grayscale: np.ndarray) -> np.ndarray:
    """
    Blue(0) -> Cyan -> Green -> Yellow -> Red(255) 팔레트로 매핑합니다.
    """
    # 0~255 스케일로 변환
    v = (np.clip(grayscale, 0, 1) * 255).astype(np.int32)
    step = 64  # 256 / 4

    r = np.zeros_like(v, dtype=np.uint8)
    g = np.zeros_like(v, dtype=np.uint8)
    b = np.zeros_like(v, dtype=np.uint8)

    # Blue to Cyan (0~63)
    mask = v < step
    r[mask] = 0
    g[mask] = (v[mask] * 4).astype(np.uint8)
    b[mask] = 255

    # Cyan to Green (64~127)
    mask = (v >= step) & (v < step * 2)
    r[mask] = 0
    g[mask] = 255
    b[mask] = (255 - (v[mask] - step) * 4).astype(np.uint8)

    # Green to Yellow (128~191)
    mask = (v >= step * 2) & (v < step * 3)
    r[mask] = ((v[mask] - step * 2) * 4).astype(np.uint8)
    g[mask] = 255
    b[mask] = 0

    # Yellow to Red (192~255)
    mask = v >= step * 3
    r[mask] = 255
    g[mask] = (255 - (v[mask] - step * 3) * 4).astype(np.uint8)
    b[mask] = 0

    return np.stack([r, g, b], axis=-1)


def generate_heatmap(image: Image.Image, input_tensor: torch.Tensor) -> str:
    """
    Grad-CAM을 이용해 히트맵을 생성하고 base64 문자열로 반환합니다.
    """
    input_tensor.requires_grad_(True)

    # Forward pass
    output = model(input_tensor)

    # 예측 클래스에 대해 backward
    pred_class = output.argmax(dim=1).item()
    model.zero_grad()
    output[0, pred_class].backward()

    # Grad-CAM 계산
    grads = gradients['value']
    fmaps = feature_maps['value']
    weights = grads.mean(dim=[2, 3], keepdim=True)
    cam = (weights * fmaps).sum(dim=1, keepdim=True)
    cam = torch.relu(cam)

    # 정규화 (0~1)
    cam = cam.squeeze().detach().cpu().numpy()
    if cam.max() > 0:
        cam = (cam - cam.min()) / (cam.max() - cam.min())
        print(f"[DEBUG] cam min: {cam.min():.4f}, max: {cam.max():.4f}, mean: {cam.mean():.4f}")

    # 224x224로 리사이즈 (PIL 사용)
    cam_pil = Image.fromarray((cam * 255).astype(np.uint8))
    cam_resized = cam_pil.resize((224, 224), Image.BILINEAR)
    cam_resized = np.array(cam_resized, dtype=np.float32) / 255.0

# Jet 컬러맵 적용
    heatmap_colored = apply_jet_colormap(cam_resized)

    # 원본 이미지를 224x224로 리사이즈 후 오버레이
    image_resized = image.resize((224, 224))
    rgb_img = np.array(image_resized, dtype=np.float32)
    overlay = (rgb_img * 0.6 + heatmap_colored.astype(np.float32) * 0.4)
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    # PIL -> base64
    overlay_pil = Image.fromarray(overlay)
    buffer = io.BytesIO()
    overlay_pil.save(buffer, format="PNG")
    buffer.seek(0)
    base64_str = base64.b64encode(buffer.read()).decode("utf-8")

    return base64_str


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

    # Grad-CAM 히트맵 생성 (gradient 계산이 필요하므로 no_grad 밖에서 별도 실행)
    input_tensor_for_cam = transform(image).unsqueeze(0).to(device)
    heatmap_base64 = generate_heatmap(image, input_tensor_for_cam)

    return {
        "is_defect": bool(is_defect),
        "anomaly_score": anomaly_score,
        "prob_normal": round(prob_normal * 100, 1),
        "prob_defect": round(prob_defect * 100, 1),
        "heatmap_data": heatmap_base64
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