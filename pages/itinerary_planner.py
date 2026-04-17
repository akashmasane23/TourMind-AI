"""
AI Powered Itinerary Planner Page — Travel/Nature Theme
"""

import streamlit as st
from utils.openai_itinerary import get_openai_itinerary
from utils.pdf_generator import generate_itinerary_pdf
from utils.data_handlers import save_itinerary
from config import TRIP_TYPES, TRAVEL_PREFERENCES


def show():

    # ============================================
    # PAGE STYLES
    # ============================================

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=Nunito:wght@400;600;700&display=swap');

    /* ── Hero ── */
    .tm-itin-hero {
        background: linear-gradient(135deg,
            rgba(139,110,71,0.90) 0%,
            rgba(45,80,22,0.85) 45%,
            rgba(74,124,89,0.78) 100%);
        border-radius: 22px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(139,110,71,0.22);
        position: relative;
        overflow: hidden;
        animation: fadeUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
    }
    .tm-itin-hero::after {
        content: "🗓️";
        position: absolute;
        right: 2.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 5.5rem;
        opacity: 0.10;
        pointer-events: none;
    }
    .tm-itin-hero h1 {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: clamp(1.6rem, 3vw, 2.4rem) !important;
        color: #fff !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 0.5rem !important;
        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    .tm-itin-hero p {
        font-family: 'Nunito', sans-serif;
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        margin: 0;
        line-height: 1.6;
    }
    .tm-itin-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(244,185,66,0.22);
        border: 1px solid rgba(244,185,66,0.45);
        color: #F4B942;
        font-family: 'Nunito', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        padding: 4px 14px;
        border-radius: 99px;
        margin-bottom: 0.9rem;
    }

    /* ── Form card ── */
    .tm-form-card {
        background: rgba(250,247,240,0.93);
        border: 1.5px solid rgba(74,124,89,0.18);
        border-radius: 22px;
        padding: 2rem 2.2rem 1.6rem;
        box-shadow: 0 4px 24px rgba(44,36,22,0.09);
        backdrop-filter: blur(10px);
        margin-bottom: 1.6rem;
        animation: fadeUp 0.5s 0.1s both;
    }
    .tm-form-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #2D5016;
        margin: 0 0 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── All labels black ── */
    [data-testid="stTextInput"] label,
    [data-testid="stTextInput"] label p,
    [data-testid="stSelectbox"] label,
    [data-testid="stSelectbox"] label p,
    [data-testid="stSlider"] label,
    [data-testid="stSlider"] label p,
    [data-testid="stMultiSelect"] label,
    [data-testid="stMultiSelect"] label p {
        color: #1a1a1a !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    /* ── Input & selectbox text ── */
    [data-testid="stTextInput"] input {
        color: #1a1a1a !important;
        background: #fff !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        border: 1.5px solid rgba(74,124,89,0.25) !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        color: #999 !important;
        font-style: italic !important;
        opacity: 1 !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #4A7C59 !important;
        box-shadow: 0 0 0 3px rgba(74,124,89,0.15) !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #fff !important;
        border-radius: 10px !important;
        border: 1.5px solid rgba(74,124,89,0.25) !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSelectbox"] span { color: #1a1a1a !important; }

    /* ── Multiselect ── */
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #fff !important;
        border-radius: 10px !important;
        border: 1.5px solid rgba(74,124,89,0.25) !important;
        color: #1a1a1a !important;
    }
    [data-testid="stMultiSelect"] span { color: #1a1a1a !important; }

    /* Multiselect tags */
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: linear-gradient(135deg, #4A7C59, #2D5016) !important;
        border-radius: 99px !important;
        color: #fff !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 0.8rem !important;
    }

    /* ── Slider ── */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background: #4A7C59 !important;
        border-color: #2D5016 !important;
    }
    [data-testid="stSlider"] div[data-testid="stTickBarMin"],
    [data-testid="stSlider"] div[data-testid="stTickBarMax"] {
        color: #8B7355 !important;
        font-family: 'Nunito', sans-serif !important;
    }

    /* ── Form submit button ── */
    [data-testid="stFormSubmitButton"] button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.4px !important;
        width: 100% !important;
        border-radius: 14px !important;
        height: 3.2em !important;
        background: linear-gradient(135deg, #4A7C59 0%, #2D5016 100%) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 6px 22px rgba(45,80,22,0.32) !important;
        transition: all 0.28s cubic-bezier(0.34,1.56,0.64,1) !important;
        margin-top: 0.8rem !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #5A8E6A 0%, #3A6028 100%) !important;
        box-shadow: 0 10px 30px rgba(45,80,22,0.40) !important;
        transform: translateY(-3px) scale(1.01) !important;
    }

    /* ── Day counter pill (slider value) ── */
    [data-testid="stSlider"] .st-emotion-cache-1dp5vir,
    [data-testid="stSlider"] p {
        color: #2D5016 !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
    }

    /* ── Result card ── */
    .tm-result-card {
        background: linear-gradient(135deg,
            rgba(232,213,163,0.20), rgba(200,221,212,0.18));
        border: 1.5px solid rgba(201,169,110,0.28);
        border-radius: 22px;
        padding: 2rem 2.4rem;
        margin: 1.2rem 0;
        box-shadow: 0 6px 28px rgba(139,110,71,0.12);
        animation: fadeUp 0.5s both;
    }
    .tm-result-card h1, .tm-result-card h2, .tm-result-card h3 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #2D5016 !important;
        border: none !important;
    }
    .tm-result-card p, .tm-result-card li {
        font-family: 'Nunito', sans-serif !important;
        color: #2C2416 !important;
        line-height: 1.75 !important;
        font-size: 0.95rem !important;
    }
    .tm-result-card strong { color: #4A7C59 !important; }

    /* ── Success / warning / error ── */
    .stAlert {
        border-radius: 14px !important;
        font-family: 'Nunito', sans-serif !important;
    }

    /* ── PDF download button (golden) ── */
    [data-testid="stDownloadButton"]:first-of-type button {
        background: linear-gradient(135deg, #2E86AB, #1A5F7A) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(46,134,171,0.30) !important;
    }
    [data-testid="stDownloadButton"]:first-of-type button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(46,134,171,0.40) !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] button {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #C9A96E, #8B6E47) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(139,110,71,0.28) !important;
        transition: all 0.25s ease !important;
        padding: 0.55rem 1.6rem !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(139,110,71,0.36) !important;
    }

    /* ── Tip box ── */
    .tm-tip-strip {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        background: linear-gradient(135deg,
            rgba(244,185,66,0.10), rgba(232,132,90,0.08));
        border: 1.5px solid rgba(244,185,66,0.30);
        border-radius: 14px;
        padding: 1rem 1.4rem;
        margin-top: 0.8rem;
        animation: fadeUp 0.5s 0.2s both;
    }
    .tm-tip-strip .tip-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .tm-tip-strip p {
        font-family: 'Nunito', sans-serif;
        font-size: 0.88rem;
        color: #5C4A32;
        margin: 0;
        line-height: 1.5;
    }
    .tm-tip-strip strong { color: #8B6E47; }

    /* ── Section header ── */
    .tm-sec-head {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.8rem 0 1rem;
    }
    .tm-sec-head .icon-box {
        width: 40px; height: 40px;
        border-radius: 11px;
        background: linear-gradient(135deg, #4A7C59, #2D5016);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 14px rgba(45,80,22,0.22);
        flex-shrink: 0;
    }
    .tm-sec-head .sec-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #2D5016;
        margin: 0;
    }
    .tm-sec-head .sec-sub {
        font-family: 'Nunito', sans-serif;
        font-size: 0.78rem;
        color: #8B7355;
        margin: 2px 0 0;
    }

    /* ── Action row ── */
    .tm-action-row {
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 1.2rem;
        padding: 1rem 1.4rem;
        background: rgba(200,221,212,0.25);
        border-radius: 14px;
        border: 1px solid rgba(74,124,89,0.15);
    }

    /* ── Divider ── */
    .tm-divider {
        border: none;
        height: 1.5px;
        background: linear-gradient(90deg,
            transparent, rgba(74,124,89,0.3),
            rgba(201,169,110,0.25), transparent);
        margin: 1.6rem 0;
    }

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
    <div class="tm-itin-hero">
        <div class="tm-itin-badge">🤖 AI Powered</div>
        <h1>Smart Itinerary Planner</h1>
        <p>
            Tell us where you're headed — we'll craft the perfect
            day-by-day travel plan just for you ✨
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # FORM
    # ============================================

    st.markdown("""
    <div class="tm-sec-head">
        <div class="icon-box">📋</div>
        <div>
            <p class="sec-title">Trip Details</p>
            <p class="sec-sub">Fill in your preferences below</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("itinerary_form"):

        col1, col2, col3 = st.columns(3, gap="medium")

        with col1:
            destination = st.text_input(
                "🌍 Destination *",
                placeholder="e.g. Pune, Goa, Paris"
            )
        with col2:
            num_days = st.slider("📅 Trip Duration (Days)", 1, 14, 3)
        with col3:
            trip_type = st.selectbox("🎒 Trip Type", TRIP_TYPES)

        preferences = st.multiselect(
            "✨ Travel Preferences  (Optional — pick all that apply)",
            TRAVEL_PREFERENCES,
            help="These help us personalise your itinerary with relevant activities."
        )

        submit = st.form_submit_button(
            "🤖  Generate My AI Itinerary",
            use_container_width=True
        )

    # ============================================
    # TIP STRIP
    # ============================================

    st.markdown("""
    <div class="tm-tip-strip">
        <span class="tip-icon">💡</span>
        <p>
            <strong>Pro tip:</strong> Try different trip types (Adventure, Cultural, Relaxation)
            and mix preferences for a more personalised itinerary.
            The more detail you add, the better your plan will be!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ============================================
    # GENERATE ITINERARY
    # ============================================

    if submit:

        if not destination.strip():
            st.error("⚠️ Please enter a destination to continue.")
            return

        with st.spinner("🧠 TourMind AI is crafting your perfect trip… hang tight!"):
            itinerary, error = get_openai_itinerary(
                destination,
                num_days,
                trip_type,
                preferences
            )

        if error:
            st.error(f"❌ {error}")
            return

        # ── SUCCESS BANNER ─────────────────────
        st.success(f"✅ Your {num_days}-day {trip_type.lower()} itinerary for **{destination.title()}** is ready!")

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ── ITINERARY DISPLAY ──────────────────
        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box">🗺️</div>
            <div>
                <p class="sec-title">Your Itinerary</p>
                <p class="sec-sub">AI-generated, personalised just for you</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="tm-result-card">', unsafe_allow_html=True)
        st.markdown(itinerary)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr class="tm-divider">', unsafe_allow_html=True)

        # ── SAVE + DOWNLOAD ────────────────────
        st.markdown("""
        <div class="tm-sec-head">
            <div class="icon-box" style="background:linear-gradient(135deg,#C9A96E,#8B6E47);">💾</div>
            <div>
                <p class="sec-title">Save & Download</p>
                <p class="sec-sub">Keep your itinerary for offline use</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        saved = save_itinerary(destination, num_days, {
            "trip_type":   trip_type,
            "preferences": preferences,
            "itinerary":   itinerary
        })

        if saved:
            st.success("💾 Itinerary saved to your collection!")
        else:
            st.warning("⚠️ Could not save itinerary locally — you can still download it.")

        # ── Generate PDF ──────────────────────────────
        with st.spinner("📄 Preparing PDF…"):
            try:
                pdf_bytes = generate_itinerary_pdf(
                    itinerary_text=itinerary,
                    destination=destination,
                    num_days=num_days,
                    trip_type=trip_type,
                    preferences=preferences,
                )
                pdf_ok = True
            except Exception as e:
                pdf_ok = False
                pdf_error = str(e)

        # ── Download buttons ──────────────────────────
        dl_c1, dl_c2, _ = st.columns([1, 1, 2])

        with dl_c1:
            if pdf_ok:
                st.download_button(
                    label="📄  Download PDF",
                    data=pdf_bytes,
                    file_name=f"{destination.title().replace(' ','_')}_{num_days}days_itinerary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.warning(f"PDF generation failed: {pdf_error}")

        with dl_c2:
            st.download_button(
                label="📝  Download TXT",
                data=itinerary,
                file_name=f"{destination.title().replace(' ','_')}_{num_days}days_itinerary.txt",
                mime="text/plain",
                use_container_width=True,
            )