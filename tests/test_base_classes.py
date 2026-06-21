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
