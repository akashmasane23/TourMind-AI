"""
API handler functions for external services
Handles Unsplash, OpenWeatherMap, and Wikipedia APIs
"""
import requests
import streamlit as st
import wikipediaapi
from typing import Optional, Dict, List
from config import *

# ============================================
# UNSPLASH API - IMAGE FETCHING
# ============================================

@st.cache_data(ttl=CACHE_TTL_LONG)
def get_unsplash_image(query: str, count: int = 1) -> List[Dict]:
    """
    Fetch images from Unsplash API with fallback
    
    Args:
        query: Search query for images
        count: Number of images to fetch (default: 1)
        
    Returns:
        List of image dictionaries with URLs and metadata
    """
    try:
        # Check if API key is configured
        if UNSPLASH_ACCESS_KEY == "YOUR_UNSPLASH_ACCESS_KEY":
            st.warning("⚠️ Unsplash API key not configured. Using fallback image source.")
            # Return fallback using Unsplash Source (no API key needed)
            return [{
                "url": f"https://source.unsplash.com/800x600/?{query.replace(' ', ',')}",
                "alt": query,
                "photographer": "Unsplash",
                "photographer_url": "https://unsplash.com"
            }]
        
        # Make API request
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape"
        }
        
        response = requests.get(
            UNSPLASH_API_URL,
            headers=headers,
            params=params,
            timeout=10
        )
        
        # Check response status
        if response.status_code == 200:
            data = response.json()
            images = []
            
            for result in data.get("results", [])[:count]:
                images.append({
                    "url": result["urls"]["regular"],
                    "alt": result.get("alt_description", query),
                    "photographer": result["user"]["name"],
                    "photographer_url": result["user"]["links"]["html"]
                })
            
            if images:
                return images
            else:
                # No results found, use fallback
                return [{
                    "url": f"https://source.unsplash.com/800x600/?{query.replace(' ', ',')}",
                    "alt": query,
                    "photographer": "Unsplash",
                    "photographer_url": "https://unsplash.com"
                }]
        
        elif response.status_code == 401:
            st.error("❌ Invalid Unsplash API key. Please check your config.py")
            return []
        
        elif response.status_code == 403:
            st.error("⚠️ Unsplash API rate limit exceeded. Try again later.")
            return [{
                "url": f"https://source.unsplash.com/800x600/?{query.replace(' ', ',')}",
                "alt": query,
                "photographer": "Unsplash",
                "photographer_url": "https://unsplash.com"
            }]
        
        else:
            st.warning(f"⚠️ Unsplash API error: {response.status_code}")
            return []
            
    except requests.exceptions.Timeout:
        st.warning("⏱️ Image request timed out. Please try again.")
        return []
    
    except requests.exceptions.RequestException as e:
        st.warning(f"🌐 Network error: {str(e)}")
        return []
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return []


# ============================================
# WIKIPEDIA API - PLACE INFORMATION
# ============================================

@st.cache_data(ttl=CACHE_TTL_LONG)
def get_wikipedia_summary(place_name: str) -> Optional[Dict]:
    """
    Fetch Wikipedia summary for a place
    
    Args:
        place_name: Name of the place
        
    Returns:
        Dictionary with title, summary, and URL
    """
    try:
        # Initialize Wikipedia API (no key required!)
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=WIKI_USER_AGENT,
            language=WIKI_LANGUAGE
        )
        
        # Get page
        page = wiki_wiki.page(place_name)
        
        if page.exists():
            # Truncate summary to 500 characters
            summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
            
            return {
                "title": page.title,
                "summary": summary,
                "url": page.fullurl,
                "exists": True
            }
        else:
            # Page doesn't exist
            return {
                "title": place_name,
                "summary": f"No detailed information available for {place_name} on Wikipedia.",
                "url": None,
                "exists": False
            }
    
    except Exception as e:
        return {
            "title": place_name,
            "summary": f"Unable to fetch Wikipedia information: {str(e)}",
            "url": None,
            "exists": False
        }


@st.cache_data(ttl=CACHE_TTL_LONG)
def search_wikipedia_places(query: str, max_results: int = 10) -> List[str]:
    """
    Search Wikipedia for places matching query
    
    Args:
        query: Search query (city/state name)
        max_results: Maximum number of results
        
    Returns:
        List of Wikipedia page titles
    """
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=WIKI_USER_AGENT,
            language=WIKI_LANGUAGE
        )
        
        # Search Wikipedia
        import wikipedia
        wikipedia.set_lang(WIKI_LANGUAGE)
        
        search_results = wikipedia.search(query, results=max_results)
        
        # Filter for places/locations (basic filtering)
        places = []
        for result in search_results:
            # Add all results, could be enhanced with filtering
            places.append(result)
        
        return places[:max_results]
    
    except Exception as e:
        st.warning(f"Wikipedia search error: {str(e)}")
        return []


# ============================================
# OPENWEATHERMAP API - WEATHER FORECAST
# ============================================

@st.cache_data(ttl=CACHE_TTL_SHORT)
def get_weather_forecast(city: str, days: int = 5) -> Optional[Dict]:
    """
    Fetch weather forecast from OpenWeatherMap
    
    Args:
        city: City name
        days: Number of days for forecast (max 5 for free tier)
        
    Returns:
        Dictionary with current and forecast weather data
    """
    try:
        # Check if API key is configured
        if OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
            st.warning("⚠️ OpenWeatherMap API key not configured. Please add your API key in config.py")
            return None
        
        # Current weather
        current_url = f"{OPENWEATHER_API_URL}/weather"
        current_params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        current_response = requests.get(
            current_url,
            params=current_params,
            timeout=10
        )
        
        # Forecast weather
        forecast_url = f"{OPENWEATHER_API_URL}/forecast"
        forecast_params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": min(days * 8, 40)  # API returns 3-hour intervals
        }
        
        forecast_response = requests.get(
            forecast_url,
            params=forecast_params,
            timeout=10
        )
        
        # Check responses
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            
            # Process current weather
            current_weather = {
                "temp": round(current_data["main"]["temp"], 1),
                "feels_like": round(current_data["main"]["feels_like"], 1),
                "description": current_data["weather"][0]["description"].capitalize(),
                "humidity": current_data["main"]["humidity"],
                "wind_speed": round(current_data["wind"]["speed"], 1),
                "pressure": current_data["main"]["pressure"],
                "icon": current_data["weather"][0]["icon"],
                "city": current_data["name"],
                "country": current_data["sys"]["country"]
            }
            
            # Process forecast (daily aggregation)
            daily_forecast = []
            processed_dates = set()
            
            for item in forecast_data["list"]:
                date = item["dt_txt"].split()[0]
                
                if date not in processed_dates:
                    daily_forecast.append({
                        "date": date,
                        "temp_max": round(item["main"]["temp_max"], 1),
                        "temp_min": round(item["main"]["temp_min"], 1),
                        "description": item["weather"][0]["description"].capitalize(),
                        "humidity": item["main"]["humidity"],
                        "wind_speed": round(item["wind"]["speed"], 1),
                        "icon": item["weather"][0]["icon"]
                    })
                    processed_dates.add(date)
                
                if len(daily_forecast) >= days:
                    break
            
            return {
                "current": current_weather,
                "forecast": daily_forecast,
                "success": True
            }
        
        elif current_response.status_code == 401:
            st.error("❌ Invalid OpenWeatherMap API key. Please check your config.py")
            return None
        
        elif current_response.status_code == 404:
            st.error(f"❌ City '{city}' not found. Please check the spelling.")
            return None
        
        elif current_response.status_code == 429:
            st.error("⚠️ API rate limit exceeded. Please try again later.")
            return None
        
        else:
            st.warning(f"⚠️ Weather API error: {current_response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning("⏱️ Weather request timed out. Please try again.")
        return None
    
    except requests.exceptions.RequestException as e:
        st.warning(f"🌐 Network error: {str(e)}")
        return None
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None


# ============================================
# CHATBOT - RULE-BASED RESPONSE
# ============================================

def get_chatbot_response(user_message: str) -> str:
    """
    Generate chatbot response using rule-based system
    
    Args:
        user_message: User's question
        
    Returns:
        Bot response string
    """
    message_lower = user_message.lower()
    
    # Check for keywords in user message
    for keyword, response in CHATBOT_KEYWORDS.items():
        if keyword in message_lower:
            return response
    
    # Default response if no keyword matched
    return DEFAULT_CHATBOT_RESPONSE


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_weather_icon_url(icon_code: str) -> str:
    """Get OpenWeatherMap icon URL"""
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


def format_temperature(temp: float, unit: str = "C") -> str:
    """Format temperature with unit"""
    return f"{temp}°{unit}"


def get_google_maps_url(place_name: str) -> str:
    """Generate Google Maps search URL"""
    query = place_name.replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={query}"
