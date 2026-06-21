import backtrader as bt
import pandas as pd
from datetime import datetime
from src.data import DataFetcher
from src.config import Config


class OptimizableMomentumStrategy(bt.Strategy):
    """Backtrader strategy with tunable parameters."""

    params = (
        ('sma_fast', 10),
        ('sma_slow', 30),
        ('tp_pct', 0.03),
        ('sl_pct', 0.02),
    )

    def __init__(self):
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.params.sma_fast)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.params.sma_slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                size = int(self.broker.getcash() * 0.95 / self.data.close[0])
                if size > 0:
                    self.buy(size=size)
        else:
            current_price = self.data.close[0]
            entry_price = self.position.price

            if current_price >= entry_price * (1 + self.params.tp_pct):
                self.sell()
            elif current_price <= entry_price * (1 - self.params.sl_pct):
                self.sell()
            elif self.crossover < 0:
                self.sell()


class StrategyOptimizer:
    """Optimize strategy parameters."""

    def __init__(self, config: Config):
        self.config = config
        self.fetcher = DataFetcher()

    def backtest_with_params(self, params: dict, watchlist, start_date: str, end_date: str) -> dict:
        """Run backtest with specific parameters."""
        cerebro = bt.Cerebro()

        # Add data feeds
        for symbol in watchlist[:5]:
            try:
                df = self.fetcher.fetch_ohlcv(symbol, start_date, end_date, interval="1d")
                if df.empty:
                    continue

                data = bt.feeds.PandasData(
                    dataname=df,
                    fromdate=pd.to_datetime(start_date),
                    todate=pd.to_datetime(end_date),
                )
                cerebro.adddata(data, name=symbol)
            except:
                continue

        # Add strategy with parameters
        cerebro.addstrategy(OptimizableMomentumStrategy, **params)
        cerebro.broker.setcash(self.config.backtest.initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # Run backtest
        try:
            results = cerebro.run()
            strat = results[0]
        except:
            return self._empty_metrics()

        # Extract metrics
        initial_value = self.config.backtest.initial_cash
        final_value = cerebro.broker.getvalue()
        total_return = (final_value - initial_value) / initial_value

        sharpe = strat.analyzers.sharpe.get_analysis() if strat.analyzers.sharpe else {}
        drawdown = strat.analyzers.drawdown.get_analysis() if strat.analyzers.drawdown else {}
        trades_analysis = strat.analyzers.trades.get_analysis() if strat.analyzers.trades else {}

        total_trades = 0
        winning_trades = 0
        losing_trades = 0

        if trades_analysis:
            for key, value in trades_analysis.items():
                if isinstance(value, dict) and 'total' in value:
                    total_trades += value['total']

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
            "params": params,
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
            "profit_factor": (winning_trades / total_trades if total_trades > 0 else 0),
        }

    def _empty_metrics(self) -> dict:
        return {
            "params": {},
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
            "profit_factor": 0,
        }

    def optimize(self, watchlist, start_date: str, end_date: str) -> tuple:
        """Test 10 parameter combinations."""

        # 10 different parameter sets to test
        param_sets = [
            {"sma_fast": 5, "sma_slow": 20, "tp_pct": 0.03, "sl_pct": 0.02},
            {"sma_fast": 10, "sma_slow": 30, "tp_pct": 0.03, "sl_pct": 0.02},
            {"sma_fast": 10, "sma_slow": 30, "tp_pct": 0.05, "sl_pct": 0.015},
            {"sma_fast": 8, "sma_slow": 25, "tp_pct": 0.04, "sl_pct": 0.02},
            {"sma_fast": 12, "sma_slow": 35, "tp_pct": 0.05, "sl_pct": 0.025},
            {"sma_fast": 6, "sma_slow": 18, "tp_pct": 0.03, "sl_pct": 0.015},
            {"sma_fast": 15, "sma_slow": 40, "tp_pct": 0.06, "sl_pct": 0.03},
            {"sma_fast": 9, "sma_slow": 28, "tp_pct": 0.04, "sl_pct": 0.018},
            {"sma_fast": 7, "sma_slow": 22, "tp_pct": 0.035, "sl_pct": 0.017},
            {"sma_fast": 11, "sma_slow": 32, "tp_pct": 0.045, "sl_pct": 0.022},
        ]

        print("\n" + "=" * 90)
        print("PARAMETER OPTIMIZATION - Testing 10 Strategy Combinations")
        print("=" * 90)
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.config.backtest.initial_cash}\n")

        results = []
        for i, params in enumerate(param_sets, 1):
            print(f"[{i}/10] Testing: SMA({params['sma_fast']},{params['sma_slow']}) "
                  f"TP={params['tp_pct']*100:.1f}% SL={params['sl_pct']*100:.1f}%...", end=" ")

            metrics = self.backtest_with_params(params, watchlist, start_date, end_date)
            results.append(metrics)

            print(f"✓ Return: {metrics['total_return_pct']:+.2f}% | "
                  f"Trades: {metrics['total_trades']} | "
                  f"WR: {metrics['win_rate']:.1f}% | "
                  f"Sharpe: {metrics['sharpe_ratio']:.2f}")

        return param_sets, results

    def report_results(self, param_sets: list, results: list) -> dict:
        """Print detailed results and find best strategy."""

        print("\n" + "=" * 90)
        print("DETAILED RESULTS - All 10 Parameter Sets")
        print("=" * 90)

        # Create table header
        print(f"\n{'#':<3} {'SMA Fast':<10} {'SMA Slow':<10} {'TP%':<8} {'SL%':<8} "
              f"{'Return%':<12} {'Trades':<8} {'Win%':<8} {'Sharpe':<8} {'Drawdown%':<12}")
        print("-" * 90)

        # Print each result
        for i, metrics in enumerate(results, 1):
            params = metrics['params']
            print(f"{i:<3} {params['sma_fast']:<10} {params['sma_slow']:<10} "
                  f"{params['tp_pct']*100:<8.1f} {params['sl_pct']*100:<8.1f} "
                  f"{metrics['total_return_pct']:<12.2f} {metrics['total_trades']:<8} "
                  f"{metrics['win_rate']:<8.1f} {metrics['sharpe_ratio']:<8.2f} "
                  f"{metrics['max_drawdown']:<12.2f}")

        # Find best by different criteria
        print("\n" + "=" * 90)
        print("TOP PERFORMERS BY METRIC")
        print("=" * 90)

        best_return = max(results, key=lambda x: x['total_return_pct'])
        best_sharpe = max(results, key=lambda x: x['sharpe_ratio'])
        best_win_rate = max(results, key=lambda x: x['win_rate'])
        best_trades = max(results, key=lambda x: x['total_trades'])

        print(f"\n🏆 BEST RETURN:")
        self._print_strategy(best_return)

        print(f"\n📊 BEST SHARPE RATIO (Risk-adjusted returns):")
        self._print_strategy(best_sharpe)

        print(f"\n✓ BEST WIN RATE:")
        self._print_strategy(best_win_rate)

        print(f"\n📈 MOST TRADES:")
        self._print_strategy(best_trades)

        # Overall best (combination of metrics)
        print(f"\n🎯 OVERALL BEST (Balanced):")

        # Score: favor positive return + good Sharpe + win rate > 45%
        def score_strategy(metrics):
            return_score = max(0, metrics['total_return_pct']) * 0.4
            sharpe_score = max(0, metrics['sharpe_ratio']) * 0.4
            win_score = (metrics['win_rate'] - 40) if metrics['win_rate'] > 40 else 0
            return return_score + sharpe_score + win_score

        best_overall = max(results, key=score_strategy)
        self._print_strategy(best_overall)

        return best_overall

    def _print_strategy(self, metrics: dict) -> None:
        """Print strategy details."""
        params = metrics['params']
        print(f"   Parameters: SMA({params['sma_fast']}, {params['sma_slow']}) "
              f"TP={params['tp_pct']*100:.1f}% SL={params['sl_pct']*100:.1f}%")
        print(f"   Initial: ${metrics['initial_cash']:.2f} → Final: ${metrics['final_value']:.2f}")
        print(f"   Return: {metrics['total_return_pct']:+.2f}% | "
              f"Trades: {metrics['total_trades']} | "
              f"Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Sharpe: {metrics['sharpe_ratio']:.2f} | "
              f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
