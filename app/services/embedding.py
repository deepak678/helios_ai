import logging

from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

from app.config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_ENDPOINT, is_azure_configured

logger = logging.getLogger(__name__)

client = None
if is_azure_configured():
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )
    logger.info("Azure OpenAI client initialized for embeddings")
else:
    logger.warning(
        "Azure OpenAI not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file."
    )


def get_embeddings(text_list):
    """Generate embeddings using Azure OpenAI text-embedding-ada-002."""
    if not text_list:
        return []

    if not client:
        logger.error("Azure OpenAI client not initialized. Check AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY.")
        return [[0.0] * 1536 for _ in text_list]  # Return dummy embeddings

    try:
        response = client.embeddings.create(
            input=text_list,
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
        )
        embeddings = [item.embedding for item in response.data]
        logger.info(f"Generated embeddings for {len(text_list)} texts")
        return embeddings
    except Exception as exc:
        logger.exception(f"Failed to generate embeddings: {exc}")
        return [[0.0] * 1536 for _ in text_list]  # Return dummy embeddings on error
