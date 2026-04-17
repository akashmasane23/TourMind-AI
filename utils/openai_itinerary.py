"""
TourMind AI Itinerary Generator
Used by: pages/itinerary_planner.py

Improvements over original:
  - Fixed model name (gpt-4.1-mini -> gpt-4o-mini)
  - Unified API key lookup (secrets flat + nested + env)
  - Richer, structured prompt with budget & packing tips
  - Longer timeout for multi-day itineraries
  - Retry logic with backoff for 429 / 5xx
  - Specific error messages per failure type
  - Token limit scales with number of days
"""

import os
import time
import requests
import streamlit as st
from typing import Optional

# Constants
_MODEL       = "gpt-4o-mini"
_TEMPERATURE = 0.72
_TIMEOUT     = 60        # itineraries take longer than chat replies
_MAX_RETRIES = 2


def _get_api_key() -> Optional[str]:
    """
    Fetch OpenAI key — checks all common secret locations:
      1. st.secrets["OPENAI_API_KEY"]          (flat)
      2. st.secrets["api_keys"]["OPENAI_API_KEY"] (nested)
      3. OS environment variable
    """
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
        if "api_keys" in st.secrets:
            key = st.secrets["api_keys"].get("OPENAI_API_KEY")
            if key:
                return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def _build_prompt(
    destination: str,
    days: int,
    trip_type: str,
    preferences: list,
) -> str:
    """
    Build a detailed, structured itinerary prompt.
    More days = more explicit instruction to be thorough.
    """
    prefs_text = ", ".join(preferences) if preferences else "general sightseeing"
    multi_day_note = (
        "Since this is a multi-day trip, ensure each day has a distinct focus "
        "and activities are geographically optimised to minimise travel time."
        if days > 2 else ""
    )

    return f"""You are TourMind, a professional travel planner with deep knowledge of India.

Create a detailed, realistic {days}-day {trip_type.lower()} itinerary for {destination}.

Traveller Preferences: {prefs_text}
{multi_day_note}

FORMAT — follow this structure exactly for every day:

---
### Day [N]: [Creative Day Title]

**Morning** 🌅
[2-3 activities with brief descriptions and practical tips]

**Afternoon** ☀️
[2-3 activities including lunch recommendation with cuisine type]

**Evening** 🌆
[1-2 activities + dinner recommendation]

**Travel Tips for the Day** 💡
- [Transport tip]
- [Cost/booking tip]
- [Local etiquette or safety tip]
---

After all days, add these two sections:

### 🎒 What to Pack
[5-6 destination-specific packing suggestions]

### 💰 Estimated Budget (per person)
| Category | Estimated Cost |
|----------|---------------|
| Accommodation | ₹ |
| Food | ₹ |
| Transport | ₹ |
| Activities | ₹ |
| **Total** | **₹** |

Start with a 2-sentence warm welcome that mentions {destination} and the {trip_type.lower()} theme.
Keep the tone friendly, practical, and enthusiastic."""


def get_openai_itinerary(
    destination: str,
    days: int,
    trip_type: str,
    preferences: list,
) -> tuple[Optional[str], Optional[str]]:
    """
    Generate a structured travel itinerary using OpenAI.

    Args:
        destination:  City or region name.
        days:         Number of trip days (1-14).
        trip_type:    e.g. Adventure, Cultural, Relaxation.
        preferences:  List of traveller preference strings.

    Returns:
        (itinerary_text, None)  on success
        (None, error_message)   on failure
    """
    # Guards
    api_key = _get_api_key()
    if not api_key:
        return None, (
            "OpenAI API key is not configured. "
            "Add OPENAI_API_KEY to your .streamlit/secrets.toml and restart."
        )

    if not destination or not destination.strip():
        return None, "Please enter a valid destination."

    days = max(1, min(int(days), 14))   # clamp 1-14

    # Scale token limit with days (roughly 350 tokens per day + overhead)
    max_tokens = min(350 * days + 600, 4000)

    prompt   = _build_prompt(destination.strip(), days, trip_type, preferences or [])
    headers  = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
    }
    payload  = {
        "model":       _MODEL,
        "messages": [
            {
                "role":    "system",
                "content": (
                    "You are an expert travel planner for India. "
                    "Always respond in clean Markdown format. "
                    "Be practical, specific, and enthusiastic."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": _TEMPERATURE,
        "max_tokens":  max_tokens,
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

            # Success
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                return text, None

            # Rate limited
            if resp.status_code == 429:
                last_error = "Rate limit reached. Please wait a moment."
                if attempt < _MAX_RETRIES:
                    time.sleep(2 ** attempt)
                continue

            # Auth error
            if resp.status_code == 401:
                return None, (
                    "Invalid OpenAI API key. "
                    "Please check your .streamlit/secrets.toml."
                )

            # Server error — retry
            if resp.status_code >= 500:
                last_error = f"OpenAI server error ({resp.status_code})."
                if attempt < _MAX_RETRIES:
                    time.sleep(2)
                continue

            # Other 4xx — don't retry
            err_msg = resp.json().get("error", {}).get("message", resp.text)
            return None, f"OpenAI Error {resp.status_code}: {err_msg}"

        except requests.exceptions.Timeout:
            last_error = (
                f"Request timed out after {_TIMEOUT}s. "
                "Try a shorter trip duration or try again."
            )
            if attempt < _MAX_RETRIES:
                time.sleep(1)

        except requests.exceptions.ConnectionError:
            last_error = "Could not connect to OpenAI. Check your internet connection."
            if attempt < _MAX_RETRIES:
                time.sleep(1.5)

        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

    return None, f"{last_error}\n\nPlease try again shortly."