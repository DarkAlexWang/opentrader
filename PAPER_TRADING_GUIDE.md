# Paper Trading Guide

## Overview

Paper trading allows you to test the optimized strategy with real market data using simulated execution. No real money is deployed, but all trades are recorded and analyzed.

## Features

- ✅ **Real Market Data**: Fetches live quotes from Yahoo Finance
- ✅ **Simulated Execution**: All trades are simulated (no real orders)
- ✅ **Live Dashboard**: Real-time portfolio updates every 30 seconds
- ✅ **Trade Logging**: All trades recorded for performance analysis
- ✅ **Market Hours Detection**: Automatically runs only during US market hours
- ✅ **Risk Management**: Enforces position sizing and stop losses
- ✅ **Performance Tracking**: Shows P&L, win rate, and trade statistics

## Usage

### Start Paper Trading

```bash
python paper_trader.py
```

The script will:
1. Check if market is open (9:30 AM - 4:00 PM EST, Mon-Fri)
2. Initialize paper trading account with $1000
3. Run live trading simulation
4. Update positions every 30 seconds
5. Execute trades based on strategy signals
6. Show live dashboard updates

### What to Expect

**During Market Hours:**
```
[02:45 PM] Checking market data... ✓ Updated 3 symbols

💰 Portfolio Status:
   Cash:          $950.00
   Positions:     1
   Total Value:   $1050.00
   Day P&L:       +$50.00
   Total P&L:     +$50.00 (+5.00%)

📈 Open Positions:
   AAPL: 10 shares @ $150.00 → $155.00 (+3.33%, +$50.00)
```

**Market Closed:**
```
⏸️  Market closed at 04:00 PM EST
Paper trading will resume next trading day at 9:30 AM EST
```

## Performance Metrics

The paper trader tracks:
- **Cash**: Available capital for new positions
- **Positions**: Open trades with entry/current price
- **P&L**: Unrealized and realized profits/losses
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted returns
- **Drawdown**: Maximum loss from peak

## Backtest vs Paper Trading

| Aspect | Backtest | Paper Trading |
|--------|----------|---------------|
| **Data** | Historical (2022-2024) | Live market data |
| **Execution** | Instant, perfect fills | Simulated market fills |
| **Slippage** | Not modeled | 0.01% assumed |
| **Commissions** | 0.001% | 0.001% |
| **Speed** | Fast (seconds) | Real-time (minutes to hours) |
| **Use Case** | Strategy validation | Real trading preparation |

## Paper vs Live Trading

### Paper Trading
- ✅ Same strategy as backtesting
- ✅ Real market data and conditions
- ✅ No real capital at risk
- ✅ Reveals slippage and execution issues
- ✅ Tests risk management in real scenarios
- ✅ Typically run for 1 week

### Live Trading
- ✅ Real capital deployment
- ✅ Real order execution
- ✅ Real P&L impact
- ✅ Only after successful paper trading
- ✅ Start with small position size ($1000)

## Typical Paper Trading Schedule

**Week 1: Paper Trading**
- Run during market hours (9:30 AM - 4:00 PM EST)
- Monitor daily P&L and trade execution
- Compare results to backtest expectations
- Note any slippage or execution differences

**If Successful (positive P&L):**
- Proceed to live trading with optimized parameters
- Start with $1000 capital
- Monitor first 2 weeks closely

**If Unsuccessful (negative P&L):**
- Investigate root cause
- Check for strategy fit vs market conditions
- Consider parameter adjustments
- Run another week of paper trading

## Monitoring Tips

1. **Check Daily**: Review trades and P&L each day
2. **Compare to Backtest**: Expect ±5% variance from backtest
3. **Watch for Issues**: Slippage, gaps, execution delays
4. **Track Wins/Losses**: Monitor win rate (target: >50%)
5. **Monitor Drawdown**: Should not exceed 10%

## Next Steps After Paper Trading

```bash
# After successful week of paper trading:
python main.py --mode live
```

This will:
1. Connect to Robinhood
2. Execute real orders
3. Risk your capital
4. Require monitoring

## Safety Precautions

- ⚠️ Never skip paper trading before going live
- ⚠️ Start with small capital ($1000 recommended)
- ⚠️ Monitor actively - don't set and forget
- ⚠️ Have stop loss discipline - stick to SL=1.8%
- ⚠️ Track slippage vs backtest expectations

## Troubleshooting

**"No data available"**
- Check internet connection
- Verify symbols in watchlist
- Ensure market is open

**"Market closed"**
- Paper trading only runs 9:30 AM - 4:00 PM EST
- Wait for market to open Monday-Friday
- Weekend/holiday: no trading

**P&L differs from backtest**
- Normal variation (±5%)
- Real slippage vs simulated
- Market conditions may differ
- Run full week for statistical significance

## Configuration

Paper trading uses:
- **Strategy**: SMA(13, 36) TP=10% SL=1.8%
- **Capital**: $1000
- **Risk**: 2% per trade (stocks)
- **Market Hours**: 9:30 AM - 4:00 PM EST
- **Trade Frequency**: Based on momentum signals

## Expected Results

Based on backtesting:
- **Estimated Return**: +2% to +21% per week
- **Win Rate**: 72.5% average
- **Max Drawdown**: <5%
- **Trade Frequency**: 1-2 trades per day

## Duration

Run paper trading for **1 full week** (5 trading days) before going live.

This allows:
- ✅ Collection of statistical data
- ✅ Observation of different market conditions
- ✅ Verification of strategy performance
- ✅ Confidence in live deployment

---

Ready to trade? Start paper trading now:
```bash
python paper_trader.py
```
