# OpenTrader

Automated trading bot for momentum stocks and options spreads with backtesting, paper trading, and live execution on Robinhood.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Strategies

Edit `config/config.json` with your strategy parameters and watchlist.

### 3. Setup Robinhood Credentials (Optional)

Copy `config/secrets.example.json` to `config/secrets.json` and add your credentials:

```json
{
  "robinhood": {
    "username": "your_email@example.com",
    "password": "your_password"
  }
}
```

## Usage

### Optimize Strategy Parameters

**Quick optimization (10 combinations):**
```bash
python optimize.py
```

**Comprehensive optimization (1000 combinations + stability testing):**
```bash
python optimize_1000.py
```
This tests 1000 parameter combinations and runs the best strategy 10 times across different time periods to verify stability. Runtime: ~5 minutes.

### Backtesting

Validate strategies on historical data:

```bash
python main.py --mode backtest
```

### Paper Trading

Test with live data but no real money:

```bash
python main.py --mode paper
```

### Live Trading

Trade with real capital on Robinhood:

```bash
python main.py --mode live
```

## Architecture

- **Data Layer** (`src/data/`): Market data fetching and technical indicators
- **Strategies** (`src/strategies/`): Momentum and options spread logic
- **Execution** (`src/execution/`): Backtesting, paper trading, and live execution
- **Risk** (`src/risk/`): Position sizing and portfolio risk management
- **Monitoring** (`src/monitoring/`): Trade logging and terminal dashboard
- **Optimization** (`src/execution/optimizer.py`): Parameter search and backtesting engine

## Configuration

Edit `config/config.json` to control:

- Strategy parameters (SMA periods, entry/exit logic, hold times)
- Risk settings (position sizes, daily loss limits, drawdown limits)
- Watchlist (symbols to trade)
- Backtest dates and initial capital

## Strategy Parameters

The strategy uses Golden Cross (SMA crossover) momentum trading:

- **SMA Fast Period**: Fast-moving simple average (detects trends quickly)
- **SMA Slow Period**: Slow-moving simple average (confirms trend)
- **Take Profit %**: Exit profit target (e.g., 6% = sell at +6% gain)
- **Stop Loss %**: Exit loss limit (e.g., 3% = sell at -3% loss)

### Example Configuration

```json
"momentum": {
  "resistance_period": 15,
  "stop_loss_pct": 0.03,
  "take_profit_target_1": 0.06,
  "take_profit_target_2": 0.06
}
```

## Parameter Optimization

The bot includes two optimization scripts:

1. **optimize.py** - Tests 10 parameter combinations
   - Fast execution (~30 seconds)
   - Good for quick validation

2. **optimize_1000.py** - Tests 1000 parameter combinations
   - Comprehensive search (~5 minutes)
   - Tests broader parameter ranges
   - Runs best strategy 10 times on different time windows
   - Reports average performance and stability

**Search Space (optimize_1000.py):**
- SMA Fast: 5-20
- SMA Slow: 25-60
- Take Profit: 2%-10%
- Stop Loss: 1%-4%

## Trading Timeline

- **Week 1:** Parameter optimization + backtesting
- **Week 2:** Paper trading phase (live market data, simulated execution)
- **Week 3+:** Live trading with $1000 starting capital

## Testing

Run full test suite:

```bash
pytest tests/ -v
```

## Disclaimer

This bot uses real capital when in live mode. **Trade at your own risk.** Always validate strategies thoroughly in optimization, backtesting, and paper trading before going live. Losses are possible.

## Project Structure

```
opentrader/
├── src/
│   ├── strategies/          # Trading strategies
│   ├── data/                # Market data & indicators
│   ├── execution/           # Order execution engines
│   ├── risk/                # Position management
│   ├── monitoring/          # Logging & dashboard
│   ├── config/              # Configuration system
│   └── opentrader.py        # Main orchestrator
├── config/
│   ├── config.json          # Strategy & risk params
│   └── secrets.example.json # Credentials template
├── tests/                   # Test suite
├── optimize.py              # Quick optimization (10 combos)
├── optimize_1000.py         # Full optimization (1000 combos)
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

## Next Steps

1. Run `python optimize_1000.py` to find optimal strategy
2. Review results and stability metrics
3. Test in paper trading mode for 1 week
4. Deploy to live trading if profitable

Happy trading! 📈
