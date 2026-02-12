import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()


def get_model():
    """Returns a LiteLlm model instance using the MODEL_NAME environment variable.

    Uses LiteLlm wrapper to support non-Google models (OpenAI, Anthropic, etc.)
    via the LiteLLM library.

    The MODEL_NAME should follow LiteLLM format, e.g.:
      - openai/gpt-4.1-nano
      - openai/gpt-4o
      - anthropic/claude-3-haiku-20240307
    """
    model_name = os.getenv("MODEL_NAME", "openai/gpt-4.1-nano")
    return LiteLlm(model=model_name)
