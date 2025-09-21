#!/bin/bash

# Kitchen API Startup Script

echo "🚀 Starting Kitchen API Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "🌐 Starting API server on http://localhost:8000"
echo "📖 API docs available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

python main.py
