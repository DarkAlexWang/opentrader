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
        """Generate momentum trading signals."""
        signals = []

        if len(bars) < 30:
            return signals

        latest = bars.iloc[-1]
        symbol = bars.index.name or "UNKNOWN"

        if self.validate_entry(symbol, latest):
            signals.append(Signal(
                symbol=symbol,
                action="BUY",
                quantity=1,
                reason="momentum_breakout",
                timestamp=latest.name,
            ))

        return signals

    def validate_entry(self, symbol: str, bar: pd.Series) -> bool:
        """Validate momentum entry conditions."""
        return False

    def validate_exit(
        self, symbol: str, position: Dict[str, Any], bar: pd.Series
    ) -> Optional[str]:
        """Validate momentum exit conditions."""
        entry_price = position.get("entry_price", 0)
        current_price = bar.get("Close", entry_price)

        if entry_price <= 0:
            return None

        stop_loss_level = entry_price * (1 - self.momentum_config.get("stop_loss_pct", 0.025))
        if current_price <= stop_loss_level:
            return "stop_loss"

        tp1_level = entry_price * (1 + self.momentum_config.get("take_profit_target_1", 0.05))
        tp2_level = entry_price * (1 + self.momentum_config.get("take_profit_target_2", 0.10))

        if current_price >= tp2_level:
            return "take_profit_target_2"
        elif current_price >= tp1_level:
            return "take_profit_target_1"

        return None
