import MetaTrader5 as mt5
import time

# ----------------------------
# GLOBAL LOG LIST (for app UI)
# ----------------------------
# This will store messages that your Streamlit app can display
logs = []

# ----------------------------
# CONNECT TO MT5
# ----------------------------
# Initializes connection between Python and MetaTrader 5
if not mt5.initialize():
    print("Initialization failed")
    quit()

print("Connected to MT5 ✅")
logs.append("Connected to MT5")

# ----------------------------
# ACCOUNT INFO
# ----------------------------
# Retrieves account details like balance
account = mt5.account_info()
if account is None:
    print("Failed to get account info")
    quit()

print("Balance:", account.balance)
logs.append(f"Balance: {account.balance}")

# ----------------------------
# SYMBOL SETUP
# ----------------------------
# Define what market you want to trade
symbol = "EURUSD"

# Ensure the symbol is available in MT5
if not mt5.symbol_select(symbol, True):
    print("Failed to select symbol")
    quit()

# ----------------------------
# TRADE CONTROL SETTINGS
# ----------------------------
# Prevents overtrading (cooldown between trades)
last_trade_time = 0
cooldown = 60  # seconds

# ----------------------------
# CHECK IF TRADE IS OPEN
# ----------------------------
# Prevents opening multiple trades at the same time
def has_open_trade():
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0

# ----------------------------
# BUY FUNCTION
# ----------------------------
def place_buy():
    lot = 0.01  # trade size

    # Get current price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        msg = "Failed to get tick data"
        print(msg)
        logs.append(msg)
        return None

    price = tick.ask  # buy price

    # Risk management (Stop Loss & Take Profit)
    sl = price - 0.0010  # 10 pips loss
    tp = price + 0.0020  # 20 pips profit

    # Trade request dictionary
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "Bot Buy",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Send order
    result = mt5.order_send(request)

    print("BUY ORDER RESULT:", result)
    logs.append(f"BUY attempt → {result.comment}")

    return result

# ----------------------------
# SELL FUNCTION
# ----------------------------
def place_sell():
    lot = 0.01

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        msg = "Failed to get tick data"
        print(msg)
        logs.append(msg)
        return None

    price = tick.bid  # sell price

    sl = price + 0.0010
    tp = price - 0.0020

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "Bot Sell",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    result = mt5.order_send(request)

    print("SELL ORDER RESULT:", result)
    logs.append(f"SELL attempt → {result.comment}")

    return result

# ----------------------------
# MAIN BOT FUNCTION
# ----------------------------
# This runs continuously when triggered from the app
def run_bot():
    print("Bot running... 🚀")
    logs.append("Bot started")

    global last_trade_time

    while True:
        # Fetch market data (last 100 candles on M5 timeframe)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)

        if rates is None:
            msg = "No data from MT5"
            print(msg)
            logs.append(msg)
            time.sleep(5)
            continue

        # Extract closing prices
        closes = [rate['close'] for rate in rates]

        # Calculate moving averages
        fast_ma = sum(closes[-10:]) / 10
        slow_ma = sum(closes[-20:]) / 20

        print("Fast MA:", fast_ma, "| Slow MA:", slow_ma)

        current_time = time.time()

        # ----------------------------
        # BUY CONDITION
        # ----------------------------
        if (fast_ma > slow_ma and 
            (fast_ma - slow_ma) > 0.0002 and 
            not has_open_trade() and 
            (current_time - last_trade_time > cooldown)):

            msg = "BUY signal detected"
            print(msg)
            logs.append(msg)

            result = place_buy()

            # Only confirm trade if successful
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logs.append("BUY executed ✅")
                last_trade_time = current_time

        # ----------------------------
        # SELL CONDITION
        # ----------------------------
        elif (fast_ma < slow_ma and 
              (slow_ma - fast_ma) > 0.0002 and 
              not has_open_trade() and 
              (current_time - last_trade_time > cooldown)):

            msg = "SELL signal detected"
            print(msg)
            logs.append(msg)

            result = place_sell()

            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                logs.append("SELL executed ✅")
                last_trade_time = current_time

        else:
            msg = "No trade condition met"
            print(msg)
            logs.append(msg)

        # Wait before checking again
        time.sleep(5)