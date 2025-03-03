from fastapi import FastAPI
from app.routers import upload, employees, companies

app = FastAPI()

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload Excel"])
app.include_router(employees.router, prefix="/api", tags=["Employees"])
app.include_router(companies.router, prefix="/api", tags=["Companies"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Excel-DB API"}
