from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Company, Employee
import logging
from fastapi import HTTPException


def process_bulk_upload(file, db: Session):
    """
    Process bulk employee data upload from an Excel file.

    Args:
        file: Uploaded file object.
        db: SQLAlchemy database session.

    Returns:
        dict: Success or error message with appropriate status code.
    Raises:
        HTTPException: When an error occurs with appropriate status code
    """
    try:
        # Read file contents into a DataFrame
        contents = file.read()
        df = pd.read_excel(pd.io.common.BytesIO(contents))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file does not contain any data."
            )

        required_columns = ["COMPANY_NAME", "EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", 
                           "PHONE_NUMBER", "SALARY", "MANAGER_ID", "DEPARTMENT_ID"]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}. Please check the template."
            )

        # Extract unique company names
        company_names = df["COMPANY_NAME"].dropna().unique().tolist()

        # Fetch existing companies from the database
        existing_companies = db.query(Company).filter(Company.company_name.in_(company_names)).all()
        existing_company_names = {company.company_name for company in existing_companies}

        # Insert new companies if they don't already exist
        new_companies = [{"company_name": name} for name in company_names if name not in existing_company_names]
        
        if new_companies:
            try:
                db.bulk_insert_mappings(Company, new_companies)
                db.commit()
            except SQLAlchemyError:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="Unable to add new companies. Database operation failed."
                )

        # Create a mapping of company names to their IDs
        companies = db.query(Company).filter(Company.company_name.in_(company_names)).all()
        company_map = {company.company_name: company.id for company in companies}

        # Prepare employee records for insertion
        employee_records = []
        
        for _, row in df.iterrows():
            company_id = company_map.get(row["COMPANY_NAME"])
            
            if not company_id:
                continue
                
            employee = {
                "employee_id": row["EMPLOYEE_ID"],
                "first_name": row["FIRST_NAME"],
                "last_name": row["LAST_NAME"],
                "phone_number": str(row["PHONE_NUMBER"]) if not pd.isna(row["PHONE_NUMBER"]) else None,
                "salary": row["SALARY"],
                "manager_id": row["MANAGER_ID"] if not pd.isna(row["MANAGER_ID"]) else None,
                "department_id": row["DEPARTMENT_ID"] if not pd.isna(row["DEPARTMENT_ID"]) else None,
                "company_id": company_id,
            }
            employee_records.append(employee)

        # Bulk insert employee records
        try:
            db.bulk_insert_mappings(Employee, employee_records)
            db.commit()
            
            return {
                "status": "success",
                "message": f"Successfully imported {len(employee_records)} employee records."
            }
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Same data already exists in database. Please check your file for duplicate entries and try again."
            )

    except HTTPException:
        # Re-raise HTTPExceptions that were already set
        raise
        
    except Exception as e:
        db.rollback()
        # For any other unexpected exceptions
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )