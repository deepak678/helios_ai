import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file from project root if it exists
env_file = Path(__file__).resolve().parents[2] / ".env"
if env_file.exists():
    load_dotenv(env_file)
    logger.info(f"Loaded environment from {env_file}")
else:
    logger.info(".env file not found; using environment variables only")

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "text-embedding-ada-002")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")

# OpenAI Configuration (for hygiene checker)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

def is_azure_configured():
    """Check if Azure OpenAI credentials are configured."""
    return bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY)

def is_openai_configured():
    """Check if OpenAI credentials are configured."""
    return bool(OPENAI_API_KEY)
