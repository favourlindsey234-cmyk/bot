from unittest import result

import MetaTrader5 as mt5
import time

# ----------------------------
# CONNECT TO MT5
# ----------------------------
if not mt5.initialize():
    print("Initialization failed")
    quit()

print("Connected to MT5 ✅")

# ----------------------------
# ACCOUNT INFO
# ----------------------------
account = mt5.account_info()
if account is None:
    print("Failed to get account info")
    quit()

print("Balance:", account.balance)

# ----------------------------
# SYMBOL SETUP
# ----------------------------
symbol = "EURUSD"

if not mt5.symbol_select(symbol, True):
    print("Failed to select symbol")
    quit()

# ----------------------------
# CHECK IF TRADE IS OPEN
# ----------------------------
def has_open_trade():
    positions = mt5.positions_get(symbol=symbol)
    return positions is not None and len(positions) > 0

# ----------------------------
# BUY FUNCTION
# ----------------------------
def place_buy():
    lot = 0.01

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("Failed to get tick data")
        return

    price = tick.ask

    # Stop Loss & Take Profit (1:2 RR)
    sl = price - 0.0010   # 10 pips
    tp = price + 0.0020   # 20 pips

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

    result = mt5.order_send(request)
    print("BUY ORDER RESULT:", result)
    return result

# ----------------------------
# SELL FUNCTION has bee
# ----------------------------
def place_sell():
    lot = 0.01

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("Failed to get tick data")
        return

    price = tick.bid

    # Stop Loss & Take Profit (1:2 RR)
    sl = price + 0.0010   # 10 pips
    tp = price - 0.0020   # 20 pips

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
    return result

# ----------------------------
# MAIN LOOP (AUTO TRADING)
# ----------------------------
print("Bot running... 🚀")

while True:
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)

    print("Rates length:", 0 if rates is None else len(rates))

    if rates is not None and len(rates) > 20:
        closes = [rate['close'] for rate in rates]

        # Moving averages
        fast_ma = sum(closes[-10:]) / 10
        slow_ma = sum(closes[-20:]) / 20

        print("Fast MA:", fast_ma, "| Slow MA:", slow_ma)

        # STRATEGY
        if fast_ma > slow_ma and not has_open_trade():
            print("BUY signal (trend up)")
            place_buy()
            time.sleep(10)

        elif fast_ma < slow_ma and not has_open_trade():
            print("SELL signal (trend down)")
            place_sell()
            time.sleep(10)

        else:
            print("No trade")

    else:
        print("No data yet...")

    time.sleep(5)