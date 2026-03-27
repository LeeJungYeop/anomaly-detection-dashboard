from fastapi import FastAPI

from routers import predict

app = FastAPI(title="GoogleNet Anomaly Detection API")

app.include_router(predict.router)
