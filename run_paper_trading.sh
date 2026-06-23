#!/bin/bash
# Wrapper script for automated paper trading
# Called by launchd at 9:30 AM EST on trading days

PROJECT_DIR="$HOME/Projects/opentrader"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/paper_trading_$(date +%Y%m%d).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log start time
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting paper trading..." >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR"

# Run paper trading
python paper_trader.py >> "$LOG_FILE" 2>&1

# Log completion
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Paper trading completed" >> "$LOG_FILE"

# Exit gracefully
exit 0
