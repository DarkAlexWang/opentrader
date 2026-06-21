import sys
from src.config import Config
from src.data import DataFetcher
from src.strategies.momentum import MomentumStrategy
from src.execution.paper_trader import PaperTrader
from src.risk import PositionManager
from src.monitoring import TradeLogger, Dashboard


class OpenTrader:
    """Main orchestrator for automated trading."""

    def __init__(self, config: Config):
        self.config = config
        self.fetcher = DataFetcher()
        self.strategy = MomentumStrategy(config.strategy.__dict__)
        self.position_manager = PositionManager(config.risk.__dict__)
        self.logger = TradeLogger()
        self.dashboard = Dashboard()
        self.executor = None

    def run_backtest(self) -> dict:
        """Run backtesting mode."""
        from src.execution.backtester import Backtester

        backtester = Backtester(self.config)
        metrics = backtester.run_backtest(
            self.config.watchlist,
            self.config.backtest.start_date,
            self.config.backtest.end_date,
        )
        return metrics

    def run_paper_trading(self) -> None:
        """Run paper trading mode."""
        print("Starting paper trading...")
        self.executor = PaperTrader(self.config.backtest.initial_cash)

        acct = self.executor.get_account_value()
        print(f"✓ Paper trading account initialized with ${acct['total_value']:.2f}")
        print("Paper trading mode ready for live market data ingestion")

    def run_live_trading(self) -> None:
        """Run live trading mode."""
        print("Starting live trading...")

        try:
            from src.execution.robinhood_trader import RobinhoodTrader

            secrets = Config.load_secrets()
            rh_config = secrets.get("robinhood", {})

            self.executor = RobinhoodTrader(
                username=rh_config.get("username"),
                password=rh_config.get("password"),
            )

            if self.executor.authenticated:
                acct = self.executor.get_account_value()
                print(f"✓ Connected to Robinhood. Account value: ${acct.get('total_value', 0):.2f}")
            else:
                print("✗ Failed to authenticate with Robinhood")
        except FileNotFoundError:
            print("✗ Secrets file not found. Please create config/secrets.json")
            sys.exit(1)
        except ImportError:
            print("✗ robin_stocks module not installed. Run: pip install robin-stocks")
            sys.exit(1)
