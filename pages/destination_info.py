"""
Destination Info Page
"""
import streamlit as st
from utils.api_handlers import get_weather_forecast, get_unsplash_image, get_wikipedia_summary

def show():
    st.title("🌤️ Destination Information")
    st.markdown("Get weather forecasts, images, and information!")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        destination = st.text_input("🌍 Enter Destination", placeholder="e.g., Paris")
    with col2:
        forecast_days = st.selectbox("Forecast Days", [3, 5], index=1)
    
    if st.button("🔍 Get Info", type="primary"):
        if destination:
            with st.spinner("Loading information..."):
                # Images
                st.markdown("## 📸 Gallery")
                images = get_unsplash_image(destination, count=3)
                if images:
                    cols = st.columns(3)
                    for idx, img in enumerate(images):
                        with cols[idx]:
                            st.image(img["url"], use_container_width=True)
                
                st.markdown("---")
                
                # Weather
                st.markdown("## 🌤️ Weather Forecast")
                weather = get_weather_forecast(destination, days=forecast_days)
                if weather:
                    current = weather["current"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Temperature", f"{current['temp']}°C")
                    with col2:
                        st.metric("Humidity", f"{current['humidity']}%")
                    with col3:
                        st.metric("Wind", f"{current['wind_speed']} m/s")
                    
                    st.markdown("### Forecast")
                    cols = st.columns(len(weather["forecast"]))
                    for idx, day in enumerate(weather["forecast"]):
                        with cols[idx]:
                            st.markdown(f"**{day['date']}**")
                            st.write(f"High: {day['temp_max']}°C")
                            st.write(f"Low: {day['temp_min']}°C")
                            st.write(day['description'])
                else:
                    st.warning("Weather data not available.")
                
                st.markdown("---")
                
                # Wikipedia
                st.markdown("## 📖 About")
                wiki = get_wikipedia_summary(destination)
                if wiki and wiki["exists"]:
                    st.write(wiki["summary"])
                    if wiki["url"]:
                        st.link_button("Read More", wiki["url"])
        else:
            st.error("Please enter a destination.")
