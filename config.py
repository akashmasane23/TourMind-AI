"""
Configuration file - Uses Streamlit secrets for API keys
TourMind Pro - Secure Configuration
"""
import streamlit as st

# ============================================
# SECURE API KEY LOADING
# ============================================

def get_api_key(secret_path, fallback=""):
    """
    Load API key from Streamlit secrets
    Falls back to placeholder if secrets not found
    """
    try:
        keys = st.secrets
        for key in secret_path.split("."):
            keys = keys[key]
        return keys
    except (KeyError, FileNotFoundError, AttributeError):
        return fallback

# Load API keys from secrets.toml
UNSPLASH_ACCESS_KEY = get_api_key("api_keys.unsplash_access_key", "YOUR_UNSPLASH_ACCESS_KEY")
OPENWEATHER_API_KEY = get_api_key("api_keys.openweather_api_key", "YOUR_OPENWEATHER_API_KEY")
OPENAI_API_KEY = get_api_key("api_keys.openai_api_key", "")

# ============================================
# API ENDPOINTS
# ============================================

UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# ============================================
# APP SETTINGS
# ============================================

APP_TITLE = "TourMind Pro"
APP_ICON = "🌍"
APP_VERSION = "1.0.0"
DEFAULT_RESULTS_LIMIT = 5

# ============================================
# WIKIPEDIA SETTINGS
# ============================================

WIKI_USER_AGENT = "TourMindPro/1.0 (tourmind@example.com)"
WIKI_LANGUAGE = "en"

# ============================================
# TIME SLOTS FOR PEAK HOURS
# ============================================

TIME_SLOTS = [
    "Early Morning (5-8 AM)", 
    "Morning (8-11 AM)", 
    "Afternoon (11-2 PM)", 
    "Evening (2-6 PM)", 
    "Night (6-10 PM)"
]

# ============================================
# TRIP TYPES AND PREFERENCES
# ============================================

TRIP_TYPES = [
    "Relaxation",
    "Adventure", 
    "Cultural",
    "Family",
    "Solo",
    "Romantic",
    "Business",
    "Spiritual"
]

TRAVEL_PREFERENCES = [
    "Historical Sites",
    "Beaches",
    "Mountains",
    "Food Tours",
    "Shopping",
    "Wildlife",
    "Photography",
    "Nightlife",
    "Spiritual",
    "Architecture",
    "Museums",
    "Adventure Sports"
]

# ============================================
# RATING CONFIGURATION
# ============================================

MIN_RATING = 1
MAX_RATING = 5
RATING_LABELS = {
    1: "😞 Poor",
    2: "😐 Fair",
    3: "🙂 Good",
    4: "😊 Very Good",
    5: "😍 Excellent"
}

# ============================================
# MAP CONFIGURATION
# ============================================

DEFAULT_MAP_ZOOM = 12
MAP_TILE_STYLE = "OpenStreetMap"

# ============================================
# CHATBOT RESPONSES (RULE-BASED)
# ============================================

CHATBOT_KEYWORDS = {
    "weather": "I can help you check the weather! 🌤️ Go to the 'Destination Info' page and enter a city name to see current weather and 5-day forecasts.",
    
    "itinerary": "Planning a trip? 🗓️ Visit the 'Itinerary Planner' page and enter your destination, number of days, and travel preferences. I'll create a personalized day-by-day plan for you!",
    
    "place": "Looking for tourist places? 🏖️ Head to the 'Place Recommendations' page. Search by city or state to discover amazing destinations with photos and details!",
    
    "review": "Want to see reviews? ⭐ Check the 'Reviews and Ratings' page to read experiences from other travelers or leave your own review and rating.",
    
    "peak": "To find the best time to visit a place ⏰ go to the 'Peak Hours & Nearby' page. You'll see best visiting times, times to avoid crowds, peak seasons, and nearby attractions.",
    
    "hello": "Hello! 👋 I'm your TourMind assistant. How can I help you plan your perfect trip today? Ask me about places, weather, itineraries, reviews, or best visiting times!",
    
    "help": "I can assist with: 🏖️ Finding tourist places | 🗓️ Planning itineraries | 🌤️ Checking weather | ⭐ Reading reviews | ⏰ Best visiting times | 💬 Travel tips. What would you like to know?",
    
    "thanks": "You're welcome! 😊 Happy to help with your travel plans! Have a wonderful trip! 🌍✈️"
}

DEFAULT_CHATBOT_RESPONSE = "I'm here to help with your travel planning! 🌍 Try asking about weather forecasts, places to visit, trip itineraries, user reviews, or best times to visit attractions."

# ============================================
# UI/UX SETTINGS
# ============================================

IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 300

ITEMS_PER_PAGE = 10

CACHE_TTL_SHORT = 1800   # 30 minutes
CACHE_TTL_LONG = 3600    # 1 hour

# ============================================
# ERROR MESSAGES
# ============================================

ERROR_MESSAGES = {
    "api_key_missing": "⚠️ API key not configured. Please add your API key in .streamlit/secrets.toml",
    "api_error": "⚠️ API request failed. Please try again later.",
    "no_results": "😔 No results found. Try a different search term.",
    "network_error": "🌐 Network error. Please check your connection.",
    "invalid_input": "❌ Invalid input. Please check your entry and try again."
}

SUCCESS_MESSAGES = {
    "review_saved": "✅ Thank you! Your review has been submitted successfully.",
    "itinerary_saved": "✅ Itinerary saved successfully!",
    "data_loaded": "✅ Data loaded successfully!"
}

HELP_TEXT = {
    "place_search": "Enter a city or state name to discover tourist attractions. Examples: Goa, Rajasthan, Mumbai",
    "review_rating": "Rate your experience from 1-5 stars. Be honest and helpful for other travelers!",
    "itinerary_days": "Select the number of days for your trip (1-14 days)",
    "weather_forecast": "Enter a city name to see current weather and 5-day forecast",
    "peak_hours": "Find the best times to visit popular attractions and avoid crowds"
}

# ============================================
# API SETUP INSTRUCTIONS
# ============================================

API_SETUP_INSTRUCTIONS = """
### 🔑 How to Get Free API Keys

#### 1. Unsplash API (Images) - Required
- Visit: https://unsplash.com/developers
- Sign up / Log in
- Click "New Application"
- Accept terms and fill in details
- Copy your Access Key
- Paste in .streamlit/secrets.toml
- Free tier: 50 requests/hour

#### 2. OpenWeatherMap API (Weather) - Required
- Visit: https://openweathermap.org/appid
- Sign up / Log in
- Check email for API key
- Copy your API key
- Paste in .streamlit/secrets.toml
- Free tier: 1000 calls/day

#### 3. Wikipedia API - No Key Needed ✅
- Already configured and ready to use!

#### 4. OpenAI API (Chatbot) - Optional
- Visit: https://platform.openai.com/api-keys
- Note: OPTIONAL - app has free rule-based chatbot
"""

# ============================================
# HELPER FUNCTIONS
# ============================================

def check_api_keys():
    """Check which API keys are configured"""
    status = {
        "unsplash": UNSPLASH_ACCESS_KEY != "YOUR_UNSPLASH_ACCESS_KEY" and UNSPLASH_ACCESS_KEY != "",
        "openweather": OPENWEATHER_API_KEY != "YOUR_OPENWEATHER_API_KEY" and OPENWEATHER_API_KEY != "",
        "openai": OPENAI_API_KEY != "" and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY",
        "wikipedia": True  # Always available
    }
    return status

def get_missing_keys():
    """Get list of missing API keys"""
    status = check_api_keys()
    missing = []
    if not status["unsplash"]:
        missing.append("Unsplash (for images)")
    if not status["openweather"]:
        missing.append("OpenWeatherMap (for weather)")
    return missing
