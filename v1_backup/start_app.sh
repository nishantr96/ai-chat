#!/bin/bash

# Data Chat Interface Startup Script

echo "🚀 Starting Data Chat Interface..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env file from template..."
    cp env_template.txt .env
    echo "💡 Please update .env file with your credentials before using LLM features."
fi

# Find available port
PORT=8501
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    echo "⚠️  Port $PORT is in use, trying next port..."
    PORT=$((PORT + 1))
done

echo "📊 Starting application on port $PORT..."
echo "🌐 Open your browser to: http://localhost:$PORT"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

# Start the application
streamlit run app.py --server.port $PORT --server.headless true 