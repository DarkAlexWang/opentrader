import yfinance as yf
import pandas as pd
from typing import Optional


class DataFetcher:
    """Fetches market data from yfinance."""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self._cache = {}

    def fetch_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol.

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Candle interval ("1m", "5m", "1h", "1d")

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)

        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")

        self._cache[cache_key] = df
        return df

    def fetch_latest_quote(self, symbol: str) -> dict:
        """
        Fetch latest quote for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Dict with {price, bid, ask, volume}
        """
        ticker = yf.Ticker(symbol)
        data = ticker.info

        return {
            "price": data.get("currentPrice", data.get("regularMarketPrice")),
            "bid": data.get("bid"),
            "ask": data.get("ask"),
            "volume": data.get("volume"),
        }

    def fetch_intraday(self, symbol: str, interval: str = "5m") -> pd.DataFrame:
        """
        Fetch intraday data for today.

        Args:
            symbol: Stock symbol
            interval: Candle interval ("1m", "5m", "15m", "1h")

        Returns:
            DataFrame with OHLCV
        """
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval=interval)
        return df
