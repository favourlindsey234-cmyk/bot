import streamlit as st
import threading
import pandas as pd
import random
import time
import numpy as np
from bot import run_bot
from auth import login, signup, db

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Trading Bot Pro", layout="wide")

# ----------------------------
# SESSION STATE
# ----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

if "profit" not in st.session_state:
    st.session_state.profit = 0.0

# ----------------------------
# AUTH PAGE
# ----------------------------
def auth_page():
    st.title("🔐 Login")

    choice = st.selectbox("Login / Signup", ["Login", "Signup"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            user = signup(email, password)
            if user:
                st.success("Account created")

    if choice == "Login":
        if st.button("Login"):
            user = login(email, password)
            if user:
                st.session_state.user = user
                st.rerun()

# ----------------------------
# MAIN APP
# ----------------------------
def main_app():
    st.title("🚀 Trading Bot Pro")

    user_id = st.session_state.user["localId"]

    # PROFIT SIMULATION
    if st.session_state.bot_running:
        st.session_state.profit += random.uniform(-0.5, 2.5)

    profit = round(st.session_state.profit, 2)

    # ----------------------------
    # METRICS
    # ----------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Strategy", "MA Cross")

    col2.metric("Status", "RUNNING" if st.session_state.bot_running else "STOPPED")

    col3.metric("Profit", f"${profit}")

    st.divider()

    # ----------------------------
    # BOT CONTROL
    # ----------------------------
    col4, col5 = st.columns(2)

    with col4:
        if st.button("Start Bot"):
            if not st.session_state.bot_running:
                st.session_state.bot_running = True
                threading.Thread(target=run_bot, args=(user_id,)).start()

    with col5:
        if st.button("Stop Bot"):
            st.session_state.bot_running = False

    st.divider()

    # ----------------------------
    # STATS
    # ----------------------------
    st.subheader("📊 Stats")

    try:
        trades = db.child("users").child(user_id).child("trades").get().val()

        if trades:
            trade_list = list(trades.values())

            total = len(trade_list)
            wins = sum(1 for t in trade_list if t["result"] == "win")
            losses = sum(1 for t in trade_list if t["result"] == "loss")

            win_rate = (wins / total) * 100 if total > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", total)
            c2.metric("Wins", wins)
            c3.metric("Losses", losses)
            c4.metric("Win Rate", f"{win_rate:.1f}%")

        else:
            st.write("No trades yet")

    except:
        st.write("Error loading stats")

    # ----------------------------
    # CHART
    # ----------------------------
    st.subheader("📈 Profit Curve")
    profit_curve = np.cumsum([random.uniform(-2, 5) for _ in range(30)])
    st.line_chart(profit_curve)

    # ----------------------------
    # LOGS
    # ----------------------------
    st.subheader("📜 Logs")

    try:
        logs = db.child("users").child(user_id).child("logs").get().val()

        if logs:
            log_list = [x["message"] for x in logs.values()]
            st.code("\n".join(log_list[-20:]))
        else:
            st.write("No logs yet")

    except:
        st.write("Error loading logs")

    # ----------------------------
    # LOGOUT
    # ----------------------------
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # AUTO REFRESH
    time.sleep(2)
    st.rerun()

# ----------------------------
# ROUTING
# ----------------------------
if st.session_state.user is None:
    auth_page()
else:
    main_app()