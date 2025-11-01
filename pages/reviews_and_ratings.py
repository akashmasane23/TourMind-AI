"""
Reviews and Ratings Page
"""
import streamlit as st
from utils.data_handlers import load_reviews, save_review, get_review_statistics
from config import RATING_LABELS

def show():
    st.title("⭐ Reviews and Ratings")
    st.markdown("Share your experiences and read what others have to say!")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Submit Review", "📖 View Reviews"])
    
    with tab1:
        st.markdown("### Share Your Experience")
        
        with st.form("review_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                place_name = st.text_input("Place Name *", placeholder="e.g., Taj Mahal")
                user_name = st.text_input("Your Name *", placeholder="Your name")
            
            with col2:
                rating = st.select_slider(
                    "Rating *",
                    options=[1, 2, 3, 4, 5],
                    value=5,
                    format_func=lambda x: f"{'⭐' * x}"
                )
            
            comment = st.text_area("Your Review *", placeholder="Share your experience...", height=150)
            
            if st.form_submit_button("✅ Submit Review", type="primary"):
                if place_name and user_name and comment:
                    if save_review(place_name, user_name, rating, comment):
                        st.success("✅ Review submitted successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to save review.")
                else:
                    st.error("Please fill all fields.")
    
    with tab2:
        st.markdown("### Browse Reviews")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_place = st.text_input("Search by Place", key="search_reviews")
        with col2:
            min_rating = st.selectbox("Min Rating", [1, 2, 3, 4, 5], key="min_rating")
        with col3:
            sort_by = st.selectbox("Sort", ["Latest", "Highest Rated", "Lowest Rated"], key="sort_reviews")
        
        all_reviews = load_reviews()
        
        if not all_reviews.empty:
            filtered = all_reviews.copy()
            
            if search_place:
                filtered = filtered[filtered["place"].str.contains(search_place, case=False, na=False)]
            
            filtered = filtered[filtered["rating"] >= min_rating]
            
            if sort_by == "Highest Rated":
                filtered = filtered.sort_values("rating", ascending=False)
            elif sort_by == "Lowest Rated":
                filtered = filtered.sort_values("rating", ascending=True)
            else:
                filtered = filtered.sort_values("date", ascending=False)
            
            if not filtered.empty:
                st.markdown("---")
                for idx, row in filtered.iterrows():
                    with st.expander(f"📍 {row['place']} - {'⭐' * int(row['rating'])}", expanded=False):
                        st.markdown(f"**👤 {row['user_name']}** • {row['date']}")
                        st.write(row['comment'])
            else:
                st.info("No reviews match your criteria.")
        else:
            st.info("No reviews yet. Be the first!")
