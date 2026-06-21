#!/usr/bin/env python3
"""
Comprehensive strategy optimization: 1000 parameter combinations.
Tests broad parameter ranges and finds optimal configuration.
Then runs best strategy 10 times to verify stability.
"""

import sys
import numpy as np
from src.config import Config
from src.execution.optimizer import StrategyOptimizer


def generate_parameter_grid(n_params=1000):
    """Generate 1000 parameter combinations across meaningful ranges."""

    # Define parameter ranges (broader search space)
    sma_fast_range = np.linspace(5, 20, 8).astype(int)      # 5-20, 8 values
    sma_slow_range = np.linspace(25, 60, 10).astype(int)    # 25-60, 10 values
    tp_range = np.linspace(0.02, 0.10, 5)                   # 2%-10%, 5 values
    sl_range = np.linspace(0.01, 0.04, 5)                   # 1%-4%, 5 values

    # Generate combinations: 8 * 10 * 5 * 5 = 2000 potential combinations
    # We'll sample 1000 of them systematically

    params_list = []
    total_combos = len(sma_fast_range) * len(sma_slow_range) * len(tp_range) * len(sl_range)

    # Create systematic sampling to get ~1000 combinations
    step = max(1, total_combos // 1000)

    combo_idx = 0
    for sma_fast in sma_fast_range:
        for sma_slow in sma_slow_range:
            if sma_slow <= sma_fast:  # Slow must be > fast
                continue
            for tp in tp_range:
                for sl in sl_range:
                    if combo_idx % step == 0:
                        params_list.append({
                            "sma_fast": int(sma_fast),
                            "sma_slow": int(sma_slow),
                            "tp_pct": float(tp),
                            "sl_pct": float(sl),
                        })
                    combo_idx += 1

    # If we don't have enough, add some random combinations
    while len(params_list) < 1000:
        params_list.append({
            "sma_fast": int(np.random.choice(sma_fast_range)),
            "sma_slow": int(np.random.choice(sma_slow_range)),
            "tp_pct": float(np.random.choice(tp_range)),
            "sl_pct": float(np.random.choice(sl_range)),
        })

    return params_list[:1000]


def main():
    print("\n" + "="*100)
    print("🚀 OPENTRADER - EXHAUSTIVE PARAMETER OPTIMIZATION (1000 Combinations)")
    print("="*100 + "\n")

    # Load config
    try:
        config = Config.load("config/config.json")
    except FileNotFoundError:
        print("❌ Config file not found: config/config.json")
        sys.exit(1)

    # Generate 1000 parameter combinations
    print("📋 Generating 1000 parameter combinations...")
    param_sets = generate_parameter_grid(1000)
    print(f"✓ Generated {len(param_sets)} parameter combinations\n")

    # Print search space info
    print("Search Space:")
    print(f"  SMA Fast:    5-20")
    print(f"  SMA Slow:    25-60")
    print(f"  Take Profit: 2%-10%")
    print(f"  Stop Loss:   1%-4%")
    print(f"  Total combinations tested: {len(param_sets)}\n")

    # Initialize optimizer
    optimizer = StrategyOptimizer(config)

    # Run optimization
    print("🔄 Running backtest on all 1000 combinations...")
    print("(This may take 2-5 minutes)\n")

    results = []
    best_return = None
    best_strategy = None

    for i, params in enumerate(param_sets, 1):
        if i % 100 == 0 or i == 1:
            print(f"  Progress: {i}/1000 combinations tested...", end="\r")

        metrics = optimizer.backtest_with_params(params, config.watchlist,
                                                 config.backtest.start_date,
                                                 config.backtest.end_date)
        results.append(metrics)

        # Track best
        if best_return is None or metrics['total_return_pct'] > best_return:
            best_return = metrics['total_return_pct']
            best_strategy = metrics

    print(f"  Progress: {len(param_sets)}/1000 combinations tested...✓\n")

    # Report results
    print("="*100)
    print("TOP 10 STRATEGIES BY RETURN")
    print("="*100 + "\n")

    # Sort by return
    sorted_results = sorted(results, key=lambda x: x['total_return_pct'], reverse=True)

    print(f"{'Rank':<5} {'SMA F':<8} {'SMA S':<8} {'TP%':<8} {'SL%':<8} "
          f"{'Return%':<12} {'Trades':<8} {'Win%':<8} {'Sharpe':<8} {'Drawdown%':<12}\n")
    print("-"*100)

    for rank, strategy in enumerate(sorted_results[:10], 1):
        p = strategy['params']
        print(f"{rank:<5} {p['sma_fast']:<8} {p['sma_slow']:<8} {p['tp_pct']*100:<8.1f} {p['sl_pct']*100:<8.1f} "
              f"{strategy['total_return_pct']:<12.2f} {strategy['total_trades']:<8} "
              f"{strategy['win_rate']:<8.1f} {strategy['sharpe_ratio']:<8.2f} "
              f"{strategy['max_drawdown']:<12.2f}")

    # Best strategy details
    best_strategy = sorted_results[0]
    print("\n" + "="*100)
    print("🏆 BEST STRATEGY (By Return)")
    print("="*100)
    print(f"\nParameters:")
    print(f"  SMA Fast:      {best_strategy['params']['sma_fast']}")
    print(f"  SMA Slow:      {best_strategy['params']['sma_slow']}")
    print(f"  Take Profit:   {best_strategy['params']['tp_pct']*100:.1f}%")
    print(f"  Stop Loss:     {best_strategy['params']['sl_pct']*100:.1f}%")

    print(f"\nPerformance Metrics:")
    print(f"  Return:        {best_strategy['total_return_pct']:+.2f}%")
    print(f"  Initial:       ${best_strategy['initial_cash']:.2f}")
    print(f"  Final:         ${best_strategy['final_value']:.2f}")
    print(f"  Trades:        {best_strategy['total_trades']}")
    print(f"  Win Rate:      {best_strategy['win_rate']:.1f}%")
    print(f"  Sharpe Ratio:  {best_strategy['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:  {best_strategy['max_drawdown']:.2f}%")

    # Stability analysis: Run best strategy 10 times
    print("\n" + "="*100)
    print("📊 STABILITY TEST: Running Best Strategy 10 Times (Different Time Periods)")
    print("="*100 + "\n")

    stability_results = []
    print("Testing stability across different time windows...\n")

    # Create 10 different time windows
    import pandas as pd
    from datetime import datetime, timedelta

    start_date = datetime.strptime(config.backtest.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(config.backtest.end_date, "%Y-%m-%d")
    total_days = (end_date - start_date).days

    for run in range(1, 11):
        # Create sliding windows
        window_size = total_days // 2  # Use half the data for each window
        offset = (total_days - window_size) * (run - 1) // 9

        window_start = start_date + timedelta(days=offset)
        window_end = window_start + timedelta(days=window_size)

        window_start_str = window_start.strftime("%Y-%m-%d")
        window_end_str = window_end.strftime("%Y-%m-%d")

        print(f"[{run}/10] Testing {window_start_str} to {window_end_str}...", end=" ")

        metrics = optimizer.backtest_with_params(
            best_strategy['params'],
            config.watchlist,
            window_start_str,
            window_end_str
        )
        stability_results.append(metrics)

        print(f"✓ Return: {metrics['total_return_pct']:+.2f}% | "
              f"Win%: {metrics['win_rate']:.1f}% | Sharpe: {metrics['sharpe_ratio']:.2f}")

    # Calculate average performance
    print("\n" + "="*100)
    print("STABILITY ANALYSIS RESULTS")
    print("="*100 + "\n")

    avg_return = np.mean([r['total_return_pct'] for r in stability_results])
    std_return = np.std([r['total_return_pct'] for r in stability_results])
    avg_win_rate = np.mean([r['win_rate'] for r in stability_results])
    std_win_rate = np.std([r['win_rate'] for r in stability_results])
    avg_sharpe = np.mean([r['sharpe_ratio'] for r in stability_results])
    std_sharpe = np.std([r['sharpe_ratio'] for r in stability_results])
    avg_drawdown = np.mean([r['max_drawdown'] for r in stability_results])
    std_drawdown = np.std([r['max_drawdown'] for r in stability_results])

    print(f"📈 Return Statistics (10 runs):")
    print(f"   Average:  {avg_return:+.2f}%")
    print(f"   Std Dev:  {std_return:.2f}%")
    print(f"   Range:    {min([r['total_return_pct'] for r in stability_results]):+.2f}% to "
          f"{max([r['total_return_pct'] for r in stability_results]):+.2f}%")
    print(f"   Consistency: {'✓ STABLE' if std_return < 5 else '⚠️  VOLATILE'}")

    print(f"\n✓ Win Rate Statistics:")
    print(f"   Average:  {avg_win_rate:.1f}%")
    print(f"   Std Dev:  {std_win_rate:.1f}%")
    print(f"   Range:    {min([r['win_rate'] for r in stability_results]):.1f}% to "
          f"{max([r['win_rate'] for r in stability_results]):.1f}%")

    print(f"\n📊 Sharpe Ratio Statistics:")
    print(f"   Average:  {avg_sharpe:.2f}")
    print(f"   Std Dev:  {std_sharpe:.2f}")
    print(f"   Range:    {min([r['sharpe_ratio'] for r in stability_results]):.2f} to "
          f"{max([r['sharpe_ratio'] for r in stability_results]):.2f}")

    print(f"\n⚠️  Max Drawdown Statistics:")
    print(f"   Average:  {avg_drawdown:.2f}%")
    print(f"   Std Dev:  {std_drawdown:.2f}%")
    print(f"   Range:    {min([r['max_drawdown'] for r in stability_results]):.2f}% to "
          f"{max([r['max_drawdown'] for r in stability_results]):.2f}%")

    # Final verdict
    print("\n" + "="*100)
    print("FINAL VERDICT")
    print("="*100)

    if avg_return > 5 and std_return < 10 and avg_win_rate > 50:
        verdict = "✅ EXCELLENT - Ready for live trading"
    elif avg_return > 0 and std_return < 15 and avg_win_rate > 45:
        verdict = "✓ GOOD - Monitor closely before going live"
    else:
        verdict = "⚠️  CAUTION - Further optimization needed"

    print(f"\nStrategy: SMA({best_strategy['params']['sma_fast']}, "
          f"{best_strategy['params']['sma_slow']}) "
          f"TP={best_strategy['params']['tp_pct']*100:.1f}% "
          f"SL={best_strategy['params']['sl_pct']*100:.1f}%")
    print(f"\nAverage Performance (10 runs):")
    print(f"  Return: {avg_return:+.2f}% ± {std_return:.2f}%")
    print(f"  Win Rate: {avg_win_rate:.1f}% ± {std_win_rate:.1f}%")
    print(f"  Sharpe: {avg_sharpe:.2f} ± {std_sharpe:.2f}")
    print(f"\n{verdict}\n")

    return best_strategy, stability_results


if __name__ == "__main__":
    best_strategy, stability_results = main()
