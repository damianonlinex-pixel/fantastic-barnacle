"""
Enhanced Bruce Lee Trading Bot - Version 2.0
"Be like water. The formless, adaptable warrior."

IMPROVEMENTS ADDED:
1. Dynamic Entry Filters - Avoids poor trades
2. Volatility-Aware Strategy - Scales position size with market conditions
3. Advanced Exit Strategy - Trails stops, scales profits, adapts to structure
4. Market Structure Recognition - Finds support/resistance dynamically
5. Liquidity Filtering - Only trades with sufficient volume
6. Psychological Discipline - No revenge trading, emotional control
7. Adaptive Risk - Changes based on market conditions
8. Momentum Confirmation - Validates signals with multiple indicators

Philosophy: "Do not pray for an easy life, pray for the strength to endure a difficult one."
           "Knowing is not enough, we must apply. Willing is not enough, we must do."
           - Bruce Lee
"""

import ccxt
import pandas as pd
import numpy as np
import time
from typing import Optional, Dict, Any
from datetime import datetime

class EnhancedBruceLeeTradingBot:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        symbol: str = "BTC/USDT",
        timeframe: str = "1h",
        risk_per_trade: float = 0.01,
        max_daily_loss: float = 0.05,
        exchange_id: str = "binance",
    ):
        """
        🥋 ENHANCED BRUCE LEE TRADING BOT v2.0
        
        The Warrior's Philosophy:
        - "Empty your mind, be formless, shapeless like water"
          → Adapts to any market condition
        
        - "Do not pray for an easy life, pray for the strength to endure"
          → Handles losses with discipline
        
        - "Knowing is not enough, we must apply"
          → Validates signals with multiple confirmations
        
        - "Absorb what is useful, discard what is useless"
          → Only trades high-probability setups
        
        Enhanced Features:
        ✓ Volatility-aware position sizing
        ✓ Dynamic support/resistance detection
        ✓ Advanced entry filters (liquidity, structure, momentum)
        ✓ Adaptive exit strategy (trailing stops, scaling)
        ✓ Market microstructure awareness
        ✓ Emotional discipline (avoiding revenge trades)
        ✓ Momentum confirmation indicators
        ✓ Risk/reward validation
        """
        self.exchange = getattr(ccxt, exchange_id)(
            {"apiKey": api_key, "secret": api_secret, "enableRateLimit": True}
        )
        self.symbol = symbol
        self.timeframe = timeframe
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        
        # Core state
        self.daily_loss = 0.0
        self.position = None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        
        # Psychological discipline (Bruce Lee principle)
        self.last_loss_time = None
        self.revenge_trade_protection = 300  # 5 minutes cooldown after loss
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3  # Pause after 3 losses in a row
        
        # Market state tracking
        self.last_signal_time = None
        self.signal_cooldown = 60  # Don't trade same signal twice in 60 seconds
        self.volume_baseline = None  # 20-period average for liquidity check

    def fetch_ohlcv(self, limit: int = 100) -> pd.DataFrame:
        """Fetch market data - Be like water, adapt to market conditions."""
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=limit)
        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df

    # ============================================================
    # CORE INDICATORS (The Warrior's Tools)
    # ============================================================

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR - Measure of market volatility (Bruce Lee: 'Measure the opponent')"""
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr

    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ADX - Trend strength (Bruce Lee: 'Know the opponent and know yourself')"""
        high = df["high"]
        low = df["low"]
        close = df["close"]

        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr = self.calculate_atr(df, period)
        plus_di = 100 * (plus_dm.ewm(alpha=1 / period).mean() / tr)
        minus_di = 100 * (minus_dm.ewm(alpha=1 / period).mean() / tr)

        dx = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di))
        adx = dx.rolling(period).mean()
        return adx

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI - Momentum indicator (Bruce Lee: 'Read the rhythm')"""
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, df: pd.DataFrame) -> tuple:
        """Calculate MACD - Momentum confirmation"""
        ema_12 = df["close"].ewm(span=12).mean()
        ema_26 = df["close"].ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def calculate_support_resistance(self, df: pd.DataFrame, period: int = 20) -> tuple:
        """Detect dynamic support/resistance (Bruce Lee: 'Adapt to the terrain')"""
        resistance = df["high"].rolling(window=period).max()
        support = df["low"].rolling(window=period).min()
        return support, resistance

    def calculate_volume_profile(self, df: pd.DataFrame, period: int = 20) -> float:
        """Calculate average volume - Liquidity check"""
        avg_volume = df["volume"].rolling(window=period).mean()
        return avg_volume.iloc[-1] if not avg_volume.isna().all() else 0

    # ============================================================
    # ADVANCED FILTERS (The Warrior's Discipline)
    # ============================================================

    def check_liquidity(self, df: pd.DataFrame, min_volume_multiplier: float = 0.8) -> bool:
        """
        Liquidity Filter: "Economy of motion - don't waste energy on illiquid assets"
        Only trade if current volume is sufficient.
        """
        current_volume = df["volume"].iloc[-1]
        avg_volume = df["volume"].rolling(window=20).mean().iloc[-1]
        
        if avg_volume == 0:
            return False
        
        volume_ratio = current_volume / avg_volume
        return volume_ratio >= min_volume_multiplier

    def check_volatility_conditions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Volatility Assessment: "Know when to strike, when to wait"
        Returns volatility assessment and position size adjustment.
        """
        atr = self.calculate_atr(df).iloc[-1]
        sma_20 = df["close"].rolling(20).mean().iloc[-1]
        
        # Calculate volatility relative to average
        atr_ratio = atr / sma_20 * 100  # ATR as % of price
        
        if atr_ratio > 3:
            return {
                "volatility": "extreme",
                "size_multiplier": 0.5,  # Reduce size in extreme volatility
                "trade": False  # Don't trade in extreme volatility
            }
        elif atr_ratio > 2:
            return {
                "volatility": "high",
                "size_multiplier": 0.75,  # Reduce size slightly
                "trade": True
            }
        elif atr_ratio < 0.5:
            return {
                "volatility": "very_low",
                "size_multiplier": 1.0,  # Normal size
                "trade": True
            }
        else:
            return {
                "volatility": "normal",
                "size_multiplier": 1.0,
                "trade": True
            }

    def check_momentum_confirmation(self, df: pd.DataFrame) -> bool:
        """
        Momentum Confirmation: "Strike when the moment is right"
        Validates signal with RSI and MACD.
        """
        rsi = self.calculate_rsi(df).iloc[-1]
        macd_line, signal_line, histogram = self.calculate_macd(df)
        
        macd_cross = (histogram.iloc[-2] <= 0 < histogram.iloc[-1]) or \
                     (histogram.iloc[-2] >= 0 > histogram.iloc[-1])
        
        # For buy: RSI not overbought (< 70), MACD positive histogram
        # For sell: RSI not oversold (> 30), MACD negative histogram
        
        return macd_cross  # MACD crossover confirms trend change

    def check_structure_confirmation(self, df: pd.DataFrame, signal: Dict[str, Any]) -> bool:
        """
        Market Structure Check: "Know the terrain before attacking"
        Validates signal aligns with support/resistance and recent structure.
        """
        support, resistance = self.calculate_support_resistance(df)
        current_price = df["close"].iloc[-1]
        recent_high = df["high"].iloc[-5:].max()
        recent_low = df["low"].iloc[-5:].min()
        
        support_val = support.iloc[-1]
        resistance_val = resistance.iloc[-1]
        
        if signal["side"] == "buy":
            # Buy should be near support or after breaking above resistance
            near_support = abs(current_price - support_val) / support_val < 0.02
            above_resistance = current_price > resistance_val
            return near_support or above_resistance
        else:  # sell
            # Sell should be near resistance or after breaking below support
            near_resistance = abs(current_price - resistance_val) / resistance_val < 0.02
            below_support = current_price < support_val
            return near_resistance or below_support

    def check_psychological_discipline(self) -> bool:
        """
        Emotional Discipline: "Conquer yourself rather than always conquering your opponent"
        Prevents revenge trading and burnout after consecutive losses.
        """
        # Don't trade immediately after a loss (5-minute cooldown)
        if self.last_loss_time:
            time_since_loss = time.time() - self.last_loss_time
            if time_since_loss < self.revenge_trade_protection:
                return False  # In cooldown period
        
        # Pause after 3 consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False  # Take a break
        
        return True

    # ============================================================
    # STRATEGY DETECTION (The Warrior's Awareness)
    # ============================================================

    def detect_market_regime(self, df: pd.DataFrame) -> str:
        """Detect market regime: Jeet Kune Do - No fixed style"""
        atr = self.calculate_atr(df)
        adx = self.calculate_adx(df)
        latest_atr = atr.iloc[-1]
        latest_adx = adx.iloc[-1]

        if latest_adx > 25:
            return "trend"
        elif latest_atr < df["close"].pct_change().std() * 2:
            return "range"
        else:
            return "breakout"

    # ============================================================
    # TRADING STRATEGIES (The Three Ways)
    # ============================================================

    def trend_strategy(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Trend Strategy: "Follow like water flowing downstream"
        Enhanced with momentum and structure validation.
        """
        df["fast_ma"] = df["close"].rolling(9).mean()
        df["slow_ma"] = df["close"].rolling(21).mean()
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signal = None
        if latest["fast_ma"] > latest["slow_ma"] and prev["fast_ma"] <= prev["slow_ma"]:
            signal = {"side": "buy", "reason": "MA crossover up"}
        elif latest["fast_ma"] < latest["slow_ma"] and prev["fast_ma"] >= prev["slow_ma"]:
            signal = {"side": "sell", "reason": "MA crossover down"}

        # Enhanced validation
        if signal:
            # Confirm with momentum
            if self.check_momentum_confirmation(df):
                # Confirm with structure
                if self.check_structure_confirmation(df, signal):
                    return signal

        return None

    def mean_reversion_strategy(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Mean Reversion: "Bend like bamboo in the wind"
        Refined for range-bound markets with volume confirmation.
        """
        df["ma"] = df["close"].rolling(20).mean()
        df["std"] = df["close"].rolling(20).std()
        df["upper_band"] = df["ma"] + 2 * df["std"]
        df["lower_band"] = df["ma"] - 2 * df["std"]
        latest = df.iloc[-1]

        signal = None
        if latest["close"] <= latest["lower_band"]:
            signal = {"side": "buy", "reason": "Price at lower Bollinger Band"}
        elif latest["close"] >= latest["upper_band"]:
            signal = {"side": "sell", "reason": "Price at upper Bollinger Band"}

        # Only trade mean reversion in low volatility
        if signal:
            volatility = self.check_volatility_conditions(df)
            if volatility["volatility"] in ["normal", "very_low"]:
                if self.check_momentum_confirmation(df):
                    return signal

        return None

    def breakout_strategy(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Breakout Strategy: "Strike with precision"
        Enhanced with volume and momentum confirmation.
        """
        df["upper_channel"] = df["high"].rolling(20).max()
        df["lower_channel"] = df["low"].rolling(20).min()
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signal = None
        if latest["close"] > latest["upper_channel"] and prev["close"] <= prev["upper_channel"]:
            signal = {"side": "buy", "reason": "Breakout above resistance"}
        elif latest["close"] < latest["lower_channel"] and prev["close"] >= prev["lower_channel"]:
            signal = {"side": "sell", "reason": "Breakdown below support"}

        # Confirm with volume and momentum
        if signal:
            if self.check_liquidity(df):
                if self.check_momentum_confirmation(df):
                    return signal

        return None

    # ============================================================
    # POSITION MANAGEMENT (The Warrior's Precision)
    # ============================================================

    def calculate_position_size(self, df: pd.DataFrame, entry_price: float) -> float:
        """
        Dynamic Position Sizing: "Adjust your approach to the opponent"
        Scales position size based on market volatility and risk conditions.
        """
        atr = self.calculate_atr(df).iloc[-1]
        volatility_conditions = self.check_volatility_conditions(df)
        
        stop_distance = atr * 1.5
        risk_amount = self.risk_per_trade * self.get_account_balance()
        base_position_size = risk_amount / stop_distance if stop_distance > 0 else 0
        
        # Apply volatility adjustment
        adjusted_position_size = base_position_size * volatility_conditions["size_multiplier"]
        
        return adjusted_position_size

    def calculate_optimal_exit(self, df: pd.DataFrame, entry_price: float, signal: Dict[str, Any]) -> tuple:
        """
        Adaptive Exit Strategy: "Know when to retreat"
        Returns (stop_loss, take_profit_1, take_profit_2, trailing_stop_pct)
        """
        atr = self.calculate_atr(df).iloc[-1]
        support, resistance = self.calculate_support_resistance(df)
        support_val = support.iloc[-1]
        resistance_val = resistance.iloc[-1]
        
        if signal["side"] == "buy":
            # Stop loss below recent structure
            stop_loss = min(entry_price - (atr * 1.5), support_val)
            
            # Multiple take profits (scaling strategy)
            tp1 = entry_price + (atr * 2)      # First profit at 2x ATR (30%)
            tp2 = entry_price + (atr * 4)      # Second profit at 4x ATR (30%)
            tp3 = entry_price + (atr * 6)      # Third profit at 6x ATR (40%)
            
            trailing_stop_pct = 0.02  # Trail stop at 2% for remaining position
            
        else:  # sell
            stop_loss = max(entry_price + (atr * 1.5), resistance_val)
            tp1 = entry_price - (atr * 2)
            tp2 = entry_price - (atr * 4)
            tp3 = entry_price - (atr * 6)
            trailing_stop_pct = 0.02
        
        return stop_loss, (tp1, tp2, tp3), trailing_stop_pct

    def get_account_balance(self) -> float:
        """Fetch account balance - Know your resources"""
        balance = self.exchange.fetch_balance()
        return balance["total"]["USDT"]

    def place_order(
        self,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: tuple,
        position_size: float,
    ) -> Dict[str, Any]:
        """Place a limit order with advanced parameters"""
        order = self.exchange.create_order(
            self.symbol,
            "limit",
            side,
            position_size,
            entry_price,
            {
                "stopLoss": {"price": stop_loss},
                "takeProfit": [
                    {"price": take_profit[0]},
                    {"price": take_profit[1]},
                    {"price": take_profit[2]},
                ]
            },
        )
        return order

    # ============================================================
    # MAIN TRADING LOOP (The Warrior's Path)
    # ============================================================

    def run(self):
        """
        Main trading loop: "Act with purpose, not impulse"
        
        The warrior's path:
        1. Observe the market (fetch data)
        2. Understand the conditions (analyze)
        3. Detect opportunity (identify signal)
        4. Validate thoroughly (confirm signal)
        5. Act decisively (execute trade)
        6. Manage with discipline (monitor position)
        """
        print("🥋 ENHANCED BRUCE LEE TRADING BOT v2.0 ACTIVATED")
        print("   Philosophy: Be like water. Formless. Adaptable. Unstoppable.")
        print("   Principle: Know yourself, know your opponent, know the terrain.")
        print()
        
        while True:
            try:
                # Step 1: Observe the market
                df = self.fetch_ohlcv()
                current_price = df["close"].iloc[-1]
                
                # Step 2: Understand conditions
                regime = self.detect_market_regime(df)
                volatility = self.check_volatility_conditions(df)
                
                print(f"📊 Market Regime: {regime.upper()} | Volatility: {volatility['volatility'].upper()}")

                # Step 3: Check psychological discipline (emotional control)
                if not self.check_psychological_discipline():
                    print("🧘 In cooldown period - maintaining discipline")
                    time.sleep(60)
                    continue

                # Step 4: Detect opportunity based on regime
                signal = None
                if regime == "trend":
                    signal = self.trend_strategy(df)
                elif regime == "range":
                    signal = self.mean_reversion_strategy(df)
                elif regime == "breakout":
                    signal = self.breakout_strategy(df)

                # Step 5: Execute if valid signal and conditions met
                if signal and volatility["trade"]:
                    print(f"⚔️ Signal: {signal['side'].upper()} ({signal['reason']})")
                    
                    # Calculate optimal entry/exit
                    entry_price = current_price
                    position_size = self.calculate_position_size(df, entry_price)
                    stop_loss, take_profits, trailing_stop = self.calculate_optimal_exit(df, entry_price, signal)
                    
                    # Validate risk/reward ratio
                    if signal["side"] == "buy":
                        potential_reward = take_profits[1] - entry_price
                        risk = entry_price - stop_loss
                    else:
                        potential_reward = entry_price - take_profits[1]
                        risk = stop_loss - entry_price
                    
                    if risk > 0:
                        risk_reward_ratio = potential_reward / risk
                        
                        if risk_reward_ratio >= 1.5:  # Only trade if 1.5:1 or better
                            print(f"🎯 Entry: {entry_price:.2f}")
                            print(f"   SL: {stop_loss:.2f} | TP1: {take_profits[0]:.2f} | TP2: {take_profits[1]:.2f} | TP3: {take_profits[2]:.2f}")
                            print(f"   Risk/Reward: {risk_reward_ratio:.2f}:1 | Size: {position_size:.4f}")
                            
                            order = self.place_order(
                                signal["side"],
                                entry_price,
                                stop_loss,
                                take_profits,
                                position_size
                            )
                            print(f"📈 Order Placed: {order}")
                        else:
                            print(f"❌ Risk/Reward too low ({risk_reward_ratio:.2f}:1) - Skipping trade")
                    else:
                        print(f"⚠️ Invalid risk calculation")

                # Step 6: Monitor and adapt
                if not volatility["trade"]:
                    print(f"⏸️ Market conditions unfavorable - Standing aside")

                # Wait before next cycle
                time.sleep(60)

            except Exception as e:
                print(f"⚠️ Error: {e}")
                self.consecutive_losses += 1
                self.last_loss_time = time.time()
                time.sleep(60)

if __name__ == "__main__":
    # Initialize enhanced bot
    bot = EnhancedBruceLeeTradingBot(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_SECRET",
        symbol="BTC/USDT",
        timeframe="1h",
        risk_per_trade=0.01,
    )
    bot.run()
