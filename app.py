"""
TourMind Pro - Main Application with Horizontal Navbar
Complete version with all features
"""

import streamlit as st
from streamlit_option_menu import option_menu
from config import *
from utils.api_handlers import get_wikipedia_summary
from utils.data_handlers import (
    ensure_data_directory,
    get_review_statistics,
    get_popular_destinations
)

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/yourusername/tourmind-pro',
        'Report a bug': 'https://github.com/yourusername/tourmind-pro/issues',
        'About': f"""
        # {APP_TITLE} {APP_VERSION}
        
        Your ultimate travel companion for discovering, planning, and 
        enjoying your travels with intelligent recommendations and 
        real-time information.
        
        Built with ❤️ using Streamlit
        """
    }
)

# ============================================
# CUSTOM CSS STYLING
# ============================================

st.markdown("""
    <style>
    /* Hide default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main content area */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #FF6B6B;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom headers */
    h1 {
        color: #FF4B4B;
        padding-bottom: 10px;
        border-bottom: 3px solid #FF4B4B;
    }
    
    h2 {
        color: #333;
        margin-top: 20px;
    }
    
    h3 {
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# INITIALIZE
# ============================================

ensure_data_directory()

# ============================================
# HORIZONTAL NAVIGATION BAR
# ============================================

selected = option_menu(
    menu_title=None,
    options=["Home", "Places", "Reviews", "Itinerary", "Chatbot", "Weather", "Peak Hours"],
    icons=["house", "map", "star", "calendar", "chat", "cloud-sun", "clock"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#262730"},
        "icon": {"color": "white", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "padding": "10px 15px",
            "color": "white",
            "--hover-color": "#FF4B4B"
        },
        "nav-link-selected": {"background-color": "#FF4B4B"},
    }
)

st.markdown("---")

# ============================================
# PAGE ROUTING
# ============================================

if selected == "Home":
    # HOME PAGE CONTENT
    st.title(f"{APP_ICON} Welcome to {APP_TITLE}")
    st.markdown("### 🌏 Your Ultimate Travel Companion")
    
    st.markdown("""
    Welcome to **TourMind Pro**, your comprehensive tourist guide application! 
    Discover amazing destinations, plan perfect itineraries, check real-time weather, 
    read authentic reviews, and find the best times to visit popular attractions.
    """)
    
    st.markdown("---")
    
    # API Status Check
    api_status = check_api_keys()
    missing_keys = get_missing_keys()
    
    if missing_keys:
        with st.expander("⚠️ API Configuration Required - Click to Setup", expanded=False):
            st.warning("Some API keys are not configured. The app will work with limited functionality.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Missing Keys:")
                for key in missing_keys:
                    st.markdown(f"- ❌ {key}")
            
            with col2:
                st.markdown("#### Configured Keys:")
                if api_status["unsplash"]:
                    st.markdown("- ✅ Unsplash API")
                if api_status["openweather"]:
                    st.markdown("- ✅ OpenWeatherMap API")
                st.markdown("- ✅ Wikipedia API (no key needed)")
            
            st.markdown("---")
            st.info("""
            **Quick Setup Instructions:**
            
            1. Open `.streamlit/secrets.toml` in your text editor
            2. Add your API keys in the correct format
            3. Save the file and restart the app
            
            Get free API keys:
            - **Unsplash**: https://unsplash.com/developers
            - **OpenWeatherMap**: https://openweathermap.org/appid
            """)
    
    # Feature Showcase - UPDATED WITH NATIVE STREAMLIT COMPONENTS
    st.markdown("## 🎯 Explore Our Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🏖️ **Place Recommendations**\n\nDiscover top tourist destinations with stunning photos, detailed Wikipedia information, and Google Maps integration.")
        
        st.markdown("")  # Spacer
        
        st.warning("⭐ **Reviews & Ratings**\n\nRead authentic experiences from fellow travelers and share your own reviews to help the community.")
    
    with col2:
        st.success("🗓️ **Itinerary Planner**\n\nCreate personalized day-by-day travel plans based on your preferences and trip duration.")
        
        st.markdown("")  # Spacer
        
        st.error("💬 **Chatbot Assistant**\n\nGet instant answers to your travel questions with our intelligent AI-powered assistant.")
    
    with col3:
        st.info("🌤️ **Destination Info**\n\nCheck real-time weather forecasts, view destination images, and read comprehensive Wikipedia articles.")
        
        st.markdown("")  # Spacer
        
        st.warning("⏰ **Peak Hours & Nearby**\n\nFind the best times to visit attractions, avoid crowds, and discover nearby hidden gems.")
    
    st.markdown("---")
    
    # Statistics
    st.markdown("## 📊 App Statistics")
    
    stats = get_review_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Reviews",
            value=stats["total_reviews"],
            delta="Growing daily" if stats["total_reviews"] > 0 else None
        )
    
    with col2:
        st.metric(
            label="Average Rating",
            value=f"{stats['average_rating']}⭐" if stats["total_reviews"] > 0 else "N/A"
        )
    
    with col3:
        st.metric(
            label="Places Reviewed",
            value=stats["total_places"]
        )
    
    with col4:
        st.metric(
            label="API Status",
            value="Active" if api_status["unsplash"] and api_status["openweather"] else "Limited"
        )
    
    st.markdown("---")
    
    # Popular Destinations
    st.markdown("## 🔥 Trending Destinations")
    
    popular = get_popular_destinations(limit=5)
    
    if popular:
        cols = st.columns(min(5, len(popular)))
        for idx, (place, count) in enumerate(popular):
            with cols[idx]:
                st.markdown(f"""
                <div style='text-align: center; padding: 15px; background-color: #f8f9fa; 
                            border-radius: 10px; border: 2px solid #FF4B4B;'>
                    <h4 style='margin: 0; color: #FF4B4B;'>{place}</h4>
                    <p style='margin: 5px 0; color: #666;'>{count} reviews</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No reviews yet. Be the first to share your travel experiences!")
    
    st.markdown("---")
    
    # Getting Started
    st.markdown("## 🚀 Getting Started")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### How to Use TourMind Pro:
        
        1. **🏖️ Discover Places**: Click "Places" in the navbar to search for destinations
        2. **⭐ Read Reviews**: Visit "Reviews" to see traveler experiences
        3. **🗓️ Plan Your Trip**: Use "Itinerary" to create travel schedules
        4. **🌤️ Check Weather**: Go to "Weather" for real-time forecasts
        5. **⏰ Optimize Timing**: Click "Peak Hours" for best visiting times
        6. **💬 Ask Questions**: Use "Chatbot" for instant travel advice
        
        ### Tips for Best Experience:
        - 📍 Use specific city or state names for better results
        - ⭐ Leave reviews to help fellow travelers
        - 🔑 Configure API keys for full functionality
        - 🗺️ Use Google Maps integration for navigation
        """)
    
    with col2:
        st.info("""
        **💡 Navigation:**
        
        Use the horizontal navbar 
        at the top to switch between 
        different features.
        """)
        
        st.success("""
        **✅ Ready to Explore!**
        
        Click any option in the 
        navbar above to start your 
        travel planning journey.
        """)
    
    st.markdown("---")
    
    # Featured Destination
    st.markdown("## 🌟 Featured Destination")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://source.unsplash.com/800x600/?taj,mahal", use_container_width=True)
    
    with col2:
        st.markdown("### Taj Mahal, Agra")
        taj_info = get_wikipedia_summary("Taj Mahal")
        if taj_info and taj_info["exists"]:
            st.write(taj_info["summary"])
            if taj_info["url"]:
                st.link_button("📖 Read More", taj_info["url"], use_container_width=True)
        else:
            st.write("One of the Seven Wonders of the World, a symbol of love and architectural brilliance.")
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='color: #666; font-size: 14px;'>
            Made with ❤️ for travelers around the world | 
            © 2025 TourMind Pro
        </p>
    </div>
    """, unsafe_allow_html=True)

elif selected == "Places":
    from pages import place_recommendations
    place_recommendations.show()

elif selected == "Reviews":
    from pages import reviews_and_ratings
    reviews_and_ratings.show()

elif selected == "Itinerary":
    from pages import itinerary_planner
    itinerary_planner.show()

elif selected == "Chatbot":
    from pages import chatbot_assistant
    chatbot_assistant.show()

elif selected == "Weather":
    from pages import destination_info
    destination_info.show()

elif selected == "Peak Hours":
    from pages import peak_hours_nearby
    peak_hours_nearby.show()
