from fastapi import FastAPI, File, UploadFile
import os

app = FastAPI()

# 이미지가 저장될 디렉토리 설정
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/api/")
def api():
    return {"message": "hello backend"}

# 프론트엔드에서 formData.append('image', ...)와 같이 설정한 키값과 이 변수명이 반드시 일치해야만 서버가 해당 바이너리 데이터를 특정하여 수신
@app.post("/api/upload")
async def upload_image(image: UploadFile = File(...)):
    # 파일 내용 읽기
    content = await image.read()
    
    # 서버 로컬에 파일 저장
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(file_path, "wb") as f: # wb = write binary
        f.write(content)

    # 프론트엔드의 res.json()으로 전달될 응답 데이터
    return {
        "message": "업로드 성공!",
        "filename": image.filename,
        "content_type": image.content_type,
        "size": len(content)
    }