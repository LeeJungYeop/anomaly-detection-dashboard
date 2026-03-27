from data import ai_client, file_repo
from models import PredictResponse


async def run(filename: str, model_name: str) -> PredictResponse:
    if not file_repo.exists(filename):
        raise FileNotFoundError("파일을 찾을 수 없습니다.")

    file_bytes = file_repo.get_file_bytes(filename)
    ai_result = await ai_client.call(filename, file_bytes)

    heatmap_filename = file_repo.save_heatmap(filename, ai_result.get("heatmap_data", ""))

    return PredictResponse(
        is_defect=ai_result.get("is_defect", False),
        anomaly_score=ai_result.get("anomaly_score", 0.0),
        heatmap_url=f"/uploads/{heatmap_filename}",
        message=f"{model_name} 모델 분석 완료",
        filename=filename,
    )
