import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text # Import text for raw query execution

from app.dependencies import get_db, engine
from app.schemas.room import RoomCreate, AutocompleteRequest, AutocompleteResponse
from app.crud import room_crud
from app.core.ws_manager import manager
from app.core.logger import logger

router = APIRouter()

# --- HEALTH AND LIVENESS ENDPOINTS ---

@router.get("/liveness")
def get_liveness():
    """
    Returns application status. Used to check if the process is running.
    """
    return {"status": "alive"}

@router.get("/health")
def get_health_check(db: Session = Depends(get_db)):
    """
    Performs a health check by testing the database connection.
    Returns 200 OK if the database is accessible.
    """
    try:
        # Attempt a simple query to check the database connection
        db.execute(text("SELECT 1"))
        logger.info("Health check passed: Database connection successful.")
        return {"status": "ok", "database": "accessible"}
    except Exception as e:
        logger.error(f"Health check failed: Database connection error. {e}")
        # Use HTTP 503 Service Unavailable status code
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ok", "database": "unreachable"}
        )

@router.post("/rooms", response_model=RoomCreate)
def rest_create_room(request: Request, db: Session = Depends(get_db)):
    """
    POST /rooms: Creates a new room. 
    Also logs incoming request headers.
    """
    # 1. Log Request Headers
    # We log a subset of relevant headers for clarity, but request.headers contains all of them.
    relevant_headers = {
        'x-username': request.headers.get('x-username', 'N/A'),
        'x-usermail': request.headers.get('x-usermail', 'N/A'),
    }
    logger.info(f"Request to POST /rooms received. Headers logged: {relevant_headers}")
    
    # 2. Process Request
    room_id = room_crud.create_room(db)
    logger.info(f"New room created with ID: {room_id}")
    
    return {"roomId": room_id}

@router.post("/autocomplete", response_model=AutocompleteResponse)
def rest_get_autocomplete(payload: AutocompleteRequest):
    """POST /autocomplete: Provides a mocked suggestion."""
    
    logger.debug(f"Autocomplete requested for language: {payload.language}")
    
    # Mock logic based on keywords
    suggestion = ""
    if payload.code.endswith("def "):
         suggestion = "function_name():\n    pass"
    elif payload.code.endswith("class "):
         suggestion = "ClassName:\n    pass"
    else:
         suggestion = " # (Mock AI) Continue code..."

    return {"suggestion": suggestion}

# ... (rest of the WebSocket implementation remains the same)