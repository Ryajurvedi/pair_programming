from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text 
from backend.app.dependencies import get_db
from backend.app.schemas.room import RoomCreate, AutocompleteRequest, AutocompleteResponse
from backend.app.crud import room_crud
from backend.app.core.ws_manager import manager
from backend.app.core.logger import logger

common_responses = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Not Found"},
    500: {"description": "Internal Server Error"},
}

router = APIRouter(responses=common_responses)


@router.get("/liveness")
def get_liveness():
    """
    Returns application status. Used to check if the process is running.
    """
    return {"status": "alive"}

@router.get("/health", responses={503: {"description": "Service Unavailable"}})
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

@router.websocket("/ws/{room_id}")
async def ws_coding(websocket: WebSocket, room_id: str, db: Session = Depends(get_db)):
    """/ws/{room_id}: Handles real-time code updates."""
    
    # 1. Check if room exists before connecting (THE FIX)
    room = room_crud.get_room_by_id(db, room_id)
    
    if not room:
         # Close with code 1008 Policy Violation if room is invalid/missing
         await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room does not exist.")
         logger.warning(f"WebSocket rejected connection for unknown room ID: {room_id}")
         return


    # 2. Connect and Send initial state
    await manager.connect(websocket, room_id)
    
    # Use the retrieved room object's code content
    initial_code = room.code_content 
    
    if initial_code:
        # Send existing code to the newly connected client
        await websocket.send_text(initial_code)
        logger.info(f"WebSocket client connected to room {room_id}. Sent initial state.")

    try:
        while True:
            # Data received is the full content of the editor
            data = await websocket.receive_text()
          
            room_crud.update_room_code(db, room_id, data)

            # 4. Broadcast to all others in the room
            await manager.broadcast(data, room_id, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        logger.info(f"WebSocket client disconnected from room {room_id}.")