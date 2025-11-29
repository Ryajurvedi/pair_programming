from pydantic import BaseModel

class RoomCreate(BaseModel):
    # Output schema for room creation
    roomId: str

class AutocompleteRequest(BaseModel):
    code: str
    cursorPosition: int
    language: str # e.g., "python"

class AutocompleteResponse(BaseModel):
    suggestion: str