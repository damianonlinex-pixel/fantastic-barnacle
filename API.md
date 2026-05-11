# Bruce Lee Trading Bot - API Documentation

## Overview

This document describes the integration between the dashboard, bot manager, and paper trading engine.

## Core Components

### 1. BotManager (bot_manager.py)

Manages bot state, status, and metrics.

#### Methods

```python
bot_manager.start(mode: BotMode) -> Dict
# Start the bot in PAPER or LIVE mode

bot_manager.stop() -> Dict
# Stop the bot

bot_manager.pause() -> Dict
# Pause without stopping

bot_manager.resume() -> Dict
# Resume from pause

bot_manager.get_state() -> Dict
# Get current bot state

bot_manager.get_metrics() -> Dict
# Get performance metrics

bot_manager.update_market_data(current_price, market_regime, signal)
# Update market information

bot_manager.record_trade(trade, success)
# Record a completed trade
```

#### State Structure

```json
{
  "status": "running|stopped|paused|error",
  "mode": "paper|live",
  "start_time": "ISO timestamp",
  "current_price": 0.0,
  "market_regime": "trend|range|breakout",
  "current_signal": {
    "side": "buy|sell",
    "reason": "string"
  }
}
```

### 2. PaperTradingEngine (paper_trading.py)

Simulates trading with realistic slippage and commission.

#### Methods

```python
engine.create_order(
    symbol: str,
    side: str,  # "buy" or "sell"
    quantity: float,
    price: float,
    order_type: str = "limit",
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
) -> Dict
# Create and execute a trade order

engine.get_balance() -> float
# Get current cash balance

engine.get_equity(current_prices: Dict) -> float
# Get total equity (balance + unrealized P&L)

engine.get_positions() -> Dict
# Get all open positions

engine.get_trades(limit: int = 50) -> List
# Get recent closed trades

engine.get_statistics(current_prices: Dict) -> Dict
# Get performance statistics

engine.get_summary(current_prices: Dict) -> Dict
# Get complete account summary
```

#### Order Response

```json
{
  "order_id": "string",
  "status": "filled|pending|rejected",
  "symbol": "BTC/USDT",
  "side": "buy|sell",
  "quantity": 0.0,
  "price": 0.0,
  "commission": 0.0,
  "timestamp": "ISO timestamp"
}
```

#### Trade Record

```json
{
  "trade_id": "string",
  "symbol": "BTC/USDT",
  "entry_price": 0.0,
  "exit_price": 0.0,
  "quantity": 0.0,
  "pnl": 0.0,
  "pnl_percent": 0.0,
  "entry_time": "ISO timestamp",
  "exit_time": "ISO timestamp"
}
```

### 3. BotIntegrationLayer (bot_integration.py)

Connects the dashboard with trading logic and paper trading.

#### Methods

```python
integration.start()
# Start the trading loop

integration.stop()
# Stop trading loop

integration.pause()
# Pause trading

integration.resume()
# Resume trading

integration.execute_trading_cycle()
# Run one complete trading cycle

integration.fetch_market_data(limit: int = 100) -> pd.DataFrame
# Get OHLCV data
```

## Dashboard Usage

### Importing in Streamlit App

```python
from bot_manager import bot_manager, BotMode
from paper_trading import paper_trading_engine
from bot_integration import integration

# Get current state
state = bot_manager.get_state()
metrics = bot_manager.get_metrics()

# Get trading summary
summary = paper_trading_engine.get_summary(current_prices)

# Record a trade
bot_manager.record_trade({
    "symbol": "BTC/USDT",
    "entry_price": 50000,
    "exit_price": 51000,
    "quantity": 1.0
})
```

## Configuration

All settings are in `config.py`:

```python
# API Configuration
API_CONFIG.exchange_id = "binance"
API_CONFIG.api_key = "YOUR_KEY"
API_CONFIG.api_secret = "YOUR_SECRET"

# Trading Config
TRADING_CONFIG.symbol = "BTC/USDT"
TRADING_CONFIG.timeframe = "1h"
TRADING_CONFIG.risk_per_trade = 0.01  # 1%

# Paper Trading Config
PAPER_TRADING_CONFIG.initial_balance = 10000.0
PAPER_TRADING_CONFIG.slippage = 0.001  # 0.1%
PAPER_TRADING_CONFIG.commission = 0.001  # 0.1%
```

## Event Flow

### Trading Cycle

1. **Fetch Market Data** → Get OHLCV from exchange
2. **Calculate Indicators** → ATR, ADX, moving averages
3. **Detect Regime** → Identify trend/range/breakout
4. **Generate Signal** → Select strategy and produce signal
5. **Execute Order** → If signal, create order in paper trading
6. **Record Trade** → Save trade data for analysis
7. **Update State** → Sync to bot manager

### Data Persistence

All data is saved to JSON files in `data/` directory:

- `bot_state.json` - Current bot state
- `bot_metrics.json` - Performance metrics
- `trading_history.json` - All trades
- `paper_trading_history.json` - Paper trading account state

## Performance Calculations

### Win Rate
```
Win Rate = (Winning Trades / Total Trades) × 100
```

### Profit Factor
```
Profit Factor = Gross Profit / Gross Loss
```

### Max Drawdown
```
Max Drawdown = (Peak Equity - Trough Equity) / Peak Equity × 100
```

### P&L Percent
```
P&L % = (Current Equity - Initial Balance) / Initial Balance × 100
```

## Error Handling

### Error States

- **Insufficient Balance**: Order rejected if not enough funds
- **Invalid Price**: Orders with invalid prices are rejected
- **API Errors**: Caught and logged, status set to ERROR
- **Data Errors**: Missing data points are skipped

### Recovery

All errors are logged and stored in `bot_state.json`:

```json
{
  "status": "error",
  "error_message": "Description of error"
}
```

## Testing

### Unit Test Example

```python
from paper_trading import PaperTradingEngine

engine = PaperTradingEngine(initial_balance=10000)

# Create a buy order
order = engine.create_order(
    symbol="BTC/USDT",
    side="buy",
    quantity=0.1,
    price=50000
)

assert order["status"] == "filled"
assert engine.get_balance() < 10000  # Balance decreased
```

## Rate Limiting

CCXT exchange connections have rate limiting enabled:

```python
self.exchange = ccxt.binance({
    "enableRateLimit": True
})
```

Each trading cycle waits 60 seconds to respect rate limits.

## Security Considerations

1. **API Keys**: Never commit .env file
2. **Testnet**: Use testnet for initial testing
3. **Risk Management**: Always use conservative risk settings
4. **Position Limits**: Max 3 concurrent positions by default
5. **Daily Loss Limit**: Stops trading after 5% daily loss

## Extending the System

### Adding a New Strategy

```python
# In bot_integration.py
def custom_strategy(self, df: pd.DataFrame) -> Optional[Dict]:
    # Your strategy logic here
    if signal_condition:
        return {"side": "buy", "reason": "Custom strategy signal"}
    return None

# In execute_trading_cycle()
if self.market_regime == "custom":
    signal = self.custom_strategy(df)
```

### Adding a New Metric

```python
# In bot_manager.py
self.metrics["custom_metric"] = 0

def update_custom_metric(self, value):
    self.metrics["custom_metric"] = value
    self._save_metrics()
```

## License

MIT License - See LICENSE file
