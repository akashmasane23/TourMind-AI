"""
Itinerary Planner Page
"""
import streamlit as st
from utils.api_handlers import search_wikipedia_places, get_wikipedia_summary
from utils.data_handlers import save_itinerary
from config import TRIP_TYPES, TRAVEL_PREFERENCES
import random

def show():
    st.title("🗓️ Smart Itinerary Planner")
    st.markdown("Plan your perfect trip with personalized itineraries!")
    st.markdown("---")
    
    with st.form("itinerary_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            destination = st.text_input("Destination *", placeholder="e.g., Paris")
        with col2:
            num_days = st.slider("Days", 1, 14, 3)
        with col3:
            trip_type = st.selectbox("Trip Type", TRIP_TYPES)
        
        preferences = st.multiselect("Preferences (Optional)", TRAVEL_PREFERENCES)
        
        if st.form_submit_button("🎯 Generate Itinerary", type="primary"):
            if destination:
                with st.spinner(f"Creating {num_days}-day itinerary..."):
                    places = search_wikipedia_places(destination, max_results=15)
                    
                    if not places:
                        places = [f"{destination} Landmark {i}" for i in range(1, 10)]
                    
                    st.success(f"✅ {num_days}-Day Itinerary Created!")
                    st.markdown("---")
                    
                    for day in range(1, num_days + 1):
                        with st.expander(f"📅 Day {day}", expanded=day==1):
                            st.markdown(f"### Day {day}")
                            
                            day_places = places[(day-1)*2:(day-1)*2+2] if len(places) > (day-1)*2 else random.sample(places, min(2, len(places)))
                            
                            st.markdown("#### 🌅 Morning")
                            if day_places:
                                st.markdown(f"**Visit:** {day_places[0]}")
                            
                            st.markdown("#### ☀️ Afternoon")
                            if len(day_places) > 1:
                                st.markdown(f"**Explore:** {day_places[1]}")
                            st.markdown("🍽️ Lunch break")
                            
                            st.markdown("#### 🌆 Evening")
                            st.markdown(f"Sunset viewing and local exploration")
                            
                            st.markdown("#### 💡 Tips")
                            st.markdown("- Start early\n- Book tickets online\n- Try local food")
            else:
                st.error("Please enter a destination.")
