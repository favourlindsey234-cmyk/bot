import MetaTrader5 as mt5
import pandas as pd
import time

class TradingBot:
    def __init__(self, login, password, server):
        self.login = int(login)
        self.password = password
        self.server = server

        self.symbol = "EURUSD"
        self.lot = 0.03
        self.max_trades = 1  # 🔥 sniper = fewer trades

        # Risk settings
        self.stop_loss_pips = 25
        self.take_profit_pips = 80
        self.trailing_stop_pips = 15
        self.max_loss_per_trade = -15

        self.running = False

    def connect(self):
        if not mt5.initialize():
            print("❌ MT5 init failed")
            return False

        if not mt5.login(self.login, password=self.password, server=self.server):
            print("❌ Login failed")
            return False

        print("✅ Connected to MT5")
        return True

    # 📊 MARKET DATA (H1 for trend)
    def get_data(self):
        rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_H1, 0, 200)
        df = pd.DataFrame(rates)

        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()

        return df

    # 📉 RSI
    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    # 🎯 SNIPER SIGNAL
    def get_signal(self):
        df = self.get_data()
        df['rsi'] = self.calculate_rsi(df['close'])

        last = df.iloc[-1]

        trend_up = last['ma20'] > last['ma50']
        trend_down = last['ma20'] < last['ma50']

        # 🔥 SNIPER ENTRIES (pullbacks only)
        if trend_up and 40 < last['rsi'] < 55:
            print("🎯 SNIPER BUY SETUP")
            return "buy"

        elif trend_down and 45 < last['rsi'] < 60:
            print("🎯 SNIPER SELL SETUP")
            return "sell"

        return None

    def calculate_sl_tp(self, price, signal):
        point = mt5.symbol_info(self.symbol).point

        if signal == "buy":
            sl = price - self.stop_loss_pips * point * 10
            tp = price + self.take_profit_pips * point * 10
        else:
            sl = price + self.stop_loss_pips * point * 10
            tp = price - self.take_profit_pips * point * 10

        return sl, tp

    def place_trade(self, signal):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            print("⚠️ Trade already running (sniper mode)")
            return

        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print("❌ No tick data")
            return

        price = tick.ask if signal == "buy" else tick.bid
        sl, tp = self.calculate_sl_tp(price, signal)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot,
            "type": mt5.ORDER_TYPE_BUY if signal == "buy" else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 123456,
            "comment": "Gravity Sniper",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,  # ✅ FIXED
        }

        result = mt5.order_send(request)

        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            print("🚀 SNIPER TRADE OPENED")
        else:
            print("❌ Trade failed:", result)

    # 🛡️ SMART MANAGEMENT
    def manage_trades(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if not positions:
            return

        for pos in positions:
            tick = mt5.symbol_info_tick(self.symbol)
            price = tick.bid if pos.type == 0 else tick.ask
            point = mt5.symbol_info(self.symbol).point

            # ❌ Cut loss early
            if pos.profit <= self.max_loss_per_trade:
                print("❌ Cutting loss")
                mt5.order_send({
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.symbol,
                    "volume": pos.volume,
                    "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                    "position": pos.ticket,
                    "price": price,
                    "deviation": 20,
                })
                continue

            # ✅ Trailing stop
            if pos.type == 0:
                new_sl = price - self.trailing_stop_pips * point * 10
                if new_sl > pos.sl:
                    mt5.order_send({
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "sl": new_sl,
                        "tp": pos.tp
                    })
            else:
                new_sl = price + self.trailing_stop_pips * point * 10
                if new_sl < pos.sl:
                    mt5.order_send({
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": pos.ticket,
                        "sl": new_sl,
                        "tp": pos.tp
                    })

    def run(self):
        self.running = True
        print("🎯 Sniper Bot running...")

        while self.running:
            signal = self.get_signal()
            print("Signal:", signal)

            if signal:
                self.place_trade(signal)

            self.manage_trades()

            time.sleep(15)

    def stop(self):
        self.running = False
        print("🛑 Bot stopped")