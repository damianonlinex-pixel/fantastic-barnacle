"""
Paper Trading Engine
Simulates trading with exact same logic as live trading
Includes realistic slippage and commission
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderType(Enum):
    """Order type"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"

class PaperTradingEngine:
    """
    Paper trading simulation engine
    Simulates trades with realistic slippage and commissions
    """
    
    def __init__(
        self,
        initial_balance: float = 10000.0,
        slippage: float = 0.001,  # 0.1%
        commission: float = 0.001,  # 0.1%
    ):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.slippage = slippage
        self.commission = commission
        
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []
        self.equity_history: List[Dict[str, Any]] = []
        
        self.start_time = datetime.now()
        self.last_update = datetime.now()
        
        self.history_file = "data/paper_trading_history.json"
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Ensure history file exists"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.history_file):
            self._save_history()
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def get_equity(self, current_prices: Dict[str, float]) -> float:
        """Calculate total equity (balance + unrealized P&L)"""
        equity = self.balance
        
        for symbol, position in self.positions.items():
            if position["quantity"] > 0:
                current_price = current_prices.get(symbol, position["entry_price"])
                unrealized_pnl = (current_price - position["entry_price"]) * position["quantity"]
                equity += unrealized_pnl
        
        return equity
    
    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_type: str = "limit",
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create an order"""
        order_id = str(uuid.uuid4())[:8]
        
        # Apply slippage
        slipped_price = self._apply_slippage(price, side)
        
        # Calculate cost with commission
        order_cost = quantity * slipped_price
        commission_cost = order_cost * self.commission
        total_cost = order_cost + commission_cost
        
        # Check if we have enough balance for buy orders
        if side.lower() == "buy" and total_cost > self.balance:
            return {
                "order_id": order_id,
                "status": OrderStatus.REJECTED.value,
                "reason": f"Insufficient balance. Required: {total_cost:.2f}, Available: {self.balance:.2f}",
                "timestamp": datetime.now().isoformat(),
            }
        
        # Create order
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side.lower(),
            "quantity": quantity,
            "price": price,
            "slipped_price": slipped_price,
            "order_type": order_type,
            "status": OrderStatus.FILLED.value,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "created_at": datetime.now().isoformat(),
            "filled_at": datetime.now().isoformat(),
            "commission": commission_cost,
        }
        
        # Execute order
        if side.lower() == "buy":
            self._execute_buy(symbol, quantity, slipped_price, commission_cost, order_id)
        elif side.lower() == "sell":
            self._execute_sell(symbol, quantity, slipped_price, commission_cost, order_id)
        
        self.orders.append(order)
        self.last_update = datetime.now()
        self._save_history()
        
        return order
    
    def _apply_slippage(self, price: float, side: str) -> float:
        """Apply realistic slippage to price"""
        if side.lower() == "buy":
            return price * (1 + self.slippage)
        else:  # sell
            return price * (1 - self.slippage)
    
    def _execute_buy(
        self,
        symbol: str,
        quantity: float,
        price: float,
        commission: float,
        order_id: str,
    ):
        """Execute buy order"""
        cost = quantity * price + commission
        self.balance -= cost
        
        if symbol not in self.positions:
            self.positions[symbol] = {
                "quantity": 0,
                "entry_price": 0,
                "entry_time": None,
                "orders": [],
            }
        
        # Calculate weighted average entry price
        pos = self.positions[symbol]
        total_quantity = pos["quantity"] + quantity
        
        if total_quantity > 0:
            pos["entry_price"] = (
                (pos["quantity"] * pos["entry_price"]) + (quantity * price)
            ) / total_quantity
        
        pos["quantity"] = total_quantity
        pos["entry_time"] = datetime.now().isoformat()
        pos["orders"].append(order_id)
    
    def _execute_sell(
        self,
        symbol: str,
        quantity: float,
        price: float,
        commission: float,
        order_id: str,
    ):
        """Execute sell order"""
        if symbol not in self.positions or self.positions[symbol]["quantity"] < quantity:
            return False
        
        pos = self.positions[symbol]
        proceeds = quantity * price - commission
        self.balance += proceeds
        
        # Record trade
        pnl = (price - pos["entry_price"]) * quantity
        pnl_percent = (pnl / (pos["entry_price"] * quantity)) * 100 if pos["entry_price"] > 0 else 0
        
        trade = {
            "trade_id": str(uuid.uuid4())[:8],
            "symbol": symbol,
            "entry_price": pos["entry_price"],
            "exit_price": price,
            "quantity": quantity,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "entry_time": pos["entry_time"],
            "exit_time": datetime.now().isoformat(),
            "order_id": order_id,
        }
        self.trades.append(trade)
        
        # Update position
        pos["quantity"] -= quantity
        pos["orders"].append(order_id)
        
        if pos["quantity"] == 0:
            del self.positions[symbol]
        
        return True
    
    def close_position(self, symbol: str, current_price: float) -> Optional[Dict[str, Any]]:
        """Close a position at current market price"""
        if symbol not in self.positions or self.positions[symbol]["quantity"] <= 0:
            return None
        
        quantity = self.positions[symbol]["quantity"]
        return self.create_order(
            symbol=symbol,
            side="sell",
            quantity=quantity,
            price=current_price,
            order_type="market",
        )
    
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get all open positions"""
        return self.positions.copy()
    
    def get_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent orders"""
        return self.orders[-limit:]
    
    def get_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades"""
        return self.trades[-limit:]
    
    def get_statistics(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculate trading statistics"""
        if not self.trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "total_pnl_percent": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "max_drawdown": 0,
                "profit_factor": 0,
            }
        
        closed_trades = self.trades
        winning_trades = [t for t in closed_trades if t["pnl"] > 0]
        losing_trades = [t for t in closed_trades if t["pnl"] < 0]
        
        total_pnl = sum(t["pnl"] for t in closed_trades)
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        
        avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        gross_profit = sum(t["pnl"] for t in winning_trades)
        gross_loss = abs(sum(t["pnl"] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        current_equity = self.get_equity(current_prices)
        total_pnl_percent = ((current_equity - self.initial_balance) / self.initial_balance * 100)
        
        # Calculate max drawdown (simplified)
        max_drawdown = self._calculate_max_drawdown()
        
        return {
            "total_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "max_drawdown": max_drawdown,
            "profit_factor": profit_factor,
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.equity_history:
            return 0.0
        
        max_equity = self.initial_balance
        max_drawdown = 0.0
        
        for entry in self.equity_history:
            if entry["equity"] > max_equity:
                max_equity = entry["equity"]
            
            drawdown = (max_equity - entry["equity"]) / max_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown * 100
    
    def record_equity_snapshot(self, current_prices: Dict[str, float]):
        """Record equity snapshot for drawdown calculation"""
        equity = self.get_equity(current_prices)
        self.equity_history.append({
            "timestamp": datetime.now().isoformat(),
            "equity": equity,
        })
    
    def get_summary(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Get complete trading summary"""
        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "current_equity": self.get_equity(current_prices),
            "positions": self.get_positions(),
            "orders": len(self.orders),
            "trades": len(self.trades),
            "statistics": self.get_statistics(current_prices),
            "start_time": self.start_time.isoformat(),
            "last_update": self.last_update.isoformat(),
        }
    
    def reset(self):
        """Reset paper trading account"""
        self.balance = self.initial_balance
        self.positions = {}
        self.orders = []
        self.trades = []
        self.equity_history = []
        self.start_time = datetime.now()
        self.last_update = datetime.now()
        self._save_history()
    
    def _save_history(self):
        """Save trading history to file"""
        history = {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "orders": self.orders,
            "trades": self.trades,
            "positions": self.positions,
            "start_time": self.start_time.isoformat(),
            "last_update": self.last_update.isoformat(),
        }
        
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving paper trading history: {e}")
    
    def load_history(self):
        """Load trading history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    self.balance = history.get("current_balance", self.initial_balance)
                    self.orders = history.get("orders", [])
                    self.trades = history.get("trades", [])
                    self.positions = history.get("positions", {})
        except Exception as e:
            print(f"Error loading paper trading history: {e}")

# Global paper trading engine
paper_trading_engine = PaperTradingEngine()
