#!/bin/bash
# Setup script for the AI Social Media Pipeline
# Run this once: bash setup.sh

set -e

echo "=== AI Social Media Pipeline Setup ==="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Install Python 3.10+ first."
    exit 1
fi

echo "Python: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your actual credentials:"
    echo "   - GEMINI_API_KEY (from aistudio.google.com)"
    echo "   - GMAIL_ADDRESS"
    echo "   - GMAIL_APP_PASSWORD (from myaccount.google.com/apppasswords)"
    echo ""
fi

# Create log directory
mkdir -p logs

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Test: source venv/bin/activate && python task1_news_monitor.py"
echo "  3. Set up scheduling (see README below)"
echo ""
echo "=== macOS Scheduling (cron) ==="
echo "Run 'crontab -e' and add:"
echo ""
echo "  # AI Social Pipeline — News Monitor (every 30 min, 8am-10pm)"
echo "  */30 8-22 * * * cd ~/social-pipeline && source venv/bin/activate && python task1_news_monitor.py"
echo ""
echo "  # AI Social Pipeline — Daily Content (8am daily)"
echo "  0 8 * * * cd ~/social-pipeline && source venv/bin/activate && python task2_daily_content.py"
echo ""
echo "  # AI Social Pipeline — Weekly Review Prompt (9am Sundays)"
echo "  0 9 * * 0 cd ~/social-pipeline && source venv/bin/activate && python task3_weekly_performance.py --prompt"
echo ""
