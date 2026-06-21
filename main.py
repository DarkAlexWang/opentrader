import sys
import argparse
from src.config import Config
from src.opentrader import OpenTrader


def main():
    parser = argparse.ArgumentParser(description="OpenTrader - Automated Trading Bot")
    parser.add_argument(
        "--mode",
        choices=["backtest", "paper", "live"],
        default="backtest",
        help="Trading mode: backtest (historical), paper (simulation), or live (real money)",
    )
    parser.add_argument(
        "--config",
        default="config/config.json",
        help="Path to config file",
    )

    args = parser.parse_args()

    try:
        config = Config.load(args.config)
    except FileNotFoundError:
        print(f"✗ Config file not found: {args.config}")
        sys.exit(1)

    trader = OpenTrader(config)

    if args.mode == "backtest":
        trader.run_backtest()
    elif args.mode == "paper":
        trader.run_paper_trading()
    elif args.mode == "live":
        trader.run_live_trading()


if __name__ == "__main__":
    main()
