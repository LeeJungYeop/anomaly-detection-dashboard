from fastapi import APIRouter, HTTPException

from models import PredictRequest, PredictResponse
from services import predict_service

router = APIRouter(prefix="/api", tags=["AI"])


@router.post("/predict", response_model=PredictResponse)
async def predict_image(request: PredictRequest):
    try:
        return await predict_service.run(request.filename, request.model_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
