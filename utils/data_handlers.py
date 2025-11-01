"""
Data handling functions for local storage
Manages reviews, itineraries, peak hours, and places data
"""
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Data directory
DATA_DIR = "data"

# ============================================
# DIRECTORY MANAGEMENT
# ============================================

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"✅ Created data directory: {DATA_DIR}")

# ============================================
# REVIEWS MANAGEMENT
# ============================================

def load_reviews() -> pd.DataFrame:
    """Load reviews from CSV file"""
    ensure_data_directory()
    reviews_file = os.path.join(DATA_DIR, "reviews.csv")
    
    if os.path.exists(reviews_file):
        try:
            df = pd.read_csv(reviews_file)
            return df
        except Exception as e:
            print(f"Error loading reviews: {e}")
            return _create_empty_reviews_df(reviews_file)
    else:
        return _create_empty_reviews_df(reviews_file)

def _create_empty_reviews_df(file_path: str) -> pd.DataFrame:
    """Create empty reviews DataFrame with schema"""
    df = pd.DataFrame(columns=[
        "place",
        "user_name",
        "rating",
        "comment",
        "date"
    ])
    df.to_csv(file_path, index=False)
    return df

def save_review(place: str, user_name: str, rating: int, comment: str) -> bool:
    """Save a new review"""
    try:
        df = load_reviews()
        new_review = pd.DataFrame([{
            "place": place.strip(),
            "user_name": user_name.strip(),
            "rating": int(rating),
            "comment": comment.strip(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        df = pd.concat([df, new_review], ignore_index=True)
        df.to_csv(os.path.join(DATA_DIR, "reviews.csv"), index=False)
        return True
    except Exception as e:
        print(f"Error saving review: {e}")
        return False

def get_place_reviews(place: str) -> pd.DataFrame:
    """Get reviews for a specific place"""
    df = load_reviews()
    if df.empty:
        return df
    filtered = df[df["place"].str.lower() == place.lower()]
    return filtered

def get_average_rating(place: str) -> Optional[float]:
    """Get average rating for a place"""
    reviews = get_place_reviews(place)
    if reviews.empty:
        return None
    return reviews["rating"].mean()

def get_review_count(place: str) -> int:
    """Get number of reviews for a place"""
    reviews = get_place_reviews(place)
    return len(reviews)

# ============================================
# ITINERARIES MANAGEMENT
# ============================================

def load_itineraries() -> Dict:
    """Load saved itineraries from JSON"""
    ensure_data_directory()
    itineraries_file = os.path.join(DATA_DIR, "itineraries.json")
    
    if os.path.exists(itineraries_file):
        try:
            with open(itineraries_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading itineraries: {e}")
            return _create_empty_itineraries(itineraries_file)
    else:
        return _create_empty_itineraries(itineraries_file)

def _create_empty_itineraries(file_path: str) -> Dict:
    """Create empty itineraries JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({}, f)
    return {}

def save_itinerary(destination: str, days: int, itinerary_data: Dict) -> bool:
    """Save an itinerary"""
    try:
        itineraries = load_itineraries()
        key = f"{destination.lower().replace(' ', '_')}_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        itinerary_data["destination"] = destination
        itinerary_data["days"] = days
        itinerary_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        itineraries[key] = itinerary_data
        
        with open(os.path.join(DATA_DIR, "itineraries.json"), 'w', encoding='utf-8') as f:
            json.dump(itineraries, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving itinerary: {e}")
        return False

def get_saved_itineraries(limit: int = 10) -> List[Dict]:
    """Get list of saved itineraries"""
    itineraries = load_itineraries()
    itinerary_list = []
    for key, data in itineraries.items():
        data["key"] = key
        itinerary_list.append(data)
    itinerary_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return itinerary_list[:limit]

# ============================================
# PEAK HOURS MANAGEMENT
# ============================================

def load_peak_hours() -> pd.DataFrame:
    """Load peak hours data from CSV"""
    ensure_data_directory()
    peak_hours_file = os.path.join(DATA_DIR, "peak_hours.csv")
    
    if os.path.exists(peak_hours_file):
        try:
            df = pd.read_csv(peak_hours_file)
            return df
        except Exception as e:
            print(f"Error loading peak hours: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def get_place_peak_hours(place: str) -> Optional[Dict]:
    """Get peak hours information for a specific place"""
    df = load_peak_hours()
    if df.empty:
        return None
    result = df[df["place"].str.lower().str.contains(place.lower(), na=False)]
    if result.empty:
        return None
    return result.iloc[0].to_dict()

def search_nearby_attractions(place: str, limit: int = 5) -> List[str]:
    """Search for nearby attractions"""
    df = load_peak_hours()
    if df.empty:
        return []
    all_places = df["place"].tolist()
    nearby = [p for p in all_places if p.lower() != place.lower()]
    return nearby[:limit]

# ============================================
# STATISTICS FUNCTIONS
# ============================================

def get_review_statistics() -> Dict:
    """Get overall review statistics"""
    df = load_reviews()
    if df.empty:
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "total_places": 0,
            "top_rated_place": None
        }
    stats = {
        "total_reviews": len(df),
        "average_rating": round(df["rating"].mean(), 2),
        "total_places": df["place"].nunique(),
        "top_rated_place": df.groupby("place")["rating"].mean().idxmax()
    }
    return stats

def get_popular_destinations(limit: int = 5) -> List[tuple]:
    """Get most reviewed destinations"""
    df = load_reviews()
    if df.empty:
        return []
    popular = df["place"].value_counts().head(limit)
    return list(popular.items())

# ============================================
# PLACES MANAGEMENT (NEW)
# ============================================

PLACES_CSV = os.path.join(DATA_DIR, "places.csv")

def load_places():
    """Load tourist places dataset from CSV"""
    if os.path.exists(PLACES_CSV):
        try:
            df = pd.read_csv(PLACES_CSV)
            return df
        except Exception as e:
            print(f"Error loading places data: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def search_places(city: str = None, state: str = None, activity_type: str = None) -> pd.DataFrame:
    """Return places filtered by city, state, and/or activity"""
    df = load_places()
    if df.empty:
        return df
    filtered = df
    if city:
        filtered = filtered[filtered["city"].str.lower() == city.lower()]
    if state:
        filtered = filtered[filtered["state"].str.lower() == state.lower()]
    if activity_type:
        filtered = filtered[
            filtered["activity_type"].str.contains(activity_type, case=False, na=False)
        ]
    return filtered
