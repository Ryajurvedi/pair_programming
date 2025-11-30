import pytest
from unittest import mock
from sqlalchemy.orm import Session
from backend.app.dependencies import (
    # Assuming these elements are defined in backend/app/dependencies.py
    engine, 
    SessionLocal, 
    get_db, 
    Base,
    create_engine, 
    sessionmaker 
)

# Mocking the settings object
@pytest.fixture(autouse=True)
def mock_settings(mocker):
    """Mocks the settings object to use a test database URL."""
    # Patch the reference to settings, assuming it's imported within dependencies.py
    mock_settings = mocker.patch("backend.app.dependencies.settings")
    # Use a generic in-memory database URL for testing
    mock_settings.SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    return mock_settings

# --- Tests for get_db Dependency ---

def test_get_db_dependency(mocker):
    """Test that get_db yields a session and calls close() correctly upon exit."""
    
    # 1. Mock the SessionLocal object and its session instance
    mock_session_instance = mocker.MagicMock(spec=Session)
    
    # Mock the SessionLocal call to return the mock session instance
    # We patch the function where it is used (in the dependencies module)
    mock_session_local = mocker.patch('backend.app.dependencies.SessionLocal', return_value=mock_session_instance)

    # 2. Execute the generator
    db_generator = get_db()
    
    # 3. Assert the session is yielded (enters the 'try' block)
    try:
        db = next(db_generator)
        assert db is mock_session_instance
        mock_session_local.assert_called_once() # SessionLocal was called
        mock_session_instance.close.assert_not_called() # Not closed yet
    except StopIteration:
        pytest.fail("Generator did not yield a value.")
    
    # 4. Assert the session is closed when the generator is finished 
    # (The finally block executes when the generator is consumed or closed/thrown).
    try:
        next(db_generator)
    except StopIteration:
        pass # Expected when generator finishes
    
    mock_session_instance.close.assert_called_once()


def test_get_db_handles_exception(mocker):
    """Test that get_db ensures db.close() is called even if an exception occurs in the route."""
    
    # 1. Mock the SessionLocal object and session instance
    mock_session_instance = mocker.MagicMock(spec=Session)
    
    # Mock the SessionLocal call to return the mock session instance
    mocker.patch('backend.app.dependencies.SessionLocal', return_value=mock_session_instance)

    # 2. Execute the generator and force an exception to happen after yielding
    db_generator = get_db()
    
    try:
        next(db_generator) # Yields the session
        
        # Simulate an exception happening in the API route after yield
        db_generator.throw(RuntimeError("Simulated API error"))
            
    except RuntimeError:
        # The exception should propagate out
        pass 
        
    # 3. Assert the session was closed, regardless of the exception
    mock_session_instance.close.assert_called_once()
    
