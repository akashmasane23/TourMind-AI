"""
Peak Hours & Nearby Page — Travel/Nature Theme
"""

import streamlit as st
from utils.data_handlers import load_peak_hours, get_place_peak_hours, load_places
from utils.realtime_places import get_nearby_attractions
from utils.realtime_crowd import predict_live_crowd


# ============================================
# HELPER FUNCTIONS
# ============================================

def crowd_to_value(level):
    return {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}.get(level, 1)


def crowd_to_color(level):
    return {
        "Low":       ("#4A7C59", "#2D5016"),
        "Medium":    ("#C9A96E", "#8B6E47"),
        "High":      ("#E8845A", "#C0623C"),
        "Very High": ("#C0392B", "#922B21"),
    }.get(level, ("#4A7C59", "#2D5016"))


def crowd_to_emoji(level):
    return {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Very High": "🔴"}.get(level, "🟢")


def get_coordinates(place_name):
    df = load_places()
    if df.empty:
        return None, None
    result = df[df["place_name"].str.lower().str.contains(place_name.lower(), na=False)]
    if result.empty:
        return None, None
    row = result.iloc[0]
    return row["latitude"], row["longitude"]


# ============================================
# MAIN PAGE
# ============================================

def show():

    # ============================================
    # STYLES
    # ============================================

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Nunito:wght@400;600;700&display=swap');

    /* ── Hero ── */
    .tm-peak-hero {
        background: linear-gradient(135deg,
            rgba(46,134,171,0.88) 0%,
            rgba(45,80,22,0.82) 50%,
            rgba(139,110,71,0.78) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(46,134,171,0.20);
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }
    .tm-peak-hero::after {
        content: "⏰";
        position: absolute;
        right: 2.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 5.5rem;
        opacity: 0.10;
        pointer-events: none;
    }
    .tm-peak-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .tm-peak-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        margin: 0; line-height: 1.6;
    }
    .tm-peak-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(135,206,235,0.22);
        border: 1px solid rgba(135,206,235,0.45);
        color: #87CEEB;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 1.8px; text-transform: uppercase;
        padding: 4px 14px; border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── Search bar ── */
    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInput"] input {
        color: #1a1a1a !important;
        background: #fff !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.95rem !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(74,124,89,0.28) !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #999 !important; font-style: italic !important; opacity: 1 !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #4A7C59 !important;
        box-shadow: 0 0 0 3px rgba(74,124,89,0.15) !important;
    }

    /* ── Info cards row ── */
    .tm-info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0 1.4rem;
    }
    .tm-info-tile {
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        font-family: 'Nunito', sans-serif;
        backdrop-filter: blur(8px);
        box-shadow: 0 3px 14px rgba(44,36,22,0.09);
        transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.22s;
        animation: fadeUp 0.45s both;
    }
    .tm-info-tile:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(44,36,22,0.14); }
    .tm-info-tile .tile-label {
        font-size: 0.72rem; font-weight: 700; letter-spacing: 1.4px;
        text-transform: uppercase; margin: 0 0 0.35rem; opacity: 0.75;
    }
    .tm-info-tile .tile-value {
        font-size: 0.95rem; font-weight: 700; margin: 0; line-height: 1.4;
    }

    .tm-tile-green  { background: linear-gradient(135deg, rgba(74,124,89,0.14), rgba(45,80,22,0.08));  border: 1.5px solid rgba(74,124,89,0.25); color: #2D5016; }
    .tm-tile-red    { background: linear-gradient(135deg, rgba(232,132,90,0.14), rgba(192,98,60,0.08)); border: 1.5px solid rgba(232,132,90,0.28); color: #C0623C; }
    .tm-tile-blue   { background: linear-gradient(135deg, rgba(46,134,171,0.14), rgba(26,95,122,0.08)); border: 1.5px solid rgba(46,134,171,0.25); color: #1A5F7A; }
    .tm-tile-golden { background: linear-gradient(135deg, rgba(244,185,66,0.14), rgba(201,169,110,0.08)); border: 1.5px solid rgba(244,185,66,0.28); color: #8B6E47; }

    /* ── Section header ── */
    .tm-sec-head {
        display: flex; align-items: center;
        gap: 0.75rem; margin: 1.8rem 0 1rem;
    }
    .tm-sec-head .icon-box {
        width: 40px; height: 40px; border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 14px rgba(45,80,22,0.22);
        flex-shrink: 0;
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

    /* ── Crowd meter ── */
    .tm-crowd-wrap {
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 18px rgba(44,36,22,0.09);
        backdrop-filter: blur(8px);
        animation: fadeUp 0.5s both;
    }
    .tm-crowd-label {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem; font-weight: 700;
        letter-spacing: 1.3px; text-transform: uppercase;
        margin: 0 0 0.6rem; opacity: 0.75;
    }
    .tm-crowd-row {
        display: flex; align-items: center; gap: 1rem;
    }
    .tm-crowd-bar-outer {
        flex: 1; height: 14px; border-radius: 99px;
        background: rgba(255,255,255,0.35);
        overflow: hidden;
    }
    .tm-crowd-bar-inner {
        height: 100%; border-radius: 99px;
        transition: width 0.8s cubic-bezier(0.34,1.2,0.64,1);
    }
    .tm-crowd-badge {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1rem; font-weight: 700;
        white-space: nowrap;
    }

    /* ── Recommendation card ── */
    .tm-rec-card {
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 0.8rem;
        display: flex; align-items: flex-start; gap: 1rem;
        box-shadow: 0 3px 14px rgba(44,36,22,0.09);
        backdrop-filter: blur(6px);
        animation: fadeUp 0.5s both;
        font-family: 'Nunito', sans-serif;
    }
    .tm-rec-card .rec-icon { font-size: 1.6rem; flex-shrink: 0; margin-top: 2px; }
    .tm-rec-card .rec-text { font-size: 0.92rem; line-height: 1.55; margin: 0; }
    .tm-rec-card .rec-text strong { font-size: 0.95rem; }
    .tm-rec-best  { background: linear-gradient(135deg, rgba(74,124,89,0.13), rgba(45,80,22,0.07));  border: 1.5px solid rgba(74,124,89,0.25);  color: #2D5016; }
    .tm-rec-avoid { background: linear-gradient(135deg, rgba(232,132,90,0.13), rgba(192,98,60,0.07)); border: 1.5px solid rgba(232,132,90,0.28); color: #8B3A1A; }

    /* ── Nearby attraction cards ── */
    .tm-nearby-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.15);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 4px 18px rgba(44,36,22,0.10);
        margin-bottom: 1rem;
        display: flex;
        gap: 0;
        transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s;
        animation: fadeUp 0.5s both;
    }
    .tm-nearby-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 32px rgba(44,36,22,0.16);
    }
    .tm-nearby-img {
        width: 140px; min-height: 130px;
        object-fit: cover; flex-shrink: 0;
    }
    .tm-nearby-body {
        padding: 1rem 1.2rem;
        display: flex; flex-direction: column; justify-content: center;
    }
    .tm-nearby-name {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.05rem; font-weight: 700;
        color: #2D5016; margin: 0 0 0.35rem;
    }
    .tm-nearby-rating {
        font-family: 'Nunito', sans-serif;
        font-size: 0.85rem; font-weight: 700;
        color: #C9A96E; margin: 0 0 0.25rem;
    }
    .tm-nearby-addr {
        font-family: 'Nunito', sans-serif;
        font-size: 0.82rem; color: #8B7355;
        margin: 0; line-height: 1.45;
    }

    /* ── Data table ── */
    .tm-table-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.16);
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px rgba(44,36,22,0.09);
        animation: fadeUp 0.5s both;
    }

    /* ── Divider ── */
    .tm-divider {
        border: none; height: 1.5px;
        background: linear-gradient(90deg, transparent, rgba(74,124,89,0.3), rgba(201,169,110,0.25), transparent);
        margin: 1.6rem 0;
    }

    /* ── Empty state ── */
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

    /* ── Stagger ── */
    .tm-nearby-card:nth-child(1) { animation-delay: 0.04s; }
    .tm-nearby-card:nth-child(2) { animation-delay: 0.09s; }
    .tm-nearby-card:nth-child(3) { animation-delay: 0.14s; }
    .tm-nearby-card:nth-child(4) { animation-delay: 0.19s; }
    .tm-nearby-card:nth-child(5) { animation-delay: 0.24s; }

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
    <div class="tm-peak-hero">
        <div class="tm-peak-badge">📍 Live Crowd Intelligence</div>
        <h1>Peak Hours & Nearby Attractions</h1>
        <p>
            Find the best times to visit, dodge the crowds,
            and discover hidden gems near any attraction.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # SEARCH
    # ============================================

    col_inp, col_btn = st.columns([5, 1], gap="small")
    with col_inp:
        place_search = st.text_input(
            "🔍 Search Place",
            placeholder="e.g. Shaniwar Wada, Aga Khan Palace…"
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("Search 🔍", use_container_width=True)

    # ============================================
    # RESULTS
    # ============================================

    if search_clicked:

        if not place_search.strip():
            st.error("⚠️ Please enter a place name to search.")
        else:
            info = get_place_peak_hours(place_search)

            if not info:
                st.markdown("""
                <div class="tm-empty-state">
                    <span class="es-icon">🗺️</span>
                    <p>No information found for this place.<br>
                    Try a different spelling or nearby landmark.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"✅ Showing results for: **{info['place']}**")

                # ── INFO TILES ──────────────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#4A7C59,#2D5016);">🕐</div>
                    <div>
                        <p class="sec-title">Visit Intelligence</p>
                        <p class="sec-sub">Timing & crowd overview</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="tm-info-grid">
                    <div class="tm-info-tile tm-tile-green">
                        <p class="tile-label">✅ Best Time to Visit</p>
                        <p class="tile-value">{info['best_time']}</p>
                    </div>
                    <div class="tm-info-tile tm-tile-red">
                        <p class="tile-label">❌ Avoid During</p>
                        <p class="tile-value">{info['avoid_time']}</p>
                    </div>
                    <div class="tm-info-tile tm-tile-blue">
                        <p class="tile-label">📅 Peak Season</p>
                        <p class="tile-value">{info['peak_season']}</p>
                    </div>
                    <div class="tm-info-tile tm-tile-golden">
                        <p class="tile-label">👥 Average Crowd</p>
                        <p class="tile-value">{crowd_to_emoji(info['average_crowd'])} {info['average_crowd']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

                # ── CROWD METERS ────────────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#2E86AB,#1A5F7A);">🌡️</div>
                    <div>
                        <p class="sec-title">Crowd Levels</p>
                        <p class="sec-sub">Average & live AI prediction</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Average crowd
                avg_val   = crowd_to_value(info["average_crowd"])
                avg_c1, avg_c2 = crowd_to_color(info["average_crowd"])
                avg_pct   = int((avg_val / 4) * 100)

                st.markdown(f"""
                <div class="tm-crowd-wrap" style="background:linear-gradient(135deg,{avg_c1}18,{avg_c2}0d); border:1.5px solid {avg_c1}44;">
                    <p class="tm-crowd-label" style="color:{avg_c1};">📊 Average Crowd Level</p>
                    <div class="tm-crowd-row">
                        <div class="tm-crowd-bar-outer">
                            <div class="tm-crowd-bar-inner"
                                 style="width:{avg_pct}%; background:linear-gradient(90deg,{avg_c1},{avg_c2});"></div>
                        </div>
                        <span class="tm-crowd-badge" style="color:{avg_c1};">
                            {crowd_to_emoji(info['average_crowd'])} {info['average_crowd']}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Live crowd
                live_level = predict_live_crowd("Pune")
                live_val   = crowd_to_value(live_level)
                live_c1, live_c2 = crowd_to_color(live_level)
                live_pct   = int((live_val / 4) * 100)

                st.markdown(f"""
                <div class="tm-crowd-wrap" style="background:linear-gradient(135deg,{live_c1}18,{live_c2}0d); border:1.5px solid {live_c1}44;">
                    <p class="tm-crowd-label" style="color:{live_c1};">🔴 Live Crowd Now (AI Prediction)</p>
                    <div class="tm-crowd-row">
                        <div class="tm-crowd-bar-outer">
                            <div class="tm-crowd-bar-inner"
                                 style="width:{live_pct}%; background:linear-gradient(90deg,{live_c1},{live_c2});"></div>
                        </div>
                        <span class="tm-crowd-badge" style="color:{live_c1};">
                            {crowd_to_emoji(live_level)} {live_level}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

                # ── SMART RECOMMENDATION ────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#C9A96E,#8B6E47);">🧭</div>
                    <div>
                        <p class="sec-title">Smart Recommendation</p>
                        <p class="sec-sub">When to go & when to skip</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="tm-rec-card tm-rec-best">
                    <span class="rec-icon">✅</span>
                    <p class="rec-text">
                        <strong>Best time to visit {info['place']}:</strong><br>
                        {info['best_time']} — you'll enjoy fewer crowds and a better experience.
                    </p>
                </div>
                <div class="tm-rec-card tm-rec-avoid">
                    <span class="rec-icon">⚠️</span>
                    <p class="rec-text">
                        <strong>Avoid visiting during:</strong><br>
                        {info['avoid_time']} — expect heavy footfall and longer wait times.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

                # ── NEARBY ATTRACTIONS ──────────────
                st.markdown("""
                <div class="tm-sec-head">
                    <div class="icon-box" style="background:linear-gradient(135deg,#2E86AB,#1A5F7A);">📍</div>
                    <div>
                        <p class="sec-title">Nearby Attractions</p>
                        <p class="sec-sub">Live results from Google Places</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                lat, lng = get_coordinates(place_search)

                if lat and lng:
                    nearby_places = get_nearby_attractions(lat, lng)

                    if nearby_places:
                        for p in nearby_places:
                            photo = p.get("photo") or \
                                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300&q=80"
                            st.markdown(f"""
                            <div class="tm-nearby-card">
                                <img class="tm-nearby-img" src="{photo}" alt="{p['name']}">
                                <div class="tm-nearby-body">
                                    <p class="tm-nearby-name">🗺️ {p['name']}</p>
                                    <p class="tm-nearby-rating">⭐ {p['rating']}</p>
                                    <p class="tm-nearby-addr">📍 {p['vicinity']}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="tm-empty-state">
                            <span class="es-icon">📍</span>
                            <p>No nearby attractions found via Google Places API.</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="tm-empty-state">
                        <span class="es-icon">🌐</span>
                        <p>Coordinates not available for this place.<br>
                        Make sure it exists in your places dataset.</p>
                    </div>
                    """, unsafe_allow_html=True)

    # ============================================
    # ALL PLACES TABLE
    # ============================================

    st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div class="tm-sec-head">
        <div class="icon-box" style="background:linear-gradient(135deg,#4A7C59,#2D5016);">📋</div>
        <div>
            <p class="sec-title">All Places Directory</p>
            <p class="sec-sub">Browse our full crowd & timing database</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = load_peak_hours()

    if not df.empty:
        st.markdown('<div class="tm-table-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="tm-empty-state">
            <span class="es-icon">📋</span>
            <p>No places data available yet.</p>
        </div>
        """, unsafe_allow_html=True)