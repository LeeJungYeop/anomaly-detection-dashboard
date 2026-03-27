import os

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
AI_MODEL_URL = "http://ai-model:5000/predict"

os.makedirs(UPLOAD_DIR, exist_ok=True)
