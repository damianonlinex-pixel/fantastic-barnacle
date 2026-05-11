"""
Configuration file for Bruce Lee Trading Bot
Contains all settings, API configurations, and trading parameters
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class APIConfig:
    """API Configuration for different exchanges"""
    exchange_id: str = "binance"
    api_key: str = os.getenv("EXCHANGE_API_KEY", "YOUR_API_KEY")
    api_secret: str = os.getenv("EXCHANGE_API_SECRET", "YOUR_API_SECRET")
    testnet: bool = True

@dataclass
class TradingConfig:
    """Trading parameters"""
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"
    risk_per_trade: float = 0.01  # 1% risk per trade
    max_daily_loss: float = 0.05  # 5% max daily loss
    initial_balance: float = 10000.0  # For paper trading
    max_positions: int = 3
    
@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    host: str = "0.0.0.0"
    port: int = 8501
    debug: bool = True
    theme: str = "dark"
    refresh_interval: int = 60  # seconds
    
@dataclass
class PaperTradingConfig:
    """Paper trading specific settings"""
    enabled: bool = True
    initial_balance: float = 10000.0
    slippage: float = 0.001  # 0.1% slippage
    commission: float = 0.001  # 0.1% commission

# Global configurations
API_CONFIG = APIConfig()
TRADING_CONFIG = TradingConfig()
DASHBOARD_CONFIG = DashboardConfig()
PAPER_TRADING_CONFIG = PaperTradingConfig()

# Thresholds and parameters
TREND_ADX_THRESHOLD = 25
BREAKOUT_PERIOD = 20
MA_FAST_PERIOD = 9
MA_SLOW_PERIOD = 21
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 1.5
ATR_MULTIPLIER_TP = 3

# Database and logging
DB_PATH = "data/"
LOG_PATH = "logs/"
HISTORY_FILE = f"{DB_PATH}trading_history.json"
PAPER_HISTORY_FILE = f"{DB_PATH}paper_trading_history.json"

os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)
