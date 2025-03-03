from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee
from sqlalchemy import asc

router = APIRouter()


@router.get("/employees/")
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).order_by(asc(Employee.employee_id)).all()
    return employees
