#!/bin/bash
# Start script for AiResearcher application

cd "$(dirname "$0")"

# Verify environment configuration
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create it with your GOOGLE_API_KEY"
    echo "   Example: echo 'GOOGLE_API_KEY=your_key_here' > .env"
    exit 1
fi

# Start the application
echo "🚀 Starting AiResearcher..."
streamlit run app.py




