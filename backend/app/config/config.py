import json
import os
from typing import  Any, Dict

from pydantic_settings import BaseSettings
from pydantic import model_validator

# Define the path to your config file
CONFIG_FILE_PATH = "config.json" 

# Use an environment variable to determine which block of the config file to use
ENVIRONMENT = os.environ.get("ENV_STATE", "PRODUCTION")

# --- Helper Function (Outside the class) ---

def _load_db_config_url() -> str:
    """Reads database credentials from the JSON file and constructs the connection URL."""
    try:
        # Check if running inside a container (e.g., Docker Compose)
        if os.environ.get("SQLALCHEMY_DATABASE_URL"):
             return os.environ["SQLALCHEMY_DATABASE_URL"]
             
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
        
        # 1. Retrieve the environment block (e.g., "PRODUCTION")
        env_config = config.get(ENVIRONMENT, {}) 
        
        # 2. Retrieve the db_config from within that block
        db_conf = env_config.get("db_config", {})
        
        # 3. Extract credentials with fallbacks
        host = db_conf.get("host", "localhost")
        port = db_conf.get("port", 5432)
        user = db_conf.get("user", "postgres")
        password = db_conf.get("password", "default_password") 
        database = db_conf.get("database", "collab_db")

        # Constructing the Postgres URL string
        db_url = (
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
        return db_url
    
    except FileNotFoundError:
        print(f"Warning: {CONFIG_FILE_PATH} not found. Falling back to SQLite.")
        return "sqlite:///./code_collab.db"
    
    except Exception as e:
        print(f"Error loading config for '{ENVIRONMENT}': {e}. Falling back to SQLite.")
        return "sqlite:///./code_collab.db"

# --- Settings Class ---

class Settings(BaseSettings):
    PROJECT_NAME: str = "PairProgrammingAPI"
    
    # Define SQLALCHEMY_DATABASE_URL as Optional, but with a required validator
    SQLALCHEMY_DATABASE_URL: str

    @model_validator(mode='before')
    @classmethod
    def set_db_url(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads and injects the database URL into the values dictionary 
        before Pydantic validates the fields.
        """
        if not values.get('SQLALCHEMY_DATABASE_URL'):
             values['SQLALCHEMY_DATABASE_URL'] = _load_db_config_url()
        return values

settings = Settings()