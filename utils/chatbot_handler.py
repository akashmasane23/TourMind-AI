"""
TourMind AI Chatbot — OpenAI + Semantic Search
Improvements:
  - Lazy model loading (no startup freeze)
  - Cached embeddings (no recompute on every call)
  - Full conversation memory passed to OpenAI
  - Streaming response support
  - Robust error handling with user-friendly messages
  - Richer, travel-specific system prompt
"""

import os
import time
import numpy as np
import pandas as pd
import requests
import streamlit as st

# ── Lazy imports (heavy libs loaded only when first needed) ──
_model = None
_place_embeddings = None
_places_df = None


# ============================================
# INTERNAL HELPERS
# ============================================

def _get_api_key() -> str | None:
    """Retrieve OpenAI API key from Streamlit secrets or env vars."""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return os.getenv("OPENAI_API_KEY")


@st.cache_resource(show_spinner="Loading AI model…")
def _load_model():
    """
    Load SentenceTransformer once per session and cache it.
    Using cache_resource so the model is shared across reruns.
    """
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_data(show_spinner="Indexing places…")
def _load_places_and_embeddings() -> tuple:
    """
    Load places CSV and pre-compute embeddings.
    Cached so embeddings are only generated once per session.
    Returns (DataFrame, np.ndarray).
    """
    try:
        df = pd.read_csv("data/places.csv")
    except FileNotFoundError:
        return pd.DataFrame(), np.array([])

    if df.empty:
        return df, np.array([])

    model = _load_model()

    texts = (
        df["place_name"].astype(str)       + " " +
        df["description_keyword"].astype(str) + " " +
        df["activity_type"].astype(str)
    ).tolist()

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return df, embeddings


def _get_top_places(query: str, top_k: int = 4) -> str:
    """
    Semantic search over places dataset.
    Returns a formatted context string of the top-k matches.
    """
    from sklearn.metrics.pairwise import cosine_similarity

    df, embeddings = _load_places_and_embeddings()

    if df.empty or embeddings.size == 0:
        return "No places data available."

    model = _load_model()
    query_emb = model.encode([query], convert_to_numpy=True)
    scores = cosine_similarity(query_emb, embeddings)[0]
    top_idx = scores.argsort()[-top_k:][::-1]
    top = df.iloc[top_idx]

    lines = []
    for _, row in top.iterrows():
        lines.append(
            f"• {row.get('place_name','?')} "
            f"({row.get('city','?')}, {row.get('state','?')}) | "
            f"Activities: {row.get('activity_type','?')} | "
            f"Tags: {row.get('description_keyword','?')}"
        )
    return "\n".join(lines)


def _build_messages(
    user_query: str,
    context: str,
    history: list[tuple[str, str]]
) -> list[dict]:
    """
    Build the full OpenAI messages array including:
    - A rich travel-guide system prompt
    - Full conversation history
    - Current user query with injected context
    """
    system_prompt = """You are TourMind 🌿, an expert AI travel guide specialising in India.

Your personality:
- Warm, enthusiastic, and knowledgeable
- Concise but rich with practical tips
- Use emojis naturally — not excessively
- Always encourage the traveller's curiosity

Your capabilities:
- Recommend destinations, routes, and hidden gems
- Suggest itineraries based on duration and interests
- Advise on best seasons, local food, culture, and budget
- Answer questions about transport, accommodation, and safety

Rules:
- Always stay on travel-related topics
- If unsure, say so honestly — never fabricate facts
- Keep responses under 300 words unless a detailed itinerary is requested
- End with a helpful follow-up question or tip when appropriate"""

    messages = [{"role": "system", "content": system_prompt}]

    # Inject conversation history (last 10 turns max to stay within token limits)
    for role, content in history[-10:]:
        messages.append({"role": role, "content": content})

    # Inject semantic context + user query
    user_content = f"""Relevant places from our database:
{context}

User question:
{user_query}"""

    messages.append({"role": "user", "content": user_content})
    return messages


# ============================================
# PUBLIC API
# ============================================

def get_openai_response(
    user_query: str,
    history: list[tuple[str, str]] | None = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.65,
    max_tokens: int = 600,
    retries: int = 2,
) -> str:
    """
    Main entry point for the chatbot.

    Args:
        user_query:  The user's latest message.
        history:     List of (role, content) tuples from previous turns.
                     role must be "user" or "assistant".
        model:       OpenAI model name.
        temperature: Creativity (0 = deterministic, 1 = creative).
        max_tokens:  Max response length.
        retries:     Number of retry attempts on transient failures.

    Returns:
        AI response as a string.
    """
    api_key = _get_api_key()
    if not api_key:
        return (
            "⚠️ OpenAI API key is not configured.\n\n"
            "Add `OPENAI_API_KEY` to your `.streamlit/secrets.toml` file."
        )

    if not user_query.strip():
        return "Please ask me something about your travel plans! 🌍"

    history = history or []

    # Semantic context from places DB
    context = _get_top_places(user_query)

    # Build messages
    messages = _build_messages(user_query, context, history)

    # ── OpenAI call with retry ────────────────
    last_error = ""
    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       model,
                    "messages":    messages,
                    "temperature": temperature,
                    "max_tokens":  max_tokens,
                },
                timeout=30,
            )

            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()

            elif resp.status_code == 429:
                # Rate limited — back off and retry
                wait = 2 ** attempt
                time.sleep(wait)
                last_error = "Rate limit reached. Please wait a moment."

            elif resp.status_code == 401:
                return "❌ Invalid OpenAI API key. Please check your secrets configuration."

            elif resp.status_code == 503:
                time.sleep(1.5)
                last_error = "OpenAI service is temporarily unavailable."

            else:
                error_detail = resp.json().get("error", {}).get("message", resp.text)
                last_error = f"OpenAI Error {resp.status_code}: {error_detail}"
                break  # Don't retry 4xx errors

        except requests.exceptions.Timeout:
            last_error = "Request timed out. OpenAI may be busy — please try again."
            if attempt < retries:
                time.sleep(1)

        except requests.exceptions.ConnectionError:
            last_error = "Could not connect to OpenAI. Check your internet connection."
            if attempt < retries:
                time.sleep(1.5)

        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            break

    return f"❌ {last_error}\n\n_Try rephrasing your question or try again shortly._"


def get_streaming_response(
    user_query: str,
    history: list[tuple[str, str]] | None = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.65,
):
    """
    Generator that yields response chunks for streaming display.
    Use with st.write_stream() in Streamlit.

    Usage:
        with st.chat_message("assistant"):
            response = st.write_stream(
                get_streaming_response(user_input, chat_history)
            )
    """
    api_key = _get_api_key()
    if not api_key:
        yield "⚠️ OpenAI API key not configured."
        return

    history = history or []
    context = _get_top_places(user_query)
    messages = _build_messages(user_query, context, history)

    try:
        with requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":       model,
                "messages":    messages,
                "temperature": temperature,
                "stream":      True,
            },
            stream=True,
            timeout=60,
        ) as resp:

            if resp.status_code != 200:
                yield f"❌ OpenAI Error {resp.status_code}"
                return

            for line in resp.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                if line == "[DONE]":
                    break
                try:
                    import json
                    chunk = json.loads(line)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except Exception:
                    continue

    except Exception as e:
        yield f"❌ Streaming error: {str(e)}"