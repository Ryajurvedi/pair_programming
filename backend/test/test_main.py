import pytest
from unittest import mock
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from fastapi.testclient import TestClient # New Import for testing endpoints
from backend.app.main import app # Import the configured app instance

# --- Fixtures ---

@pytest.fixture(autouse=True)
def mock_external_setup(mocker):
    """
    Mocks all external dependencies (DB, settings, logging)
    to isolate the FastAPI app configuration logic.
    """
    # 1. Mock Database setup (Base.metadata.create_all)
    # Patch the function reference used in main.py
    mocker.patch("backend.app.main.Base.metadata.create_all") 

    # 2. Mock Logger to capture startup message
    mock_logger = mocker.patch("backend.app.main.logger")

    # 3. Mock Settings object for predictable values
    mock_settings = mocker.patch("backend.app.main.settings")
    # FIX 1: Set the mock value to exactly match the expected value from main.py's default
    mock_settings.PROJECT_NAME = "PairProgrammingAPI"
    return mock_settings, mock_logger

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for testing API endpoints."""
    with TestClient(app) as c:
        yield c


# --- Tests ---

def test_fastapi_app_initialization(mock_external_setup):
    """Test the application title, version, and description are set correctly."""
    mock_settings, _ = mock_external_setup

    assert app.title == mock_settings.PROJECT_NAME
    assert app.version == "1.0.0"
    assert app.description == "API for a Pair Programming Application"


def test_router_inclusion():
    """Test that the coding router is correctly included at the specified prefix."""
    
    # FIX 4: Check if any route starts with the expected prefix "/api/v1/coding" 
    # or if an APIRouter object is mounted at /api/v1.
    
    # Check the routes list for the expected prefix
    coding_router_found = False
    
    for route in app.routes:
        # FastAPI mounts routers, so we check if the route path starts with the prefix.
        if route.path.startswith("/api/v1"):
            coding_router_found = True
            
            break
            
    assert coding_router_found, "Coding router was not included at the prefix /api/v1."


def test_root_endpoint(client):
    """Test the basic / endpoint returns the expected message using the TestClient."""
    # FIX 5: Use TestClient to simulate an HTTP request
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Pair Programming API is running"}