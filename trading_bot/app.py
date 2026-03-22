import streamlit as st
import threading
import MetaTrader5 as mt5
import pandas as pd
import random
from bot import run_bot, logs

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Trading Bot Pro", layout="wide")

st.title("🚀 Trading Bot Pro Dashboard")

# ----------------------------
# TOP METRICS
# ----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    if not mt5.initialize():
        st.error("🔴 MT5 Not Connected")
    else:
        account = mt5.account_info()
        if account:
            st.success("🟢 Connected")
            st.metric("💰 Balance", account.balance)

with col2:
    st.metric("📊 Strategy", "MA Crossover")

with col3:
    st.metric("⚖️ Risk", "1:2 RR")

# ----------------------------
# BOT CONTROL
# ----------------------------
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

col4, col5 = st.columns(2)

with col4:
    if st.button("▶️ Start Bot"):
        if not st.session_state.bot_running:
            st.session_state.bot_running = True
            threading.Thread(target=run_bot).start()
            st.success("Bot Started ✅")
        else:
            st.warning("Already running")

with col5:
    if st.button("⏹ Stop Bot"):
        st.session_state.bot_running = False
        st.warning("Bot Stopped ❌")

# ----------------------------
# AI MODE (presentation trick)
# ----------------------------
st.subheader("🤖 AI Mode")

ai_mode = st.toggle("Enable Smart AI Trading")

if ai_mode:
    st.success("AI Mode Active 🚀")
else:
    st.info("Standard Strategy Mode")

# ----------------------------
# STATUS
# ----------------------------
st.subheader("📡 Status")

if st.session_state.bot_running:
    st.success("🟢 RUNNING")
else:
    st.error("🔴 STOPPED")

# ----------------------------
# FAKE LIVE CHART (for visuals)
# ----------------------------
st.subheader("📈 Market Overview")

# Generate fake price data (for demo)
data = [1.15 + random.uniform(-0.002, 0.002) for _ in range(50)]
chart_df = pd.DataFrame(data, columns=["Price"])

st.line_chart(chart_df)

# ----------------------------
# TRADE HISTORY (demo table)
# ----------------------------
st.subheader("📊 Trade History")

# Fake trade history for presentation
trade_data = {
    "Type": ["BUY", "SELL", "BUY", "SELL"],
    "Lot": [0.01, 0.01, 0.02, 0.01],
    "Profit": ["+$5", "-$3", "+$8", "+$2"],
}

df = pd.DataFrame(trade_data)
st.dataframe(df)

# ----------------------------
# LIVE LOGS
# ----------------------------
st.subheader("📜 Live Activity")

log_container = st.empty()

if logs:
    recent_logs = logs[-15:]
    log_text = "\n".join(reversed(recent_logs))
    log_container.text_area("Logs", log_text, height=250)
else:
    st.write("No activity yet...")