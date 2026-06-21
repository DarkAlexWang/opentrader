from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any
from src.execution.base_executor import Position


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

        for trade in trades[-10:]:
            table.add_row(
                trade.get("timestamp", "")[-8:],
                trade.get("side", ""),
                trade.get("symbol", ""),
                str(trade.get("quantity", "")),
                f"${trade.get('price', 0):.2f}",
            )

        self.console.print(table)
