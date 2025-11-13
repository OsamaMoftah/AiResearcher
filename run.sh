#!/bin/bash
# Start script for AiResearcher application

set -e  # Exit on error

cd "$(dirname "$0")"

echo "🔬 AiResearcher - Starting Application..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required"
    echo "   Current version: Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Verify environment configuration
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found. Please create it with your GOOGLE_API_KEY"
    echo "   You can copy the example file and add your API key:"
    echo ""
    echo "   cp .env.example .env"
    echo "   echo 'GOOGLE_API_KEY=your_key_here' > .env"
    echo ""
    echo "   Get your API key from: https://aistudio.google.com/app/apikey"
    echo ""
    exit 1
fi

echo "✓ Configuration file found"

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo ""
    echo "⚠️  Dependencies not installed. Installing..."
    pip3 install -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Start the application
echo ""
echo "🚀 Starting Streamlit server..."
echo "   Open your browser at: http://localhost:8501"
echo ""

streamlit run app.py
