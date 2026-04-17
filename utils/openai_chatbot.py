"""
TourMind OpenAI Chatbot Handler
Used by: pages/chatbot_assistant.py

Improvements over original:
  - Fixed model name (gpt-4.1-mini -> gpt-4o-mini)
  - Rich travel-specific system prompt
  - Retry logic with backoff for 429 / 5xx
  - Specific error messages per failure type
  - History window configurable, default 10 turns
  - Safe API key fetch (secrets -> env -> None)
  - Response stripped of leading/trailing whitespace
"""

import os
import time
import requests
import streamlit as st
from typing import Optional

# Constants
_MODEL         = "gpt-4o-mini"
_TEMPERATURE   = 0.65
_MAX_TOKENS    = 600
_TIMEOUT       = 30
_HISTORY_TURNS = 10
_MAX_RETRIES   = 2

_SYSTEM_PROMPT = """You are TourMind, an expert AI travel guide specialising in India.

Your personality:
- Warm, enthusiastic, and knowledgeable about travel
- Concise but rich with practical, actionable tips
- Use emojis naturally, not excessively
- Always encourage the traveller's curiosity

Your capabilities:
- Recommend destinations, routes, and hidden gems
- Suggest day-by-day itineraries based on duration and interests
- Advise on best seasons, local food, culture, budget, and safety
- Help with transport options and accommodation choices

Rules:
- Stay on travel-related topics only
- If unsure about a fact, say so honestly, never fabricate
- Keep responses under 300 words unless a full itinerary is requested
- End with a helpful follow-up question or tip when appropriate"""


def _get_api_key() -> Optional[str]:
    """Fetch OpenAI key from Streamlit secrets, then environment."""
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def _build_messages(query: str, chat_history) -> list:
    """Build the OpenAI messages array with system prompt + history + query."""
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]

    if chat_history:
        recent = chat_history[-(_HISTORY_TURNS * 2):]
        for role, content in recent:
            if role in ("user", "assistant") and content.strip():
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": query.strip()})
    return messages


def get_openai_response(query: str, chat_history=None) -> str:
    """
    Send a query to OpenAI and return the assistant reply.

    Args:
        query:        The user current message.
        chat_history: List of (role, content) tuples from prior turns.

    Returns:
        Assistant reply string, or a user-friendly error message.
    """
    api_key = _get_api_key()
    if not api_key:
        return (
            "OpenAI API key is not configured.\n\n"
            "Add OPENAI_API_KEY to your .streamlit/secrets.toml file and restart."
        )

    if not query or not query.strip():
        return "Please ask me something about your travel plans!"

    messages = _build_messages(query, chat_history)
    headers  = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       _MODEL,
        "messages":    messages,
        "temperature": _TEMPERATURE,
        "max_tokens":  _MAX_TOKENS,
    }

    last_error = "Unknown error."

    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=_TIMEOUT,
            )

            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()

            if resp.status_code == 429:
                last_error = "Rate limit reached. Trying again shortly."
                if attempt < _MAX_RETRIES:
                    time.sleep(2 ** attempt)
                continue

            if resp.status_code == 401:
                return (
                    "Invalid OpenAI API key. "
                    "Please check the key in your .streamlit/secrets.toml."
                )

            if resp.status_code >= 500:
                last_error = f"OpenAI server error ({resp.status_code})."
                if attempt < _MAX_RETRIES:
                    time.sleep(1.5)
                continue

            err_msg = resp.json().get("error", {}).get("message", resp.text)
            return f"OpenAI Error {resp.status_code}: {err_msg}"

        except requests.exceptions.Timeout:
            last_error = "Request timed out. Please try again."
            if attempt < _MAX_RETRIES:
                time.sleep(1)

        except requests.exceptions.ConnectionError:
            last_error = "Could not connect to OpenAI. Check your internet connection."
            if attempt < _MAX_RETRIES:
                time.sleep(1.5)

        except Exception as e:
            return f"Unexpected error: {str(e)}"

    return f"{last_error}\n\nTry rephrasing your question or wait a moment."