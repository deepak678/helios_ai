import json
import logging
import os

from openai import OpenAI

from app.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_HYGIENE_DEPLOYMENT_NAME,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    is_azure_configured,
    is_openai_configured,
)

logger = logging.getLogger(__name__)

# Configure environment for Azure OpenAI if present
use_azure = is_azure_configured()
if use_azure:
    os.environ.setdefault("OPENAI_API_KEY", AZURE_OPENAI_API_KEY)
    os.environ.setdefault("OPENAI_API_BASE", AZURE_OPENAI_ENDPOINT)
    os.environ.setdefault("OPENAI_API_TYPE", "azure")
    os.environ.setdefault("OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION)
    logger.info("Configured environment for Azure OpenAI hygiene checks")

# If standard OpenAI key is provided and Azure not used, ensure env var present
if not use_azure and is_openai_configured():
    os.environ.setdefault("OPENAI_API_KEY", OPENAI_API_KEY)
    logger.info("Configured environment for standard OpenAI hygiene checks")

# Initialize OpenAI SDK client
try:
    client = OpenAI()
    logger.info("OpenAI SDK client initialized for hygiene checker")
except Exception:
    client = None
    logger.exception("Failed to initialize OpenAI SDK client for hygiene checker")

PROMPT_TEMPLATE = (
    "You are an expert operational risk analyst. "
    "Evaluate the following risk issues for clarity, completeness, and risk rating justification. "
    "For each issue, respond with a JSON array where each entry contains:\n"
    "  - issue_id (integer)\n"
    "  - score (1-10)\n"
    "  - issues (list of concerns)\n"
    "  - suggestions (list of concrete improvements)\n"
    "Issues: {items}"
)


def evaluate_issue_hygiene(issues, max_items=5):
    """Evaluate the first issues with OpenAI/Azure to return structured hygiene feedback."""
    subset = issues[:max_items]
    if not subset:
        return []

    if not client:
        logger.warning("OpenAI client not initialized; returning default hygiene results.")
        return [
            {
                "issue_id": int(item["issue_id"]),
                "score": 5.0,
                "issues": ["OpenAI/Azure OpenAI not configured. Unable to evaluate."],
                "suggestions": ["Set Azure or OpenAI credentials in your .env file and retry."],
            }
            for item in subset
        ]

    prompt_items = "\n".join(
        [f'- id: {item["issue_id"]}, text: "{item["description"]}"' for item in subset]
    )
    prompt = PROMPT_TEMPLATE.format(items=prompt_items)

    try:
        # Choose deployment/model: Azure uses deployment name, OpenAI uses model name
        deployment_or_model = AZURE_OPENAI_HYGIENE_DEPLOYMENT_NAME if use_azure else OPENAI_MODEL

        response = client.chat.completions.create(
            model=deployment_or_model,
            messages=[
                {"role": "system", "content": "You analyze operational risk issue descriptions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )

        # Response parsing compatible with OpenAI SDK chat completion structure
        content = None
        if hasattr(response, "choices") and len(response.choices) > 0:
            # SDK may expose as response.choices[0].message.content
            choice = response.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                content = choice.message.content
            elif hasattr(choice, "text"):
                content = choice.text

        if not content:
            logger.error("OpenAI response did not contain text. Full response: %s", response)
            raise ValueError("Empty response from OpenAI")

        content = content.strip()
        logger.info("Received hygiene response from OpenAI/Azure OpenAI")

        # Attempt to parse JSON from the response
        parsed = json.loads(content)
        return [
            {
                "issue_id": int(item.get("issue_id", 0)),
                "score": float(item.get("score", 0)),
                "issues": item.get("issues", []),
                "suggestions": item.get("suggestions", []),
            }
            for item in parsed
        ]
    except json.JSONDecodeError:
        logger.exception("Failed to parse JSON from OpenAI hygiene response")
        return [
            {
                "issue_id": int(item["issue_id"]),
                "score": 5.0,
                "issues": ["Could not parse OpenAI response."],
                "suggestions": [
                    "Review the OpenAI API response or adjust the prompt for stricter JSON formatting."
                ],
            }
            for item in subset
        ]
    except Exception as exc:
        logger.exception("OpenAI/Azure OpenAI hygiene evaluation failed: %s", exc)
        return [
            {
                "issue_id": int(item["issue_id"]),
                "score": 5.0,
                "issues": ["OpenAI/Azure OpenAI service error."],
                "suggestions": ["Check credentials, deployment name, network connectivity, and API usage limits."],
            }
            for item in subset
        ]
