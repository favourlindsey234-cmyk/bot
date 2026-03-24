import streamlit as st
from bot import TradingBot
import threading
import MetaTrader5 as mt5
import pandas as pd

# 🎨 PAGE
st.set_page_config(page_title="Trading Bot", layout="wide")

# 🎨 STYLE
st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Trading Dashboard")

# 🔐 LOGIN
with st.sidebar:
    st.header("🔐 MT5 Login")
    login = st.text_input("Login ID")
    password = st.text_input("Password", type="password")
    server = st.text_input("Server")

# SESSION STATE
if "bot" not in st.session_state:
    st.session_state.bot = None

if "running" not in st.session_state:
    st.session_state.running = False

# 🎮 BUTTONS
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Start Bot"):
        if login and password and server:
            bot = TradingBot(login, password, server)
            thread = threading.Thread(target=bot.run)
            thread.start()

            st.session_state.bot = bot
            st.session_state.running = True
            st.success("Bot Started")
        else:
            st.error("Fill all fields")

with col2:
    if st.button("🛑 Stop Bot"):
        if st.session_state.bot:
            st.session_state.bot.stop()
            st.session_state.running = False
            st.warning("Bot Stopped")

# STATUS
st.markdown("---")
status = "🟢 Running" if st.session_state.running else "🔴 Stopped"
st.subheader(f"Status: {status}")

# CONNECT MT5
if mt5.initialize():

    account = mt5.account_info()

    if account:
        st.markdown("### 📊 Account Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Balance", f"${account.balance}")
        col2.metric("📈 Equity", f"${account.equity}")
        col3.metric("📉 Profit", f"${account.profit}")

    # 📉 OPEN TRADES
    st.markdown("### 📉 Open Trades")
    positions = mt5.positions_get()

    if positions:
        data = []
        for pos in positions:
            data.append({
                "Symbol": pos.symbol,
                "Lot": pos.volume,
                "Profit": round(pos.profit, 2)
            })
        st.dataframe(pd.DataFrame(data))
    else:
        st.info("No open trades")

    # 📜 TRADE HISTORY
    st.markdown("### 📜 Trade History")

    history = mt5.history_deals_get()

    if history:
        hist_data = []
        for h in history[-10:]:
            hist_data.append({
                "Symbol": h.symbol,
                "Profit": round(h.profit, 2),
                "Type": h.type
            })

        df = pd.DataFrame(hist_data)
        st.dataframe(df)

        # 📊 STATS
        wins = sum(1 for h in hist_data if h["Profit"] > 0)
        losses = sum(1 for h in hist_data if h["Profit"] <= 0)
        total = len(hist_data)

        win_rate = (wins / total * 100) if total > 0 else 0

        st.markdown("### 📊 Performance")

        col1, col2, col3 = st.columns(3)
        col1.metric("Trades", total)
        col2.metric("Wins", wins)
        col3.metric("Win Rate", f"{win_rate:.1f}%")

else:
    st.error("MT5 not connected")