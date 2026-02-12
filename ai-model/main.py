from fastapi import FastAPI, File, UploadFile
import random
import time

app = FastAPI()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # AI 추론 시뮬레이션 (시간 소요)
    time.sleep(1.5)
    
    # 분석 로직 시뮬레이션
    is_defect = random.random() > 0.7
    anomaly_score = round(random.uniform(70.0, 99.9), 1) if is_defect else round(random.uniform(1.0, 30.0), 1)
    
    return {
        "is_defect": is_defect,
        "anomaly_score": anomaly_score,
        "heatmap_data": "simulated_heatmap_binary_base64_or_path"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
