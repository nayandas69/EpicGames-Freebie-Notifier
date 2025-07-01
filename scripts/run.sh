#!/bin/bash

# Epic Games Discord Bot Run Script

set -e

echo "🎮 Starting Epic Games Discord Bot..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p data logs

# Run the bot
echo "🚀 Starting bot..."
python main.py