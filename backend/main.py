from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import UPLOAD_DIR
from routers import upload, predict

app = FastAPI(
    title="Internship Project API",
    description="Backend API for AI Anomaly Detection",
    version="2.0.0"
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.include_router(upload.router)
app.include_router(predict.router)
