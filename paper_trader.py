#!/usr/bin/env python3
"""
Live Paper Trading Mode - Simulated execution with real market data.
Runs continuously during market hours, shows live dashboard.
"""

import sys
import time
from datetime import datetime, time as dtime
import pytz
from src.config import Config
from src.data import DataFetcher, Indicators
from src.execution.paper_trader import PaperTrader
from src.strategies.momentum import MomentumStrategy
from src.risk import PositionManager
from src.monitoring import Dashboard, TradeLogger


def is_market_hours():
    """Check if current time is during US market hours."""
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz).time()
    # Market hours: 9:30 AM - 4:00 PM EST
    return dtime(9, 30) <= now <= dtime(16, 0)


def get_market_day():
    """Check if today is a trading day."""
    tz = pytz.timezone('US/Eastern')
    today = datetime.now(tz).weekday()
    # 0-4 = Monday-Friday, 5-6 = Saturday-Sunday
    return today < 5


def main():
    print("\n" + "="*90)
    print("📊 OPENTRADER - LIVE PAPER TRADING MODE")
    print("="*90)
    print()

    # Load configuration
    try:
        config = Config.load("config/config.json")
    except FileNotFoundError:
        print("❌ Config file not found: config/config.json")
        sys.exit(1)

    # Initialize components
    print("🔧 Initializing paper trading components...")
    fetcher = DataFetcher()
    strategy = MomentumStrategy(config.strategy.__dict__)
    position_manager = PositionManager(config.risk.__dict__)
    paper_trader = PaperTrader(config.backtest.initial_cash)
    dashboard = Dashboard()
    logger = TradeLogger()

    print(f"✓ Strategy: Momentum (SMA 13, 36)")
    print(f"✓ Initial Capital: ${config.backtest.initial_cash:.2f}")
    print(f"✓ Risk per Trade: {config.risk.stock_risk_pct*100:.0f}% (stocks)")
    print(f"✓ Watchlist: {', '.join(config.watchlist[:5])}...")
    print()

    # Check market hours
    if not get_market_day():
        print("⚠️  Today is not a trading day (weekend)")
        print("Paper trading will start on the next trading day during market hours\n")
        return

    if not is_market_hours():
        tz = pytz.timezone('US/Eastern')
        now = datetime.now(tz)
        print(f"⏰ Current time: {now.strftime('%I:%M %p %Z')}")
        print("⏰ Market hours: 9:30 AM - 4:00 PM EST")
        print("Paper trading will start when market opens\n")
        return

    # Start paper trading loop
    print("="*90)
    print("🔄 LIVE PAPER TRADING ACTIVE")
    print("="*90)
    print()

    trade_count = 0
    iteration = 0

    try:
        while True:
            iteration += 1
            tz = pytz.timezone('US/Eastern')
            now = datetime.now(tz)

            # Check if market is closed
            if not is_market_hours() or not get_market_day():
                print(f"\n⏸️  Market closed at {now.strftime('%I:%M %p %Z')}")
                print("Paper trading will resume next trading day at 9:30 AM EST\n")
                break

            # Fetch latest data for watchlist
            print(f"\n[{now.strftime('%I:%M %p')}] Checking market data...", end=" ")

            try:
                latest_data = {}
                for symbol in config.watchlist[:3]:  # Check top 3 for speed
                    try:
                        quote = fetcher.fetch_latest_quote(symbol)
                        latest_data[symbol] = quote
                    except Exception as e:
                        pass

                if not latest_data:
                    print("⚠️ No data available yet")
                    time.sleep(30)
                    continue

                print(f"✓ Updated {len(latest_data)} symbols")

                # Show current portfolio
                account = paper_trader.get_account_value()
                positions = paper_trader.get_positions()

                daily_pnl = sum(p.unrealized_pnl for p in positions)
                total_pnl = account['total_value'] - config.backtest.initial_cash

                print(f"\n💰 Portfolio Status:")
                print(f"   Cash:          ${account['cash']:.2f}")
                print(f"   Positions:     {len(positions)}")
                print(f"   Total Value:   ${account['total_value']:.2f}")
                print(f"   Day P&L:       ${daily_pnl:+.2f}")
                print(f"   Total P&L:     ${total_pnl:+.2f} ({total_pnl/config.backtest.initial_cash*100:+.2f}%)")

                # Show open positions
                if positions:
                    print(f"\n📈 Open Positions:")
                    for pos in positions:
                        pnl_pct = (pos.unrealized_pnl / (pos.entry_price * pos.quantity)) * 100
                        print(f"   {pos.symbol}: {pos.quantity} shares @ ${pos.entry_price:.2f} → "
                              f"${pos.current_price:.2f} ({pnl_pct:+.2f}%, ${pos.unrealized_pnl:+.2f})")

                # Demo: Simulate occasional trades (for testing)
                if iteration % 5 == 0 and len(positions) < 2:  # Example trade every 5 iterations
                    symbol = config.watchlist[0]
                    price = latest_data.get(symbol, {}).get('price', 150)

                    if price and account['cash'] > price * 10:
                        # Simulate buy
                        order = paper_trader.place_order(symbol, 10, "BUY", price)
                        if order.status == "FILLED":
                            print(f"\n✅ BUY: {symbol} 10 @ ${price:.2f} [Demo]")
                            trade_count += 1

                # Check for exit conditions
                for pos in positions:
                    current_price = latest_data.get(pos.symbol, {}).get('price', pos.current_price)
                    if current_price:
                        paper_trader.update_position_prices(pos.symbol, current_price)

                        # Simple exit logic
                        entry_price = pos.entry_price
                        pnl_pct = (current_price - entry_price) / entry_price

                        if pnl_pct >= 0.10 or pnl_pct <= -0.018:  # TP or SL
                            order = paper_trader.place_order(pos.symbol, pos.quantity, "SELL", current_price)
                            if order.status == "FILLED":
                                exit_type = "TAKE PROFIT" if pnl_pct >= 0.10 else "STOP LOSS"
                                print(f"\n📉 {exit_type}: {pos.symbol} {pos.quantity} @ ${current_price:.2f} "
                                      f"({pnl_pct:+.2f}%)")
                                trade_count += 1

                # Sleep before next update (check market every 30 seconds)
                time.sleep(30)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️  Error: {str(e)[:50]}")
                time.sleep(30)
                continue

    except KeyboardInterrupt:
        print("\n\n⏹️  Paper trading stopped by user")

    # Final summary
    print("\n" + "="*90)
    print("📊 PAPER TRADING SESSION SUMMARY")
    print("="*90)

    final_account = paper_trader.get_account_value()
    final_pnl = final_account['total_value'] - config.backtest.initial_cash
    final_pnl_pct = final_pnl / config.backtest.initial_cash * 100

    print(f"\nInitial Capital:   ${config.backtest.initial_cash:.2f}")
    print(f"Final Value:       ${final_account['total_value']:.2f}")
    print(f"Total P&L:         ${final_pnl:+.2f} ({final_pnl_pct:+.2f}%)")
    print(f"Trades Executed:   {trade_count}")
    print(f"Open Positions:    {len(paper_trader.get_positions())}")

    print(f"\n💡 Next Steps:")
    print(f"   1. Monitor results over 1 week")
    print(f"   2. Compare to backtest expectations")
    print(f"   3. Go live when confident: python main.py --mode live\n")


if __name__ == "__main__":
    main()
