from fastapi import APIRouter, File, UploadFile

from data import file_repo
from models import UploadResponse

router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_image(image: UploadFile = File(...)):
    content = await image.read()
    file_repo.save_upload(image.filename, content)
    return UploadResponse(filename=image.filename, message="파일 업로드 완료")
