from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config.config import settings

# Setup database engine and session
# The URL is pulled dynamically from the config file via the settings object
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL
    # Removed connect_args={"check_same_thread": False} as it's SQLite specific.
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for API routes remains the same
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()