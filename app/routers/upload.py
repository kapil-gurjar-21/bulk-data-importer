from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal,get_db
from app.services import process_bulk_upload

router = APIRouter()


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        return {"error": "Invalid file format. Only Excel files are supported."}

    result = process_bulk_upload(file.file, db)
    return result
