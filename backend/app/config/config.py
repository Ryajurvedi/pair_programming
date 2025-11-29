import json
from pydantic_settings import BaseSettings

# Define the path to your config file
CONFIG_FILE_PATH = "config.json" 

class Settings(BaseSettings):
    PROJECT_NAME: str = "PairProgrammingAPI"
    SQLALCHEMY_DATABASE_URL: str = ""

    def __init__(self, **values):
        super().__init__(**values)
        self.SQLALCHEMY_DATABASE_URL = self._load_db_config()

    def _load_db_config(self) -> str:
        """Reads database credentials from the JSON file and constructs the connection URL."""
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                config = json.load(f)
            
            db_conf = config.get("db_config", {})
            host = db_conf.get("host", "localhost")
            port = db_conf.get("port", 5432)
            user = db_conf.get("user", "postgres")
            password = db_conf.get("password", "default_password")
            database = db_conf.get("database", "collab_db")

            # Constructing the Postgres URL string
            db_url = (
                f"postgresql://{user}:{password}@{host}:{port}/{database}"
            )
            return db_url\
        except FileNotFoundError:
            # Fallback for when the JSON file isn't found
            print(f"Warning: {CONFIG_FILE_PATH} not found. Falling back to SQLite.")
            return "sqlite:///./code_collab.db"
        except Exception as e:
            print(f"Error loading config: {e}. Falling back to SQLite.")
            return "sqlite:///./code_collab.db"

settings = Settings()