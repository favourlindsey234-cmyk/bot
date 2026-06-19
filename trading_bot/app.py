import streamlit as st
from auth import login, signup

st.set_page_config(
    page_title="Gravity Bot",
    page_icon="◈",
    layout="centered"
)

# ── Shared CSS (also imported by child pages via utils.py) ────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0D1117; color: #E6EDF3; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }

input[type="text"], input[type="password"], input[type="email"] {
    background: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 6px !important;
    color: #E6EDF3 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}
input:focus { border-color: #4F6EF7 !important; box-shadow: 0 0 0 2px rgba(79,110,247,.18) !important; }

.stButton > button {
    background: #4F6EF7 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    width: 100%;
}
.stButton > button:hover { background: #6B85F8 !important; }
.stSuccess, .stError, .stWarning, .stInfo { border-radius: 6px !important; font-size: 0.8rem !important; }

.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid #21262D; background: transparent; }
.stTabs [data-baseweb="tab"] { font-size: 0.75rem !important; font-weight: 500 !important; color: #8B949E !important; padding: 0.5rem 1.25rem !important; border-bottom: 2px solid transparent !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: #E6EDF3 !important; border-bottom: 2px solid #4F6EF7 !important; }

[data-testid="stSidebar"] { background-color: #0D1117 !important; border-right: 1px solid #21262D !important; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Redirect if already logged in ────────────────────────────
if st.session_state.get("user"):
    st.switch_page("pages/1_dashboard.py")

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2.5rem 0 1.75rem">
    <div style="font-size:1.6rem;font-weight:600;color:#E6EDF3;letter-spacing:-.03em">Gravity Bot</div>
    <div style="font-size:0.72rem;color:#8B949E;margin-top:6px;letter-spacing:.06em;text-transform:uppercase">MT5 Algorithmic Trading</div>
</div>
""", unsafe_allow_html=True)

tab_login, tab_signup = st.tabs(["Sign in", "Create account"])

# ── Sign in ───────────────────────────────────────────────────
with tab_login:
    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
    email    = st.text_input("Email", key="li_email")
    password = st.text_input("Password", type="password", key="li_pass")
    st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
    if st.button("Sign in", key="btn_login"):
        if not email or not password:
            st.warning("Enter your email and password.")
        else:
            user = login(email, password)
            if user:
                st.session_state.user  = user
                st.session_state.email = email
                st.success("Signed in — redirecting…")
                st.switch_page("pages/1_dashboard.py")
            else:
                st.error("Incorrect email or password.")

# ── Create account ────────────────────────────────────────────
with tab_signup:
    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
    su_email = st.text_input("Email", key="su_email")
    su_pass  = st.text_input("Password (min 6 chars)", type="password", key="su_pass")
    su_pass2 = st.text_input("Confirm password", type="password", key="su_pass2")
    st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
    if st.button("Create account", key="btn_signup"):
        if not su_email or not su_pass:
            st.warning("Fill in all fields.")
        elif su_pass != su_pass2:
            st.error("Passwords don't match.")
        elif len(su_pass) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            user = signup(su_email, su_pass)
            if user:
                st.session_state.user  = user
                st.session_state.email = su_email
                st.success("Account created — redirecting…")
                st.switch_page("pages/1_dashboard.py")
            else:
                st.error("Could not create account. Email may already be in use.")

st.markdown("""
<div style="text-align:center;margin-top:2.5rem;font-size:.65rem;color:#484F58;letter-spacing:.04em">
    Gravity Bot &nbsp;·&nbsp; Secure login via Firebase
</div>
""", unsafe_allow_html=True)