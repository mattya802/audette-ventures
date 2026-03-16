"""Wrapper around Google Gemini API for content generation."""

import json
import logging
from google import genai

from config import GEMINI_API_KEY, STYLE_GUIDE

logger = logging.getLogger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"


def generate(prompt: str, system_instruction: str = STYLE_GUIDE) -> str:
    """Generate text using Gemini, with the style guide as system context."""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8,
            ),
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def generate_json(prompt: str, system_instruction: str = STYLE_GUIDE) -> dict:
    """Generate and parse JSON from Gemini. Prompt must ask for JSON output."""
    full_prompt = prompt + "\n\nRespond ONLY with valid JSON. No markdown, no code fences."
    text = generate(full_prompt, system_instruction)

    # Strip any accidental code fences
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    return json.loads(text)
