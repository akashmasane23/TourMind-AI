"""
Place Recommendations Page
"""
import streamlit as st
from utils.api_handlers import (
    get_unsplash_image,
    get_wikipedia_summary,
    get_google_maps_url
)
from utils.data_handlers import search_places
from config import DEFAULT_RESULTS_LIMIT

def show():
    st.title("🏖️ Tourist Place Recommendations")
    st.markdown("Discover amazing destinations with photos, descriptions, and detailed information!")
    st.markdown("---")
    
    # Search section 
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        city = st.text_input("City Name", placeholder="e.g., Goa", key="city_search")
    with col2:
        state = st.text_input("State Name", placeholder="e.g., Goa", key="state_search")
    with col3:
        num_results = st.selectbox("Results", [3, 5, 10], index=1, key="num_results")
    
    if st.button("🔍 Search Places", type="primary", key="search_btn"):
        if city and state:
            with st.spinner(f"Searching for places in {city}, {state}..."):
                places_df = search_places(city=city, state=state)
                
                if not places_df.empty:
                    st.success(f"✅ Found {len(places_df)} places!")
                    st.markdown("---")
                    
                    for idx, row in places_df.head(num_results).iterrows():
                        col_img, col_info = st.columns([1, 2])
                        with col_img:
                            images = get_unsplash_image(row["place_name"], count=1)
                            if images:
                                st.image(images[0]["url"], use_container_width=True)
                                st.caption(f"📸 {images[0]['photographer']}")

                        with col_info:
                            st.subheader(f"{idx + 1}. {row['place_name']}")
                            st.write(f"**Location:** {row['city']}, {row['state']}")
                            st.write(f"**Keywords:** {row['description_keyword']}, Activity: {row['activity_type']}")
                            st.write(f"**Coordinates:** Latitude {row['latitude']}, Longitude {row['longitude']}")
                            
                            wiki_info = get_wikipedia_summary(row["place_name"])
                            if wiki_info and wiki_info.get("summary"):
                                st.write(wiki_info["summary"])
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if wiki_info.get("url"):
                                        st.link_button("📖 Read More", wiki_info["url"], use_container_width=True)
                                with col_b:
                                    st.link_button("🗺️ View Map", get_google_maps_url(row["place_name"]), use_container_width=True)
                                
                            st.markdown("---")
                else:
                    st.warning("No places found. Try a different city and state.")
        else:
            st.error("Please enter both city and state to search for places.")
