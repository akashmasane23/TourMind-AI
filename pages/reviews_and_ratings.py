"""
Reviews and Ratings Page — Travel/Nature Theme
"""
import streamlit as st
from utils.data_handlers import load_reviews, save_review, get_review_statistics
from config import RATING_LABELS


def show():

    # ============================================
    # STYLES
    # ============================================

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Nunito:wght@400;600;700&display=swap');

    /* ── Hero ── */
    .tm-rev-hero {
        background: linear-gradient(135deg,
            rgba(139,110,71,0.88) 0%,
            rgba(74,124,89,0.82) 50%,
            rgba(45,80,22,0.88) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(139,110,71,0.22);
        position: relative; overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }
    .tm-rev-hero::after {
        content: "⭐";
        position: absolute; right: 2.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 5.5rem; opacity: 0.10;
        pointer-events: none;
    }
    .tm-rev-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important; border: none !important;
        padding: 0 !important; margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .tm-rev-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem; margin: 0; line-height: 1.6;
    }
    .tm-rev-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(244,185,66,0.22);
        border: 1px solid rgba(244,185,66,0.45);
        color: #F4B942;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 1.8px; text-transform: uppercase;
        padding: 4px 14px; border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── Stats bar ── */
    .tm-stats-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem; margin-bottom: 1.6rem;
        animation: fadeUp 0.5s 0.1s both;
    }
    .tm-stat-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 16px; padding: 1.1rem 1rem;
        text-align: center;
        box-shadow: 0 3px 14px rgba(44,36,22,0.08);
        backdrop-filter: blur(6px);
        transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.22s;
    }
    .tm-stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(44,36,22,0.13); }
    .tm-stat-val {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.9rem; font-weight: 700;
        color: #2D5016; margin: 0 0 0.2rem;
        line-height: 1;
    }
    .tm-stat-lbl {
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem; font-weight: 700;
        color: #8B7355; text-transform: uppercase;
        letter-spacing: 1.2px; margin: 0;
    }

    /* ── Tabs ── */
    [data-baseweb="tab-list"] {
        background: rgba(200,221,212,0.35) !important;
        border-radius: 14px !important;
        padding: 4px !important; gap: 4px !important;
        border: 1.5px solid rgba(74,124,89,0.15) !important;
    }
    [data-baseweb="tab"] {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important; font-size: 0.92rem !important;
        color: #5C4A32 !important;
        border-radius: 10px !important;
        padding: 8px 24px !important;
        transition: all 0.2s ease !important;
    }
    [aria-selected="true"] {
        background: linear-gradient(135deg, #4A7C59, #2D5016) !important;
        color: #fff !important;
        box-shadow: 0 4px 14px rgba(45,80,22,0.28) !important;
    }

    /* ── All labels black ── */
    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p,
    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] label p,
    [data-testid="stTextArea"] label,
    [data-testid="stTextArea"] label p,
    [data-testid="stSlider"] label,
    [data-testid="stSlider"] label p {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important; font-weight: 700 !important;
        opacity: 1 !important;
    }

    /* ── Inputs ── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        color: #1a1a1a !important; background: #fff !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.95rem !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(74,124,89,0.28) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #999 !important; font-style: italic !important; opacity: 1 !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #4A7C59 !important;
        box-shadow: 0 0 0 3px rgba(74,124,89,0.15) !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #fff !important; border-radius: 12px !important;
        border: 1.5px solid rgba(74,124,89,0.28) !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSelectbox"] span { color: #1a1a1a !important; }

    /* ── Form card ── */
    .tm-form-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.16);
        border-radius: 20px; padding: 1.8rem 2rem;
        box-shadow: 0 4px 22px rgba(44,36,22,0.09);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        animation: fadeUp 0.5s 0.1s both;
    }

    /* ── Submit button ── */
    [data-testid="stFormSubmitButton"] button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important; font-size: 1rem !important;
        width: 100% !important; border-radius: 14px !important;
        height: 3.2em !important;
        background: linear-gradient(135deg, #4A7C59 0%, #2D5016 100%) !important;
        color: #fff !important; border: none !important;
        box-shadow: 0 6px 22px rgba(45,80,22,0.32) !important;
        transition: all 0.28s cubic-bezier(0.34,1.56,0.64,1) !important;
        margin-top: 0.6rem !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #5A8E6A 0%, #3A6028 100%) !important;
        box-shadow: 0 10px 30px rgba(45,80,22,0.40) !important;
        transform: translateY(-3px) scale(1.01) !important;
    }

    /* ── Star slider ── */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background: #C9A96E !important;
        border-color: #8B6E47 !important;
        width: 22px !important; height: 22px !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
        font-family: 'Nunito', sans-serif !important;
        font-size: 1rem !important; font-weight: 700 !important;
        color: #8B6E47 !important;
    }

    /* ── Review card ── */
    .tm-review-card {
        background: rgba(250,247,240,0.95);
        border: 1.5px solid rgba(74,124,89,0.14);
        border-radius: 18px; padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 16px rgba(44,36,22,0.08);
        backdrop-filter: blur(8px);
        transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s, border-color 0.22s;
        animation: fadeUp 0.5s both;
        position: relative; overflow: hidden;
    }
    .tm-review-card::before {
        content: "";
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #C9A96E, #4A7C59, #2E86AB);
        border-radius: 18px 18px 0 0;
    }
    .tm-review-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(44,36,22,0.14);
        border-color: rgba(74,124,89,0.28);
    }
    .tm-review-place {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.1rem; font-weight: 700;
        color: #2D5016; margin: 0 0 0.35rem;
    }
    .tm-review-meta {
        display: flex; align-items: center; gap: 10px;
        flex-wrap: wrap; margin-bottom: 0.7rem;
    }
    .tm-review-user {
        font-family: 'Nunito', sans-serif;
        font-size: 0.85rem; font-weight: 700;
        color: #4A7C59;
    }
    .tm-review-date {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem; color: #8B7355;
    }
    .tm-review-stars {
        font-size: 0.92rem; letter-spacing: 1px;
    }
    .tm-review-comment {
        font-family: 'Nunito', sans-serif;
        font-size: 0.92rem; color: #3A2E1E;
        line-height: 1.7; margin: 0;
        padding: 0.8rem 1rem;
        background: linear-gradient(135deg,
            rgba(232,213,163,0.15), rgba(200,221,212,0.12));
        border-left: 3px solid rgba(74,124,89,0.4);
        border-radius: 0 10px 10px 0;
    }

    /* ── Filter bar ── */
    .tm-filter-bar {
        background: rgba(200,221,212,0.28);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 16px; padding: 1.2rem 1.4rem;
        margin-bottom: 1.4rem;
        animation: fadeUp 0.4s both;
    }

    /* ── No results ── */
    .tm-empty-state {
        text-align: center; padding: 2.5rem 1rem;
        border-radius: 18px;
        background: rgba(250,247,240,0.75);
        border: 1.5px dashed rgba(74,124,89,0.25);
    }
    .tm-empty-state .es-icon { font-size: 3rem; display: block; margin-bottom: 0.7rem; }
    .tm-empty-state p {
        font-family: 'Nunito', sans-serif;
        color: #8B7355; font-size: 0.92rem; margin: 0;
    }

    /* ── Section head ── */
    .tm-sec-head {
        display: flex; align-items: center;
        gap: 0.75rem; margin: 0.4rem 0 1.2rem;
    }
    .tm-sec-head .icon-box {
        width: 40px; height: 40px; border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem; flex-shrink: 0;
        box-shadow: 0 4px 14px rgba(45,80,22,0.22);
    }
    .tm-sec-head .sec-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.2rem; font-weight: 700;
        color: #2D5016; margin: 0;
    }
    .tm-sec-head .sec-sub {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem; color: #8B7355; margin: 2px 0 0;
    }

    /* ── Result count pill ── */
    .tm-rev-count {
        display: inline-flex; align-items: center; gap: 6px;
        background: linear-gradient(135deg, rgba(74,124,89,0.12), rgba(45,80,22,0.07));
        border: 1.5px solid rgba(74,124,89,0.25);
        color: #2D5016;
        font-family: 'Nunito', sans-serif;
        font-size: 0.85rem; font-weight: 700;
        padding: 5px 16px; border-radius: 99px;
        margin-bottom: 1rem;
    }

    /* ── Divider ── */
    .tm-divider {
        border: none; height: 1.5px;
        background: linear-gradient(90deg,
            transparent, rgba(74,124,89,0.3),
            rgba(201,169,110,0.25), transparent);
        margin: 1.4rem 0;
    }

    /* Stagger review cards */
    .tm-review-card:nth-child(1)  { animation-delay: 0.03s; }
    .tm-review-card:nth-child(2)  { animation-delay: 0.07s; }
    .tm-review-card:nth-child(3)  { animation-delay: 0.11s; }
    .tm-review-card:nth-child(4)  { animation-delay: 0.15s; }
    .tm-review-card:nth-child(5)  { animation-delay: 0.19s; }
    .tm-review-card:nth-child(6)  { animation-delay: 0.23s; }
    .tm-review-card:nth-child(7)  { animation-delay: 0.27s; }
    .tm-review-card:nth-child(8)  { animation-delay: 0.31s; }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # HERO
    # ============================================

    st.markdown("""
    <div class="tm-rev-hero">
        <div class="tm-rev-badge">✍️ Traveller Stories</div>
        <h1>Reviews & Ratings</h1>
        <p>
            Share your experiences and discover what fellow
            travellers are saying about amazing destinations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # STATS BAR
    # ============================================

    stats = get_review_statistics()
    avg   = stats.get("average_rating", 0)
    total = stats.get("total_reviews", 0)
    places_count = stats.get("total_places", 0)

    st.markdown(f"""
    <div class="tm-stats-row">
        <div class="tm-stat-card">
            <p class="tm-stat-val">{total}</p>
            <p class="tm-stat-lbl">Total Reviews</p>
        </div>
        <div class="tm-stat-card">
            <p class="tm-stat-val">{"⭐ " + str(avg) if total else "—"}</p>
            <p class="tm-stat-lbl">Avg Rating</p>
        </div>
        <div class="tm-stat-card">
            <p class="tm-stat-val">{places_count}</p>
            <p class="tm-stat-lbl">Places Reviewed</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # TABS
    # ============================================

    tab1, tab2 = st.tabs(["✍️  Submit a Review", "📖  Browse Reviews"])

    # ──────────────────────────────────────────
    # TAB 1 — SUBMIT
    # ──────────────────────────────────────────
    with tab1:

        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box" style="background:linear-gradient(135deg,#C9A96E,#8B6E47);">✍️</div>
            <div>
                <p class="sec-title">Share Your Experience</p>
                <p class="sec-sub">Help fellow travellers make better choices</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Rating slider OUTSIDE form for live preview ──
        rating_labels = {
            1: ("😞", "Poor",      "#C0392B"),
            2: ("😕", "Fair",      "#E8845A"),
            3: ("😐", "Good",      "#C9A96E"),
            4: ("😊", "Very Good", "#4A7C59"),
            5: ("🤩", "Excellent", "#2D5016"),
        }

        st.markdown("""
        <style>
        [data-testid="stSlider"] label,
        [data-testid="stSlider"] label p {
            color: #1a1a1a !important;
            font-family: 'Nunito', sans-serif !important;
            font-size: 0.88rem !important; font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        rating = st.select_slider(
            "⭐ Your Rating",
            options=[1, 2, 3, 4, 5],
            value=st.session_state.get("live_rating", 5),
            format_func=lambda x: f"{'⭐' * x}  ({x}/5)",
            key="live_rating"
        )

        emoji, label, color = rating_labels[rating]
        st.markdown(f"""
        <div style="
            background:{color}18; border:1.5px solid {color}55;
            border-radius:14px; padding:0.85rem 1.2rem;
            display:flex; align-items:center; gap:12px;
            margin-bottom:1.2rem;
            font-family:'Nunito',sans-serif;
            box-shadow:0 3px 12px {color}22;
            transition: all 0.3s ease;
        ">
            <span style="font-size:2.2rem; line-height:1;">{emoji}</span>
            <div>
                <p style="margin:0; font-size:1.05rem; font-weight:800; color:{color};">{label}</p>
                <p style="margin:0; font-size:0.78rem; color:{color}99;">{"⭐" * rating} · {rating} out of 5</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("review_form", clear_on_submit=True):

            col1, col2 = st.columns(2, gap="medium")

            with col1:
                place_name = st.text_input(
                    "📍 Place Name *",
                    placeholder="e.g. Shaniwar Wada, Goa Beach…"
                )
            with col2:
                user_name = st.text_input(
                    "👤 Your Name *",
                    placeholder="e.g. Priya Sharma"
                )

            comment = st.text_area(
                "💬 Your Review *",
                placeholder="Describe your visit — what did you love, what could be better?",
                height=140
            )

            submitted = st.form_submit_button(
                "✅  Submit My Review",
                use_container_width=True
            )

            if submitted:
                if place_name and user_name and comment:
                    success = save_review(place_name, user_name, rating, comment)
                    if success:
                        st.session_state["review_submitted"] = True
                        st.session_state["review_place"]     = place_name
                    else:
                        st.session_state["review_submitted"] = False
                        st.error("❌ Failed to save review. Please try again.")
                else:
                    st.session_state["review_submitted"] = False
                    st.error("⚠️ Please fill in all required fields (Place, Name, Review).")

        # ── Rerun & success banner OUTSIDE the form ──
        if st.session_state.get("review_submitted"):
            place_done = st.session_state.get("review_place", "")
            st.success(f"🎉 Review for **{place_done}** submitted successfully!")
            st.balloons()
            st.session_state["review_submitted"] = False
            st.cache_data.clear()

    # ──────────────────────────────────────────
    # TAB 2 — BROWSE
    # ──────────────────────────────────────────
    with tab2:

        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box" style="background:linear-gradient(135deg,#4A7C59,#2D5016);">📖</div>
            <div>
                <p class="sec-title">Browse Reviews</p>
                <p class="sec-sub">Filter, sort and explore traveller stories</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Filter bar
        st.markdown('<div class="tm-filter-bar">', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3, gap="medium")

        with fc1:
            search_place = st.text_input(
                "🔍 Search by Place",
                placeholder="e.g. Lonavala, Pune…",
                key="search_reviews"
            )
        with fc2:
            min_rating = st.selectbox(
                "⭐ Min Rating",
                [1, 2, 3, 4, 5],
                format_func=lambda x: f"{'⭐' * x}+",
                key="min_rating"
            )
        with fc3:
            sort_by = st.selectbox(
                "🔀 Sort By",
                ["Latest", "Highest Rated", "Lowest Rated"],
                key="sort_reviews"
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Load & filter
        all_reviews = load_reviews()

        if not all_reviews.empty:
            filtered = all_reviews.copy()

            if search_place:
                filtered = filtered[
                    filtered["place"].str.contains(search_place, case=False, na=False)
                ]

            filtered = filtered[filtered["rating"] >= min_rating]

            if sort_by == "Highest Rated":
                filtered = filtered.sort_values("rating", ascending=False)
            elif sort_by == "Lowest Rated":
                filtered = filtered.sort_values("rating", ascending=True)
            else:
                filtered = filtered.sort_values("date", ascending=False)

            if not filtered.empty:
                st.markdown(f"""
                <div class="tm-rev-count">
                    📋 Showing <strong>{len(filtered)}</strong> review{"s" if len(filtered) != 1 else ""}
                </div>
                """, unsafe_allow_html=True)

                for idx, row in filtered.iterrows():
                    stars = "⭐" * int(row["rating"])
                    st.markdown(f"""
                    <div class="tm-review-card">
                        <p class="tm-review-place">📍 {row['place']}</p>
                        <div class="tm-review-meta">
                            <span class="tm-review-user">👤 {row['user_name']}</span>
                            <span class="tm-review-date">🗓️ {row['date']}</span>
                            <span class="tm-review-stars">{stars}</span>
                        </div>
                        <p class="tm-review-comment">{row['comment']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="tm-empty-state">
                    <span class="es-icon">🔍</span>
                    <p>No reviews match your filters.<br>
                    Try a different place name or lower the minimum rating.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tm-empty-state">
                <span class="es-icon">✍️</span>
                <p>No reviews yet — be the first to share your travel story!</p>
            </div>
            """, unsafe_allow_html=True)