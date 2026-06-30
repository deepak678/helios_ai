import logging
import os

from openai import OpenAI

from app.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
    is_azure_configured,
)

logger = logging.getLogger(__name__)

# Configure environment for OpenAI SDK when using Azure OpenAI
if is_azure_configured():
    # Set environment variables expected by the OpenAI SDK to target Azure
    os.environ.setdefault("OPENAI_API_KEY", AZURE_OPENAI_API_KEY)
    os.environ.setdefault("OPENAI_API_BASE", AZURE_OPENAI_ENDPOINT)
    os.environ.setdefault("OPENAI_API_TYPE", "azure")
    os.environ.setdefault("OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION)
    logger.info("Configured environment for Azure OpenAI embeddings")

# Initialize OpenAI SDK client (reads from env vars)
try:
    client = OpenAI()
    logger.info("OpenAI SDK client initialized for embeddings")
except Exception:
    client = None
    logger.exception("Failed to initialize OpenAI SDK client for embeddings")


def get_embeddings(text_list):
    """Generate embeddings for a list of text strings via the OpenAI SDK.

    This function uses environment-driven config to support Azure OpenAI (set
    OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_API_TYPE, OPENAI_API_VERSION) or
    regular OpenAI (OPENAI_API_KEY).
    """
    if not text_list:
        return []

    if not client:
        logger.error("OpenAI client not initialized. Returning placeholder embeddings.")
        return [[0.0] * 1536 for _ in text_list]

    try:
        # call embeddings endpoint; model name should be deployment name for Azure
        response = client.embeddings.create(model=AZURE_OPENAI_DEPLOYMENT_NAME, input=text_list)
        embeddings = [item.embedding for item in response.data]
        logger.info("Generated embeddings for %d texts", len(embeddings))
        return embeddings
    except Exception:
        logger.exception("Failed to generate embeddings via OpenAI SDK")
        return [[0.0] * 1536 for _ in text_list]
