import os
import base64
import shutil

from config import UPLOAD_DIR


def save_upload(filename: str, content: bytes) -> None:
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)


def save_heatmap(original_filename: str, heatmap_data: str) -> str:
    heatmap_filename = f"heatmap_{original_filename}"
    heatmap_path = os.path.join(UPLOAD_DIR, heatmap_filename)
    if heatmap_data:
        with open(heatmap_path, "wb") as f:
            f.write(base64.b64decode(heatmap_data))
    else:
        shutil.copy(os.path.join(UPLOAD_DIR, original_filename), heatmap_path)
    return heatmap_filename


def get_file_bytes(filename: str) -> bytes:
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "rb") as f:
        return f.read()


def exists(filename: str) -> bool:
    return os.path.exists(os.path.join(UPLOAD_DIR, filename))
