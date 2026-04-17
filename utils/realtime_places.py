"""
TourMind — Nearby Attractions
Used by: pages/peak_hours_nearby.py

Replaced Google Places API with:
  1. Local places.csv database (primary) — Haversine distance calc
  2. Wikipedia + Unsplash enrichment for photos & descriptions
  3. Overpass API fallback (free OpenStreetMap data, no key needed)

get_nearby_attractions(lat, lng) returns same structure as before
so peak_hours_nearby.py needs zero changes.
"""

import math
import requests
import streamlit as st
import pandas as pd
import os
from typing import Optional

# Constants
DATA_DIR    = "data"
PLACES_FILE = os.path.join(DATA_DIR, "places.csv")
ENCODINGS   = ["utf-8", "utf-8-sig", "cp1252", "latin1"]


# ============================================
# HAVERSINE DISTANCE
# ============================================

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two coordinates."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ============================================
# LOAD PLACES CSV
# ============================================

@st.cache_data(ttl=3600)
def _load_places_df() -> pd.DataFrame:
    """Load places.csv with multi-encoding fallback."""
    if not os.path.exists(PLACES_FILE):
        return pd.DataFrame()

    for enc in ENCODINGS:
        try:
            df = pd.read_csv(PLACES_FILE, encoding=enc)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            # Drop rows without coordinates
            df = df.dropna(subset=["latitude", "longitude"])
            df["latitude"]  = pd.to_numeric(df["latitude"],  errors="coerce")
            df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
            df = df.dropna(subset=["latitude", "longitude"])
            return df
        except UnicodeDecodeError:
            continue
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


# ============================================
# UNSPLASH FALLBACK PHOTO
# ============================================

def _get_place_photo(place_name: str) -> str:
    """
    Try Unsplash API for a photo; fall back to Picsum if unavailable.
    Returns a usable image URL.
    """
    try:
        key = st.secrets.get("UNSPLASH_ACCESS_KEY") or st.secrets.get("UNSPLASH_API_KEY")
    except Exception:
        key = None

    if key:
        try:
            resp = requests.get(
                "https://api.unsplash.com/search/photos",
                params={"query": place_name, "per_page": 1, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {key}"},
                timeout=5,
            )
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    return results[0]["urls"]["regular"]
        except Exception:
            pass

    # Deterministic Picsum fallback — no API key needed
    seed = abs(hash(place_name)) % 1000
    return f"https://picsum.photos/seed/{seed}/800/500"


# ============================================
# OVERPASS (OpenStreetMap) FALLBACK
# ============================================

def _get_osm_nearby(
    lat: float, lng: float,
    radius_m: int = 5000,
    limit: int = 6
) -> list[dict]:
    """
    Query OpenStreetMap Overpass API for tourist attractions near a point.
    Free, no API key needed.
    Returns list of place dicts or [] on failure.
    """
    query = f"""
    [out:json][timeout:10];
    (
      node["tourism"="attraction"](around:{radius_m},{lat},{lng});
      node["tourism"="museum"](around:{radius_m},{lat},{lng});
      node["historic"](around:{radius_m},{lat},{lng});
      node["leisure"="park"](around:{radius_m},{lat},{lng});
    );
    out body {limit};
    """
    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=12,
        )
        if resp.status_code != 200:
            return []

        elements = resp.json().get("elements", [])
        results  = []

        for el in elements[:limit]:
            tags  = el.get("tags", {})
            name  = tags.get("name") or tags.get("name:en")
            if not name:
                continue

            el_lat = el.get("lat", lat)
            el_lon = el.get("lon", lng)
            dist   = _haversine_km(lat, lng, el_lat, el_lon)

            results.append({
                "name":     name,
                "rating":   tags.get("stars", "N/A"),
                "vicinity": tags.get("addr:city") or tags.get("addr:suburb") or "Nearby",
                "photo":    _get_place_photo(name),
                "distance_km": round(dist, 2),
                "source":   "OpenStreetMap",
            })

        return sorted(results, key=lambda x: x["distance_km"])

    except Exception:
        return []


# ============================================
# PUBLIC API
# ============================================

def get_nearby_attractions(
    lat: float,
    lng: float,
    radius_km: float = 10.0,
    limit: int = 6,
    exclude_name: Optional[str] = None,
) -> list[dict]:
    """
    Find nearby tourist attractions using local database + OSM fallback.
    Returns same structure as original Google Places version:
      [{"name", "rating", "vicinity", "photo", "distance_km"}, ...]

    Priority order:
      1. Local places.csv  (instant, no API call)
      2. OpenStreetMap Overpass API (free, no key)

    Args:
        lat:          Centre latitude.
        lng:          Centre longitude.
        radius_km:    Search radius in kilometres (default 10 km).
        limit:        Max results to return (default 6).
        exclude_name: Optionally exclude the place being searched itself.
    """
    results = []

    # ── 1. Local database ─────────────────────
    df = _load_places_df()

    if not df.empty:
        df = df.copy()
        df["distance_km"] = df.apply(
            lambda r: _haversine_km(lat, lng, r["latitude"], r["longitude"]),
            axis=1
        )

        nearby = df[df["distance_km"] <= radius_km].copy()

        # Exclude the source place itself if provided
        if exclude_name and "place_name" in nearby.columns:
            nearby = nearby[
                nearby["place_name"].str.lower() != exclude_name.lower()
            ]

        nearby = nearby.sort_values("distance_km").head(limit)

        for _, row in nearby.iterrows():
            name = row.get("place_name", "Unknown")
            results.append({
                "name":        name,
                "rating":      row.get("rating", "N/A"),
                "vicinity":    f"{row.get('city', '')}, {row.get('state', '')}".strip(", "),
                "photo":       _get_place_photo(name),
                "distance_km": round(row["distance_km"], 2),
                "activity":    row.get("activity_type", ""),
                "source":      "Local Database",
            })

    # ── 2. OSM fallback if local DB has < 3 results ──
    if len(results) < 3:
        osm_results = _get_osm_nearby(lat, lng, radius_m=int(radius_km * 1000), limit=limit)

        # Merge, avoiding duplicates by name
        existing_names = {r["name"].lower() for r in results}
        for place in osm_results:
            if place["name"].lower() not in existing_names:
                results.append(place)
                existing_names.add(place["name"].lower())

        results = results[:limit]

    return results