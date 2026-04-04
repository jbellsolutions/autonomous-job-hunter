#!/bin/bash

# 🚀 Autonomous Job Hunter - Auto-Setup Script
# This script automates the entire environment configuration.

set -e

echo "------------------------------------------------"
echo "🛠️ Starting Autonomous Job Hunter Setup..."
echo "------------------------------------------------"

# 1. Check Python Version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.11 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version $PYTHON_VERSION is compatible."

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# 3. Install Dependencies
echo "📥 Installing dependencies (this may take a minute)..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright Browsers
echo "🌐 Installing Playwright browser dependencies..."
playwright install chromium

# 5. Handle .env Configuration
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from example..."
        cp .env.example .env
        echo "⚠️  Action Required: Open .env and add your OPENAI_API_KEY."
    else
        echo "⚠️  Warning: .env.example not found. Creating a blank .env..."
        echo "OPENAI_API_KEY=your_key_here" > .env
        echo "BROWSER_CONTEXT_PATH=./user_data" >> .env
    fi
else
    echo "✅ .env file already exists."
fi

echo "------------------------------------------------"
echo "🎉 Setup Complete!"
echo "------------------------------------------------"
echo "To start hunting jobs, run:"
echo "source venv/bin/activate"
echo "python3 main.py --platform [linkedin|upwork|onlinejobs]"
echo "------------------------------------------------"
