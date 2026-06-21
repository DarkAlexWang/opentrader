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
        """Simulate order placement."""
        order_id = f"PAPER_{len(self.orders) + 1}"

        fill_price = price or 100.0
        fill_amount = quantity * fill_price

        if side == "BUY":
            if fill_amount > self.cash:
                status = "REJECTED"
            else:
                self.cash -= fill_amount
                status = "FILLED"
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=fill_price,
                    entry_time=datetime.now(),
                    current_price=fill_price,
                    unrealized_pnl=0,
                )
        else:
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
