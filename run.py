#!/usr/bin/env python3
"""
Entry point for running the dashboard and bot
Simply run: python run.py
"""

import subprocess
import sys
import os

def main():
    """
    Run the Streamlit dashboard
    """
    print("🥋 Bruce Lee Trading Bot Dashboard")
    print("===================================\n")
    
    # Check if requirements are installed
    try:
        import streamlit
        import ccxt
        import plotly
        print("✅ All dependencies installed\n")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall with: pip install -r requirements.txt\n")
        sys.exit(1)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("🚀 Starting dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501\n")
    
    # Run Streamlit
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "dashboard.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

if __name__ == "__main__":
    main()
