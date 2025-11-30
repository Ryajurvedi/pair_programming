import pytest
from unittest import mock
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import text
import asyncio

# FIX 1: Import WebSocketDisconnect from starlette
from starlette.websockets import WebSocketDisconnect 

from backend.app.api.v1.endpoints.coding import router
from backend.app.dependencies import get_db
from sqlalchemy.sql.elements import TextClause


# --- SETUP FIXTURES AND MOCKS ---

# 1. Create a minimal FastAPI app just for testing this router
app = FastAPI()
app.include_router(router, prefix="/api/v1")

# Create a fixture for the test client
@pytest.fixture(scope="module")
def client():
    # Use httpx.TestClient for synchronous testing of REST endpoints
    with TestClient(app) as c:
        yield c

# Mock Room model (assuming it has a code_content attribute)
class MockRoom:
    def __init__(self, room_id="TEST_ROOM_ID", code_content="initial code"):
        self.room_id = room_id
        self.code_content = code_content

# --- TEST REST ENDPOINTS ---

def test_liveness(client):
    """Test the /liveness endpoint."""
    response = client.get("/api/v1/liveness")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "alive"}


@pytest.mark.parametrize("db_up", [True, False])
def test_health_check(client, mocker, db_up):
    """Test the /health endpoint with database success and failure."""
    mock_session = mocker.MagicMock(spec=Session)

    def override_get_db():
        return mock_session

    app.dependency_overrides[get_db] = override_get_db

    # Mock the db.execute call
    if db_up:
        mock_session.execute.return_value = mock.MagicMock()
        expected_status = status.HTTP_200_OK
        expected_json = {"status": "ok", "database": "accessible"}
    else:
        mock_session.execute.side_effect = Exception("DB Connection Error")
        expected_status = status.HTTP_503_SERVICE_UNAVAILABLE
        expected_json = {"detail": {"status": "not ok", "database": "unreachable"}}

    response = client.get("/api/v1/health")
    
    assert response.status_code == expected_status
    assert response.json() == expected_json
    
    # Use a lambda to check the argument content
    def check_text_clause(arg):
        return isinstance(arg, TextClause) and str(arg) == "SELECT 1"

    mock_session.execute.assert_called_once()
    assert check_text_clause(mock_session.execute.call_args[0][0])
    
    app.dependency_overrides = {}


def test_create_room(client, mocker):
    """Test the POST /rooms endpoint."""
    mock_room_id = "mocked_room_123"
    
    # 1. Mock the CRUD function to return a fixed ID
    mocker.patch("backend.app.crud.room_crud.create_room", return_value=mock_room_id)
    
    # 2. Mock the logger (optional, but good practice to prevent log file spam)
    mock_logger_info = mocker.patch("backend.app.core.logger.logger.info")

    # 3. Headers used by the endpoint
    headers = {
        "x-username": "TestUser",
        "x-usermail": "test@example.com"
    }

    response = client.post("/api/v1/rooms", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"roomId": mock_room_id}

    # 4. Verify logging was called with the correct headers
    mock_logger_info.assert_any_call(
        f"Request to POST /rooms received. Headers logged: {{'x-username': 'TestUser', 'x-usermail': 'test@example.com'}}"
    )

@pytest.mark.parametrize(
    "code, expected_suggestion",
    [
        # Standardized suggestions to avoid \xa0 errors
        ("print('hi')\ndef ", "function_name():\n    pass"), 
        ("class MyC", " # (Mock AI) Continue code..."),
        ("from module import *\nclass ", "ClassName:\n    pass"),
        ("just some code", " # (Mock AI) Continue code..."),
    ]
)
def test_autocomplete(client, code, expected_suggestion):
    """Test the POST /autocomplete endpoint with various payloads."""
    payload = {
        "code": code,
        "cursorPosition": len(code),
        "language": "python"
    }
    
    response = client.post("/api/v1/autocomplete", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    
    # Re-normalize the expected suggestion for comparison
    normalized_expected = expected_suggestion.replace('\xa0', ' ').replace('\t', ' ')
    
    # We use the original parametrized values, assuming the endpoint output is fixed.
    assert response.json()["suggestion"] == expected_suggestion


# --- TEST WEB SOCKET ENDPOINT ---

@pytest.mark.asyncio
async def test_ws_connect_and_disconnect(client, mocker):
    """Test successful connection and graceful disconnection."""
    room_id = "ws_test_room"
    
    mock_session = mocker.MagicMock(spec=Session)
    mock_room = MockRoom(code_content="initial code")
    mocker.patch("backend.app.crud.room_crud.get_room_by_id", return_value=mock_room)
    
    mocker.patch("backend.app.crud.room_crud.update_room_code")
    mock_disconnect = mocker.patch("backend.app.core.ws_manager.manager.disconnect")
    
    # Mock connect to call accept
    mock_connect = mocker.patch("backend.app.core.ws_manager.manager.connect", new_callable=mock.AsyncMock)

    async def mock_connect_side_effect(websocket, room_id):
        await websocket.accept() 

    mock_connect.side_effect = mock_connect_side_effect
    
    app.dependency_overrides[get_db] = lambda: mock_session

    with client.websocket_connect(f"/api/v1/ws/{room_id}") as websocket:
        # 1. Connection check
        mock_connect.assert_awaited_once() 

        # 2. Initial state check: The code is sent immediately after accept()
        initial_message = websocket.receive_text() 
        assert initial_message == "initial code"
        
        # 3. Simulate client sending data
        # await websocket.send_text("def new_func():") 
        
        await asyncio.sleep(0.01)

    # 4. Disconnection check
    mock_disconnect.assert_called_once()
    
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_ws_room_not_found(client, mocker):
    """Test connection attempt with a non-existent room."""
    room_id = "non_existent_room"

    # Mock dependencies
    mock_session = mocker.MagicMock(spec=Session)
    mocker.patch("backend.app.crud.room_crud.get_room_by_id", return_value=None)
    mock_logger_warning = mocker.patch("backend.app.core.logger.logger.warning")
    
    app.dependency_overrides[get_db] = lambda: mock_session

    # Catch the correct exception: WebSocketDisconnect (now imported)
    with pytest.raises(WebSocketDisconnect): 
        with client.websocket_connect(f"/api/v1/ws/{room_id}") as websocket:
            # The endpoint should immediately close the connection upon checking the room
            pass

    # Verify the warning was logged
    mock_logger_warning.assert_called_once_with(
        f"WebSocket rejected connection for unknown room ID: {room_id}"
    )

    app.dependency_overrides = {}

