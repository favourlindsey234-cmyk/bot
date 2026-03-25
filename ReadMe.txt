# 🚀 Trading Bot Application

## 📌 Overview
This is a web-based trading bot application that connects to MetaTrader 5 (MT5) to automate trading and provide a real-time dashboard for monitoring trades and performance.

---

## ⚙️ Features

- Start and Stop automated trading
- Connect to MT5 account (Login, Password, Server)
- Real-time account monitoring (Balance, Equity, Profit)
- View open trades
- Trade history tracking
- Smart trading strategy (Moving Average + RSI)
- Risk management (lot size, stop loss, take profit)

---

## 🧠 How It Works

The bot uses:
- Moving Averages to detect trends
- RSI to filter trade entries

It automatically:
- Scans the market
- Generates BUY/SELL signals
- Executes trades on MT5

---

## 🖥️ Requirements

Before running the app, ensure you have:

- Python 3.10+
- MetaTrader 5 installed
- MT5 account (Demo or Live)
- Internet connection

---

## 📦 Installation

1. Open terminal in project folder

2. Install dependencies:
   pip install -r requirements.txt

3. Run the app:
   python -m streamlit run app.py

---

## 🔐 MT5 Setup

- Open MetaTrader 5
- Log into your account
- Enable "AutoTrading"

---

## ▶️ Running the App

1. Launch the app
2. Enter:
   - Login ID
   - Password
   - Server (e.g. MetaQuotes-Demo)
3. Click "Start Bot"

---

## ⚠️ Disclaimer

This bot is for educational purposes only.
Trading involves risk. Always test on a demo account first.

---

## 👨‍💻 Developers

Built using:
- Python
- Streamlit
- MetaTrader5 API



pip install -r requirements.txt
python -m streamlit run app.py