#!/usr/bin/env python3
"""
Strategy parameter optimization script.
Tests 10 different parameter combinations and reports the best performer.
"""

import sys
from src.config import Config
from src.execution.optimizer import StrategyOptimizer


def main():
    print("\n🚀 OpenTrader - Strategy Parameter Optimization\n")

    # Load config
    try:
        config = Config.load("config/config.json")
    except FileNotFoundError:
        print("❌ Config file not found: config/config.json")
        sys.exit(1)

    # Initialize optimizer
    optimizer = StrategyOptimizer(config)

    # Run optimization
    param_sets, results = optimizer.optimize(
        config.watchlist,
        config.backtest.start_date,
        config.backtest.end_date,
    )

    # Report results
    best_strategy = optimizer.report_results(param_sets, results)

    # Save best parameters to config
    print("\n" + "=" * 90)
    print("✅ OPTIMIZATION COMPLETE")
    print("=" * 90)
    print(f"\n💾 Best Strategy Parameters:")
    print(f"   SMA Fast:  {best_strategy['params']['sma_fast']}")
    print(f"   SMA Slow:  {best_strategy['params']['sma_slow']}")
    print(f"   Take Profit: {best_strategy['params']['tp_pct']*100:.1f}%")
    print(f"   Stop Loss: {best_strategy['params']['sl_pct']*100:.1f}%")
    print(f"\n📊 Expected Performance:")
    print(f"   Return: {best_strategy['total_return_pct']:+.2f}%")
    print(f"   Win Rate: {best_strategy['win_rate']:.1f}%")
    print(f"   Sharpe Ratio: {best_strategy['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {best_strategy['max_drawdown']:.2f}%")

    print(f"\n💡 Next Steps:")
    print(f"   1. Update config.json with best parameters")
    print(f"   2. Run: python main.py --mode paper")
    print(f"   3. Trade for 1 week in paper mode")
    print(f"   4. Go live if profitable: python main.py --mode live\n")


if __name__ == "__main__":
    main()
