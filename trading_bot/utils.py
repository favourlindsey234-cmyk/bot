"""
utils.py — shared helpers for all Gravity Bot pages.
Import at the top of every page file.
"""
import streamlit as st

# ── Design tokens ─────────────────────────────────────────────
C_BG       = "#0D1117"
C_SURFACE  = "#161B22"
C_BORDER   = "#21262D"
C_BORDER2  = "#30363D"
C_TEXT     = "#E6EDF3"
C_MUTED    = "#8B949E"
C_ACCENT   = "#4F6EF7"
C_GREEN    = "#3FB950"
C_RED      = "#F85149"
C_FOOTER   = "#484F58"

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background-color: {C_BG}; color: {C_TEXT}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 1.5rem 2rem 4rem; max-width: 1200px; }}

/* inputs */
input[type="text"], input[type="password"], input[type="email"], input[type="number"] {{
    background: {C_SURFACE} !important;
    border: 1px solid {C_BORDER2} !important;
    border-radius: 6px !important;
    color: {C_TEXT} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}}
input:focus {{ border-color: {C_ACCENT} !important; box-shadow: 0 0 0 2px rgba(79,110,247,.18) !important; }}

/* select / number inputs */
[data-baseweb="select"] > div {{
    background: {C_SURFACE} !important;
    border-color: {C_BORDER2} !important;
    border-radius: 6px !important;
    color: {C_TEXT} !important;
    font-size: 0.8rem !important;
}}

/* sliders */
[data-testid="stSlider"] > div > div > div {{ background: {C_ACCENT} !important; }}

/* primary button */
.stButton > button {{
    background: {C_ACCENT} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.1rem !important;
    transition: background .15s ease !important;
}}
.stButton > button:hover {{ background: #6B85F8 !important; }}

/* alerts */
.stSuccess, .stError, .stWarning, .stInfo {{ border-radius: 6px !important; font-size: 0.8rem !important; }}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {C_BORDER}; background: transparent; }}
.stTabs [data-baseweb="tab"] {{ font-size: 0.75rem !important; font-weight: 500 !important; color: {C_MUTED} !important; padding: 0.5rem 1.25rem !important; border-bottom: 2px solid transparent !important; background: transparent !important; }}
.stTabs [aria-selected="true"] {{ color: {C_TEXT} !important; border-bottom: 2px solid {C_ACCENT} !important; }}

/* sidebar */
[data-testid="stSidebar"] {{ background-color: {C_BG} !important; border-right: 1px solid {C_BORDER} !important; }}
[data-testid="stSidebar"] label {{ font-size: 0.7rem !important; color: {C_MUTED} !important; font-weight: 500 !important; }}
[data-testid="stSidebar"] .stTextInput input {{ font-size: 0.78rem !important; }}

/* dataframe */
[data-testid="stDataFrame"] {{ border: 1px solid {C_BORDER} !important; border-radius: 8px !important; overflow: hidden; }}
</style>
"""

# ── Component helpers ─────────────────────────────────────────

def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def require_auth():
    """Redirect to login if the user is not authenticated. Call at top of every page."""
    if not st.session_state.get("user"):
        st.switch_page("app.py")


def page_header(title: str, subtitle: str = "", badge: str = ""):
    badge_html = (
        f"<span style='font-size:.6rem;font-weight:600;letter-spacing:.1em;"
        f"text-transform:uppercase;color:{C_ACCENT};background:rgba(79,110,247,.1);"
        f"border:1px solid rgba(79,110,247,.25);padding:2px 8px;border-radius:4px;"
        f"margin-left:10px'>{badge}</span>"
        if badge else ""
    )
    sub_html = (
        f"<div style='font-size:.75rem;color:{C_MUTED};margin-top:4px;letter-spacing:.01em'>{subtitle}</div>"
        if subtitle else ""
    )
    st.markdown(f"""
    <div style='margin-bottom:1.5rem'>
        <div style='font-size:1.15rem;font-weight:600;color:{C_TEXT};letter-spacing:-.02em'>
            {title}{badge_html}
        </div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def section_label(text: str):
    st.markdown(
        f"<div style='font-size:.62rem;font-weight:600;letter-spacing:.1em;"
        f"text-transform:uppercase;color:{C_MUTED};margin:.1rem 0 .65rem'>{text}</div>",
        unsafe_allow_html=True
    )


def divider():
    st.markdown(
        f"<hr style='border:none;border-top:1px solid {C_BORDER};margin:1.4rem 0'>",
        unsafe_allow_html=True
    )


def status_cards(cards: list[dict]):
    """
    Render a row of status cards.
    Each dict: { label, value, state }  where state is 'ok' | 'err' | 'info' | 'neu'
    """
    color_map = { "ok": C_GREEN, "err": C_RED, "info": C_ACCENT, "neu": C_BORDER2 }
    cols_html  = ""
    for c in cards:
        bar_color = color_map.get(c.get("state", "neu"), C_BORDER2)
        val_color = bar_color if c.get("state") in ("ok","err","info") else C_TEXT
        cols_html += f"""
        <div style='background:{C_SURFACE};padding:.9rem 1.1rem;position:relative;flex:1'>
            <div style='position:absolute;top:0;left:0;right:0;height:2px;background:{bar_color}'></div>
            <div style='font-size:.6rem;font-weight:500;letter-spacing:.09em;text-transform:uppercase;
                        color:{C_MUTED};margin-bottom:.4rem'>{c['label']}</div>
            <div style='font-family:"JetBrains Mono",monospace;font-size:.85rem;font-weight:500;
                        color:{val_color}'>{c['value']}</div>
        </div>"""

    st.markdown(f"""
    <div style='display:flex;gap:1px;background:{C_BORDER};border:1px solid {C_BORDER};
                border-radius:10px;overflow:hidden;margin-bottom:1.5rem'>
        {cols_html}
    </div>
    """, unsafe_allow_html=True)


def sidebar_nav(email: str):
    """Sidebar navigation + user info + sign out."""
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:.5rem 0 1.25rem'>
            <div style='font-size:1rem;font-weight:600;color:{C_TEXT};letter-spacing:-.02em'>Gravity Bot</div>
            <div style='font-size:.6rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
                        color:{C_ACCENT};margin-top:2px'>MT5 live</div>
        </div>
        <div style='border-top:1px solid {C_BORDER};padding-top:1rem;margin-bottom:.5rem'>
            <div style='font-size:.6rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
                        color:{C_MUTED};margin-bottom:.6rem'>Navigation</div>
        </div>
        """, unsafe_allow_html=True)

        st.page_link("pages/1_dashboard.py",     label="Dashboard",      icon="◈")
        st.page_link("pages/2_trade_history.py", label="Trade history",  icon="◎")
        st.page_link("pages/3_risk_settings.py", label="Risk settings",  icon="◇")

        st.markdown(f"""
        <div style='border-top:1px solid {C_BORDER};margin-top:1.5rem;padding-top:1rem'>
            <div style='font-size:.65rem;color:{C_MUTED}'>{email}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign out"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")


def page_footer(status: str = "Idle"):
    dot_color = C_GREEN if status == "Live" else C_BORDER2
    st.markdown(f"""
    <div style='position:fixed;bottom:0;left:0;right:0;background:{C_BG};
                border-top:1px solid {C_BORDER};padding:.55rem 2rem;
                display:flex;justify-content:space-between;align-items:center;
                font-size:.65rem;color:{C_FOOTER};z-index:999;letter-spacing:.04em'>
        <span>Gravity Bot &nbsp;·&nbsp; MT5 Execution Engine</span>
        <span>
            <span style='width:6px;height:6px;border-radius:50%;background:{dot_color};
                         display:inline-block;margin-right:5px;vertical-align:middle'></span>
            {status}
        </span>
    </div>
    """, unsafe_allow_html=True)
