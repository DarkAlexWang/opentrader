from typing import Dict, Any


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
        """
        if entry_price <= 0 or stop_price >= entry_price:
            return 0

        risk_amount = account_value * risk_pct
        price_risk = entry_price - stop_price

        position_size = int(risk_amount / price_risk)

        if asset_type == "stock":
            max_qty = int(account_value / entry_price)
        else:
            max_qty = 10

        return min(position_size, max_qty)

    def get_recommended_risk_pct(self, asset_type: str = "stock") -> float:
        """Get recommended risk percentage for asset type."""
        if asset_type == "option":
            return self.options_risk_pct
        return self.stock_risk_pct
