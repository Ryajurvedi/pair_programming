import uuid
from sqlalchemy.orm import Session
from app.models.room import Room

def create_room(db: Session) -> str:
    """Generates ID, creates room in DB, and returns ID."""
    room_id = str(uuid.uuid4())[:8]
    new_room = Room(room_id=room_id, code_content="")
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return room_id

def get_room_code(db: Session, room_id: str) -> str | None:
    """Retrieves the current code content for a room."""
    room = db.query(Room).filter(Room.room_id == room_id).first()
    return room.code_content if room else None

def update_room_code(db: Session, room_id: str, code_content: str):
    """Updates the persistent code content for a room."""
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if room:
        room.code_content = code_content
        db.commit()