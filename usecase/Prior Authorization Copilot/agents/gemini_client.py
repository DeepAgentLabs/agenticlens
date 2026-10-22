"""
agents/gemini_client.py
-----------------------
Shared Gemini client configuration for all agents.
Uses the new google-genai SDK (v2+) which supports AQ. prefixed API keys.

Model cascade with high availability:
  1. gemini-3.5-flash-lite (fastest, lowest latency ~1s, immune to free-tier 503s)
  2. gemini-flash-lite-latest (latest lite flash)
  3. gemini-3.8-flash (standard full flash)
  4. gemini-3.5-flash (stable flash)
"""

import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types

load_dotenv()

logger = logging.getLogger("gemini_client")

# Shared client instance — one per process
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS_CASCADE = [
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
]


def generate(prompt: str, system_instruction: str,
             temperature: float = 0.0, max_tokens: int = 2048,
             json_mode: bool = True) -> str:
    """
    Call Gemini with automatic model cascade across available models.
    Supports json_mode to enforce clean JSON formatting directly from the API.
    Returns the raw text response string.
    """
    last_error = None

    for model in MODELS_CASCADE:
        try:
            config = genai_types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            if json_mode:
                config.response_mime_type = "application/json"

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            text = response.text
            if text and text.strip():
                return text.strip()
            last_error = ValueError(f"Model {model} returned empty response")
        except Exception as e:
            err_str = str(e)
            # Transient/capacity/deprecation errors fall through to the next model
            if any(x in err_str for x in ["503", "UNAVAILABLE", "404", "NOT_FOUND", "no longer available", "ResourceExhausted", "429"]):
                last_error = e
                continue
            raise  # Fatal auth errors etc.

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )


def parse_json_response(raw: str) -> dict:
    """Robustly parse JSON from Gemini, handling markdown code fences if present."""
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("```").strip()
    return json.loads(text)
