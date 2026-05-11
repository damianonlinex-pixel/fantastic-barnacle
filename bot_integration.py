"""
Bot Integration Layer
Connects the Bruce Lee Trading Bot with Dashboard and Paper Trading Engine
Does NOT modify the original bot - only interfaces with it
"""

import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime
import ccxt
import pandas as pd
import numpy as np

from config import TRADING_CONFIG, API_CONFIG, PAPER_TRADING_CONFIG
from bot_manager import bot_manager, BotStatus, BotMode
from paper_trading import paper_trading_engine

class BotIntegrationLayer:
    """
    Integration layer between the Bruce Lee Trading Bot and the Dashboard
    Manages bot execution, market data fetching, and paper trading simulation
    """
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.exchange = None
        self.current_price = 0.0
        self.market_regime = "unknown"
        
    def initialize_exchange(self):
        """Initialize exchange connection"""
        try:
            self.exchange = getattr(ccxt, API_CONFIG.exchange_id)({
                "apiKey": API_CONFIG.api_key,
                "secret": API_CONFIG.api_secret,
                "enableRateLimit": True,
            })
            return True
        except Exception as e:
            bot_manager.set_error(f"Exchange initialization failed: {str(e)}")
            return False
    
    def fetch_market_data(self, limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from exchange"""
        try:
            if not self.exchange:
                self.initialize_exchange()
            
            ohlcv = self.exchange.fetch_ohlcv(
                TRADING_CONFIG.symbol,
                TRADING_CONFIG.timeframe,
                limit=limit
            )
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR (from original bot logic)"""
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ADX (from original bot logic)"""
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
    
    def detect_market_regime(self, df: pd.DataFrame) -> str:
        """Detect market regime (Jeet Kune Do: no fixed style)"""
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
    
    def trend_strategy(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Trend-following strategy"""
        df["fast_ma"] = df["close"].rolling(9).mean()
        df["slow_ma"] = df["close"].rolling(21).mean()
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        if latest["fast_ma"] > latest["slow_ma"] and prev["fast_ma"] <= prev["slow_ma"]:
            return {"side": "buy", "reason": "MA crossover up"}
        elif latest["fast_ma"] < latest["slow_ma"] and prev["fast_ma"] >= prev["slow_ma"]:
            return {"side": "sell", "reason": "MA crossover down"}
        return None
    
    def mean_reversion_strategy(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Mean-reversion strategy"""
        df["ma"] = df["close"].rolling(20).mean()
        df["std"] = df["close"].rolling(20).std()
        df["upper_band"] = df["ma"] + 2 * df["std"]
        df["lower_band"] = df["ma"] - 2 * df["std"]
        latest = df.iloc[-1]
        
        if latest["close"] <= latest["lower_band"]:
            return {"side": "buy", "reason": "Price at lower Bollinger Band"}
        elif latest["close"] >= latest["upper_band"]:
            return {"side": "sell", "reason": "Price at upper Bollinger Band"}
        return None
    
    def breakout_strategy(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Breakout strategy"""
        df["upper_channel"] = df["high"].rolling(20).max()
        df["lower_channel"] = df["low"].rolling(20).min()
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        if latest["close"] > latest["upper_channel"] and prev["close"] <= prev["upper_channel"]:
            return {"side": "buy", "reason": "Breakout above resistance"}
        elif latest["close"] < latest["lower_channel"] and prev["close"] >= prev["lower_channel"]:
            return {"side": "sell", "reason": "Breakdown below support"}
        return None
    
    def execute_trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # Fetch market data
            df = self.fetch_market_data()
            if df is None:
                return
            
            # Update current price
            self.current_price = df["close"].iloc[-1]
            
            # Detect market regime
            self.market_regime = self.detect_market_regime(df)
            
            # Select strategy based on regime
            signal = None
            if self.market_regime == "trend":
                signal = self.trend_strategy(df)
            elif self.market_regime == "range":
                signal = self.mean_reversion_strategy(df)
            elif self.market_regime == "breakout":
                signal = self.breakout_strategy(df)
            
            # Update bot manager with current state
            bot_manager.update_market_data(
                current_price=self.current_price,
                market_regime=self.market_regime,
                signal=signal
            )
            
            # Execute signal if present and in paper trading mode
            if signal and bot_manager.mode == BotMode.PAPER:
                self._execute_signal(signal, df)
            
            # Record equity snapshot
            paper_trading_engine.record_equity_snapshot({TRADING_CONFIG.symbol: self.current_price})
            
        except Exception as e:
            bot_manager.set_error(str(e))
            print(f"Error in trading cycle: {e}")
    
    def _execute_signal(self, signal: Dict[str, Any], df: pd.DataFrame):
        """Execute a trading signal in paper trading mode"""
        try:
            entry_price = df["close"].iloc[-1]
            atr = self.calculate_atr(df).iloc[-1]
            
            # Calculate position sizing
            stop_distance = atr * 1.5
            risk_amount = TRADING_CONFIG.risk_per_trade * paper_trading_engine.get_balance()
            position_size = risk_amount / stop_distance if stop_distance > 0 else 0
            
            if position_size <= 0:
                return
            
            # Calculate stop loss and take profit
            if signal["side"].lower() == "buy":
                stop_loss = entry_price - (atr * 1.5)
                take_profit = entry_price + (atr * 3)
            else:  # sell
                stop_loss = entry_price + (atr * 1.5)
                take_profit = entry_price - (atr * 3)
            
            # Create order in paper trading
            order = paper_trading_engine.create_order(
                symbol=TRADING_CONFIG.symbol,
                side=signal["side"],
                quantity=position_size,
                price=entry_price,
                order_type="market",
                stop_loss=stop_loss,
                take_profit=take_profit,
            )
            
            # Record trade if order was successful
            if order["status"] == "filled":
                bot_manager.record_trade({
                    "order_id": order["order_id"],
                    "symbol": TRADING_CONFIG.symbol,
                    "side": signal["side"],
                    "quantity": position_size,
                    "entry_price": entry_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": signal["reason"],
                })
        
        except Exception as e:
            print(f"Error executing signal: {e}")
    
    def start(self):
        """Start the bot integration layer"""
        if self.running:
            return
        
        self.running = True
        bot_manager.start()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the bot integration layer"""
        self.running = False
        bot_manager.stop()
        if self.thread:
            self.thread.join(timeout=5)
    
    def pause(self):
        """Pause the bot"""
        self.running = False
        bot_manager.pause()
    
    def resume(self):
        """Resume the bot"""
        self.running = True
        bot_manager.resume()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def _run_loop(self):
        """Main bot execution loop"""
        while self.running:
            try:
                self.execute_trading_cycle()
                time.sleep(60)  # Run every minute
            except Exception as e:
                bot_manager.set_error(str(e))
                time.sleep(60)

# Global integration layer instance
integration = BotIntegrationLayer()
