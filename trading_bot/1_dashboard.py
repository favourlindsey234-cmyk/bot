import streamlit as st
import threading
from bot import TradingBot
from utils import (
    inject_css, require_auth, page_header, section_label,
    divider, status_cards, sidebar_nav, page_footer
)

st.set_page_config(page_title="Dashboard · Gravity Bot", page_icon="◈", layout="wide")
inject_css()
require_auth()

email = st.session_state.get("email", "")
sidebar_nav(email)

# ── Session state defaults ────────────────────────────────────
for key, val in {
    "bot": None, "thread": None,
    "connected": False, "running": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar — MT5 connection ──────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-size:.6rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
                color:#8B949E;margin:1.25rem 0 .6rem;border-top:1px solid #21262D;padding-top:1rem'>
        MT5 credentials
    </div>
    """, unsafe_allow_html=True)

    mt5_login  = st.text_input("Login ID",  key="mt5_login")
    mt5_pass   = st.text_input("Password",  type="password", key="mt5_pass")
    mt5_server = st.text_input("Server",    value="MetaQuotes-Demo", key="mt5_server")
    mt5_symbol = st.text_input("Symbol",    value="EURUSD", key="mt5_symbol")

    if st.button("Connect to MT5"):
        risk = st.session_state.get("risk_settings", {})
        bot  = TradingBot(mt5_login, mt5_pass, mt5_server)
        bot.symbol             = mt5_symbol
        bot.lot                = risk.get("lot",                0.03)
        bot.stop_loss_pips     = risk.get("stop_loss_pips",     25)
        bot.take_profit_pips   = risk.get("take_profit_pips",   80)
        bot.trailing_stop_pips = risk.get("trailing_stop_pips", 15)
        bot.max_loss_per_trade = risk.get("max_loss_per_trade", -15.0)

        if bot.connect():
            st.session_state.bot       = bot
            st.session_state.connected = True
            st.success("Connected")
        else:
            st.error("Connection failed — check credentials")

# ── Main content ──────────────────────────────────────────────
page_header(
    "Dashboard",
    subtitle=f"Live MT5 trading · {st.session_state.get('mt5_symbol', 'EURUSD')} · H1",
    badge="Live" if st.session_state.running else "Idle"
)

# ── Status cards ──────────────────────────────────────────────
status_cards([
    {
        "label": "Connection",
        "value": "Connected"    if st.session_state.connected else "Disconnected",
        "state": "ok"           if st.session_state.connected else "err"
    },
    {
        "label": "Bot status",
        "value": "Running"      if st.session_state.running   else "Stopped",
        "state": "ok"           if st.session_state.running   else "err"
    },
    {
        "label": "Symbol",
        "value": st.session_state.get("mt5_symbol", "EURUSD"),
        "state": "info"
    },
    {
        "label": "Lot size",
        "value": str(st.session_state.get("risk_settings", {}).get("lot", 0.03)),
        "state": "neu"
    },
])

divider()

# ── Controls ──────────────────────────────────────────────────
section_label("Controls")
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    if st.button("▶  Start bot"):
        if not st.session_state.connected:
            st.warning("Connect to MT5 first.")
        elif not st.session_state.running:
            st.session_state.bot.running = True
            t = threading.Thread(target=st.session_state.bot.run, daemon=True)
            t.start()
            st.session_state.thread  = t
            st.session_state.running = True
            st.success("Bot started")

with col2:
    if st.button("■  Stop bot"):
        if st.session_state.bot:
            st.session_state.bot.stop()
            st.session_state.running = False
            st.success("Bot stopped")

divider()

# ── Live status ───────────────────────────────────────────────
section_label("Live status")

if st.session_state.running:
    st.markdown("""
    <div style='background:rgba(63,185,80,.06);border:1px solid rgba(63,185,80,.2);
                border-left:3px solid #3FB950;border-radius:6px;
                padding:.7rem 1rem;font-size:.78rem;color:#3FB950;
                font-family:"JetBrains Mono",monospace'>
        ● &nbsp; Bot active — scanning market &amp; executing trades
    </div>
    """, unsafe_allow_html=True)

    # ── Account snapshot (live) ───────────────────────────────
    if st.session_state.bot:
        import MetaTrader5 as mt5
        info = mt5.account_info()
        if info:
            divider()
            section_label("Account snapshot")
            status_cards([
                {"label": "Balance",  "value": f"${info.balance:,.2f}",  "state": "neu"},
                {"label": "Equity",   "value": f"${info.equity:,.2f}",   "state": "neu"},
                {"label": "Margin",   "value": f"${info.margin:,.2f}",   "state": "neu"},
                {"label": "Free margin", "value": f"${info.margin_free:,.2f}", "state": "info"},
            ])

        positions = mt5.positions_get()
        if positions:
            divider()
            section_label(f"Open positions ({len(positions)})")
            import pandas as pd
            rows = []
            for p in positions:
                rows.append({
                    "Ticket":  p.ticket,
                    "Symbol":  p.symbol,
                    "Type":    "Buy" if p.type == 0 else "Sell",
                    "Volume":  p.volume,
                    "Open price": p.price_open,
                    "SL":      p.sl,
                    "TP":      p.tp,
                    "P&L":     round(p.profit, 2),
                })
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )
else:
    st.markdown("""
    <div style='background:rgba(139,148,158,.06);border:1px solid rgba(139,148,158,.15);
                border-left:3px solid #8B949E;border-radius:6px;
                padding:.7rem 1rem;font-size:.78rem;color:#8B949E'>
        Connect to MT5 and start the bot to begin trading.
    </div>
    """, unsafe_allow_html=True)

page_footer("Live" if st.session_state.running else "Idle")
