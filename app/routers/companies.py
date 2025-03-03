from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Company

router = APIRouter()


@router.get("/companies/")
def get_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    return companies
