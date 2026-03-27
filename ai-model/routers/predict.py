from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from models import PredictResponse
from services import inference_service

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return inference_service.predict(contents)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/health")
def health():
    return {"status": "healthy"}
