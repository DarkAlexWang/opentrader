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
        """Place a real order on Robinhood."""
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
