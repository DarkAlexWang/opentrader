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

## Configuration

Edit `config/config.json` to control:

- Strategy parameters (entry/exit logic, hold times)
- Risk settings (position sizes, daily loss limits, drawdown limits)
- Watchlist (symbols to trade)
- Backtest dates and initial capital

## Trading Timeline

- **Week 1:** Backtesting phase (validate strategy on 2+ years of data)
- **Week 2:** Paper trading phase (live market data, simulated execution)
- **Week 3+:** Live trading with $1000 starting capital

## Strategies

### Momentum Trading
- Entry: Stock breaks above 20-day resistance + volume spike ≥20%
- Exit: Stop loss -2.3%, Take profit +5% (50%) and +10% (50%), or 6-hour timeout
- Risk: 1-2% per trade

### Options Spreads
- Strategy: Bull/bear call spreads on IV expansion
- IV Threshold: >70th percentile
- Risk: Up to 4% per trade
- Hold: 1-2 weeks to expiration

## Testing

Run full test suite:

```bash
pytest tests/ -v
```

## Disclaimer

This bot uses real capital when in live mode. **Trade at your own risk.** Always validate strategies thoroughly in backtesting and paper trading before going live. Losses are possible.

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
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

## Next Steps

1. Run backtesting to validate strategies
2. Switch to paper trading for 1 week
3. Deploy to live trading with initial $1000 capital
4. Monitor performance and iterate

Happy trading! 📈
