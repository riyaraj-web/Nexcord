from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.security import get_current_user
from app.services.s3_service import S3Service
from pydantic import BaseModel

router = APIRouter()
s3_service = S3Service()

class FileUploadResponse(BaseModel):
    url: str
    filename: str
    content_type: str
    size: int

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Validate file size (max 50MB)
    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    
    # Validate file type
    allowed_types = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "video/mp4", "video/webm",
        "audio/mpeg", "audio/wav", "audio/ogg",
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Upload to S3
    url = await s3_service.upload_file(contents, file.filename, file.content_type)
    
    return FileUploadResponse(
        url=url,
        filename=file.filename,
        content_type=file.content_type,
        size=len(contents)
    )

@router.delete("/{file_url:path}")
async def delete_file(
    file_url: str,
    current_user: dict = Depends(get_current_user)
):
    await s3_service.delete_file(file_url)
    return {"message": "File deleted successfully"}
