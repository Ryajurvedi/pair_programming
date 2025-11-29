from fastapi import FastAPI
from app.api.v1.endpoints import coding
from app.dependencies import Base, engine
from app.config.config import settings
from app.models import room
from app.core.logger import logger # IMPORT THE LOGGER

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# --- START LOGGING ---
logger.info(f"Starting {settings.PROJECT_NAME} application.")
# --- END LOGGING ---

# CORS setup
# ... (rest of the CORS middleware setup)

# Include API routes
app.include_router(coding.router, prefix="/api/v1", tags=["Coding"])

@app.get("/")
def read_root():
    return {"message": "Pair Programming API is running"}