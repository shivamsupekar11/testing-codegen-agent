import os
from dotenv import load_dotenv

load_dotenv()


def get_model_name() -> str:
    """Returns the model name from the MODEL_NAME environment variable."""
    return os.getenv("MODEL_NAME")
