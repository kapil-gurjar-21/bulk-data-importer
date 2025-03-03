
# Excel to Database API

This API reads employee data from Excel files and stores it in a database with proper relationships between companies and employees.

## Features

- FastAPI-based REST API
- Supports Excel (.xlsx) and CSV file uploads
- One-to-many relationship between companies and employees
- Bulk database operations (no SQL/ORM queries in loops)
- Automatic API documentation

## Project Structure

```
excel-db-api/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── services.py
│   ├── test.py
│   └── routers/
│       ├── __init__.py
│       ├── upload.py
│       ├── employees.py
│       └── companies.py
├── requirements.txt
├── main.py
└── README.md

```

## Installation

1. Clone the repository: 
`git clone https://github.com/your-repo/excel-db-api.git`

2. Create a virtual environment: 
`python -m venv venv`

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run Database Migrations:
    `alembic revision --autogenerate -m "create companies and employees tables"`

    
`alembic upgrade head`
## Usage

1. Start the server: `uvicorn main:app --reload`
2. Access the API documentation: http://127.0.0.1:8000/docs
3. Upload an Excel/CSV file through the `api/upload/` endpoint
4. View companies and employees through their respective endpoints

## API Endpoints

- `POST /api/upload/`: Upload Excel/CSV file with employee data
- `GET /api/employees/`: List all employees with their company information
- `GET /api/companies/`: List all companies with employee counts

### Company Table
- id (PK)
- company_name

### Employee Table
- employee_id (PK)
- first_name
- last_name
- phone_number
- salary
- manager_id
- department_id
- company_id (FK)

## Expected Excel Format

The input file should contain columns for first_name, last_name, phone_number, salary, manager_id, department_id and company_name.