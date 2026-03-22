import MetaTrader5 as mt5
import time
from auth import db

# ----------------------------
# GLOBALS
# ----------------------------
logs = []
symbol = "EURUSD"
last_trade_time = 0
cooldown = 60  # seconds

# ----------------------------
# CONNECT MT5
# ----------------------------
try:
    mt5.initialize()
except:
    pass

# ----------------------------
# LOG FUNCTION
# ----------------------------
def log_message(user_id, msg):
    print(msg)
    logs.append(msg)

    try:
        db.child("users").child(user_id).child("logs").push({
            "message": msg
        })
    except:
        pass

# ----------------------------
# CHECK OPEN TRADE
# ----------------------------
def has_open_trade():
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0

# ----------------------------
# BUY
# ----------------------------
def place_buy():
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    price = tick.ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - 0.0010,
        "tp": price + 0.0020,
        "deviation": 10,
        "magic": 123456,
        "comment": "Bot Buy",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    return mt5.order_send(request)

# ----------------------------
# SELL
# ----------------------------
def place_sell():
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    price = tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price + 0.0010,
        "tp": price - 0.0020,
        "deviation": 10,
        "magic": 123456,
        "comment": "Bot Sell",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    return mt5.order_send(request)

# ----------------------------
# MAIN BOT
# ----------------------------
def run_bot(user_id):
    global last_trade_time

    log_message(user_id, "Bot started 🚀")

    while True:
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)

        if rates is None:
            log_message(user_id, "No data")
            time.sleep(5)
            continue

        closes = [r['close'] for r in rates]

        fast_ma = sum(closes[-10:]) / 10
        slow_ma = sum(closes[-20:]) / 20

        now = time.time()

        # BUY
        if fast_ma > slow_ma and not has_open_trade() and now - last_trade_time > cooldown:
            log_message(user_id, "BUY signal")

            result = place_buy()

            if result:
                db.child("users").child(user_id).child("trades").push({
                    "type": "BUY",
                    "result": "win",
                    "time": str(now)
                })

                last_trade_time = now

        # SELL
        elif fast_ma < slow_ma and not has_open_trade() and now - last_trade_time > cooldown:
            log_message(user_id, "SELL signal")

            result = place_sell()

            if result:
                db.child("users").child(user_id).child("trades").push({
                    "type": "SELL",
                    "result": "loss",
                    "time": str(now)
                })

                last_trade_time = now

        else:
            log_message(user_id, "No trade")

        time.sleep(5)