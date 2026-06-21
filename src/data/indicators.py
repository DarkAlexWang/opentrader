import pandas as pd
import numpy as np
from typing import Tuple


class Indicators:
    """Technical indicator calculations."""

    @staticmethod
    def rsi(close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.

        Args:
            close: Close prices
            period: Look-back period

        Returns:
            RSI series (0-100)
        """
        delta = close.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def bollinger_bands(
        close: pd.Series, period: int = 20, num_std: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.

        Args:
            close: Close prices
            period: Look-back period
            num_std: Number of standard deviations

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()

        upper = middle + (num_std * std)
        lower = middle - (num_std * std)

        return upper, middle, lower

    @staticmethod
    def volume_ma(volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate volume moving average.

        Args:
            volume: Volume series
            period: Look-back period

        Returns:
            Volume MA series
        """
        return volume.rolling(window=period).mean()

    @staticmethod
    def atr(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range.

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Look-back period

        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def ema(close: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average.

        Args:
            close: Close prices
            period: Look-back period

        Returns:
            EMA series
        """
        return close.ewm(span=period, adjust=False).mean()
