# Automatic Paper Trading Setup

This guide shows how to set up automatic paper trading execution at 9:30 AM EST every trading day on macOS.

## Overview

- **Runs**: Monday-Friday at 9:30 AM EST (market open)
- **Method**: macOS launchd (native scheduler)
- **Logs**: Saved to `logs/paper_trading_YYYYMMDD.log`
- **No manual start needed**: Fully automatic

## Installation (One-time setup)

### Step 1: Make the script executable

```bash
chmod +x ~/Projects/opentrader/run_paper_trading.sh
```

### Step 2: Install the launchd agent

```bash
cp ~/Projects/opentrader/com.opentrader.papertrading.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.opentrader.papertrading.plist
```

### Step 3: Verify installation

```bash
launchctl list | grep opentrader
```

Expected output:
```
- 0	com.opentrader.papertrading
```

## How It Works

1. **Monday-Friday at 9:30 AM EST**: launchd triggers the script
2. **Script runs**: `run_paper_trading.sh` starts `paper_trader.py`
3. **Trading begins**: Paper trading runs with live market data
4. **Logs saved**: Results logged to `logs/paper_trading_YYYYMMDD.log`
5. **4:00 PM EST**: Script stops when market closes

## Monitoring

### View today's log

```bash
tail -f ~/Projects/opentrader/logs/paper_trading_$(date +%Y%m%d).log
```

### View launchd logs

```bash
tail -f ~/Projects/opentrader/logs/launchd.log
```

### Check if service is running

```bash
ps aux | grep paper_trader
```

## Managing the Service

### Stop the automatic service

```bash
launchctl unload ~/Library/LaunchAgents/com.opentrader.papertrading.plist
```

### Start the automatic service

```bash
launchctl load ~/Library/LaunchAgents/com.opentrader.papertrading.plist
```

### Restart the service

```bash
launchctl unload ~/Library/LaunchAgents/com.opentrader.papertrading.plist
launchctl load ~/Library/LaunchAgents/com.opentrader.papertrading.plist
```

## Scheduling Details

The agent runs at **9:30 AM EST** on:
- Monday (Weekday 1)
- Tuesday (Weekday 2)
- Wednesday (Weekday 3)
- Thursday (Weekday 4)
- Friday (Weekday 5)

Note: 9:30 AM EST = 14:30 UTC (converted to 24-hour format in plist)

## Troubleshooting

### Service not running

Check if it's loaded:
```bash
launchctl list | grep opentrader
```

If not listed, install it:
```bash
launchctl load ~/Library/LaunchAgents/com.opentrader.papertrading.plist
```

### No logs generated

1. Check if script is executable:
   ```bash
   ls -la ~/Projects/opentrader/run_paper_trading.sh
   ```
   Should show `-rwxr-xr-x`

2. Check launchd error log:
   ```bash
   cat ~/Projects/opentrader/logs/launchd_error.log
   ```

### Permissions issues

Ensure directories exist and are writable:
```bash
mkdir -p ~/Projects/opentrader/logs
chmod 755 ~/Projects/opentrader/logs
```

## Manual Testing

Test the script manually:
```bash
bash ~/Projects/opentrader/run_paper_trading.sh
```

This will:
1. Create necessary directories
2. Run paper trading
3. Log output to `logs/paper_trading_YYYYMMDD.log`

## Logs Location

All logs are stored in:
```
~/Projects/opentrader/logs/
```

Daily logs:
```
paper_trading_20260623.log  (today's trading)
paper_trading_20260620.log  (Friday's trading)
```

System logs:
```
launchd.log         (standard output)
launchd_error.log   (error messages)
```

## What Gets Logged

Each day's log includes:
- Start time
- Market data updates
- Trade executions
- Portfolio updates
- P&L tracking
- Completion time

Example:
```
[2026-06-23 14:30:00] Starting paper trading...
[2026-06-23 14:30:15] ✓ Paper trading account initialized with $1000.00
[2026-06-23 14:30:45] [02:30 PM] Checking market data... ✓ Updated 3 symbols
[2026-06-23 14:30:45] 💰 Portfolio Status:
...
[2026-06-23 16:00:00] Paper trading completed
```

## Next Steps

1. **Install the service**: Follow installation steps above
2. **Wait for next trading day**: 9:30 AM EST Monday
3. **Check logs**: Review `logs/paper_trading_YYYYMMDD.log`
4. **Monitor P&L**: Track daily performance
5. **After 1 week**: If successful, go live

## Live Trading

After successful paper trading week:
```bash
python main.py --mode live
```

This will deploy real capital on Robinhood.

---

**Installed and ready!** Paper trading will now run automatically every trading day at 9:30 AM EST.
