# 🥋 Bruce Lee Trading Bot - Complete Setup Guide

## 📍 WHERE TO PUT ALL THE FILES

### For Windows Users:

```
C:\Users\YourUsername\Desktop\fantastic-barnacle\
  ├── bruce_lee_bot.py          ← Your original bot file
  ├── config.py                 ← Settings file
  ├── bot_manager.py            ← Bot state management
  ├── paper_trading.py          ← Paper trading engine
  ├── bot_integration.py        ← Bot + Dashboard connection
  ├── dashboard.py              ← Main Streamlit app
  ├── run.py                    ← Quick start script
  ├── requirements.txt          ← Python packages
  ├── .env                      ← Your API keys (create this)
  ├── README.md                 ← Documentation
  ├── .streamlit/
  │   └── config.toml          ← Dashboard settings
  ├── data/                     ← Auto-created folder
  └── venv/                     ← Virtual environment (created)
```

### For Mac/Linux Users:

```
~/fantastic-barnacle/
  ├── bruce_lee_bot.py
  ├── config.py
  ├── bot_manager.py
  ├── paper_trading.py
  ├── bot_integration.py
  ├── dashboard.py
  ├── run.py
  ├── requirements.txt
  ├── .env
  ├── README.md
  ├── .streamlit/
  │   └── config.toml
  ├── data/
  └── venv/
```

---

## 🖥️ HOW TO RUN (Choose Your OS)

### 🪟 WINDOWS (PowerShell)

#### Step 1: Open PowerShell in Your Project Folder

```
1. Press Windows Key + R
2. Type: powershell
3. Press Enter
4. Navigate to your folder:
```

```powershell
cd C:\Users\YourUsername\Desktop\fantastic-barnacle
```

#### Step 2: Create & Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it (IMPORTANT - do this every time!)
.\venv\Scripts\Activate.ps1
```

**Your prompt should now show:**
```
(venv) PS C:\...\fantastic-barnacle>
```

If you get an error about execution policy, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Install Python Packages

```powershell
pip install -r requirements.txt
```

Wait for this to finish (2-5 minutes).

#### Step 4: Run the Dashboard

```powershell
python run.py
```

**Your browser should automatically open:**
```
http://localhost:8501
```

If not, open your browser and type that URL manually.

#### Step 5: Use the Bot

In the dashboard:
1. Click **"📄 Paper Trading"** in the sidebar
2. Click **"▶️ Start"** to begin
3. Watch the magic happen! ✨

**To stop the bot:**
```powershell
# Press Ctrl + C in the PowerShell window
```

---

### 🍎 macOS (Terminal)

#### Step 1: Open Terminal

```
1. Press Cmd + Space
2. Type: terminal
3. Press Enter
4. Navigate to your folder:
```

```bash
cd ~/fantastic-barnacle
```

#### Step 2: Create & Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

**Your prompt should now show:**
```
(venv) user@MacBook fantastic-barnacle %
```

#### Step 3: Install Python Packages

```bash
pip install -r requirements.txt
```

#### Step 4: Run the Dashboard

```bash
python run.py
```

**Browser opens automatically at:**
```
http://localhost:8501
```

#### Step 5: Use the Bot

Same as Windows - click buttons in the sidebar!

**To stop:**
```
Press Ctrl + C
```

---

### 🐧 Linux (Bash Terminal)

#### Step 1: Open Terminal

```
Press Ctrl + Alt + T
Navigate to folder:
```

```bash
cd ~/fantastic-barnacle
```

#### Step 2: Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Packages

```bash
pip install -r requirements.txt
```

#### Step 4: Run Dashboard

```bash
python run.py
```

#### Step 5: Use Bot

Click buttons in sidebar like Windows/Mac!

**To stop:**
```
Ctrl + C
```

---

## 🎯 QUICK COMMANDS REFERENCE

### Always Do These First (Every Time)

**Windows:**
```powershell
cd C:\your\project\path
.\venv\Scripts\Activate.ps1
python run.py
```

**Mac/Linux:**
```bash
cd ~/your/project/path
source venv/bin/activate
python run.py
```

### Common Commands

| What You Want | Windows | Mac/Linux |
|---|---|---|
| Start dashboard | `python run.py` | `python run.py` |
| Install packages | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Stop bot | `Ctrl + C` | `Ctrl + C` |
| Deactivate venv | `deactivate` | `deactivate` |
| Check Python version | `python --version` | `python3 --version` |

---

## 📊 DASHBOARD WALKTHROUGH

Once the dashboard opens in your browser:

### 1️⃣ First Look (Status Bar at Top)

```
🟢 Status: STOPPED    |    Mode: PAPER    |    Uptime: 0h 0m    |    Price: $XXXXX
```

### 2️⃣ Sidebar Controls (Left Side)

**🥋 Bruce Lee Bot Control**

```
Operating Mode:
┌─────────────────────────────┐
│ 📄 Paper Trading │ 💰 Live  │
└─────────────────────────────┘

Bot Controls:
┌─────────────────────────────┐
│ ▶️ Start │ ⏸️ Pause │ ⏹️ Stop  │
└─────────────────────────────┘
```

### 3️⃣ Steps to Start Trading

```
1. Click "📄 Paper Trading" button
   ↓
2. Click "▶️ Start" button
   ↓
3. See status change to "🟢 RUNNING"
   ↓
4. Wait 60 seconds for first market check
   ↓
5. Check "📈 Paper Trading" tab for your account
   ↓
6. See trades in "🎯 Signals & Trades" tab
```

### 4️⃣ Tabs Overview

| Tab | What It Shows |
|---|---|
| 📊 Dashboard | Current price, market signals |
| 📈 Paper Trading | Your virtual account & equity |
| 🎯 Signals & Trades | All trades you made |
| 💼 Positions | Active open positions |
| 📉 Performance | Win rate, profit factor |
| ⚙️ Settings | Configuration details |

---

## 🔐 API KEYS (For Live Trading Only)

### Paper Trading (TEST - No API Keys Needed!)

```
Just click "📄 Paper Trading" and you're ready!
Uses simulated market data - perfect for testing
```

### Live Trading (Real Money - NEED API KEYS)

#### Get Binance Testnet Keys (Recommended First)

```
1. Go to: https://testnet.binance.vision/
2. Click "Generate HMAC SHA256 Key"
3. Copy the API Key and Secret
4. Paste them in your .env file
```

#### Get Real Binance Keys (Only After Testing!)

```
1. Go to: https://www.binance.com/
2. Login
3. Click Profile → API Management
4. Click "Create API"
5. Name it "Trading Bot"
6. Enable "Enable Spot & Margin Trading"
7. Whitelist your IP
8. Copy API Key and Secret
9. Add to .env file
```

### Where to Put Keys

Create a `.env` file in your project folder:

**Contents of .env:**
```
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
```

**IMPORTANT:** Never share this file! Never commit it to GitHub!

---

## ✅ VERIFICATION CHECKLIST

After setup, verify everything works:

- [ ] Folder structure matches the diagram above
- [ ] Virtual environment created and activated
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] `.env` file created (optional for paper trading)
- [ ] `python run.py` starts dashboard
- [ ] Browser opens to http://localhost:8501
- [ ] Dashboard shows status bar at top
- [ ] Sidebar shows bot controls
- [ ] Can click "📄 Paper Trading"
- [ ] Can click "▶️ Start"
- [ ] Status changes to "🟢 RUNNING"
- [ ] Tabs show data

---

## 🚀 FIRST RUN WORKFLOW

### Day 1: Setup

```
1. Clone/download files
2. Create virtual environment
3. Install requirements
4. Run dashboard
5. Click "Paper Trading" + "Start"
6. Let it run for 1 hour
```

### Day 2-7: Test Paper Trading

```
1. Check dashboard daily
2. Review trades in "Signals & Trades" tab
3. Watch equity curve grow/shrink
4. Analyze win rate and performance
5. Decide if strategy is good
```

### Week 2+: Consider Live Trading

```
1. If win rate > 50% and profit factor good
2. Get real API keys
3. Start with TINY amount (like $10)
4. Monitor closely for first week
5. Increase position size gradually
```

---

## ⚠️ COMMON ERRORS & FIXES

### Error: "No module named 'streamlit'"

**Fix:**
```powershell
# Windows
pip install streamlit

# Or reinstall everything:
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError"

**Fix:**
```
Make sure you:
1. Have venv activated (see (venv) in prompt)
2. Ran pip install -r requirements.txt
3. Are in the right folder
```

### Error: "Could not connect to exchange"

**Fix:**
1. Check API keys are correct
2. Use testnet first (not real keys)
3. Verify exchange supports CCXT
4. Check your internet connection

### Dashboard loads but nothing shows

**Fix:**
```
1. Refresh page (Ctrl + R)
2. Click "🔄 Refresh Now" button
3. Wait 60 seconds for data
4. Check browser console for errors
```

### Bot won't start

**Fix:**
1. Check status shows "RUNNING"
2. Look for error message in dashboard
3. Check console for error output
4. Try clicking "Start" again

---

## 📚 FILE DESCRIPTIONS

| File | What It Does |
|---|---|
| `bruce_lee_bot.py` | Your original bot (NEVER MODIFY) |
| `config.py` | All settings in one place |
| `bot_manager.py` | Tracks bot status and metrics |
| `paper_trading.py` | Simulates trades with realistic fees |
| `bot_integration.py` | Connects bot to dashboard |
| `dashboard.py` | The Streamlit UI you see |
| `run.py` | Quick start script |
| `requirements.txt` | List of Python packages to install |
| `.env` | Your secret API keys |
| `README.md` | Full documentation |
| `API.md` | Developer API docs |

---

## 💾 DATA STORAGE

Your trading data is saved automatically:

```
data/
  ├── bot_state.json              ← Current status
  ├── bot_metrics.json            ← Performance stats
  ├── trading_history.json        ← All orders
  └── paper_trading_history.json  ← Paper trades
```

You can backup these files to keep your history!

---

## 🎓 LEARNING PATH

1. **Read This Document** ← You are here!
2. **Run Dashboard** - Get it working first
3. **Paper Trade 1 Week** - See if strategy works
4. **Read README.md** - Understand all features
5. **Tune Settings** - Adjust parameters
6. **Go Live (Carefully)** - Start very small

---

## 🆘 NEED HELP?

### Check These Files in Order:

1. **README.md** - Full documentation
2. **API.md** - Developer documentation
3. **QUICKSTART.md** - Quick reference guide

### If Still Stuck:

1. Check console output for error messages
2. Verify folder structure matches diagram
3. Ensure venv is activated
4. Make sure all packages installed
5. Try stopping and starting dashboard again

---

## 🎉 YOU'RE READY!

Your setup is complete. Now:

1. Open terminal/PowerShell
2. Navigate to project folder
3. Activate venv
4. Run `python run.py`
5. Click "Paper Trading" in dashboard
6. Click "Start"
7. Watch your bot trade!

---

**Remember: Always test with paper trading first!** 🥋

"Be like water, my friend." - Bruce Lee
