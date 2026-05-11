"""
Bot Manager - Manages bot instances, state, and communication
Provides interface between dashboard and trading bot
"""

import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import os

class BotStatus(Enum):
    """Bot operational status"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class BotMode(Enum):
    """Trading mode"""
    PAPER = "paper"
    LIVE = "live"

class BotManager:
    """
    Manages bot lifecycle, state, and metrics
    Provides a centralized interface for dashboard interaction
    """
    
    def __init__(self):
        self.status = BotStatus.STOPPED
        self.mode = BotMode.PAPER
        self.start_time: Optional[datetime] = None
        self.last_update: Optional[datetime] = None
        self.error_message: Optional[str] = None
        
        self.current_signal: Optional[Dict[str, Any]] = None
        self.last_trade: Optional[Dict[str, Any]] = None
        self.current_price: float = 0.0
        self.market_regime: str = "unknown"
        
        self.metrics: Dict[str, Any] = {
            "total_signals": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "failed_trades": 0,
        }
        
        self.state_file = "data/bot_state.json"
        self.metrics_file = "data/bot_metrics.json"
        self._ensure_state_files()
        self._load_state()
    
    def _ensure_state_files(self):
        """Create state files if they don't exist"""
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.state_file):
            self._save_state()
        
        if not os.path.exists(self.metrics_file):
            self._save_metrics()
    
    def start(self, mode: BotMode = BotMode.PAPER):
        """Start the bot"""
        self.status = BotStatus.RUNNING
        self.mode = mode
        self.start_time = datetime.now()
        self.error_message = None
        self._save_state()
        return {"status": "success", "message": f"Bot started in {mode.value} mode"}
    
    def stop(self):
        """Stop the bot"""
        self.status = BotStatus.STOPPED
        self.error_message = None
        self._save_state()
        return {"status": "success", "message": "Bot stopped"}
    
    def pause(self):
        """Pause the bot"""
        self.status = BotStatus.PAUSED
        self._save_state()
        return {"status": "success", "message": "Bot paused"}
    
    def resume(self):
        """Resume the bot"""
        if self.status == BotStatus.PAUSED:
            self.status = BotStatus.RUNNING
            self._save_state()
            return {"status": "success", "message": "Bot resumed"}
        return {"status": "error", "message": "Bot is not paused"}
    
    def set_error(self, error_message: str):
        """Set error status with message"""
        self.status = BotStatus.ERROR
        self.error_message = error_message
        self._save_state()
    
    def update_market_data(
        self,
        current_price: float,
        market_regime: str,
        signal: Optional[Dict[str, Any]] = None,
    ):
        """Update current market data"""
        self.current_price = current_price
        self.market_regime = market_regime
        self.last_update = datetime.now()
        
        if signal:
            self.current_signal = signal
            self.metrics["total_signals"] += 1
        
        self._save_state()
    
    def record_trade(self, trade: Dict[str, Any], success: bool = True):
        """Record a completed trade"""
        self.last_trade = {
            **trade,
            "timestamp": datetime.now().isoformat(),
        }
        self.metrics["trades_executed"] += 1
        
        if success:
            self.metrics["successful_trades"] += 1
        else:
            self.metrics["failed_trades"] += 1
        
        self._save_state()
        self._save_metrics()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current bot state"""
        return {
            "status": self.status.value,
            "mode": self.mode.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "error_message": self.error_message,
            "current_signal": self.current_signal,
            "last_trade": self.last_trade,
            "current_price": self.current_price,
            "market_regime": self.market_regime,
            "uptime_seconds": self._get_uptime_seconds(),
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def _get_uptime_seconds(self) -> int:
        """Calculate bot uptime"""
        if self.start_time and self.status == BotStatus.RUNNING:
            return int((datetime.now() - self.start_time).total_seconds())
        return 0
    
    def _save_state(self):
        """Save bot state to file"""
        state = self.get_state()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving bot state: {e}")
    
    def _load_state(self):
        """Load bot state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.status = BotStatus(state.get("status", "stopped"))
                    self.mode = BotMode(state.get("mode", "paper"))
        except Exception as e:
            print(f"Error loading bot state: {e}")
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def reset(self):
        """Reset bot manager"""
        self.status = BotStatus.STOPPED
        self.mode = BotMode.PAPER
        self.start_time = None
        self.last_update = None
        self.error_message = None
        self.current_signal = None
        self.last_trade = None
        self.current_price = 0.0
        self.market_regime = "unknown"
        self.metrics = {
            "total_signals": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "failed_trades": 0,
        }
        self._save_state()
        self._save_metrics()

# Global bot manager instance
bot_manager = BotManager()
