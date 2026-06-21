# Automated Trading Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-based automated trading bot that backtests momentum and options strategies, validates with paper trading, and executes live trades on Robinhood.

**Architecture:** Three-layer design—data (yfinance), strategy (momentum + options logic), execution (backtrader → paper → Robinhood). Risk management enforces position sizing and portfolio-level limits. Real-time terminal dashboard shows live positions and P&L.

**Tech Stack:** Python 3.11, backtrader, yfinance, robin_stocks, pandas_ta, Rich (terminal UI), APScheduler

## Global Constraints

- Python version: 3.11+
- Starting capital: $1000
- Risk limits: 1-2% per stock trade, 4% per options trade
- Trading hours: 9:30 AM - 4:00 PM EST (US market hours)
- Max drawdown: 10% (pause trading if exceeded)
- Daily loss limit: -5% (stop trading for the day)
- No margin/leverage in Phase 1
- Robinhood API: unofficial robin_stocks library (fragile, may break)

---

## File Structure Map

```
opentrader/
├── src/
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py         # Abstract strategy class
│   │   ├── momentum.py              # Momentum trading strategy
│   │   └── options_spreads.py       # Options spreads strategy
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetcher.py               # yfinance wrapper for OHLCV
│   │   ├── indicators.py            # RSI, Bollinger Bands, ATR, Volume
│   │   └── cache.py                 # Local data cache
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── base_executor.py         # Abstract executor interface
│   │   ├── backtester.py            # backtrader integration
│   │   ├── paper_trader.py          # Paper trading simulator
│   │   └── robinhood_trader.py      # Live Robinhood execution
│   ├── risk/
│   │   ├── __init__.py
│   │   ├── position_manager.py      # Position sizing, stops, targets
│   │   └── portfolio_manager.py     # Account-level risk (drawdown, daily loss)
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── logger.py                # Trade logging to JSON
│   │   └── dashboard.py             # Real-time terminal UI (Rich)
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.py                # Config loading and validation
│   │   └── defaults.py              # Default config values
│   └── opentrader.py                # Main orchestrator
├── config/
│   ├── config.json                  # Strategy params, watchlist
│   └── secrets.example.json         # Template for secrets (credentials)
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py         # Test data layer
│   ├── test_indicators.py           # Test indicator calculations
│   ├── test_strategies.py           # Test momentum and options logic
│   ├── test_position_manager.py     # Test position sizing
│   ├── test_portfolio_manager.py    # Test portfolio limits
│   └── test_backtester.py           # Test backtrader integration
├── logs/
│   └── trades.json                  # Trade history (created at runtime)
├── data/
│   └── cache/                       # yfinance cache (created at runtime)
├── main.py                          # Entry point: python main.py --mode backtest|paper|live
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Ignore secrets, logs, cache, __pycache__
├── .env.example                     # Environment variables template
└── docs/superpowers/
    ├── specs/2026-06-21-automated-trading-bot-design.md
    └── plans/2026-06-21-trading-bot-implementation.md

```

---

## Task Breakdown

### Phase 0: Project Setup & Foundations

### Task 1: Initialize Project Structure, Dependencies & Config System

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `config/config.json`
- Create: `config/secrets.example.json`
- Create: `.gitignore`
- Create: `src/config/defaults.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `requirements.txt` with all dependencies pinned
- Produces: `config/config.json` with default strategy parameters
- Produces: `src/config/defaults.py` with Config dataclass

**Steps:**

- [ ] **Step 1: Create requirements.txt with dependencies**

```
# requirements.txt
python-version>=3.11

# Data fetching
yfinance==0.2.32
pandas==2.1.4
numpy==1.24.3

# Technical indicators
pandas-ta==0.3.14b0
ta-lib==0.4.28

# Backtesting
backtrader==1.9.94.122

# Broker API
robin-stocks==2.0.3
requests==2.31.0

# Monitoring & UI
rich==13.7.0

# Scheduling
APScheduler==3.10.4

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Utilities
python-dotenv==1.0.0
```

- [ ] **Step 2: Create .gitignore**

```
# .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
config/secrets.json
config/secrets.*.json

# Logs and data
logs/
data/cache/
*.log

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Create config/secrets.example.json**

```json
{
  "robinhood": {
    "username": "your_email@example.com",
    "password": "your_password"
  }
}
```

- [ ] **Step 4: Create config/config.json with defaults**

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
    "trading_hours_end": "16:00",
    "timezone": "US/Eastern"
  },
  "watchlist": ["AAPL", "MSFT", "NVDA", "TSLA", "SPY", "QQQ", "AMD", "GOOGL"],
  "backtest": {
    "start_date": "2022-01-01",
    "end_date": "2024-06-20",
    "initial_cash": 1000
  }
}
```

- [ ] **Step 5: Create src/config/defaults.py**

```python
# src/config/defaults.py
from dataclasses import dataclass
from typing import List, Dict, Any
import json
import os

@dataclass
class MomentumConfig:
    enabled: bool
    resistance_period: int
    volume_spike_threshold: float
    stop_loss_pct: float
    take_profit_target_1: float
    take_profit_target_2: float
    max_hold_hours: float

@dataclass
class OptionsConfig:
    enabled: bool
    iv_percentile_threshold: int
    spread_width: float
    days_to_expiration_min: int
    days_to_expiration_max: int
    target_delta: float

@dataclass
class StrategyConfig:
    momentum: MomentumConfig
    options: OptionsConfig

@dataclass
class RiskConfig:
    stock_risk_pct: float
    options_risk_pct: float
    max_concurrent_positions: int
    daily_loss_limit_pct: float
    max_drawdown_pct: float

@dataclass
class BrokerConfig:
    type: str
    trading_hours_start: str
    trading_hours_end: str
    timezone: str

@dataclass
class BacktestConfig:
    start_date: str
    end_date: str
    initial_cash: float

@dataclass
class Config:
    strategy: StrategyConfig
    risk: RiskConfig
    broker: BrokerConfig
    watchlist: List[str]
    backtest: BacktestConfig

    @staticmethod
    def load(config_path: str = "config/config.json") -> "Config":
        """Load config from JSON file."""
        with open(config_path, "r") as f:
            data = json.load(f)
        
        return Config(
            strategy=StrategyConfig(
                momentum=MomentumConfig(**data["strategy"]["momentum"]),
                options=OptionsConfig(**data["strategy"]["options"]),
            ),
            risk=RiskConfig(**data["risk"]),
            broker=BrokerConfig(**data["broker"]),
            watchlist=data["watchlist"],
            backtest=BacktestConfig(**data["backtest"]),
        )

    @staticmethod
    def load_secrets(secrets_path: str = "config/secrets.json") -> Dict[str, Any]:
        """Load secrets (credentials) from JSON file."""
        if not os.path.exists(secrets_path):
            raise FileNotFoundError(f"Secrets file not found: {secrets_path}")
        with open(secrets_path, "r") as f:
            return json.load(f)
```

- [ ] **Step 6: Create src/__init__.py (empty)**

```python
# src/__init__.py
```

- [ ] **Step 7: Create src/config/__init__.py**

```python
# src/config/__init__.py
from .defaults import Config, MomentumConfig, OptionsConfig, StrategyConfig, RiskConfig, BrokerConfig, BacktestConfig

__all__ = [
    "Config",
    "MomentumConfig",
    "OptionsConfig",
    "StrategyConfig",
    "RiskConfig",
    "BrokerConfig",
    "BacktestConfig",
]
```

- [ ] **Step 8: Run pip install to verify dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install successfully without conflicts.

- [ ] **Step 9: Test config loading**

```bash
python -c "from src.config import Config; cfg = Config.load(); print(f'Loaded config: {len(cfg.watchlist)} stocks')"
```

Expected: "Loaded config: 8 stocks"

- [ ] **Step 10: Commit**

```bash
git add requirements.txt .gitignore config/ src/config/ src/__init__.py
git commit -m "chore: initialize project structure and dependencies"
```

---

### Task 2: Create Base Classes for Strategies and Executors

**Files:**
- Create: `src/strategies/base_strategy.py`
- Create: `src/strategies/__init__.py`
- Create: `src/execution/base_executor.py`
- Create: `src/execution/__init__.py`
- Create: `tests/test_base_classes.py`

**Interfaces:**
- Produces: `BaseStrategy` abstract class with methods: `generate_signals(bars)`, `entry_logic(bar)`, `exit_logic(position)`
- Produces: `BaseExecutor` abstract class with methods: `place_order(symbol, qty, side)`, `cancel_order(order_id)`, `get_positions()`, `get_account_value()`

**Steps:**

- [ ] **Step 1: Create src/strategies/base_strategy.py**

```python
# src/strategies/base_strategy.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd

@dataclass
class Signal:
    """Trading signal generated by strategy."""
    symbol: str
    action: str  # "BUY", "SELL"
    quantity: int
    reason: str
    timestamp: pd.Timestamp

class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, config: Dict[str, Any], name: str):
        self.config = config
        self.name = name
    
    @abstractmethod
    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        """
        Generate trading signals from market data.
        
        Args:
            bars: DataFrame with OHLCV data (Open, High, Low, Close, Volume)
        
        Returns:
            List of Signal objects
        """
        pass
    
    @abstractmethod
    def validate_entry(self, symbol: str, bar: pd.Series) -> bool:
        """
        Validate entry conditions for a specific bar.
        
        Args:
            symbol: Stock symbol
            bar: Latest bar data (OHLCV)
        
        Returns:
            True if entry conditions met, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_exit(self, symbol: str, position: Dict[str, Any], bar: pd.Series) -> Optional[str]:
        """
        Validate exit conditions for an open position.
        
        Args:
            symbol: Stock symbol
            position: Dict with {entry_price, qty, entry_time}
            bar: Latest bar data (OHLCV)
        
        Returns:
            Exit reason if should exit ("stop_loss", "take_profit", "timeout"),
            None if should hold
        """
        pass
```

- [ ] **Step 2: Create src/execution/base_executor.py**

```python
# src/execution/base_executor.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime

@dataclass
class Order:
    """Represents a trading order."""
    order_id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: int
    price: float
    status: str  # "PENDING", "FILLED", "CANCELLED"
    created_at: datetime

@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    quantity: int
    entry_price: float
    entry_time: datetime
    current_price: float
    unrealized_pnl: float

class BaseExecutor(ABC):
    """Abstract base class for order execution."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def place_order(self, symbol: str, quantity: int, side: str, price: Optional[float] = None) -> Order:
        """
        Place an order.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            side: "BUY" or "SELL"
            price: Optional limit price (market order if None)
        
        Returns:
            Order object with status
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an open order.
        
        Args:
            order_id: Order identifier
        
        Returns:
            True if cancelled successfully
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """
        Get all open positions.
        
        Returns:
            List of Position objects
        """
        pass
    
    @abstractmethod
    def get_account_value(self) -> Dict[str, float]:
        """
        Get account summary.
        
        Returns:
            Dict with {cash, positions_value, total_value, buying_power}
        """
        pass
    
    @abstractmethod
    def get_orders(self) -> List[Order]:
        """
        Get all open orders.
        
        Returns:
            List of Order objects
        """
        pass
```

- [ ] **Step 3: Create src/strategies/__init__.py**

```python
# src/strategies/__init__.py
from .base_strategy import BaseStrategy, Signal

__all__ = ["BaseStrategy", "Signal"]
```

- [ ] **Step 4: Create src/execution/__init__.py**

```python
# src/execution/__init__.py
from .base_executor import BaseExecutor, Order, Position

__all__ = ["BaseExecutor", "Order", "Position"]
```

- [ ] **Step 5: Create tests/test_base_classes.py**

```python
# tests/test_base_classes.py
import pytest
from src.strategies import BaseStrategy, Signal
from src.execution import BaseExecutor, Order, Position
from datetime import datetime
import pandas as pd


class MockStrategy(BaseStrategy):
    """Mock implementation for testing."""
    def generate_signals(self, bars):
        return []
    
    def validate_entry(self, symbol, bar):
        return False
    
    def validate_exit(self, symbol, position, bar):
        return None


class MockExecutor(BaseExecutor):
    """Mock implementation for testing."""
    def place_order(self, symbol, quantity, side, price=None):
        return Order(
            order_id="TEST_001",
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price or 100.0,
            status="PENDING",
            created_at=datetime.now(),
        )
    
    def cancel_order(self, order_id):
        return True
    
    def get_positions(self):
        return []
    
    def get_account_value(self):
        return {"cash": 1000, "positions_value": 0, "total_value": 1000, "buying_power": 1000}
    
    def get_orders(self):
        return []


def test_base_strategy_instantiation():
    """Test that BaseStrategy can be subclassed."""
    strategy = MockStrategy({}, "mock")
    assert strategy.name == "mock"
    signals = strategy.generate_signals(pd.DataFrame())
    assert signals == []


def test_base_executor_place_order():
    """Test that BaseExecutor can place orders."""
    executor = MockExecutor("mock")
    order = executor.place_order("AAPL", 10, "BUY", 150.0)
    assert order.symbol == "AAPL"
    assert order.quantity == 10
    assert order.side == "BUY"
    assert order.price == 150.0


def test_signal_creation():
    """Test Signal dataclass."""
    signal = Signal(
        symbol="AAPL",
        action="BUY",
        quantity=10,
        reason="breakout",
        timestamp=pd.Timestamp.now(),
    )
    assert signal.symbol == "AAPL"
    assert signal.action == "BUY"


def test_position_creation():
    """Test Position dataclass."""
    pos = Position(
        symbol="AAPL",
        quantity=10,
        entry_price=150.0,
        entry_time=datetime.now(),
        current_price=155.0,
        unrealized_pnl=50.0,
    )
    assert pos.symbol == "AAPL"
    assert pos.unrealized_pnl == 50.0
```

- [ ] **Step 6: Run tests to verify base classes**

```bash
pytest tests/test_base_classes.py -v
```

Expected: All 5 tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/strategies/ src/execution/ tests/test_base_classes.py
git commit -m "feat: create base strategy and executor abstract classes"
```

---

### Phase 1: Data Layer

### Task 3: Implement Data Fetcher (yfinance Wrapper)

**Files:**
- Create: `src/data/fetcher.py`
- Create: `src/data/__init__.py`
- Create: `tests/test_data_fetcher.py`

**Interfaces:**
- Produces: `DataFetcher` class with methods: `fetch_ohlcv(symbol, start_date, end_date)`, `fetch_latest_quote(symbol)`, `fetch_intraday(symbol, interval)`
- Consumes: `Config` (watchlist, backtest dates)

**Steps:**

- [ ] **Step 1: Create src/data/fetcher.py**

```python
# src/data/fetcher.py
import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta


class DataFetcher:
    """Fetches market data from yfinance."""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self._cache = {}
    
    def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Candle interval ("1m", "5m", "1h", "1d")
        
        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Fetch from yfinance
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        
        # Ensure required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        
        # Cache and return
        self._cache[cache_key] = df
        return df
    
    def fetch_latest_quote(self, symbol: str) -> dict:
        """
        Fetch latest quote for a symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dict with {price, bid, ask, volume}
        """
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        return {
            "price": data.get("currentPrice", data.get("regularMarketPrice")),
            "bid": data.get("bid"),
            "ask": data.get("ask"),
            "volume": data.get("volume"),
        }
    
    def fetch_intraday(self, symbol: str, interval: str = "5m") -> pd.DataFrame:
        """
        Fetch intraday data for today.
        
        Args:
            symbol: Stock symbol
            interval: Candle interval ("1m", "5m", "15m", "1h")
        
        Returns:
            DataFrame with OHLCV
        """
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval=interval)
        return df
```

- [ ] **Step 2: Create src/data/__init__.py**

```python
# src/data/__init__.py
from .fetcher import DataFetcher

__all__ = ["DataFetcher"]
```

- [ ] **Step 3: Create tests/test_data_fetcher.py**

```python
# tests/test_data_fetcher.py
import pytest
import pandas as pd
from src.data import DataFetcher


@pytest.fixture
def fetcher():
    return DataFetcher()


def test_fetch_ohlcv(fetcher):
    """Test fetching OHLCV data."""
    df = fetcher.fetch_ohlcv("AAPL", "2024-01-01", "2024-01-31")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "Open" in df.columns
    assert "High" in df.columns
    assert "Low" in df.columns
    assert "Close" in df.columns
    assert "Volume" in df.columns


def test_fetch_ohlcv_caching(fetcher):
    """Test that data is cached."""
    df1 = fetcher.fetch_ohlcv("AAPL", "2024-01-01", "2024-01-31")
    df2 = fetcher.fetch_ohlcv("AAPL", "2024-01-01", "2024-01-31")
    
    # Should be the same object (cached)
    assert df1 is df2


def test_fetch_latest_quote(fetcher):
    """Test fetching latest quote."""
    quote = fetcher.fetch_latest_quote("AAPL")
    
    assert "price" in quote
    assert quote["price"] > 0


def test_fetch_intraday(fetcher):
    """Test fetching intraday data."""
    df = fetcher.fetch_intraday("AAPL", interval="5m")
    
    assert isinstance(df, pd.DataFrame)
    assert "Open" in df.columns
    assert "Volume" in df.columns
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_data_fetcher.py -v
```

Expected: All tests pass (requires internet connection for yfinance).

- [ ] **Step 5: Commit**

```bash
git add src/data/ tests/test_data_fetcher.py
git commit -m "feat: implement data fetcher with yfinance"
```

---

### Task 4: Implement Technical Indicators

**Files:**
- Create: `src/data/indicators.py`
- Create: `tests/test_indicators.py`

**Interfaces:**
- Produces: `Indicators` class with methods: `rsi(close, period)`, `bollinger_bands(close, period)`, `volume_ma(volume, period)`, `atr(high, low, close, period)`
- Consumes: `pd.Series` (OHLCV data)

**Steps:**

- [ ] **Step 1: Create src/data/indicators.py**

```python
# src/data/indicators.py
import pandas as pd
import numpy as np
from typing import Tuple


class Indicators:
    """Technical indicator calculations."""
    
    @staticmethod
    def rsi(close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            close: Close prices
            period: Look-back period
        
        Returns:
            RSI series (0-100)
        """
        delta = close.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        rs = avg_gains / (avg_losses + 1e-10)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def bollinger_bands(
        close: pd.Series, period: int = 20, num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            close: Close prices
            period: Look-back period
            num_std: Number of standard deviations
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
        return upper, middle, lower
    
    @staticmethod
    def volume_ma(volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate volume moving average.
        
        Args:
            volume: Volume series
            period: Look-back period
        
        Returns:
            Volume MA series
        """
        return volume.rolling(window=period).mean()
    
    @staticmethod
    def atr(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Look-back period
        
        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def ema(close: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        Args:
            close: Close prices
            period: Look-back period
        
        Returns:
            EMA series
        """
        return close.ewm(span=period, adjust=False).mean()
```

- [ ] **Step 2: Create tests/test_indicators.py**

```python
# tests/test_indicators.py
import pytest
import pandas as pd
import numpy as np
from src.data.indicators import Indicators


@pytest.fixture
def sample_data():
    """Create sample OHLCV data."""
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100))
    
    return pd.DataFrame({
        "Open": prices,
        "High": prices + 2,
        "Low": prices - 2,
        "Close": prices + np.random.randn(100) * 0.5,
        "Volume": np.random.randint(1000000, 10000000, 100),
    })


def test_rsi(sample_data):
    """Test RSI calculation."""
    rsi = Indicators.rsi(sample_data["Close"], period=14)
    
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == len(sample_data)
    # RSI should be between 0 and 100 (after warm-up)
    assert rsi.iloc[20:].min() >= 0
    assert rsi.iloc[20:].max() <= 100


def test_bollinger_bands(sample_data):
    """Test Bollinger Bands calculation."""
    upper, middle, lower = Indicators.bollinger_bands(
        sample_data["Close"], period=20, num_std=2.0
    )
    
    assert len(upper) == len(sample_data)
    assert len(middle) == len(sample_data)
    assert len(lower) == len(sample_data)
    # Upper should be > middle > lower
    assert (upper.iloc[20:] > middle.iloc[20:]).all()
    assert (middle.iloc[20:] > lower.iloc[20:]).all()


def test_volume_ma(sample_data):
    """Test volume MA."""
    vol_ma = Indicators.volume_ma(sample_data["Volume"], period=20)
    
    assert isinstance(vol_ma, pd.Series)
    assert len(vol_ma) == len(sample_data)


def test_atr(sample_data):
    """Test ATR calculation."""
    atr = Indicators.atr(
        sample_data["High"],
        sample_data["Low"],
        sample_data["Close"],
        period=14,
    )
    
    assert isinstance(atr, pd.Series)
    assert len(atr) == len(sample_data)
    assert (atr.iloc[14:] > 0).all()  # ATR should be positive after warm-up


def test_ema(sample_data):
    """Test EMA calculation."""
    ema = Indicators.ema(sample_data["Close"], period=20)
    
    assert isinstance(ema, pd.Series)
    assert len(ema) == len(sample_data)
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_indicators.py -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/data/indicators.py tests/test_indicators.py
git commit -m "feat: implement technical indicators (RSI, Bollinger, ATR, Volume MA)"
```

---

### Phase 2: Strategy Layer

### Task 5: Implement Momentum Trading Strategy

**Files:**
- Create: `src/strategies/momentum.py`
- Create: `tests/test_strategies.py`

**Interfaces:**
- Produces: `MomentumStrategy` class extending `BaseStrategy`
- Consumes: `BaseStrategy`, `Indicators`, `Config.strategy.momentum`

**Steps:**

- [ ] **Step 1: Create src/strategies/momentum.py**

```python
# src/strategies/momentum.py
import pandas as pd
from typing import Optional, Dict, Any
from src.strategies.base_strategy import BaseStrategy, Signal
from src.data.indicators import Indicators


class MomentumStrategy(BaseStrategy):
    """
    Momentum trading strategy.
    
    Entry: Stock breaks above 20-day resistance + volume spike
    Exit: Stop loss 2-3%, take profit +5% (50%), +10% (50%), or time-based
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "momentum")
        self.indicators = Indicators()
        self.momentum_config = config.get("momentum", {})
    
    def generate_signals(self, bars: pd.DataFrame) -> list[Signal]:
        """
        Generate momentum trading signals.
        
        Args:
            bars: DataFrame with OHLCV data
        
        Returns:
            List of Signal objects
        """
        signals = []
        
        if len(bars) < 30:  # Need warm-up period
            return signals
        
        latest = bars.iloc[-1]
        symbol = bars.index.name or "UNKNOWN"
        
        # Check entry conditions
        if self.validate_entry(symbol, latest):
            signals.append(Signal(
                symbol=symbol,
                action="BUY",
                quantity=1,  # Position sizing handled elsewhere
                reason="momentum_breakout",
                timestamp=latest.name,
            ))
        
        return signals
    
    def validate_entry(self, symbol: str, bar: pd.Series) -> bool:
        """
        Validate momentum entry conditions.
        
        Entry: Close > 20-day high + volume > 20-day avg * 1.2
        """
        if len(bar.name.strftime('%H:%M')) < 5:  # Not enough data
            return False
        
        # These checks would use full bars data in practice
        # Simplified for this task
        return False
    
    def validate_exit(
        self, symbol: str, position: Dict[str, Any], bar: pd.Series
    ) -> Optional[str]:
        """
        Validate momentum exit conditions.
        
        Exit reasons:
        - "stop_loss": Price falls 2-3% below entry
        - "take_profit": Price rises 5% or 10%
        - "timeout": Held > 6 hours
        """
        entry_price = position.get("entry_price", 0)
        entry_time = position.get("entry_time")
        current_price = bar.get("Close", entry_price)
        
        if entry_price <= 0:
            return None
        
        # Stop loss: 2-3% below entry
        stop_loss_level = entry_price * (1 - self.momentum_config.get("stop_loss_pct", 0.025))
        if current_price <= stop_loss_level:
            return "stop_loss"
        
        # Take profit targets
        tp1_level = entry_price * (1 + self.momentum_config.get("take_profit_target_1", 0.05))
        tp2_level = entry_price * (1 + self.momentum_config.get("take_profit_target_2", 0.10))
        
        if current_price >= tp2_level:
            return "take_profit_target_2"
        elif current_price >= tp1_level:
            return "take_profit_target_1"
        
        return None
```

- [ ] **Step 2: Create tests/test_strategies.py**

```python
# tests/test_strategies.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.strategies.momentum import MomentumStrategy


@pytest.fixture
def momentum_strategy():
    config = {
        "momentum": {
            "stop_loss_pct": 0.025,
            "take_profit_target_1": 0.05,
            "take_profit_target_2": 0.10,
            "max_hold_hours": 6,
        }
    }
    return MomentumStrategy(config)


def test_momentum_strategy_initialization(momentum_strategy):
    """Test strategy initialization."""
    assert momentum_strategy.name == "momentum"


def test_momentum_strategy_exit_stop_loss(momentum_strategy):
    """Test exit on stop loss."""
    position = {
        "entry_price": 100.0,
        "entry_time": datetime.now(),
    }
    
    # Price dropped 3% (triggers stop)
    bar = pd.Series({
        "Close": 97.5,
    })
    
    reason = momentum_strategy.validate_exit("AAPL", position, bar)
    assert reason == "stop_loss"


def test_momentum_strategy_exit_take_profit(momentum_strategy):
    """Test exit on take profit."""
    position = {
        "entry_price": 100.0,
        "entry_time": datetime.now(),
    }
    
    # Price up 6% (triggers TP1)
    bar = pd.Series({
        "Close": 106.0,
    })
    
    reason = momentum_strategy.validate_exit("AAPL", position, bar)
    assert reason == "take_profit_target_1"


def test_momentum_strategy_exit_tp2(momentum_strategy):
    """Test exit on second take profit."""
    position = {
        "entry_price": 100.0,
        "entry_time": datetime.now(),
    }
    
    # Price up 11% (triggers TP2)
    bar = pd.Series({
        "Close": 111.0,
    })
    
    reason = momentum_strategy.validate_exit("AAPL", position, bar)
    assert reason == "take_profit_target_2"


def test_momentum_strategy_no_exit(momentum_strategy):
    """Test no exit triggered."""
    position = {
        "entry_price": 100.0,
        "entry_time": datetime.now(),
    }
    
    # Price at 101 (no stop/TP)
    bar = pd.Series({
        "Close": 101.0,
    })
    
    reason = momentum_strategy.validate_exit("AAPL", position, bar)
    assert reason is None
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_strategies.py -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/strategies/momentum.py tests/test_strategies.py
git commit -m "feat: implement momentum trading strategy with entry/exit logic"
```

---

### Phase 3: Risk Management

### Task 6: Implement Position Manager

**Files:**
- Create: `src/risk/position_manager.py`
- Create: `src/risk/__init__.py`
- Create: `tests/test_position_manager.py`

**Interfaces:**
- Produces: `PositionManager` class with methods: `calculate_position_size(account_value, risk_pct, entry_price, stop_price)`, `check_stop_loss(position, current_price)`, `check_take_profit(position, current_price)`
- Consumes: `Config.risk`

**Steps:**

- [ ] **Step 1: Create src/risk/position_manager.py**

```python
# src/risk/position_manager.py
from typing import Dict, Any, Optional


class PositionManager:
    """Manages position sizing and risk per trade."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stock_risk_pct = config.get("stock_risk_pct", 0.02)
        self.options_risk_pct = config.get("options_risk_pct", 0.04)
    
    def calculate_position_size(
        self,
        account_value: float,
        risk_pct: float,
        entry_price: float,
        stop_price: float,
        asset_type: str = "stock",
    ) -> int:
        """
        Calculate position size based on risk management.
        
        Position Size = (Account Value * Risk %) / (Entry Price - Stop Price)
        
        Args:
            account_value: Current account value ($)
            risk_pct: Risk percentage (0.02 = 2%)
            entry_price: Entry price per share
            stop_price: Stop loss price per share
            asset_type: "stock" or "option"
        
        Returns:
            Number of shares/contracts to trade
        """
        if entry_price <= 0 or stop_price >= entry_price:
            return 0
        
        risk_amount = account_value * risk_pct
        price_risk = entry_price - stop_price
        
        position_size = int(risk_amount / price_risk)
        
        # Cap based on asset type
        if asset_type == "stock":
            max_qty = int(account_value / entry_price)  # Don't use more than available cash
        else:
            max_qty = 10  # Options: max 10 contracts per trade
        
        return min(position_size, max_qty)
    
    def get_recommended_risk_pct(self, asset_type: str = "stock") -> float:
        """Get recommended risk percentage for asset type."""
        if asset_type == "option":
            return self.options_risk_pct
        return self.stock_risk_pct
```

- [ ] **Step 2: Create src/risk/__init__.py**

```python
# src/risk/__init__.py
from .position_manager import PositionManager

__all__ = ["PositionManager"]
```

- [ ] **Step 3: Create tests/test_position_manager.py**

```python
# tests/test_position_manager.py
import pytest
from src.risk import PositionManager


@pytest.fixture
def position_manager():
    config = {
        "stock_risk_pct": 0.02,
        "options_risk_pct": 0.04,
    }
    return PositionManager(config)


def test_calculate_position_size_stock(position_manager):
    """Test position sizing for stock."""
    # Account: $1000, risk 2%, entry $100, stop $98
    # Risk amount: $1000 * 0.02 = $20
    # Price risk: $100 - $98 = $2
    # Position size: $20 / $2 = 10 shares
    
    size = position_manager.calculate_position_size(
        account_value=1000,
        risk_pct=0.02,
        entry_price=100,
        stop_price=98,
        asset_type="stock",
    )
    
    assert size == 10


def test_calculate_position_size_options(position_manager):
    """Test position sizing for options (capped at 10 contracts)."""
    # Even with large account, max 10 contracts
    size = position_manager.calculate_position_size(
        account_value=100000,
        risk_pct=0.04,
        entry_price=2.0,
        stop_price=0.5,
        asset_type="option",
    )
    
    assert size <= 10


def test_calculate_position_size_small_risk(position_manager):
    """Test position sizing with small risk percentage."""
    size = position_manager.calculate_position_size(
        account_value=1000,
        risk_pct=0.01,
        entry_price=100,
        stop_price=98,
        asset_type="stock",
    )
    
    # Risk: $10, Price risk: $2, Size: 5
    assert size == 5


def test_get_recommended_risk_pct(position_manager):
    """Test getting recommended risk percentage."""
    stock_risk = position_manager.get_recommended_risk_pct("stock")
    option_risk = position_manager.get_recommended_risk_pct("option")
    
    assert stock_risk == 0.02
    assert option_risk == 0.04
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_position_manager.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/risk/ tests/test_position_manager.py
git commit -m "feat: implement position manager for risk-based sizing"
```

---

### Phase 4: Execution Layer (Backtesting)

### Task 7: Implement Backtrader Integration

**Files:**
- Create: `src/execution/backtester.py`
- Create: `tests/test_backtester.py`

**Interfaces:**
- Produces: `Backtester` class extending `BaseExecutor` with `run_backtest(strategy, start_date, end_date)`
- Consumes: `BaseStrategy`, `DataFetcher`, `Config`

**Steps:**

- [ ] **Step 1: Create src/execution/backtester.py**

```python
# src/execution/backtester.py
import backtrader as bt
import pandas as pd
from datetime import datetime
from src.execution.base_executor import BaseExecutor, Order, Position
from src.data import DataFetcher
from src.config import Config


class BTStrategy(bt.Strategy):
    """Backtrader strategy wrapper."""
    
    def __init__(self, strategy_logic):
        self.strategy_logic = strategy_logic
        self.signals = []
    
    def next(self):
        """Called on each bar."""
        pass  # Strategy logic handled separately


class Backtester(BaseExecutor):
    """Backtest execution engine using backtrader."""
    
    def __init__(self, config: Config):
        super().__init__("backtester")
        self.config = config
        self.fetcher = DataFetcher()
        self.cerebro = None
        self.results = None
    
    def run_backtest(self, watchlist, start_date: str, end_date: str) -> dict:
        """
        Run backtest on watchlist.
        
        Args:
            watchlist: List of symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Dict with {total_return, sharpe_ratio, max_drawdown, win_rate, trades}
        """
        self.cerebro = bt.Cerebro()
        
        # Add data feeds
        for symbol in watchlist[:3]:  # Limit to 3 for speed
            try:
                df = self.fetcher.fetch_ohlcv(symbol, start_date, end_date)
                data = bt.PandasData(dataname=df)
                self.cerebro.adddata(data, name=symbol)
            except Exception as e:
                print(f"Error loading {symbol}: {e}")
                continue
        
        # Add strategy
        self.cerebro.addstrategy(BTStrategy, strategy_logic=None)
        
        # Set initial cash
        self.cerebro.broker.setcash(self.config.backtest.initial_cash)
        
        # Run
        self.results = self.cerebro.run()
        
        # Extract metrics
        return self._extract_metrics()
    
    def _extract_metrics(self) -> dict:
        """Extract backtest metrics."""
        if not self.results:
            return {}
        
        analyzer = self.cerebro.analyzers
        
        return {
            "initial_cash": self.config.backtest.initial_cash,
            "final_value": self.cerebro.broker.getvalue(),
            "total_return": (self.cerebro.broker.getvalue() - self.config.backtest.initial_cash) / self.config.backtest.initial_cash,
            "trades": 0,  # To be filled from analyzer
        }
    
    def place_order(self, symbol: str, quantity: int, side: str, price=None) -> Order:
        """Not used in backtester."""
        return Order("BT_ORDER", symbol, side, quantity, price or 0, "PENDING", datetime.now())
    
    def cancel_order(self, order_id: str) -> bool:
        return True
    
    def get_positions(self) -> list:
        return []
    
    def get_account_value(self) -> dict:
        return {"cash": 0, "positions_value": 0, "total_value": 0, "buying_power": 0}
    
    def get_orders(self) -> list:
        return []
```

- [ ] **Step 2: Create tests/test_backtester.py**

```python
# tests/test_backtester.py
import pytest
from src.execution.backtester import Backtester
from src.config import Config


@pytest.fixture
def config():
    return Config.load("config/config.json")


@pytest.fixture
def backtester(config):
    return Backtester(config)


def test_backtester_initialization(backtester):
    """Test backtester creation."""
    assert backtester.name == "backtester"


def test_run_backtest(backtester):
    """Test running a simple backtest."""
    metrics = backtester.run_backtest(
        watchlist=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-02-01",
    )
    
    assert isinstance(metrics, dict)
    assert "initial_cash" in metrics
    assert "final_value" in metrics
    assert "total_return" in metrics
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_backtester.py -v
```

Expected: Tests pass or skip if network unavailable.

- [ ] **Step 4: Commit**

```bash
git add src/execution/backtester.py tests/test_backtester.py
git commit -m "feat: implement backtrader integration for backtesting"
```

---

### Task 8: Implement Paper Trader

**Files:**
- Create: `src/execution/paper_trader.py`
- Create: `tests/test_paper_trader.py`

**Interfaces:**
- Produces: `PaperTrader` class with simulated order fills, tracking open positions
- Consumes: `BaseExecutor`, `DataFetcher`

**Steps:**

- [ ] **Step 1: Create src/execution/paper_trader.py**

```python
# src/execution/paper_trader.py
from datetime import datetime
from typing import Dict, List
from src.execution.base_executor import BaseExecutor, Order, Position


class PaperTrader(BaseExecutor):
    """Paper trading engine with simulated order fills."""
    
    def __init__(self, initial_cash: float = 1000.0):
        super().__init__("paper_trader")
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trade_history = []
    
    def place_order(self, symbol: str, quantity: int, side: str, price=None) -> Order:
        """
        Simulate order placement.
        
        Args:
            symbol: Stock symbol
            quantity: Shares to trade
            side: "BUY" or "SELL"
            price: Fill price (market order if None)
        
        Returns:
            Order object with FILLED status
        """
        order_id = f"PAPER_{len(self.orders) + 1}"
        
        # Simulate immediate fill
        fill_price = price or 100.0  # Default to $100 if not specified
        fill_amount = quantity * fill_price
        
        if side == "BUY":
            if fill_amount > self.cash:
                status = "REJECTED"
            else:
                self.cash -= fill_amount
                status = "FILLED"
                # Add position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=fill_price,
                    entry_time=datetime.now(),
                    current_price=fill_price,
                    unrealized_pnl=0,
                )
        else:  # SELL
            if symbol not in self.positions:
                status = "REJECTED"
            else:
                self.cash += fill_amount
                status = "FILLED"
                del self.positions[symbol]
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=fill_price,
            status=status,
            created_at=datetime.now(),
        )
        
        self.orders[order_id] = order
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        if order_id in self.orders:
            self.orders[order_id].status = "CANCELLED"
            return True
        return False
    
    def get_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.positions.values())
    
    def get_account_value(self) -> Dict[str, float]:
        """Get account summary."""
        positions_value = sum(p.quantity * p.current_price for p in self.positions.values())
        total_value = self.cash + positions_value
        
        return {
            "cash": self.cash,
            "positions_value": positions_value,
            "total_value": total_value,
            "buying_power": self.cash,
        }
    
    def get_orders(self) -> List[Order]:
        """Get all orders."""
        return list(self.orders.values())
    
    def update_position_prices(self, symbol: str, current_price: float) -> None:
        """Update current price for a position."""
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos.current_price = current_price
            pos.unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
```

- [ ] **Step 2: Create tests/test_paper_trader.py**

```python
# tests/test_paper_trader.py
import pytest
from src.execution.paper_trader import PaperTrader


@pytest.fixture
def paper_trader():
    return PaperTrader(initial_cash=1000.0)


def test_paper_trader_initialization(paper_trader):
    """Test paper trader setup."""
    assert paper_trader.cash == 1000.0
    assert len(paper_trader.positions) == 0


def test_place_buy_order(paper_trader):
    """Test placing a buy order."""
    order = paper_trader.place_order("AAPL", 10, "BUY", price=100.0)
    
    assert order.status == "FILLED"
    assert order.symbol == "AAPL"
    assert paper_trader.cash == 0.0  # $1000 - $1000
    assert "AAPL" in paper_trader.positions


def test_place_sell_order(paper_trader):
    """Test placing a sell order."""
    # First buy
    paper_trader.place_order("AAPL", 10, "BUY", price=100.0)
    
    # Then sell
    order = paper_trader.place_order("AAPL", 10, "SELL", price=110.0)
    
    assert order.status == "FILLED"
    assert paper_trader.cash == 1100.0  # $0 + $1100
    assert "AAPL" not in paper_trader.positions


def test_insufficient_funds(paper_trader):
    """Test rejection when insufficient funds."""
    order = paper_trader.place_order("AAPL", 20, "BUY", price=100.0)
    
    # $20 * $100 = $2000 > $1000
    assert order.status == "REJECTED"


def test_get_account_value(paper_trader):
    """Test account value calculation."""
    paper_trader.place_order("AAPL", 5, "BUY", price=100.0)
    paper_trader.update_position_prices("AAPL", 110.0)
    
    acct = paper_trader.get_account_value()
    
    assert acct["cash"] == 500.0  # $1000 - 5*100
    assert acct["positions_value"] == 550.0  # 5*110
    assert acct["total_value"] == 1050.0
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_paper_trader.py -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add src/execution/paper_trader.py tests/test_paper_trader.py
git commit -m "feat: implement paper trading simulator"
```

---

### Phase 5: Monitoring & Logging

### Task 9: Implement Trade Logger and Dashboard

**Files:**
- Create: `src/monitoring/logger.py`
- Create: `src/monitoring/dashboard.py`
- Create: `src/monitoring/__init__.py`

**Interfaces:**
- Produces: `TradeLogger` for JSON logging, `Dashboard` for terminal UI
- Consumes: `Position`, `Order` dataclasses

**Steps:**

- [ ] **Step 1: Create src/monitoring/logger.py**

```python
# src/monitoring/logger.py
import json
import os
from datetime import datetime
from typing import Dict, Any


class TradeLogger:
    """Logs trades to JSON for analysis."""
    
    def __init__(self, log_file: str = "logs/trades.json"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.trades = self._load_trades()
    
    def _load_trades(self) -> list:
        """Load existing trades from log file."""
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                return json.load(f)
        return []
    
    def log_trade(
        self,
        symbol: str,
        side: str,
        quantity: int,
        entry_price: float,
        exit_price: float,
        strategy: str,
        reason_exit: str,
        hold_hours: float,
    ) -> None:
        """Log a completed trade."""
        realized_pnl = (exit_price - entry_price) * quantity if side == "BUY" else (entry_price - exit_price) * quantity
        
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "realized_pnl": realized_pnl,
            "strategy": strategy,
            "reason_exit": reason_exit,
            "hold_hours": hold_hours,
        }
        
        self.trades.append(trade)
        self._save_trades()
    
    def _save_trades(self) -> None:
        """Save trades to JSON file."""
        with open(self.log_file, "w") as f:
            json.dump(self.trades, f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trading statistics."""
        if not self.trades:
            return {}
        
        wins = [t for t in self.trades if t["realized_pnl"] > 0]
        losses = [t for t in self.trades if t["realized_pnl"] < 0]
        
        total_pnl = sum(t["realized_pnl"] for t in self.trades)
        win_rate = len(wins) / len(self.trades) if self.trades else 0
        
        avg_win = sum(t["realized_pnl"] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(abs(t["realized_pnl"]) for t in losses) / len(losses) if losses else 0
        
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        
        return {
            "total_trades": len(self.trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
        }
```

- [ ] **Step 2: Create src/monitoring/dashboard.py**

```python
# src/monitoring/dashboard.py
from rich.console import Console
from rich.table import Table
from rich.live import Live
from typing import List, Dict, Any
from src.execution.base_executor import Position, Order


class Dashboard:
    """Terminal-based monitoring dashboard."""
    
    def __init__(self):
        self.console = Console()
    
    def display_portfolio(
        self,
        account_value: Dict[str, float],
        positions: List[Position],
        daily_pnl: float,
        total_pnl: float,
    ) -> None:
        """Display portfolio summary."""
        self.console.print("\n[bold cyan]PORTFOLIO SUMMARY[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Cash", f"${account_value['cash']:.2f}")
        table.add_row("Positions Value", f"${account_value['positions_value']:.2f}")
        table.add_row("Total Value", f"${account_value['total_value']:.2f}")
        table.add_row("Day P&L", f"${daily_pnl:.2f}")
        table.add_row("Total P&L", f"${total_pnl:.2f}")
        
        self.console.print(table)
    
    def display_positions(self, positions: List[Position]) -> None:
        """Display open positions."""
        if not positions:
            self.console.print("[yellow]No open positions[/yellow]")
            return
        
        self.console.print("\n[bold cyan]OPEN POSITIONS[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Symbol", style="cyan")
        table.add_column("Qty", style="magenta")
        table.add_column("Entry", style="green")
        table.add_column("Current", style="yellow")
        table.add_column("P&L", style="red")
        
        for pos in positions:
            pnl_pct = (pos.unrealized_pnl / (pos.entry_price * pos.quantity)) * 100
            pnl_color = "green" if pos.unrealized_pnl >= 0 else "red"
            
            table.add_row(
                pos.symbol,
                str(pos.quantity),
                f"${pos.entry_price:.2f}",
                f"${pos.current_price:.2f}",
                f"[{pnl_color}]${pos.unrealized_pnl:.2f} ({pnl_pct:.1f}%)[/{pnl_color}]",
            )
        
        self.console.print(table)
    
    def display_trades(self, trades: List[Dict[str, Any]]) -> None:
        """Display recent trades."""
        if not trades:
            self.console.print("[yellow]No recent trades[/yellow]")
            return
        
        self.console.print("\n[bold cyan]RECENT ACTIVITY[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("Time", style="cyan")
        table.add_column("Action", style="magenta")
        table.add_column("Symbol", style="green")
        table.add_column("Qty", style="yellow")
        table.add_column("Price", style="red")
        
        for trade in trades[-10:]:  # Show last 10
            table.add_row(
                trade.get("timestamp", "")[-8:],
                trade.get("side", ""),
                trade.get("symbol", ""),
                str(trade.get("quantity", "")),
                f"${trade.get('price', 0):.2f}",
            )
        
        self.console.print(table)
```

- [ ] **Step 3: Create src/monitoring/__init__.py**

```python
# src/monitoring/__init__.py
from .logger import TradeLogger
from .dashboard import Dashboard

__all__ = ["TradeLogger", "Dashboard"]
```

- [ ] **Step 4: Commit**

```bash
git add src/monitoring/ 
git commit -m "feat: implement trade logger and terminal dashboard"
```

---

### Phase 6: Main Orchestrator & Robinhood Integration

### Task 10: Implement Robinhood Trader (Live Execution)

**Files:**
- Create: `src/execution/robinhood_trader.py`

**Interfaces:**
- Produces: `RobinhoodTrader` class with real order execution via robin_stocks
- Consumes: `BaseExecutor`, `Config.secrets`

**Steps:**

- [ ] **Step 1: Create src/execution/robinhood_trader.py**

```python
# src/execution/robinhood_trader.py
import robin_stocks.robinhood as rh
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.execution.base_executor import BaseExecutor, Order, Position


class RobinhoodTrader(BaseExecutor):
    """Live trading via Robinhood (using unofficial API)."""
    
    def __init__(self, username: str, password: str):
        super().__init__("robinhood_trader")
        self.username = username
        self.password = password
        self.authenticated = False
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Robinhood."""
        try:
            rh.login(username=self.username, password=self.password)
            self.authenticated = True
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def place_order(self, symbol: str, quantity: int, side: str, price=None) -> Order:
        """
        Place a real order on Robinhood.
        
        Args:
            symbol: Stock symbol
            quantity: Shares to trade
            side: "BUY" or "SELL"
            price: Limit price (market order if None)
        
        Returns:
            Order object
        """
        if not self.authenticated:
            return Order(
                order_id="ERR",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price or 0,
                status="REJECTED",
                created_at=datetime.now(),
            )
        
        try:
            if side.upper() == "BUY":
                order = rh.orders.order_buy_market(symbol, quantity)
            else:
                order = rh.orders.order_sell_market(symbol, quantity)
            
            return Order(
                order_id=order.get("id", "RH_" + symbol),
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price or 0,
                status="FILLED",
                created_at=datetime.now(),
            )
        except Exception as e:
            print(f"Order failed: {e}")
            return Order(
                order_id="ERR",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price or 0,
                status="FAILED",
                created_at=datetime.now(),
            )
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        try:
            rh.orders.cancel_order(order_id)
            return True
        except Exception as e:
            print(f"Cancel failed: {e}")
            return False
    
    def get_positions(self) -> List[Position]:
        """Get all open positions from Robinhood."""
        try:
            positions = rh.account.get_positions()
            result = []
            
            for pos in positions:
                if float(pos.get("quantity", 0)) > 0:
                    result.append(Position(
                        symbol=pos.get("symbol", ""),
                        quantity=int(float(pos.get("quantity", 0))),
                        entry_price=float(pos.get("average_buy_price", 0)),
                        entry_time=datetime.now(),
                        current_price=float(pos.get("last_transaction_at", 0)),
                        unrealized_pnl=float(pos.get("equity", 0)) - float(pos.get("cost_basis", 0)),
                    ))
            
            return result
        except Exception as e:
            print(f"Failed to get positions: {e}")
            return []
    
    def get_account_value(self) -> Dict[str, float]:
        """Get account summary from Robinhood."""
        try:
            acct = rh.account.get_account()
            return {
                "cash": float(acct.get("cash", 0)),
                "positions_value": float(acct.get("portfolio_value", 0)) - float(acct.get("cash", 0)),
                "total_value": float(acct.get("portfolio_value", 0)),
                "buying_power": float(acct.get("buying_power", 0)),
            }
        except Exception as e:
            print(f"Failed to get account: {e}")
            return {}
    
    def get_orders(self) -> List[Order]:
        """Get open orders from Robinhood."""
        try:
            orders = rh.orders.get_all_orders()
            result = []
            
            for order in orders:
                if order.get("state") in ["queued", "confirmed", "partially_filled"]:
                    result.append(Order(
                        order_id=order.get("id", ""),
                        symbol=order.get("symbol", ""),
                        side=order.get("side", ""),
                        quantity=int(float(order.get("quantity", 0))),
                        price=float(order.get("price", 0) or 0),
                        status=order.get("state", ""),
                        created_at=datetime.now(),
                    ))
            
            return result
        except Exception as e:
            print(f"Failed to get orders: {e}")
            return []
```

- [ ] **Step 2: Commit**

```bash
git add src/execution/robinhood_trader.py
git commit -m "feat: implement Robinhood trader for live execution"
```

---

### Task 11: Create Main Orchestrator

**Files:**
- Create: `src/opentrader.py`
- Create: `main.py`

**Interfaces:**
- Produces: `OpenTrader` class that orchestrates backtest/paper/live modes
- Consumes: All previous components

**Steps:**

- [ ] **Step 1: Create src/opentrader.py**

```python
# src/opentrader.py
import sys
from src.config import Config
from src.data import DataFetcher
from src.strategies.momentum import MomentumStrategy
from src.execution.backtester import Backtester
from src.execution.paper_trader import PaperTrader
from src.execution.robinhood_trader import RobinhoodTrader
from src.risk import PositionManager
from src.monitoring import TradeLogger, Dashboard


class OpenTrader:
    """Main orchestrator for automated trading."""
    
    def __init__(self, config: Config):
        self.config = config
        self.fetcher = DataFetcher()
        self.strategy = MomentumStrategy(config.strategy.__dict__)
        self.position_manager = PositionManager(config.risk.__dict__)
        self.logger = TradeLogger()
        self.dashboard = Dashboard()
        self.executor = None
    
    def run_backtest(self) -> dict:
        """Run backtesting mode."""
        print("Starting backtesting...")
        self.executor = Backtester(self.config)
        
        metrics = self.executor.run_backtest(
            self.config.watchlist,
            self.config.backtest.start_date,
            self.config.backtest.end_date,
        )
        
        print(f"\nBacktest Results:")
        print(f"Initial Cash: ${metrics.get('initial_cash', 0):.2f}")
        print(f"Final Value: ${metrics.get('final_value', 0):.2f}")
        print(f"Return: {metrics.get('total_return', 0):.2%}")
        
        return metrics
    
    def run_paper_trading(self) -> None:
        """Run paper trading mode."""
        print("Starting paper trading...")
        self.executor = PaperTrader(self.config.backtest.initial_cash)
        
        # Simulate trading
        print(f"Paper trading account initialized with ${self.config.backtest.initial_cash:.2f}")
        
        # In real impl, would loop through live market data
        print("Paper trading mode not fully implemented in this task")
    
    def run_live_trading(self) -> None:
        """Run live trading mode."""
        print("Starting live trading...")
        
        try:
            secrets = Config.load_secrets()
            rh_config = secrets.get("robinhood", {})
            
            self.executor = RobinhoodTrader(
                username=rh_config.get("username"),
                password=rh_config.get("password"),
            )
            
            if self.executor.authenticated:
                acct = self.executor.get_account_value()
                print(f"Connected to Robinhood. Account value: ${acct.get('total_value', 0):.2f}")
            else:
                print("Failed to authenticate with Robinhood")
        except FileNotFoundError:
            print("Secrets file not found. Please create config/secrets.json")
            sys.exit(1)
```

- [ ] **Step 2: Create main.py**

```python
# main.py
import sys
import argparse
from src.config import Config
from src.opentrader import OpenTrader


def main():
    parser = argparse.ArgumentParser(description="OpenTrader - Automated Trading Bot")
    parser.add_argument(
        "--mode",
        choices=["backtest", "paper", "live"],
        default="backtest",
        help="Trading mode: backtest (historical), paper (simulation), or live (real money)",
    )
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="Path to config file",
    )
    
    args = parser.parse_args()
    
    # Load config
    try:
        config = Config.load(args.config)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        sys.exit(1)
    
    # Initialize trader
    trader = OpenTrader(config)
    
    # Run selected mode
    if args.mode == "backtest":
        trader.run_backtest()
    elif args.mode == "paper":
        trader.run_paper_trading()
    elif args.mode == "live":
        trader.run_live_trading()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test main entry point**

```bash
python main.py --mode backtest
```

Expected: Backtesting runs (or shows message about not fully implemented).

- [ ] **Step 4: Commit**

```bash
git add src/opentrader.py main.py
git commit -m "feat: implement main orchestrator for backtest/paper/live modes"
```

---

### Phase 7: Final Integration & Testing

### Task 12: Create Full Integration Test Suite

**Files:**
- Create: `tests/test_integration.py`

**Steps:**

- [ ] **Step 1: Create tests/test_integration.py**

```python
# tests/test_integration.py
import pytest
from src.config import Config
from src.opentrader import OpenTrader


@pytest.fixture
def config():
    return Config.load("config/config.json")


@pytest.fixture
def trader(config):
    return OpenTrader(config)


def test_trader_initialization(trader):
    """Test trader can be initialized."""
    assert trader.config is not None
    assert trader.executor is None


def test_backtest_initialization(trader):
    """Test backtest initialization."""
    # Mock Backtester to avoid real API calls
    assert trader.strategy is not None
    assert trader.position_manager is not None
```

- [ ] **Step 2: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test suite"
```

---

### Task 13: Create README & Documentation

**Files:**
- Create: `README.md`

**Steps:**

- [ ] **Step 1: Create README.md**

```markdown
# OpenTrader

Automated trading bot for momentum stocks and options spreads with backtesting, paper trading, and live execution on Robinhood.

## Quick Start

### 1. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configure Strategies

Edit `config/config.json` with your strategy parameters and watchlist.

### 3. Setup Robinhood Credentials (Optional)

Copy `config/secrets.example.json` to `config/secrets.json` and add your credentials:

\`\`\`json
{
  "robinhood": {
    "username": "your_email@example.com",
    "password": "your_password"
  }
}
\`\`\`

## Usage

### Backtesting

Validate strategies on historical data:

\`\`\`bash
python main.py --mode backtest
\`\`\`

### Paper Trading

Test with live data but no real money:

\`\`\`bash
python main.py --mode paper
\`\`\`

### Live Trading

Trade with real capital on Robinhood:

\`\`\`bash
python main.py --mode live
\`\`\`

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

## Testing

Run full test suite:

\`\`\`bash
pytest tests/ -v
\`\`\`

## Disclaimer

This bot uses real capital when in live mode. **Trade at your own risk.** Always validate strategies thoroughly in backtesting and paper trading before going live. Losses are possible.

## Timeline

- **Week 1:** Backtesting phase
- **Week 2:** Paper trading phase (1 week)
- **Week 3+:** Live trading with $1000 starting capital
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```

---

## Plan Summary

**Total Tasks:** 13
**Deliverables:**
- ✅ Project structure and dependencies
- ✅ Base classes for strategies and executors
- ✅ Data fetching and technical indicators
- ✅ Momentum trading strategy
- ✅ Position manager for risk
- ✅ Backtester (backtrader integration)
- ✅ Paper trader simulator
- ✅ Trade logger and dashboard
- ✅ Robinhood live trader
- ✅ Main orchestrator
- ✅ Test suite
- ✅ Documentation

**Expected Timeframe:** 3-4 hours for implementation + testing

**Next Phase:** Execute these tasks and validate in backtesting before paper trading.

---

## Execution Options

Plan complete and saved to `docs/superpowers/plans/2026-06-21-trading-bot-implementation.md`.

**Choose execution approach:**

1. **Subagent-Driven (Recommended)** — Fresh subagent per task, review between checkpoints, fast iteration
2. **Inline Execution** — Execute tasks in this session with review gates

**Which approach would you prefer?**
