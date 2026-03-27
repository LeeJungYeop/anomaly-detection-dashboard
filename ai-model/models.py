from pydantic import BaseModel


class PredictResponse(BaseModel):
    is_defect: bool
    anomaly_score: float
    prob_normal: float
    prob_defect: float
    heatmap_data: str
