"""
API Handler Functions — TourMind
Handles Unsplash, OpenWeatherMap, Wikipedia APIs
Improvements: retry logic, specific error handling,
              deprecated URL fixes, richer responses
"""

import time
import requests
import streamlit as st
import wikipediaapi
from typing import Optional, Dict, List
from config import *


# ============================================
# INTERNAL HELPER — RETRY REQUEST
# ============================================

def _get_with_retry(
    url: str,
    params: dict = None,
    headers: dict = None,
    retries: int = 2,
    timeout: int = 10,
    backoff: float = 0.6
) -> Optional[requests.Response]:
    """
    GET request with automatic retry + exponential backoff.
    Returns Response on success, None on all failures.
    """
    for attempt in range(retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )
            if response.status_code == 200:
                return response
            # 429 = rate limited — wait longer before retry
            if response.status_code == 429:
                time.sleep(backoff * (attempt + 2))
            elif response.status_code >= 500:
                time.sleep(backoff * (attempt + 1))
            else:
                # 4xx client error — no point retrying
                return None
        except requests.exceptions.Timeout:
            if attempt < retries:
                time.sleep(backoff)
        except requests.exceptions.ConnectionError:
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
        except requests.exceptions.RequestException:
            return None
    return None


# ============================================
# UNSPLASH API
# ============================================

# ── Curated activity-type fallback search terms ──────────────
# When a specific place name returns no results, we fall back
# to a generic landscape image matching the place's category.
_ACTIVITY_FALLBACKS = {
    "historical":  ["ancient fort india", "historical monument india", "heritage architecture india"],
    "forts":       ["indian fort architecture", "maratha fort", "hilltop fort india"],
    "religious":   ["hindu temple india", "temple architecture india", "indian shrine"],
    "spiritual":   ["spiritual temple india", "pilgrimage india", "sacred place india"],
    "nature":      ["india nature landscape", "scenic india outdoors", "green hills india"],
    "adventure":   ["adventure tourism india", "paragliding india", "trekking india mountains"],
    "cultural":    ["indian culture heritage", "india cultural festival", "traditional india"],
    "shopping":    ["india bazaar market", "colorful market india", "shopping street india"],
    "food":        ["indian street food", "india food market", "traditional indian cuisine"],
    "city":        ["pune city india", "india urban cityscape", "modern india city"],
    "camping":     ["camping nature india", "lakeside camping india", "outdoor camping"],
    "mountains":   ["western ghats india", "india hill station", "mountain landscape india"],
    "wildlife":    ["indian wildlife sanctuary", "india nature wildlife", "indian animals"],
    "sports":      ["cricket stadium india", "sports india", "india sports ground"],
    "family":      ["india family tourism", "garden park india", "india attraction"],
    "mall":        ["india shopping mall", "modern mall india", "retail india"],
    "water park":  ["water park india", "amusement water slides", "fun water park"],
}

_CITY_FALLBACKS = {
    "pune":     ["pune india", "pune city maharashtra", "pune landmark"],
    "mumbai":   ["mumbai india", "mumbai gateway", "mumbai cityscape"],
    "goa":      ["goa beach india", "goa tourism", "goa coastal"],
    "jaipur":   ["jaipur rajasthan india", "jaipur pink city", "jaipur palace"],
    "delhi":    ["delhi india monument", "new delhi tourism", "india gate delhi"],
    "agra":     ["agra taj mahal", "agra india tourism"],
    "kerala":   ["kerala backwaters india", "kerala nature tourism"],
}


def _unsplash_fallback(query: str, count: int = 1,
                        activity: str = None, city: str = None) -> List[Dict]:
    """
    Multi-tier fallback:
    1. Picsum with a landscape-themed seed (deterministic per place name)
    The seed is kept consistent so the same place always shows the same image.
    """
    # Use a consistent seed so the same place always maps to same image
    seed = abs(hash(query.lower().strip())) % 1000
    return [
        {
            "url": f"https://picsum.photos/seed/{seed + i}/800/500",
            "alt": query,
            "photographer": "Picsum Photos",
            "photographer_url": "https://picsum.photos"
        }
        for i in range(count)
    ]


def _build_search_variations(place_name: str,
                               activity_type: str = None,
                               city: str = None) -> List[str]:
    """
    Build a smart, ordered list of search queries for a place name.
    Strategy:
      1. Exact place name + "india"
      2. Cleaned place name (remove parenthetical qualifiers)
      3. City + activity context
      4. Pure activity-type generic fallback
      5. Pure city fallback
    """
    variations = []
    name = place_name.strip()

    # Remove qualifiers like "(Near Pune)", "(Lonavala)" etc.
    import re
    clean_name = re.sub(r"\s*[(][^)]*[)]", "", name).strip()

    # 1. Exact + country
    variations.append(f"{name} india")

    # 2. Clean name + india
    if clean_name != name:
        variations.append(f"{clean_name} india")

    # 3. Clean name alone
    variations.append(clean_name)

    # 4. City context
    if city:
        city_l = city.lower()
        variations.append(f"{clean_name} {city_l}")
        # City-only fallback terms
        for c_key, c_terms in _CITY_FALLBACKS.items():
            if c_key in city_l:
                variations.extend(c_terms[:2])
                break

    # 5. Activity-type generic terms
    if activity_type:
        act_l = activity_type.lower()
        for a_key, a_terms in _ACTIVITY_FALLBACKS.items():
            if a_key in act_l:
                variations.extend(a_terms[:2])
                break

    # 6. Last resort — "india tourism"
    variations.append("india tourism landmark")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for v in variations:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


@st.cache_data(ttl=86400)  # 24 hours
def get_unsplash_image(query: str, count: int = 1,
                        activity_type: str = None,
                        city: str = None) -> List[Dict]:
    """
    Fetch images from Unsplash with smart multi-tier search strategy.

    Improvements:
    - Removes parenthetical qualifiers from place names before searching
    - Falls back through activity-type and city-level generic queries
    - Never returns a broken image — always falls back to Picsum
    - Validates that returned images actually have a usable URL
    """
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY":
        return _unsplash_fallback(query, count, activity_type, city)

    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    variations = _build_search_variations(query, activity_type, city)

    for search_query in variations:
        response = _get_with_retry(
            UNSPLASH_API_URL,
            params={
                "query":          search_query,
                "per_page":       max(count, 3),   # fetch a few extra to filter bad ones
                "orientation":    "landscape",
                "content_filter": "high",
            },
            headers=headers,
        )

        if not response:
            continue

        results = response.json().get("results", [])
        if not results:
            continue

        # Filter out results with missing/placeholder URLs
        valid = [
            r for r in results
            if r.get("urls", {}).get("regular")
            and r.get("user", {}).get("name")
            and r.get("width", 0) > 400   # skip tiny images
        ]

        if valid:
            return [
                {
                    "url":              r["urls"]["regular"],
                    "thumb":            r["urls"]["thumb"],
                    "alt":              r.get("alt_description") or search_query,
                    "photographer":     r["user"]["name"],
                    "photographer_url": r["user"]["links"]["html"],
                    "unsplash_link":    r["links"]["html"],
                    "query_used":       search_query,   # useful for debugging
                }
                for r in valid[:count]
            ]

    # All Unsplash queries failed — use Picsum
    return _unsplash_fallback(query, count, activity_type, city)


# ============================================
# WIKIPEDIA API
# ============================================

@st.cache_data(ttl=604800)  # 7 days — Wikipedia content rarely changes
def get_wikipedia_summary(
    place_name: str,
    max_chars: int = 600
) -> Optional[Dict]:
    """
    Fetch Wikipedia summary with auto-disambiguation fallback.
    Tries the exact name first, then appends context words on failure.
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent=WIKI_USER_AGENT,
            language=WIKI_LANGUAGE
        )

        # Try variations if exact match fails
        attempts = [
            place_name,
            f"{place_name} (city)",
            f"{place_name} (India)",
            f"{place_name} tourist attraction",
        ]

        for attempt in attempts:
            page = wiki.page(attempt)
            if page.exists() and len(page.summary.strip()) > 50:
                summary = page.summary
                if len(summary) > max_chars:
                    # Cut at sentence boundary
                    trimmed = summary[:max_chars]
                    last_dot = trimmed.rfind(".")
                    summary = trimmed[:last_dot + 1] if last_dot > 0 else trimmed + "…"

                return {
                    "title":   page.title,
                    "summary": summary,
                    "url":     page.fullurl,
                    "exists":  True,
                }

        return {
            "title":   place_name,
            "summary": f"No detailed Wikipedia article found for '{place_name}'.",
            "url":     None,
            "exists":  False,
        }

    except Exception as e:
        return {
            "title":   place_name,
            "summary": "Wikipedia information is temporarily unavailable.",
            "url":     None,
            "exists":  False,
            "error":   str(e),
        }


@st.cache_data(ttl=CACHE_TTL_LONG)
def search_wikipedia_places(query: str, max_results: int = 10) -> List[str]:
    """Search Wikipedia for place names matching a query."""
    try:
        import wikipedia
        wikipedia.set_lang(WIKI_LANGUAGE)
        return wikipedia.search(query, results=max_results)
    except Exception:
        return []


# ============================================
# OPENWEATHERMAP API
# ============================================

@st.cache_data(ttl=CACHE_TTL_SHORT)
def get_weather_forecast(city: str, days: int = 5) -> Optional[Dict]:
    """
    Fetch current weather + multi-day forecast.
    Returns structured dict or None on failure.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        return None

    base_params = {
        "q":     city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    # ── Current weather ──────────────────────
    current_resp = _get_with_retry(
        f"{OPENWEATHER_API_URL}/weather",
        params=base_params,
    )

    if not current_resp:
        return None

    current_data = current_resp.json()

    # ── Forecast ─────────────────────────────
    forecast_resp = _get_with_retry(
        f"{OPENWEATHER_API_URL}/forecast",
        params={**base_params, "cnt": min(days * 8, 40)},
    )

    # Build current conditions
    weather_main = current_data["weather"][0]
    current = {
        "temp":        round(current_data["main"]["temp"], 1),
        "feels_like":  round(current_data["main"]["feels_like"], 1),
        "description": weather_main["description"].capitalize(),
        "humidity":    current_data["main"]["humidity"],
        "wind_speed":  round(current_data["wind"]["speed"], 1),
        "icon":        weather_main["icon"],
        "icon_url":    get_weather_icon_url(weather_main["icon"]),
        "city":        current_data["name"],
        "country":     current_data["sys"].get("country", ""),
        "visibility":  round(current_data.get("visibility", 0) / 1000, 1),  # km
    }

    # Build daily forecast
    daily_forecast: List[Dict] = []
    seen_dates: set = set()

    if forecast_resp:
        for item in forecast_resp.json().get("list", []):
            date = item["dt_txt"].split()[0]
            if date in seen_dates:
                continue
            seen_dates.add(date)

            fw = item["weather"][0]
            daily_forecast.append({
                "date":        date,
                "temp_max":    round(item["main"]["temp_max"], 1),
                "temp_min":    round(item["main"]["temp_min"], 1),
                "description": fw["description"].capitalize(),
                "icon":        fw["icon"],
                "icon_url":    get_weather_icon_url(fw["icon"]),
                "humidity":    item["main"]["humidity"],
                "wind_speed":  round(item["wind"]["speed"], 1),
            })

            if len(daily_forecast) >= days:
                break

    return {
        "current":  current,
        "forecast": daily_forecast,
        "success":  True,
    }


# ============================================
# CHATBOT FALLBACK (Rule-based)
# ============================================

def get_chatbot_response(user_message: str) -> str:
    """
    Rule-based chatbot fallback when OpenAI is unavailable.
    Matches keywords defined in config.CHATBOT_KEYWORDS.
    """
    message_lower = user_message.lower().strip()

    # Longest-match first to avoid partial keyword collisions
    matched = None
    matched_len = 0
    for keyword, response in CHATBOT_KEYWORDS.items():
        if keyword in message_lower and len(keyword) > matched_len:
            matched = response
            matched_len = len(keyword)

    return matched if matched else DEFAULT_CHATBOT_RESPONSE


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_weather_icon_url(icon_code: str) -> str:
    """Return HTTPS URL for an OpenWeatherMap icon (2x resolution)."""
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


def format_temperature(temp: float, unit: str = "C") -> str:
    """Format temperature with degree symbol."""
    return f"{round(temp, 1)}°{unit}"


def get_google_maps_url(place_name: str) -> str:
    """Build a Google Maps search URL for a place name."""
    query = requests.utils.quote(place_name)
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def check_api_health() -> Dict[str, bool]:
    """
    Quick health check — verifies API keys are non-default.
    Does NOT make live calls (avoids wasting quota on startup).
    """
    return {
        "unsplash":     bool(UNSPLASH_ACCESS_KEY)    and UNSPLASH_ACCESS_KEY    != "YOUR_UNSPLASH_ACCESS_KEY",
        "openweather":  bool(OPENWEATHER_API_KEY)    and OPENWEATHER_API_KEY    != "YOUR_OPENWEATHER_API_KEY",
        "wikipedia":    True,   # No key needed
    }