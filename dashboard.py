"""
Bruce Lee Trading Bot Dashboard
Modern, intuitive Streamlit dashboard for monitoring and controlling the bot
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import ccxt
import time
from typing import Dict, Any, Optional

from config import TRADING_CONFIG, DASHBOARD_CONFIG, PAPER_TRADING_CONFIG, API_CONFIG
from bot_manager import bot_manager, BotStatus, BotMode
from paper_trading import paper_trading_engine

# Page configuration
st.set_page_config(
    page_title="🥋 Bruce Lee Trading Bot",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            padding: 20px;
        }
        .metric-card {
            background-color: #1f1f1f;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .status-running {
            color: #00ff00;
            font-weight: bold;
        }
        .status-stopped {
            color: #ff0000;
            font-weight: bold;
        }
        .status-paused {
            color: #ffaa00;
            font-weight: bold;
        }
        .status-error {
            color: #ff3333;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Dashboard"
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

def get_status_color(status: str) -> str:
    """Get color based on status"""
    status_colors = {
        "running": "🟢",
        "stopped": "🔴",
        "paused": "🟠",
        "error": "🔴",
    }
    return status_colors.get(status, "⚪")

def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"

def fetch_market_data(symbol: str = TRADING_CONFIG.symbol) -> Optional[pd.DataFrame]:
    """Fetch OHLCV data from exchange"""
    try:
        exchange = getattr(ccxt, API_CONFIG.exchange_id)(
            {
                "apiKey": API_CONFIG.api_key,
                "secret": API_CONFIG.api_secret,
                "enableRateLimit": True,
            }
        )
        ohlcv = exchange.fetch_ohlcv(symbol, TRADING_CONFIG.timeframe, limit=100)
        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return None

def create_price_chart(df: pd.DataFrame) -> go.Figure:
    """Create candlestick chart"""
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="OHLC"
        )
    ])
    
    fig.update_layout(
        title="Price Action",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        height=500,
        hovermode='x unified',
    )
    
    return fig

def create_equity_chart(trades: list) -> go.Figure:
    """Create equity curve"""
    if not trades:
        return go.Figure().add_annotation(text="No trades yet")
    
    equity_values = []
    equity = PAPER_TRADING_CONFIG.initial_balance
    timestamps = []
    
    for trade in trades:
        equity += trade.get("pnl", 0)
        equity_values.append(equity)
        timestamps.append(trade.get("exit_time", ""))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=equity_values,
        mode='lines',
        name='Equity',
        line=dict(color='#00ff00', width=2),
        fill='tozeroy',
        fillcolor='rgba(0,255,0,0.2)',
    ))
    
    fig.update_layout(
        title="Equity Curve (Paper Trading)",
        yaxis_title="Equity (USDT)",
        xaxis_title="Time",
        template="plotly_dark",
        height=400,
        hovermode='x unified',
    )
    
    return fig

def create_drawdown_chart(trades: list) -> go.Figure:
    """Create drawdown chart"""
    if not trades:
        return go.Figure().add_annotation(text="No trades yet")
    
    equity_values = []
    equity = PAPER_TRADING_CONFIG.initial_balance
    
    for trade in trades:
        equity += trade.get("pnl", 0)
        equity_values.append(equity)
    
    max_equity = PAPER_TRADING_CONFIG.initial_balance
    drawdowns = []
    
    for eq in equity_values:
        if eq > max_equity:
            max_equity = eq
        drawdown = ((max_equity - eq) / max_equity * 100) if max_equity > 0 else 0
        drawdowns.append(drawdown)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=drawdowns,
        mode='lines',
        name='Drawdown',
        line=dict(color='#ff3333', width=2),
        fill='tozeroy',
        fillcolor='rgba(255,51,51,0.2)',
    ))
    
    fig.update_layout(
        title="Drawdown (%)",
        yaxis_title="Drawdown %",
        template="plotly_dark",
        height=400,
        hovermode='x unified',
    )
    
    return fig

# Sidebar
with st.sidebar:
    st.markdown("## 🥋 Bruce Lee Bot Control")
    
    # Mode selection
    st.markdown("### Operating Mode")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Paper Trading", use_container_width=True):
            bot_manager.start(BotMode.PAPER)
            st.session_state.bot_running = True
    
    with col2:
        if st.button("💰 Live Trading", use_container_width=True):
            st.warning("⚠️ Live trading requires verified API keys")
    
    # Bot controls
    st.markdown("### Bot Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            bot_manager.start()
            st.session_state.bot_running = True
            st.success("Bot started!")
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            bot_manager.pause()
            st.info("Bot paused")
    
    with col3:
        if st.button("⏹️ Stop", use_container_width=True):
            bot_manager.stop()
            st.session_state.bot_running = False
            st.info("Bot stopped")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    
    with st.expander("Trading Parameters", expanded=False):
        symbol = st.text_input("Trading Pair", value=TRADING_CONFIG.symbol)
        timeframe = st.selectbox(
            "Timeframe",
            ["1m", "5m", "15m", "1h", "4h", "1d"],
            index=3
        )
        risk = st.slider("Risk per Trade (%)", 0.1, 5.0, TRADING_CONFIG.risk_per_trade * 100) / 100
        max_loss = st.slider("Max Daily Loss (%)", 1.0, 10.0, TRADING_CONFIG.max_daily_loss * 100) / 100
    
    with st.expander("Paper Trading Settings", expanded=False):
        initial_balance = st.number_input(
            "Initial Balance (USDT)",
            value=PAPER_TRADING_CONFIG.initial_balance,
            step=100.0
        )
        slippage = st.slider("Slippage (%)", 0.0, 1.0, PAPER_TRADING_CONFIG.slippage * 100) / 100
        commission = st.slider("Commission (%)", 0.0, 1.0, PAPER_TRADING_CONFIG.commission * 100) / 100
    
    with st.expander("API Configuration", expanded=False):
        exchange = st.selectbox("Exchange", ["binance", "coinbase", "kraken"])
        api_key = st.text_input("API Key", value="", type="password")
        api_secret = st.text_input("API Secret", value="", type="password")
    
    # Refresh settings
    st.markdown("### 🔄 Refresh")
    refresh_interval = st.slider("Refresh Interval (seconds)", 5, 300, 60)
    
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

# Main content
st.markdown("# 🥋 Bruce Lee Trading Bot Dashboard")

# Get current state
state = bot_manager.get_state()
metrics = bot_manager.get_metrics()

# Status bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    status = state["status"]
    status_emoji = get_status_color(status)
    st.metric(
        label="Status",
        value=f"{status_emoji} {status.upper()}",
        help="Current bot operational status"
    )

with col2:
    mode = state["mode"]
    st.metric(
        label="Mode",
        value=mode.upper(),
        help="Trading mode (Paper/Live)"
    )

with col3:
    uptime = state.get("uptime_seconds", 0)
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    st.metric(
        label="Uptime",
        value=f"{hours}h {minutes}m",
        help="Bot running time"
    )

with col4:
    st.metric(
        label="Current Price",
        value=format_currency(state.get("current_price", 0)),
        help="Last recorded price"
    )

# Error display
if state.get("error_message"):
    st.error(f"⚠️ Error: {state['error_message']}")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard",
    "📈 Paper Trading",
    "🎯 Signals & Trades",
    "💼 Positions",
    "📉 Performance",
    "⚙️ Settings"
])

# Dashboard Tab
with tab1:
    st.markdown("## Market Overview")
    
    try:
        df = fetch_market_data(TRADING_CONFIG.symbol)
        if df is not None:
            # Price chart
            st.plotly_chart(create_price_chart(df), use_container_width=True)
            
            # Market stats
            col1, col2, col3, col4 = st.columns(4)
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            with col1:
                st.metric("Current Price", format_currency(latest['close']))
            
            with col2:
                change = latest['close'] - prev['close']
                change_pct = (change / prev['close'] * 100) if prev['close'] > 0 else 0
                st.metric("24h Change", f"{change_pct:.2f}%", delta=change_pct)
            
            with col3:
                st.metric("24h High", format_currency(df['high'].max()))
            
            with col4:
                st.metric("24h Low", format_currency(df['low'].min()))
    
    except Exception as e:
        st.error(f"Could not load market data: {e}")
    
    # Trading signals
    st.markdown("## Current Trading Signal")
    
    if state.get("current_signal"):
        signal = state["current_signal"]
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if signal["side"].upper() == "BUY":
                st.markdown("# 📈 BUY")
            else:
                st.markdown("# 📉 SELL")
        
        with col2:
            st.info(f"**Reason:** {signal.get('reason', 'N/A')}")
    else:
        st.info("No active signal")
    
    # Market regime
    st.markdown("## Market Regime")
    regime = state.get("market_regime", "unknown").upper()
    regime_colors = {
        "TREND": "🔵",
        "RANGE": "🟡",
        "BREAKOUT": "🟢",
        "UNKNOWN": "⚪"
    }
    emoji = regime_colors.get(regime, "⚪")
    st.metric("Detected Regime", f"{emoji} {regime}")

# Paper Trading Tab
with tab2:
    st.markdown("## Paper Trading Account")
    
    trades = paper_trading_engine.get_trades()
    current_prices = {TRADING_CONFIG.symbol: state.get("current_price", 0)}
    summary = paper_trading_engine.get_summary(current_prices)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Initial Balance",
            format_currency(summary["initial_balance"])
        )
    
    with col2:
        st.metric(
            "Current Balance",
            format_currency(summary["current_balance"])
        )
    
    with col3:
        current_equity = summary["current_equity"]
        st.metric(
            "Current Equity",
            format_currency(current_equity)
        )
    
    with col4:
        pnl = current_equity - summary["initial_balance"]
        pnl_pct = (pnl / summary["initial_balance"] * 100) if summary["initial_balance"] > 0 else 0
        st.metric(
            "Total P&L",
            format_currency(pnl),
            delta=f"{pnl_pct:.2f}%"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_equity_chart(trades), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_drawdown_chart(trades), use_container_width=True)
    
    # Reset button
    if st.button("🔄 Reset Paper Trading Account"):
        paper_trading_engine.reset()
        st.success("Paper trading account reset!")
        st.rerun()

# Signals & Trades Tab
with tab3:
    st.markdown("## Trading History")
    
    trades = paper_trading_engine.get_trades()
    
    if trades:
        trades_df = pd.DataFrame(trades)
        trades_df['entry_time'] = pd.to_datetime(trades_df['entry_time'])
        trades_df['exit_time'] = pd.to_datetime(trades_df['exit_time'])
        
        # Display trades table
        display_trades = trades_df[[
            'symbol', 'entry_price', 'exit_price', 'quantity', 'pnl', 'pnl_percent'
        ]].copy()
        
        display_trades = display_trades.rename(columns={
            'symbol': 'Symbol',
            'entry_price': 'Entry',
            'exit_price': 'Exit',
            'quantity': 'Qty',
            'pnl': 'P&L',
            'pnl_percent': 'P&L %'
        })
        
        st.dataframe(display_trades, use_container_width=True)
        
        # Trade analysis
        col1, col2, col3 = st.columns(3)
        
        winning = len([t for t in trades if t['pnl'] > 0])
        losing = len([t for t in trades if t['pnl'] < 0])
        
        with col1:
            st.metric("Winning Trades", winning)
        
        with col2:
            st.metric("Losing Trades", losing)
        
        with col3:
            win_rate = (winning / len(trades) * 100) if trades else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
    else:
        st.info("No trades yet")

# Positions Tab
with tab4:
    st.markdown("## Open Positions")
    
    positions = paper_trading_engine.get_positions()
    
    if positions:
        pos_data = []
        for symbol, pos in positions.items():
            pos_data.append({
                'Symbol': symbol,
                'Quantity': pos['quantity'],
                'Entry Price': format_currency(pos['entry_price']),
                'Entry Time': pos['entry_time']
            })
        
        pos_df = pd.DataFrame(pos_data)
        st.dataframe(pos_df, use_container_width=True)
    else:
        st.info("No open positions")

# Performance Tab
with tab5:
    st.markdown("## Performance Metrics")
    
    trades = paper_trading_engine.get_trades()
    current_prices = {TRADING_CONFIG.symbol: state.get("current_price", 0)}
    stats = paper_trading_engine.get_statistics(current_prices)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", stats['total_trades'])
    
    with col2:
        st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
    
    with col3:
        st.metric("Profit Factor", f"{stats['profit_factor']:.2f}")
    
    with col4:
        st.metric("Max Drawdown", f"{stats['max_drawdown']:.2f}%")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Win", format_currency(stats['avg_win']))
    
    with col2:
        st.metric("Avg Loss", format_currency(stats['avg_loss']))
    
    with col3:
        st.metric("Total P&L %", f"{stats['total_pnl_percent']:.2f}%")

# Settings Tab
with tab6:
    st.markdown("## Configuration Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Trading Config")
        st.text_input("Symbol", value=TRADING_CONFIG.symbol, disabled=True)
        st.text_input("Timeframe", value=TRADING_CONFIG.timeframe, disabled=True)
        st.number_input("Risk per Trade", value=TRADING_CONFIG.risk_per_trade, disabled=True)
    
    with col2:
        st.markdown("### Paper Trading Config")
        st.number_input("Initial Balance", value=PAPER_TRADING_CONFIG.initial_balance, disabled=True)
        st.number_input("Slippage", value=PAPER_TRADING_CONFIG.slippage, disabled=True)
        st.number_input("Commission", value=PAPER_TRADING_CONFIG.commission, disabled=True)
    
    st.markdown("### Dashboard Info")
    st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"Refresh Interval: {refresh_interval}s")

# Auto-refresh
if st.session_state.bot_running:
    time.sleep(1)
    st.rerun()
