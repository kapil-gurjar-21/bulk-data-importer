import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import pandas as pd
from app.services import process_bulk_upload
from app.models import Company, Employee
import pandas as pd
import io
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_file():
    return MagicMock()

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = Mock()
    db.query = Mock(return_value=db)
    db.filter = Mock(return_value=db)
    db.all = Mock(return_value=[])
    db.commit = Mock()
    db.rollback = Mock()
    db.bulk_insert_mappings = Mock()
    return db

@pytest.fixture
def valid_excel_data():
    """Create a valid Excel file for testing."""
    df = pd.DataFrame({
        'COMPANY_NAME': ['Test Company', 'Test Company'],
        'EMPLOYEE_ID': ['EMP001', 'EMP002'],
        'FIRST_NAME': ['John', 'Jane'],
        'LAST_NAME': ['Doe', 'Smith'],
        'PHONE_NUMBER': ['1234567890', '0987654321'],
        'SALARY': [50000, 60000],
        'MANAGER_ID': ['MGR001', 'MGR001'],
        'DEPARTMENT_ID': ['DEP001', 'DEP001']
    })
    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    # Create a mock UploadFile object
    mock_file = Mock()
    mock_file.read = Mock(return_value=excel_file.read())
    excel_file.seek(0)  # Reset for next read
    
    return mock_file

@pytest.fixture
def empty_excel_data():
    """Create an empty Excel file for testing."""
    df = pd.DataFrame()
    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    # Create a mock UploadFile object
    mock_file = Mock()
    mock_file.read = Mock(return_value=excel_file.read())
    excel_file.seek(0)  # Reset for next read
    
    return mock_file

@pytest.fixture
def missing_columns_excel_data():
    """Create an Excel file with missing required columns."""
    df = pd.DataFrame({
        'COMPANY_NAME': ['Test Company', 'Test Company'],
        'EMPLOYEE_ID': ['EMP001', 'EMP002'],
        # Missing FIRST_NAME and LAST_NAME
        'PHONE_NUMBER': ['1234567890', '0987654321'],
        'SALARY': [50000, 60000],
        'MANAGER_ID': ['MGR001', 'MGR001'],
        'DEPARTMENT_ID': ['DEP001', 'DEP001']
    })
    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    # Create a mock UploadFile object
    mock_file = Mock()
    mock_file.read = Mock(return_value=excel_file.read())
    excel_file.seek(0)  # Reset for next read
    
    return mock_file

@pytest.fixture
def missing_employee_id_excel_data():
    """Create an Excel file with missing employee IDs."""
    df = pd.DataFrame({
        'COMPANY_NAME': ['Test Company', 'Test Company'],
        'EMPLOYEE_ID': ['EMP001', None],  # Missing EMPLOYEE_ID
        'FIRST_NAME': ['John', 'Jane'],
        'LAST_NAME': ['Doe', 'Smith'],
        'PHONE_NUMBER': ['1234567890', '0987654321'],
        'SALARY': [50000, 60000],
        'MANAGER_ID': ['MGR001', 'MGR001'],
        'DEPARTMENT_ID': ['DEP001', 'DEP001']
    })
    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    
    # Create a mock UploadFile object
    mock_file = Mock()
    mock_file.read = Mock(return_value=excel_file.read())
    excel_file.seek(0)  # Reset for next read
    
    return mock_file

def test_process_bulk_upload_success(mock_db, valid_excel_data):
    """Test successful bulk upload process."""
    # Mock company query results
    company = Mock()
    company.company_name = 'Test Company'
    company.id = 1
    mock_db.all.return_value = [company]
    
    result = process_bulk_upload(valid_excel_data, mock_db)
    
    assert mock_db.bulk_insert_mappings.call_count == 1
    mock_db.bulk_insert_mappings.assert_called()
    print(mock_db.bulk_insert_mappings.call_args_list)
    assert mock_db.commit.call_count == 1
    
    assert result['status'] == 'success'
    assert 'Successfully imported' in result['message']

def test_process_empty_file(mock_db, empty_excel_data):
    with pytest.raises(HTTPException) as excinfo:
        process_bulk_upload(empty_excel_data, mock_db)
    
    assert excinfo.value.status_code == 400
    assert "does not contain any data" in excinfo.value.detail

def test_process_missing_columns(mock_db, missing_columns_excel_data):
    with pytest.raises(HTTPException) as excinfo:
        process_bulk_upload(missing_columns_excel_data, mock_db)
    
    assert excinfo.value.status_code == 400
    assert "Missing required columns" in excinfo.value.detail


def test_company_insert_error(mock_db, valid_excel_data):
    mock_db.all.return_value = []
    
    mock_db.bulk_insert_mappings.side_effect = SQLAlchemyError("Database error")
    
    with pytest.raises(HTTPException) as excinfo:
        process_bulk_upload(valid_excel_data, mock_db)
    
    assert excinfo.value.status_code == 400
    assert "Unable to add new companies" in excinfo.value.detail
    assert mock_db.rollback.called

def test_employee_insert_duplicate_error(mock_db, valid_excel_data):
    company = Mock()
    company.company_name = 'Test Company'
    company.id = 1
    mock_db.all.return_value = [company]
    
    def side_effect(*args, **kwargs):
        if args[0] == Employee:
            raise IntegrityError("Duplicate entry", orig=Exception("Duplicate entry"), params={})
        return None
    
    mock_db.bulk_insert_mappings.side_effect = side_effect
    
    with pytest.raises(HTTPException) as excinfo:
        process_bulk_upload(valid_excel_data, mock_db)
    
    assert excinfo.value.status_code == 400
    assert "Same data already exists in database" in excinfo.value.detail
    assert mock_db.rollback.called

def test_unexpected_exception(mock_db, valid_excel_data):
    """Test handling of unexpected exceptions."""
    # Make the read method raise an unexpected exception
    mock_db.query.side_effect = Exception("Unexpected error")
    
    with pytest.raises(HTTPException) as excinfo:
        process_bulk_upload(valid_excel_data, mock_db)
    
    assert excinfo.value.status_code == 500
    assert "An unexpected error occurred" in excinfo.value.detail
    assert mock_db.rollback.called
