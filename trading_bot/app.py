import streamlit as st
import threading
from bot import TradingBot

st.set_page_config(
    page_title="Gravity Bot",
    page_icon="🌌",
    layout="wide"
)

# 🎨 STYLE
st.markdown("""
<style>
.main {
    background-color: #0e1117;
    color: white;
}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 🌌 HEADER
st.title("🌌 Gravity Bot")
st.markdown("### Precision Trading • Intelligent Execution")

if "bot" not in st.session_state:
    st.session_state.bot = None
    st.session_state.running = False

col1, col2 = st.columns(2)

# 🔐 CONNECTION
with col1:
    st.subheader("🔐 MT5 Connection")

    login = st.text_input("Login ID")
    password = st.text_input("Password", type="password")
    server = st.text_input("Server", value="MetaQuotes-Demo")

    if st.button("🔌 Connect"):
        bot = TradingBot(login, password, server)
        if bot.connect():
            st.session_state.bot = bot
            st.success("Connected to MT5")
        else:
            st.error("Connection failed")

# 🤖 CONTROL
with col2:
    st.subheader("🤖 Bot Control")

    if st.button("🚀 Start Bot"):
        if st.session_state.bot:
            thread = threading.Thread(target=st.session_state.bot.run)
            thread.start()
            st.session_state.running = True
            st.success("Bot running")
        else:
            st.error("Connect first")

    if st.button("🛑 Stop Bot"):
        if st.session_state.bot:
            st.session_state.bot.stop()
            st.session_state.running = False
            st.warning("Bot stopped")

# 📊 STATUS
st.markdown("---")
st.subheader("📊 System Status")

col3, col4, col5 = st.columns(3)

with col3:
    st.metric("Bot Status", "Running" if st.session_state.running else "Stopped")

with col4:
    st.metric("Symbol", "EURUSD")

with col5:
    st.metric("System", "Gravity Engine v5")