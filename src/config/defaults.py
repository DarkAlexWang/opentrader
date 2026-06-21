from dataclasses import dataclass
from typing import List, Dict, Any
import json
import os


@dataclass
class MomentumConfig:
    enabled: bool
    resistance_period: int
    volume_spike_threshold: float
    stop_loss_pct: float
    take_profit_target_1: float
    take_profit_target_2: float
    max_hold_hours: float


@dataclass
class OptionsConfig:
    enabled: bool
    iv_percentile_threshold: int
    spread_width: float
    days_to_expiration_min: int
    days_to_expiration_max: int
    target_delta: float


@dataclass
class StrategyConfig:
    momentum: MomentumConfig
    options: OptionsConfig


@dataclass
class RiskConfig:
    stock_risk_pct: float
    options_risk_pct: float
    max_concurrent_positions: int
    daily_loss_limit_pct: float
    max_drawdown_pct: float


@dataclass
class BrokerConfig:
    type: str
    trading_hours_start: str
    trading_hours_end: str
    timezone: str


@dataclass
class BacktestConfig:
    start_date: str
    end_date: str
    initial_cash: float


@dataclass
class Config:
    strategy: StrategyConfig
    risk: RiskConfig
    broker: BrokerConfig
    watchlist: List[str]
    backtest: BacktestConfig

    @staticmethod
    def load(config_path: str = "config/config.json") -> "Config":
        """Load config from JSON file."""
        with open(config_path, "r") as f:
            data = json.load(f)

        return Config(
            strategy=StrategyConfig(
                momentum=MomentumConfig(**data["strategy"]["momentum"]),
                options=OptionsConfig(**data["strategy"]["options"]),
            ),
            risk=RiskConfig(**data["risk"]),
            broker=BrokerConfig(**data["broker"]),
            watchlist=data["watchlist"],
            backtest=BacktestConfig(**data["backtest"]),
        )

    @staticmethod
    def load_secrets(secrets_path: str = "config/secrets.json") -> Dict[str, Any]:
        """Load secrets (credentials) from JSON file."""
        if not os.path.exists(secrets_path):
            raise FileNotFoundError(f"Secrets file not found: {secrets_path}")
        with open(secrets_path, "r") as f:
            return json.load(f)
