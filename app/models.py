from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Company(Base):
    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    
    employees = relationship("Employee", back_populates="company")




class Employee(Base):
    __tablename__ = "employee"
    
    employee_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    phone_number = Column(String, nullable=True)
    salary = Column(String, nullable=True)  
    manager_id = Column(String, nullable=True) 
    department_id = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id"))
    
    company = relationship("Company", back_populates="employees")    