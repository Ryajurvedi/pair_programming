from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.endpoints import coding
from backend.app.dependencies import Base, engine
from backend.app.config.config import settings
from backend.app.core.logger import logger

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME,version="1.0.0", description="API for a Pair Programming Application")


logger.info(f"Starting {settings.PROJECT_NAME} application.")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost:3000", 
    "http://localhost:5173", 
    "insomnia://app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
    max_age=600, 
)


# Include API routes
app.include_router(coding.router, prefix="/api/v1", tags=["Coding"])

@app.get("/")
def read_root():
    return {"message": "Pair Programming API is running"}


# python -m uvicorn backend.app.main:app --reload