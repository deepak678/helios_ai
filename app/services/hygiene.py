import json
import logging
import os

import openai

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


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
    """Evaluate the first issues with OpenAI to return structured hygiene feedback."""
    subset = issues[:max_items]
    if not subset:
        return []

    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not configured; returning default hygiene results.")
        return [
            {
                "issue_id": int(item["issue_id"]),
                "score": 5.0,
                "issues": ["OpenAI key missing. Unable to evaluate."],
                "suggestions": ["Set OPENAI_API_KEY in your environment and retry."],
            }
            for item in subset
        ]

    prompt_items = "\n".join(
        [f'- id: {item["issue_id"]}, text: "{item["description"]}"' for item in subset]
    )
    prompt = PROMPT_TEMPLATE.format(items=prompt_items)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You analyze operational risk issue descriptions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        content = response["choices"][0]["message"]["content"].strip()
        logger.info("Received hygiene response from OpenAI")

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
    except Exception:
        logger.exception("OpenAI hygiene evaluation failed")
        return [
            {
                "issue_id": int(item["issue_id"]),
                "score": 5.0,
                "issues": ["OpenAI service error."],
                "suggestions": ["Check OPENAI_API_KEY, network connectivity, and API usage limits."],
            }
            for item in subset
        ]
