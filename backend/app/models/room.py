from sqlalchemy import Column, String, Text
from app.dependencies import Base

class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(String, primary_key=True, index=True)
    code_content = Column(Text, default="")