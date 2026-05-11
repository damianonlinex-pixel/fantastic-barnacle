# 🥋 Bruce Lee Trading Bot with Dashboard

A sophisticated trading bot inspired by Bruce Lee's philosophy: "Be like water, my friend." This bot adapts to different market conditions and includes a real-time Streamlit dashboard for monitoring and paper trading simulation.

## 🌟 Features

### Core Bot Capabilities
- **Multi-Strategy Approach**: Adapts between trend-following, mean-reversion, and breakout strategies
- **Market Regime Detection**: Automatically detects market conditions (trending, ranging, breakout)
- **Dynamic Position Sizing**: Risk management based on ATR (Average True Range)
- **Realistic Slippage & Commission**: Paper trading includes realistic market conditions

### Dashboard Features
- **Real-time Monitoring**: Live price charts, market regime detection, and trading signals
- **Paper Trading Account**: Test strategies with realistic conditions before live trading
- **Performance Analytics**: Comprehensive metrics including win rate, drawdown, and profit factor
- **Trading History**: Detailed records of all trades, positions, and signals
- **Easy Controls**: Start/stop/pause bot with simple button clicks

### Paper Trading Engine
- **Exact Same Logic**: Paper trading uses identical strategy logic as live trading
- **Realistic Simulation**: Includes slippage (0.1%) and commission (0.1%)
- **Equity Tracking**: Real-time equity curve and drawdown visualization
- **Performance Stats**: Win rate, profit factor, average win/loss, and more

## 📋 Requirements

- Python 3.8+
- CCXT library for exchange connectivity
- Streamlit for dashboard
- Pandas, NumPy for data processing
- Plotly for interactive charts

See `requirements.txt` for full dependencies.

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/damianonlinex-pixel/fantastic-barnacle.git
cd fantastic-barnacle
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Settings

Edit `config.py` to set your trading parameters:
```python
# API Configuration
API_CONFIG = APIConfig(
    exchange_id="binance",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    testnet=True  # Use testnet first
)

# Trading Parameters
TRADING_CONFIG = TradingConfig(
    symbol="BTC/USDT",
    timeframe="1h",
    risk_per_trade=0.01,  # 1% per trade
    max_daily_loss=0.05,  # 5% max daily loss
)

# Paper Trading
PAPER_TRADING_CONFIG = PaperTradingConfig(
    enabled=True,
    initial_balance=10000.0,  # $10k virtual balance
    slippage=0.001,  # 0.1%
    commission=0.001,  # 0.1%
)
```

## 🎮 Usage

### Start the Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

### Dashboard Sections

1. **📊 Dashboard Tab**
   - Market overview with price action chart
   - Current trading signal (if any)
   - Detected market regime
   - 24h statistics

2. **📈 Paper Trading Tab**
   - Account balance and equity
   - Equity curve visualization
   - Drawdown chart
   - Reset account button

3. **🎯 Signals & Trades Tab**
   - Complete trading history
   - Trade analysis (win rate, winning/losing trades)
   - Detailed trade information

4. **💼 Positions Tab**
   - Current open positions
   - Entry prices and quantities
   - Position management

5. **📉 Performance Tab**
   - Key performance metrics
   - Win rate and profit factor
   - Average win/loss analysis
   - Drawdown statistics

6. **⚙️ Settings Tab**
   - View current configuration
   - Adjust trading parameters
   - API configuration

### Bot Controls

**Sidebar Controls**:
- **📄 Paper Trading**: Start bot in paper trading mode
- **💰 Live Trading**: Switch to live trading (requires API keys)
- **▶️ Start**: Begin bot execution
- **⏸️ Pause**: Pause bot without stopping
- **⏹️ Stop**: Stop bot completely

## 📊 Trading Strategies

### 1. Trend Strategy
- Uses 9-period and 21-period moving averages
- Enters on MA crossover
- Follows the direction of the trend

### 2. Mean Reversion Strategy
- Uses 20-period Bollinger Bands
- Enters when price touches upper/lower bands
- Bets on mean reversion

### 3. Breakout Strategy
- Monitors 20-period channel breakouts
- Enters on price breaking above/below resistance/support
- Captures momentum moves

### Market Regime Detection
The bot automatically selects the best strategy based on ADX (Average Directional Index):
- **ADX > 25**: Trending market → Use Trend Strategy
- **Low ATR**: Range-bound market → Use Mean Reversion
- **Other**: Volatile/breakout environment → Use Breakout Strategy

## 💰 Paper Trading

Paper trading allows you to:
- Test strategies with virtual money
- See realistic P&L with slippage and commission
- Analyze performance before risking real capital
- Compare paper trading results with live trading

### Key Metrics
- **Initial Balance**: Starting capital
- **Current Equity**: Balance + unrealized P&L
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Gross profit / Gross loss
- **Max Drawdown**: Largest peak-to-trough decline
- **P&L Percent**: Total return on investment

## 🔒 Risk Management

- **Risk Per Trade**: Limited to configurable percentage (default 1%)
- **Max Daily Loss**: Daily loss limit stops trading (default 5%)
- **Position Sizing**: Based on ATR and risk percentage
- **Stop Loss**: Always set using ATR multiplier (1.5x)
- **Take Profit**: Set using ATR multiplier (3x)

## 📁 Project Structure

```
fantastic-barnacle/
├── bruce_lee_bot.py          # Original trading bot (UNMODIFIED)
├── config.py                 # Configuration settings
├── bot_manager.py            # Bot state and metrics management
├── paper_trading.py          # Paper trading simulation engine
├── bot_integration.py        # Integration layer for dashboard
├── dashboard.py              # Streamlit dashboard
├── requirements.txt          # Python dependencies
└── data/                     # Data storage directory
    ├── trading_history.json
    ├── paper_trading_history.json
    └── bot_state.json
```

## 🛠️ Configuration Reference

### API Configuration (config.py)
```python
API_CONFIG = APIConfig(
    exchange_id="binance",      # Exchange: binance, coinbase, kraken
    api_key="YOUR_KEY",         # Your API key
    api_secret="YOUR_SECRET",   # Your API secret
    testnet=True                # Use testnet for testing
)
```

### Trading Parameters
```python
TRADING_CONFIG = TradingConfig(
    symbol="BTC/USDT",          # Trading pair
    timeframe="1h",             # 1m, 5m, 15m, 1h, 4h, 1d
    risk_per_trade=0.01,        # 1% per trade
    max_daily_loss=0.05,        # 5% max daily
    initial_balance=10000.0,    # Paper trading balance
    max_positions=3             # Max concurrent positions
)
```

### Paper Trading Parameters
```python
PAPER_TRADING_CONFIG = PaperTradingConfig(
    enabled=True,
    initial_balance=10000.0,    # $10,000 virtual
    slippage=0.001,             # 0.1% slippage
    commission=0.001            # 0.1% per trade
)
```

## 📈 Performance Monitoring

The dashboard tracks:
- **Total Trades**: Number of completed trades
- **Win Rate**: % of profitable trades
- **Avg Win/Loss**: Average profit/loss per trade
- **Profit Factor**: Gross profit / Gross loss ratio
- **Max Drawdown**: Largest decline from peak
- **Equity Curve**: Visual representation of account growth

## 🔄 Auto-Refresh

The dashboard auto-refreshes every 60 seconds when the bot is running:
- Market data updates
- Trading signals
- Performance metrics
- Account equity

## ⚠️ Important Notes

1. **Paper Trading First**: Always test strategies with paper trading before live trading
2. **API Keys**: Store API keys in environment variables, never commit them
3. **Risk Management**: The 1% risk per trade rule protects your capital
4. **Market Hours**: Be aware of exchange trading hours
5. **Slippage Realistic**: Paper trading includes realistic slippage and commission

## 🚨 Troubleshooting

### Dashboard won't start
```bash
# Check if Streamlit is installed
pip install streamlit

# Try running with verbose output
streamlit run dashboard.py --logger.level=debug
```

### Exchange connection errors
1. Verify API keys are correct
2. Check exchange is available (ccxt supports it)
3. Ensure IP whitelist allows your connection
4. Try testnet first

### No trades executing
1. Ensure paper trading is enabled
2. Check market regime detection
3. Verify strategy signal generation
4. Check account has sufficient balance

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- The original bot logic remains unmodified
- Dashboard enhancements improve usability
- All code follows the existing style
- Changes are well-documented

## 📚 References

- [CCXT Documentation](https://docs.ccxt.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Technical Analysis](https://school.stockcharts.com/)

---

**Remember**: "Be like water. The bot adapts to market conditions, not the other way around." - Bruce Lee (adapted)
