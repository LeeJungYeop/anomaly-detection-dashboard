from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    message: str


class PredictRequest(BaseModel):
    filename: str
    model_name: str


class PredictResponse(BaseModel):
    is_defect: bool
    anomaly_score: float
    heatmap_url: str
    message: str
    filename: str
