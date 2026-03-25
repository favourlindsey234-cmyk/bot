import streamlit as st
import threading
from bot import TradingBot

# 🔥 PAGE CONFIG
st.set_page_config(
    page_title="Gravity Bot",
    page_icon="🚀",
    layout="wide"
)

# 🎨 CLEAN UI STYLE
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0e1117, #1c1f26);
    color: white;
}
h1 {
    color: #00ffcc;
}
</style>
""", unsafe_allow_html=True)

# 🚀 HEADER
st.title("🚀 Gravity Bot")
st.subheader("Live MT5 Trading System")

# 🔐 SIDEBAR LOGIN
st.sidebar.header("🔐 MT5 Login")

login = st.sidebar.text_input("Login ID")
password = st.sidebar.text_input("Password", type="password")
server = st.sidebar.text_input("Server", value="MetaQuotes-Demo")

# ⚙️ SETTINGS
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.text_input("Symbol", value="EURUSD")

# 🧠 SESSION STATE
if "bot" not in st.session_state:
    st.session_state.bot = None
    st.session_state.thread = None
    st.session_state.connected = False
    st.session_state.running = False

# 🔌 CONNECT BUTTON
if st.sidebar.button("🔌 Connect to MT5"):
    bot = TradingBot(login, password, server)
    bot.symbol = symbol

    if bot.connect():
        st.session_state.bot = bot
        st.session_state.connected = True
        st.success("✅ Connected to MT5")
    else:
        st.error("❌ Connection failed")

# 📊 STATUS DISPLAY
col1, col2, col3 = st.columns(3)

connection_status = "🟢 Connected" if st.session_state.connected else "🔴 Disconnected"
bot_status = "🟢 Running" if st.session_state.running else "🔴 Stopped"

col1.metric("Connection", connection_status)
col2.metric("Bot Status", bot_status)
col3.metric("Mode", "Live Trade")

# ▶️ START BOT
if st.button("▶️ Start Bot"):
    if not st.session_state.connected:
        st.warning("⚠️ Connect to MT5 first")
    else:
        if not st.session_state.running:
            st.session_state.bot.running = True

            thread = threading.Thread(
                target=st.session_state.bot.run,
                daemon=True  # 🔥 prevents UI freeze
            )
            thread.start()

            st.session_state.thread = thread
            st.session_state.running = True

            st.success("🚀 Bot Started & Trade Sent")

# ⛔ STOP BOT
if st.button("⛔ Stop Bot"):
    if st.session_state.bot:
        st.session_state.bot.stop()
        st.session_state.running = False
        st.success("🛑 Bot Stopped")

# 📊 INFO PANEL
st.markdown("### 📊 Live Status")

if st.session_state.running:
    st.success("Bot is running and executing trades...")
else:
    st.info("Connect to MT5 and start the bot to begin trading.")

# FOOTER
st.markdown("---")
st.caption("Gravity Bot | Live MT5 Execution")