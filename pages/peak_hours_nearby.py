"""
Peak Hours & Nearby Page
"""
import streamlit as st
from utils.data_handlers import load_peak_hours, get_place_peak_hours

def show():
    st.title("⏰ Peak Hours & Nearby Attractions")
    st.markdown("Find the best times to visit!")
    st.markdown("---")
    
    place_search = st.text_input("🔍 Search Place", placeholder="e.g., Taj Mahal")
    
    if st.button("🔍 Search", type="primary"):
        if place_search:
            info = get_place_peak_hours(place_search)
            if info:
                st.success(f"✅ Found: {info['place']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**✅ Best Time:** {info['best_time']}")
                with col2:
                    st.error(f"**❌ Avoid:** {info['avoid_time']}")
                
                col3, col4 = st.columns(2)
                with col3:
                    st.info(f"**📅 Peak Season:** {info['peak_season']}")
                with col4:
                    st.warning(f"**👥 Crowd:** {info['avg_crowd']}")
            else:
                st.warning("No information found.")
        else:
            st.error("Please enter a place name.")
    
    st.markdown("---")
    st.markdown("## 📋 All Places")
    df = load_peak_hours()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available.")
