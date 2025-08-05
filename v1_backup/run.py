#!/usr/bin/env python3
"""
Simple run script for the Data Chat Interface.
This script starts the Streamlit application.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the Streamlit application."""
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  Warning: .env file not found!")
        print("📝 Please copy .env.example to .env and configure your credentials.")
        print("💡 You can still run the app with mock data for testing.")
        print()
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected!")
        print("💡 Consider running: python -m venv venv && source venv/bin/activate")
        print()
    
    # Start Streamlit
    print("🚀 Starting Data Chat Interface...")
    print("📊 Open your browser to: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure you have installed the requirements: pip install -r requirements.txt")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found!")
        print("💡 Install requirements: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main() 