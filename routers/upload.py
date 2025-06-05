import shutil
import os
import json

from fastapi import File, UploadFile, Body, APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(tags=['File Upload'])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_service_image/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename) # type: ignore
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"filename": file.filename, "url": f"/files/{file.filename}"})

@router.delete("/upload_service_image/")
async def delete_file(fileInfoString: str = Body(...)):
    
    filename = json.loads(fileInfoString)['filename']
    
    file_location = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail=f"File not found {file_location}")

    os.remove(file_location)

    return JSONResponse(content={"filename": filename, "message": "File deleted successfully"})