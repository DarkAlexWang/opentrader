import backtrader as bt
import pandas as pd
from datetime import datetime
from src.data import DataFetcher, Indicators
from src.config import Config


class MomentumBTStrategy(bt.Strategy):
    """Backtrader strategy wrapper for momentum trading."""

    def __init__(self):
        self.indicators = Indicators()
        self.trades_count = 0
        self.wins = 0
        self.losses = 0

    def next(self):
        """Called on each bar."""
        if not self.position:
            # Entry logic: simple breakout on close > 20-day high
            if len(self) >= 20:
                high_20 = max(self.data.high.get(size=20))
                if self.data.close[0] > high_20 * 0.99:  # Entry at recent high
                    self.buy(size=10)
        else:
            # Exit logic
            entry_price = self.position.barlen[0] if hasattr(self.position, 'barlen') else self.data.close[0]
            current_price = self.data.close[0]

            # Stop loss: 2.5% below entry
            stop_loss = entry_price * 0.975
            if current_price <= stop_loss:
                self.sell()
                self.losses += 1
                self.trades_count += 1
            # Take profit: +5%
            elif current_price >= entry_price * 1.05:
                self.sell()
                self.wins += 1
                self.trades_count += 1


class Backtester:
    """Backtest execution engine using backtrader."""

    def __init__(self, config: Config):
        self.config = config
        self.fetcher = DataFetcher()

    def run_backtest(self, watchlist, start_date: str, end_date: str) -> dict:
        """
        Run backtest on watchlist.

        Args:
            watchlist: List of symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dict with backtest metrics
        """
        print(f"\n📊 Running backtest on {len(watchlist)} symbols...")
        print(f"   Period: {start_date} to {end_date}")
        print(f"   Initial capital: ${self.config.backtest.initial_cash}\n")

        cerebro = bt.Cerebro()

        # Add data feeds
        data_count = 0
        for symbol in watchlist[:5]:  # Limit to 5 for speed
            try:
                df = self.fetcher.fetch_ohlcv(symbol, start_date, end_date, interval="1d")

                if df.empty:
                    print(f"   ⚠️  {symbol}: No data available")
                    continue

                # Create backtrader data feed
                data = bt.feeds.PandasData(
                    dataname=df,
                    fromdate=pd.to_datetime(start_date),
                    todate=pd.to_datetime(end_date),
                )
                cerebro.adddata(data, name=symbol)
                data_count += 1
                print(f"   ✓ {symbol}: {len(df)} bars loaded")

            except Exception as e:
                print(f"   ✗ {symbol}: {str(e)[:50]}")
                continue

        if data_count == 0:
            print("\n❌ No data loaded. Check internet connection or symbols.")
            return self._empty_metrics()

        # Add strategy and analyzers
        cerebro.addstrategy(MomentumBTStrategy)
        cerebro.broker.setcash(self.config.backtest.initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        # Run backtest
        print(f"\n🔄 Running strategy...\n")
        results = cerebro.run()
        strat = results[0]

        # Extract metrics
        metrics = self._extract_metrics(cerebro, strat)

        # Print results
        self._print_results(metrics)

        return metrics

    def _extract_metrics(self, cerebro, strat) -> dict:
        """Extract backtest metrics from results."""
        initial_value = self.config.backtest.initial_cash
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_value) / initial_value

        # Analyzers
        sharpe = strat.analyzers.sharpe.get_analysis() if strat.analyzers.sharpe else {}
        drawdown = strat.analyzers.drawdown.get_analysis() if strat.analyzers.drawdown else {}
        trades_analysis = strat.analyzers.trades.get_analysis() if strat.analyzers.trades else {}

        # Extract trade statistics
        total_trades = 0
        winning_trades = 0
        losing_trades = 0

        # Parse trades analysis
        if trades_analysis:
            # Get total trades count
            for key, value in trades_analysis.items():
                if isinstance(value, dict) and 'total' in value:
                    total_trades += value['total']

            # Count wins and losses from trade details
            if 'total' in trades_analysis:
                total_trades = trades_analysis['total'].get('total', 0)

            if 'won' in trades_analysis:
                winning_trades = trades_analysis['won'].get('total', 0)

            if 'lost' in trades_analysis:
                losing_trades = trades_analysis['lost'].get('total', 0)

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        max_drawdown = drawdown.get('max', {}).get('drawdown', 0) if drawdown else 0
        sharpe_ratio = sharpe.get('sharperatio', 0) if sharpe else 0
        sharpe_ratio = sharpe_ratio if sharpe_ratio is not None else 0

        return {
            "initial_cash": initial_value,
            "final_value": final_value,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "max_drawdown": max_drawdown,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "sharpe_ratio": sharpe_ratio,
        }

    def _empty_metrics(self) -> dict:
        """Return empty metrics dict."""
        return {
            "initial_cash": self.config.backtest.initial_cash,
            "final_value": self.config.backtest.initial_cash,
            "total_return": 0,
            "total_return_pct": 0,
            "max_drawdown": 0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "sharpe_ratio": 0,
        }

    def _print_results(self, metrics: dict) -> None:
        """Print backtest results in formatted table."""
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"Initial Capital:      ${metrics['initial_cash']:,.2f}")
        print(f"Final Value:          ${metrics['final_value']:,.2f}")
        print(f"Total Return:         {metrics['total_return_pct']:+.2f}%")
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown:       {metrics['max_drawdown']:.2f}%")
        print(f"  Sharpe Ratio:       {metrics['sharpe_ratio']:.2f}")
        print(f"\nTrade Statistics:")
        print(f"  Total Trades:       {metrics['total_trades']}")
        print(f"  Wins:               {metrics['winning_trades']}")
        print(f"  Losses:             {metrics['losing_trades']}")
        print(f"  Win Rate:           {metrics['win_rate']:.1f}%")
        print("=" * 60)

        # Verdict
        if metrics['total_return_pct'] > 0:
            status = "✓ PROFITABLE"
        else:
            status = "✗ LOSS"

        print(f"\n{status} | Ready for paper trading? {self._verdict(metrics)}\n")

    def _verdict(self, metrics: dict) -> str:
        """Determine if strategy is ready for paper trading."""
        if metrics['total_trades'] < 5:
            return "❌ Too few trades (need ≥5)"
        if metrics['win_rate'] < 40:
            return "❌ Win rate too low (need ≥40%)"
        if metrics['max_drawdown'] > 30:
            return "❌ Drawdown too high (need ≤30%)"
        if metrics['sharpe_ratio'] < 0.5:
            return "⚠️  Low Sharpe ratio (need ≥0.5)"
        return "✅ YES - Meets criteria"
