import MetaTrader5 as mt5
import time
import pandas as pd

class TradingBot:
    def __init__(self, login, password, server):
        self.login = int(login)
        self.password = password
        self.server = server
        self.running = False
        self.last_trade = None

    # 🔌 CONNECT
    def connect(self):
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            print("❌ MT5 connection failed:", mt5.last_error())
            return False
        
        print("✅ Connected to MT5")
        return True

    def disconnect(self):
        mt5.shutdown()
        print("🔌 Disconnected")

    # 📊 GET MARKET DATA
    def get_data(self, symbol, timeframe=mt5.TIMEFRAME_M5, n=200):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
        df = pd.DataFrame(rates)
        return df

    # 🧠 STRATEGY (MA + RSI)
    def check_signal(self, df):
        df['ma_fast'] = df['close'].rolling(10).mean()
        df['ma_slow'] = df['close'].rolling(30).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        prev_fast = df['ma_fast'].iloc[-2]
        prev_slow = df['ma_slow'].iloc[-2]
        curr_fast = df['ma_fast'].iloc[-1]
        curr_slow = df['ma_slow'].iloc[-1]
        rsi = df['rsi'].iloc[-1]

        # 🎯 SMART ENTRY
        if prev_fast < prev_slow and curr_fast > curr_slow and rsi < 70:
            return "buy"
        elif prev_fast > prev_slow and curr_fast < curr_slow and rsi > 30:
            return "sell"

        return None

    # 💰 LOT SIZE (RISK MANAGEMENT)
    def calculate_lot(self, balance):
        risk_percent = 0.01  # 1%
        lot = round(balance * risk_percent / 1000, 2)
        return max(lot, 0.01)

    # 🔒 LIMIT OPEN TRADES
    def can_trade(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            return True
        return len(positions) < 2  # max 2 trades

    # 💼 PLACE TRADE
    def place_trade(self, symbol, signal):
        account = mt5.account_info()
        if not account:
            return

        lot = self.calculate_lot(account.balance)
        tick = mt5.symbol_info_tick(symbol)

        if signal == "buy":
            price = tick.ask
            sl = price - 0.0020
            tp = price + 0.0040
            order_type = mt5.ORDER_TYPE_BUY

        elif signal == "sell":
            price = tick.bid
            sl = price + 0.0020
            tp = price - 0.0040
            order_type = mt5.ORDER_TYPE_SELL

        else:
            return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 123456,
            "comment": "final bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("❌ Trade failed:", result)
        else:
            print(f"✅ {signal.upper()} trade | Lot: {lot}")
            self.last_trade = signal

    # 🚀 MAIN LOOP
    def run(self):
        if not self.connect():
            return

        self.running = True
        symbol = "EURUSD"

        print("🚀 FINAL BOT RUNNING...")

        while self.running:
            try:
                df = self.get_data(symbol)
                signal = self.check_signal(df)

                if signal and signal != self.last_trade and self.can_trade(symbol):
                    print(f"📢 Signal: {signal}")
                    self.place_trade(symbol, signal)

                account = mt5.account_info()
                if account:
                    print(f"💰 Balance: {account.balance}")

                time.sleep(15)

            except Exception as e:
                print("⚠️ Error:", e)
                time.sleep(5)

        self.disconnect()

    # 🛑 STOP BOT
    def stop(self):
        self.running = False
        print("🛑 Stopping bot...")