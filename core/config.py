# db/session.py
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings



# Load environment variables from .env
load_dotenv()

# Retrieve environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
print(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)


# Check if all required environment variables are present
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Generating Database URL
encoded_password = quote_plus(str(DB_PASSWORD))

DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = "postgresql://postgres:1234@localhost:5432/cbs_dev_restore"
print(DATABASE_URL)

# Logging Configuration
class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    LOG_DATEFORMAT: str = "%Y-%m-%d %H:%M:%S"

    model_config = {
        'extra': 'allow'
    }

settings = Settings()
