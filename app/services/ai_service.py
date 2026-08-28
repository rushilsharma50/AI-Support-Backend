"""
AI Service — analyses support tickets using an LLM and returns structured results.

The LLM provider logic is isolated here so it can be swapped without touching
the API layer.  A mock provider is available for testing.
"""

import json
import logging
from app.schemas.ai import TicketAnalysis
from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — instructs the model on its role and output format.
# The ticket content is treated as *untrusted user input* and is clearly
# separated from these instructions.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a customer-support ticket analysis assistant.

Your job is to analyse a support ticket and return a JSON object with exactly
these fields:

- "category": one of BILLING, TECHNICAL, ACCOUNT, SHIPPING, GENERAL
- "priority": one of LOW, MEDIUM, HIGH, URGENT
- "sentiment": one of POSITIVE, NEUTRAL, NEGATIVE
- "summary": a concise one-or-two sentence summary of the customer's issue
- "suggested_response": a professional customer-support reply that acknowledges
  the issue.  Do NOT claim that any action (refund, escalation, fix, etc.) has
  been performed — only offer to help.

Return ONLY the JSON object, no markdown fences, no extra text.
"""


def _build_user_prompt(title: str, description: str) -> str:
    return (
        f"Analyse the following support ticket.\n\n"
        f"Title: {title}\n\n"
        f"Description: {description}"
    )


# ---------------------------------------------------------------------------
# Provider: Google Gemini
# ---------------------------------------------------------------------------
async def _call_gemini(title: str, description: str) -> TicketAnalysis:
    """Call the Gemini API and parse the response into a TicketAnalysis."""
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = await client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=_build_user_prompt(title, description),
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=TicketAnalysis,
        ),
    )

    # The SDK returns JSON text; parse + validate with Pydantic
    raw = response.text
    data = json.loads(raw)
    return TicketAnalysis.model_validate(data)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------
async def analyse_ticket(title: str, description: str) -> TicketAnalysis:
    """
    Analyse a ticket using the configured LLM provider.

    Raises:
        RuntimeError  – if no API key is configured.
        ValueError    – if the model returns an unparseable response.
        Exception     – on upstream API errors (caller should handle).
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    return await _call_gemini(title, description)
