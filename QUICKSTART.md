# Quick Start Guide

## 🥋 Get Running in 5 Minutes

### Step 1: Clone & Setup (2 minutes)
```bash
# Clone repository
git clone https://github.com/damianonlinex-pixel/fantastic-barnacle.git
cd fantastic-barnacle

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure (1 minute)
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (or use defaults for paper trading)
# For paper trading, you can skip API keys - it uses simulated data
```

### Step 3: Run Dashboard (30 seconds)
```bash
# Start the dashboard
python run.py

# Or manually:
streamlit run dashboard.py
```

**The dashboard opens at:** http://localhost:8501 🚀

---

## 🎯 First Trade (Paper Trading)

1. **Navigate to Sidebar** → Click **📄 Paper Trading**
2. **Click Start Button** → Bot begins monitoring
3. **Watch Dashboard** → See real market data and signals
4. **Check Tabs**:
   - 📊 **Dashboard**: Current price and signals
   - 📈 **Paper Trading**: Account balance and equity
   - 🎯 **Signals & Trades**: Trade history

---

## ⚙️ Configuration Reference

### Quick Config Changes (in sidebar)

**Operating Mode**
- 📄 **Paper Trading**: Test with virtual $10k (no real money at risk)
- 💰 **Live Trading**: Real trading (requires API keys)

**Trading Parameters**
- **Trading Pair**: BTC/USDT, ETH/USDT, etc.
- **Timeframe**: 1m, 5m, 15m, 1h, 4h, 1d
- **Risk per Trade**: 0.1% - 5% (how much of account per trade)
- **Max Daily Loss**: 1% - 10% (stop trading if hit)

**Paper Trading Settings**
- **Initial Balance**: Starting virtual money ($10,000 default)
- **Slippage**: Price difference when entering (0.1% realistic)
- **Commission**: Trading fees (0.1% per trade)

---

## 📊 Understanding the Dashboard

### Status Bar (Top)
- 🟢 **Status**: Running/Stopped/Paused/Error
- **Mode**: Paper or Live
- **Uptime**: How long bot has been running
- **Price**: Current market price

### 📊 Dashboard Tab
- **Candlestick Chart**: Price action
- **Current Signal**: Buy/Sell signal with reason
- **Market Regime**: Trend/Range/Breakout

### 📈 Paper Trading Tab
- **Account Balance**: Virtual money remaining
- **Current Equity**: Balance + unrealized gains/losses
- **Total P&L**: Profit/Loss percentage
- **Equity Curve**: Visual account growth
- **Drawdown Chart**: Largest loss from peak

### 🎯 Signals & Trades Tab
- **Trade Table**: All completed trades
- **Win Rate**: % of profitable trades
- **Trade Stats**: Winning vs losing trades

### 💼 Positions Tab
- **Open Positions**: Current active trades
- **Entry Price**: Price you entered at
- **Quantity**: Amount of crypto held

### 📉 Performance Tab
- **Key Metrics**: Total trades, win rate, profit factor
- **Drawdown**: Maximum account decline
- **Avg Win/Loss**: Average profit/loss per trade

---

## 🤖 How The Bot Works

### Three Strategies (Automatically Selected)

**1. Trend Strategy** 📈
- When market is trending
- Uses 9-period and 21-period moving averages
- Enters on crossover signals

**2. Mean Reversion Strategy** 🔄
- When market is range-bound
- Uses Bollinger Bands
- Enters when price touches extremes

**3. Breakout Strategy** 💥
- When market is breaking out
- Uses 20-period channel breakouts
- Enters on momentum moves

### Risk Management

✅ **Always Active**:
- Risk limited to 1% per trade (adjustable)
- Stop-loss set at 1.5x ATR
- Take-profit set at 3x ATR
- Max 3 concurrent positions
- Daily loss limit of 5%

---

## 🧪 Testing Your Setup

### Test 1: Paper Trading Works
```bash
1. Click "📄 Paper Trading" button
2. Click "▶️ Start" button
3. Wait 60 seconds for first signal
4. Check "📈 Paper Trading" tab for activity
```

### Test 2: Dashboard Responsive
```bash
1. Click "🔄 Refresh Now" button
2. Check if data updates
3. Switch between tabs
4. Verify charts load
```

### Test 3: Configuration Changes
```bash
1. Expand "Trading Parameters" in sidebar
2. Change symbol to ETH/USDT
3. Click "🔄 Refresh Now"
4. Verify chart updates with new pair
```

---

## 📁 Project Structure

```
fantastic-barnacle/
│
├── bruce_lee_bot.py           ← Original bot (don't touch!)
├── config.py                  ← All settings
├── bot_manager.py             ← Bot state tracking
├── paper_trading.py           ← Simulated trading
├── bot_integration.py         ← Dashboard connection
├── dashboard.py               ← The UI you see
│
├── requirements.txt           ← Python packages
├── .env.example              ← Template for API keys
├── run.py                    ← Simple starter script
├── README.md                 ← Full documentation
├── QUICKSTART.md             ← This file
│
├── data/                     ← Trading history
│   ├── trading_history.json
│   ├── paper_trading_history.json
│   └── bot_state.json
│
└── logs/                     ← Error logs
```

---

## 🔧 Troubleshooting

### Dashboard won't start
```bash
# Check Python version (needs 3.8+)
python --version

# Reinstall Streamlit
pip install --upgrade streamlit

# Run with debug info
streamlit run dashboard.py --logger.level=debug
```

### No trades executing
```bash
# Check bot status in sidebar
# Ensure it shows 🟢 RUNNING

# Check "Paper Trading" tab
# Should show activity if running

# Check logs for errors
# Look at console output
```

### API Key errors
```bash
# Paper trading doesn't need real API keys
# For live trading:
# 1. Get real API keys from exchange
# 2. Set testnet=false in .env
# 3. Add keys to .env file
# 4. Restart dashboard
```

---

## 💡 Tips for Success

✅ **Do:**
- Start with paper trading
- Run for at least a week before going live
- Monitor the dashboard regularly
- Keep API keys secure (never commit .env)
- Review trades in the Signals tab
- Use conservative risk settings (1%)

❌ **Don't:**
- Start with live trading immediately
- Use aggressive risk settings (>3%)
- Share your API keys
- Modify the bot code unless you know what you're doing
- Leave the dashboard unattended for days
- Use high leverage on risky assets

---

## 📞 Need Help?

1. **Check README.md** - Full documentation
2. **Review Dashboard** - Check "Settings" tab for current config
3. **Check Logs** - Console output has error messages
4. **Test Paper Trading** - Verify everything works risk-free first

---

## 🚀 Next Steps

1. ✅ Get paper trading working (this guide)
2. 📊 Run for a week, analyze results
3. 📖 Read full README.md
4. ⚙️ Tune strategy parameters
5. 💰 Consider going live with small position

**Remember**: "Be like water, my friend." - The bot adapts to market conditions. Start small, test thoroughly, then scale.

---

**Happy Trading! 🥋📈**
