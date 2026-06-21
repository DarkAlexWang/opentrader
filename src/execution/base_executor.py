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
