# Automated Trading Bot Design Spec

**Date:** 2026-06-21  
**Project:** OpenTrader  
**Objective:** Build an automated trading bot for momentum stocks and options spreads with backtesting, paper trading, and live execution on Robinhood.

---

## 1. Overview

This is a Python-based algorithmic trading system that automates momentum-driven stock trades and options spread strategies on Robinhood. The system includes backtesting capabilities for strategy validation, paper trading for live market simulation, and live trading execution with real capital.

**Starting capital:** $1000  
**Risk management:** 1-2% per trade (stocks), up to 4% (options)  
**Timeline:** 1 week backtesting → 1 week paper trading → live trading

---

## 2. Strategies

### 2.1 Momentum Trading (Stocks)

**Signal Generation:**
- Entry: Stock breaks above 20-day resistance with volume spike ≥20% above 20-day average
- Exit signals:
  - Hard stop loss: 2-3% below entry price
  - Take profit targets: Scale out (50% position at +5%, 50% at +10%)
  - Time-based exit: Close if no movement after 4-6 hours

**Position Management:**
- Risk per trade: 1-2% of account ($10-20 on $1000)
- Max concurrent momentum positions: 2-3
- Hold duration: Intraday to 6 hours max (day trading focus)
- Trading hours: 9:30 AM - 4:00 PM EST

**Technical Indicators:**
- RSI (14): Avoid oversold (<20) entries, take profit on overbought (>70)
- Bollinger Bands (20, 2): Entry on breakout above upper band + volume
- Volume MA (20): Confirm with volume spike
- ATR (14): Adjust stop loss based on volatility

### 2.2 Options Spreads

**Strategies:**
- Bull call spreads: Buy near ATM call, sell higher strike call
- Bear call spreads: Sell OTM call, buy higher strike call
- Timing: 1-2 weeks to expiration

**Signal Generation:**
- Entry: Stock near support/resistance + IV rank >70th percentile
- Exit: 50% max profit target, or hold to expiration if profitable
- Risk per spread: 4% of account ($40 on $1000, typically spread width × 100)
- Max concurrent spreads: 1-2

**Greeks Management:**
- Target delta: 0.30-0.50 (modest directional bias)
- Monitor theta decay (favorable for spreads)
- Close if delta drops below 0.10 (losing value too fast)

---

## 3. System Architecture

### 3.1 High-Level Data Flow

```
Data Source (yfinance)
    ↓
Strategy Engine (momentum + options logic)
    ├→ Backtesting Module (historical replay, validation)
    ├→ Paper Trading Module (live data, simulated execution)
    └→ Live Trading Module (real execution via robin_stocks)
    
Risk Management Layer
    └→ Position Manager (sizing, stops, profit targets)
    
Monitoring & Logging
    └→ Terminal Dashboard, Trade History
```

### 3.2 Core Components

| Component | Purpose | Tech |
|-----------|---------|------|
| **Data Ingestion** | Fetch OHLCV data, compute indicators | yfinance, pandas_ta |
| **Strategy Engine** | Generate buy/sell signals | Custom Python logic |
| **Backtesting** | Replay history, validate strategies | backtrader |
| **Paper Trading** | Live data with simulated fills | Custom module |
| **Live Trading** | Real order execution | robin_stocks (unofficial Robinhood API) |
| **Position Manager** | Position sizing, stops, targets | Custom module |
| **Monitoring** | Real-time dashboard, logging | Rich (terminal UI), JSON logs |

---

## 4. Project Structure

```
opentrader/
├── strategies/
│   ├── momentum.py          # Momentum trading strategy
│   ├── options_spreads.py   # Options spread strategies
│   └── base_strategy.py     # Abstract strategy class
├── data/
│   ├── fetcher.py           # yfinance wrapper for OHLCV
│   ├── indicators.py        # RSI, Bollinger Bands, Volume, ATR, etc.
│   └── cache.py             # Local data cache
├── execution/
│   ├── backtester.py        # backtrader integration
│   ├── paper_trader.py      # Paper trading simulation
│   ├── robinhood_trader.py  # Live trading via robin_stocks
│   └── base_executor.py     # Abstract executor class
├── risk/
│   ├── position_manager.py  # Entry/exit logic, sizing, stops
│   └── portfolio_manager.py # Account-level risk (max drawdown, daily loss limit)
├── monitoring/
│   ├── dashboard.py         # Terminal UI with Rich library
│   └── logger.py            # Trade logging (JSON)
├── config/
│   ├── config.json          # Strategy params, watchlist, risk settings
│   └── secrets.json         # Robinhood credentials (gitignore'd)
├── tests/
│   ├── test_strategies.py
│   ├── test_position_manager.py
│   └── test_robinhood_trader.py
├── main.py                  # Orchestration: backtesting → paper → live
├── requirements.txt         # Python dependencies
├── .gitignore               # secrets.json, *.log, __pycache__
└── docs/
    └── superpowers/specs/   # Design docs
```

---

## 5. Execution Flow

### 5.1 Backtesting Phase (Week 1)

1. Load 2+ years of historical OHLCV data (yfinance)
2. Compute technical indicators (RSI, Bollinger Bands, Volume, ATR)
3. Run backtrader simulation on momentum strategy
4. Run separate backtest on options spreads (estimate win rate, max loss)
5. Compute metrics: win rate, avg win/loss, Sharpe ratio, max drawdown, profit factor
6. Output: Performance report, equity curve
7. **Decision:** Adjust parameters or proceed to paper trading if metrics acceptable

### 5.2 Paper Trading Phase (Week 2, 1 week)

1. Run strategies live during market hours with real price data
2. Simulate order fills (assume 0.01% slippage)
3. Track: Entry prices, exit prices, realized P&L, trade count
4. Log all trades to JSON (timestamp, symbol, side, qty, entry, exit, P&L)
5. Compare to backtest results: Are real results in-line?
6. **Decision:** Tune logic (entry filters, indicator thresholds) or proceed to live trading

### 5.3 Live Trading Phase (Week 3+)

1. Deploy with real capital ($1000 starting)
2. Execute real orders via robin_stocks (Robinhood API)
3. Use same entry/exit logic as paper trading
4. Monitor: Real P&L, slippage, API reliability
5. Pause trading if daily loss > 5% or drawdown > 10%
6. Scale position sizes as account grows (or shrink if losses mount)

---

## 6. Risk Management

### 6.1 Position-Level Risk

- **Stock trades:** Risk 1-2% per trade
  - Example: On $1000, risk $10-20 per trade
  - Stop loss: 2-3% below entry
  - Profit target: +5% (half), +10% (remainder)

- **Options spreads:** Risk up to 4% per trade
  - Example: On $1000, risk up to $40 per trade
  - Max spread width: Typically $2-5 × 100 = $200-500 cost
  - Greeks: Delta 0.30-0.50, avoid high gamma

### 6.2 Portfolio-Level Risk

- **Max concurrent positions:** 3-5 (keep portfolio diversified)
- **Daily loss limit:** -5% of account ($50 on $1000)
  - Stop all trading if hit; resume next trading day
- **Max drawdown:** 10% (pause trading, reassess)
- **Leverage:** No margin/leverage in Phase 1 (too risky with $1000)

### 6.3 Trade Filters

- **Volume confirmation:** Momentum entries require volume spike (not just price move)
- **IV filter:** Options spreads only when IV rank >70th percentile (thesis: mean reversion)
- **Time-of-day filter:** Avoid last 30 minutes of market (high volatility, worse fills)
- **Gap filter:** Don't trade stocks that gapped 5%+ overnight (execution risk)

---

## 7. Monitoring & Logging

### 7.1 Real-Time Terminal Dashboard

Display during paper and live trading:

```
╔═══════════════════════════════════════════════════════════════════╗
║             OpenTrader - Live Monitor (Paper Trading)             ║
╠═══════════════════════════════════════════════════════════════════╣
║ Status: RUNNING  | Time: 11:45 AM EST | Account: Paper Trading    ║
╠═══════════════════════════════════════════════════════════════════╣
║ PORTFOLIO SUMMARY                                                  ║
║ Cash: $980.50 | Positions: 2 | Total Value: $1,045.23            ║
║ Day P&L: +$45.23 (+4.5%) | Total P&L: +$45.23                    ║
╠═══════════════════════════════════════════════════════════════════╣
║ OPEN POSITIONS                                                     ║
║ AAPL (100 shares) @ $152.30 | Current: $155.20 | +$290 (+1.9%)   ║
║ MSFT (50 shares) @ $420.10 | Current: $418.50 | -$80 (-0.4%)     ║
╠═══════════════════════════════════════════════════════════════════╣
║ RECENT ACTIVITY                                                    ║
║ 11:42 AM - BUY: NVDA 100@$875.40 (Momentum) [EXECUTED]            ║
║ 11:35 AM - SELL: TSLA 50@$245.80 (Take Profit) [EXECUTED]        ║
║ 11:28 AM - BUY: SPY Call Spread $420/$425 [EXECUTED]             ║
╠═══════════════════════════════════════════════════════════════════╣
║ ALERTS: None                                                       ║
╚═══════════════════════════════════════════════════════════════════╝
```

**Auto-refresh:** Every 5 seconds during market hours

**Displays:**
- Account status (cash, positions, total value, daily/total P&L)
- Open positions (symbol, qty, entry price, current price, unrealized P&L)
- Recent activity (timestamp, symbol, action, price, strategy, status)
- Alerts (stop loss hit, max drawdown, API errors, daily loss limit)

### 7.2 Trade Logging

**JSON log** (`logs/trades.json`):
```json
{
  "timestamp": "2026-06-21T11:42:30Z",
  "symbol": "NVDA",
  "strategy": "momentum",
  "side": "BUY",
  "qty": 100,
  "entry_price": 875.40,
  "exit_price": 878.50,
  "realized_pnl": 310,
  "hold_duration_hours": 1.25,
  "reason_exit": "take_profit"
}
```

**Daily reports:**
- Win rate (% profitable trades)
- Avg win / avg loss
- Profit factor (gross profit / gross loss)
- Max drawdown
- Sharpe ratio

---

## 8. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.11+ | Core logic |
| **Data** | yfinance | Historical + real-time OHLCV |
| **Indicators** | pandas_ta, ta-lib | RSI, Bollinger Bands, ATR, Volume |
| **Backtesting** | backtrader | Historical simulation |
| **Broker API** | robin_stocks | Robinhood execution (unofficial) |
| **UI** | Rich | Terminal dashboard |
| **Logging** | Python logging, JSON | Trade history |
| **Testing** | pytest | Unit tests |
| **Scheduler** | APScheduler | Market hours scheduling |

---

## 9. Deployment & Operations

### 9.1 Local Development (Phase 1-2)

- Run on local machine during backtesting and paper trading
- No cloud infrastructure needed
- Manual startup: `python main.py --mode backtest` / `--mode paper`

### 9.2 Live Trading (Phase 3)

**Option A: Local (Simple)**
- Run on home machine, keep it on during market hours (9:30 AM - 4:00 PM EST)
- Downside: Laptop must stay on, no redundancy

**Option B: Cloud (More Robust)**
- Deploy to AWS EC2 (t3.micro free tier eligible)
- Run 24/7, trade during market hours, stop at close
- Add monitoring/alerting (email on errors)
- Cost: ~$10-15/month

**Recommendation:** Start with Option A, graduate to Option B if system proves stable.

### 9.3 Error Handling

- **API failures:** Retry with exponential backoff; alert user
- **Network issues:** Pause trading, log error, attempt reconnect
- **Data gaps:** Skip bar if data unavailable, continue on next bar
- **Account low on cash:** Pause entries, exit only

---

## 10. Testing Strategy

### 10.1 Unit Tests

- Strategy signal generation (correct signals on known data)
- Position manager (correct sizing, stops, targets)
- Risk manager (daily loss limit, portfolio limits)
- Robinhood trader (order placement, cancellation)

### 10.2 Integration Tests

- Backtest → Paper trading → Live trading pipeline
- End-to-end trade execution
- Dashboard rendering with live data

### 10.3 Validation Criteria

**Backtesting:**
- Win rate ≥ 45% (acceptable for trading)
- Profit factor ≥ 1.5 (avg win is 1.5x avg loss)
- Max drawdown ≤ 20% (manageable)
- Sharpe ratio ≥ 0.5 (positive risk-adjusted returns)

**Paper Trading:**
- Results within 10% of backtest (indicator of realistic model)
- No API errors
- Fills simulated accurately

**Live Trading:**
- First week: Track real P&L vs. paper trading
- Acceptable loss: Up to -5% on initial $1000 capital
- Profitable by week 3-4 (arbitrary milestone)

---

## 11. Success Criteria

- **Week 1 (Backtesting):** Strategies pass validation (win rate ≥45%, Sharpe ≥0.5)
- **Week 2 (Paper Trading):** Paper trading results align with backtest (within 10%)
- **Week 3+ (Live Trading):** Positive P&L by end of month, no catastrophic losses

---

## 12. Future Enhancements (Out of Scope)

- Multi-broker support (Interactive Brokers, Alpaca)
- Additional strategies (mean reversion, earnings plays, statistical arbitrage)
- Machine learning for parameter optimization
- Portfolio optimization (Markowitz, risk parity)
- Advanced Greeks management (gamma, vega hedging)
- Cloud deployment with alerting

---

## 13. Appendix: Config Schema

**config.json example:**
```json
{
  "strategy": {
    "momentum": {
      "enabled": true,
      "resistance_period": 20,
      "volume_spike_threshold": 1.2,
      "stop_loss_pct": 0.025,
      "take_profit_target_1": 0.05,
      "take_profit_target_2": 0.10,
      "max_hold_hours": 6
    },
    "options": {
      "enabled": true,
      "iv_percentile_threshold": 70,
      "spread_width": 5,
      "days_to_expiration_min": 7,
      "days_to_expiration_max": 21,
      "target_delta": 0.40
    }
  },
  "risk": {
    "stock_risk_pct": 0.02,
    "options_risk_pct": 0.04,
    "max_concurrent_positions": 5,
    "daily_loss_limit_pct": 0.05,
    "max_drawdown_pct": 0.10
  },
  "broker": {
    "type": "robinhood",
    "trading_hours_start": "09:30",
    "trading_hours_end": "16:00"
  },
  "watchlist": ["AAPL", "MSFT", "NVDA", "TSLA", "SPY", "QQQ"]
}
```

---

**Design Document Status:** ✅ Complete  
**Next Step:** Implementation planning via writing-plans skill
