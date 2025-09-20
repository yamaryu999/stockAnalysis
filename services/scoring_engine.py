import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf


@dataclass
class ScoreResult:
    symbol: str
    score: float
    components: Dict[str, float]
    is_breakout: bool
    vol_zscore: float
    latest_price: float


@dataclass
class BacktestResult:
    symbol: str
    trades: int
    win_rate: float
    cum_return: float
    avg_trade_return: float


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period, min_periods=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period, min_periods=period).mean()
    rs = gain / (loss.replace(0, pd.NA))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(method="bfill").fillna(50)


def _calc_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line


def _zscore(series: pd.Series, window: int = 20) -> pd.Series:
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std(ddof=0)
    return (series - rolling_mean) / (rolling_std.replace(0, pd.NA))


def fetch_price_history(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    data = yf.Ticker(symbol).history(period=period, auto_adjust=True)
    if data is None or data.empty:
        return None
    return data.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})


def compute_composite_score(symbol: str, data: pd.DataFrame) -> ScoreResult:
    close = data["close"]
    volume = data["volume"]

    rsi = _calc_rsi(close, 14)
    macd, signal = _calc_macd(close)
    macd_hist = macd - signal

    high_252 = data["high"].rolling(252, min_periods=60).max()
    is_breakout = close.iloc[-1] >= 0.995 * high_252.iloc[-1] if not math.isnan(high_252.iloc[-1]) else False

    vol_z = _zscore(volume, 20).iloc[-1]

    # 正規化スコア（0-100）
    rsi_score = max(0.0, min(100.0, (rsi.iloc[-1] - 50) * 2))  # 50→0, 100→100 近似
    macd_score = max(0.0, min(100.0, (macd_hist.iloc[-1] / (close.iloc[-1] * 0.005)) * 50 + 50))  # スケーリング
    breakout_score = 100.0 if is_breakout else 0.0
    volume_score = max(0.0, min(100.0, (float(vol_z) if pd.notna(vol_z) else 0.0) * 15 + 50))

    # 重みづけ合成
    weights = {
        "rsi": 0.25,
        "macd": 0.25,
        "breakout": 0.30,
        "volume": 0.20,
    }
    composite = (
        rsi_score * weights["rsi"]
        + macd_score * weights["macd"]
        + breakout_score * weights["breakout"]
        + volume_score * weights["volume"]
    )

    return ScoreResult(
        symbol=symbol,
        score=round(float(composite), 2),
        components={
            "rsi": round(float(rsi_score), 2),
            "macd": round(float(macd_score), 2),
            "breakout": round(float(breakout_score), 2),
            "volume": round(float(volume_score), 2),
        },
        is_breakout=is_breakout,
        vol_zscore=float(vol_z) if pd.notna(vol_z) else 0.0,
        latest_price=float(close.iloc[-1]),
    )


def simple_rule_backtest(symbol: str, data: pd.DataFrame, score_series: pd.Series, threshold: float = 65.0, hold_days: int = 5) -> BacktestResult:
    close = data["close"].copy()
    signals = (score_series >= threshold).astype(int)

    trades = 0
    rets: List[float] = []

    i = 0
    while i < len(close) - hold_days:
        if signals.iloc[i] == 1:
            entry = close.iloc[i]
            exit_price = close.iloc[i + hold_days]
            ret = (exit_price / entry) - 1.0
            rets.append(ret)
            trades += 1
            i += hold_days  # 次のシグナルまでスキップ
        else:
            i += 1

    if trades == 0:
        return BacktestResult(symbol=symbol, trades=0, win_rate=0.0, cum_return=0.0, avg_trade_return=0.0)

    wins = sum(1 for r in rets if r > 0)
    cum_ret = 1.0
    for r in rets:
        cum_ret *= (1.0 + r)
    cum_ret -= 1.0

    return BacktestResult(
        symbol=symbol,
        trades=trades,
        win_rate=round(wins / trades * 100.0, 2),
        cum_return=round(cum_ret * 100.0, 2),
        avg_trade_return=round(statistics.mean(rets) * 100.0, 2),
    )


def compute_scores_for_symbols(symbols: List[str], period: str = "1y", threshold: float = 65.0, hold_days: int = 5) -> Tuple[pd.DataFrame, List[BacktestResult]]:
    rows = []
    bt_results: List[BacktestResult] = []

    for sym in symbols:
        data = fetch_price_history(sym, period=period)
        if data is None or len(data) < 60:
            continue
        # 時系列スコアを作るため、各日で計算（高速化のため軽量指標のみ）
        close = data["close"]
        volume = data["volume"]
        rsi_series = _calc_rsi(close, 14)
        macd, signal = _calc_macd(close)
        macd_hist = macd - signal
        high_252 = data["high"].rolling(252, min_periods=60).max()
        breakout_series = close >= (high_252 * 0.995)
        vol_z_series = _zscore(volume, 20).fillna(0)

        rsi_score = ((rsi_series - 50) * 2).clip(0, 100)
        macd_score = ((macd_hist / (close * 0.005)) * 50 + 50).clip(0, 100)
        breakout_score = breakout_series.astype(int) * 100
        volume_score = (vol_z_series * 15 + 50).clip(0, 100)

        composite_series = (
            rsi_score * 0.25 + macd_score * 0.25 + breakout_score * 0.30 + volume_score * 0.20
        )

        latest = compute_composite_score(sym, data)
        rows.append(
            {
                "symbol": sym,
                "score": latest.score,
                "price": latest.latest_price,
                "rsi": latest.components["rsi"],
                "macd": latest.components["macd"],
                "breakout": latest.components["breakout"],
                "volume": latest.components["volume"],
                "vol_z": round(latest.vol_zscore, 2),
                "is_breakout": latest.is_breakout,
            }
        )

        bt = simple_rule_backtest(sym, data, composite_series, threshold=threshold, hold_days=hold_days)
        bt_results.append(bt)

    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    return df, bt_results
