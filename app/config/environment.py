import os
from dotenv import load_dotenv
from enum import Enum

class EnvironmentVariables(Enum):
    OPENAI_API_KEY = "OPENAI_API_KEY"
    SECRET_KEY = "SECRET_KEY"
    UPLOAD_FOLDER = "UPLOAD_FOLDER"
    MAX_CONTENT_LENGTH = "MAX_CONTENT_LENGTH"


def load_environment():
    load_dotenv(dotenv_path='.env')
    return {
        EnvironmentVariables.OPENAI_API_KEY.value: os.getenv("OPENAI_API_KEY"),
        EnvironmentVariables.SECRET_KEY.value: os.getenv("SECRET_KEY"),
        EnvironmentVariables.UPLOAD_FOLDER.value: os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'),
        EnvironmentVariables.MAX_CONTENT_LENGTH.value: 16 * 1024 * 1024
    }

# Load environment variables when module is imported
config = load_environment()
