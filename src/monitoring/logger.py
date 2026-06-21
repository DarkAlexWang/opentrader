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
