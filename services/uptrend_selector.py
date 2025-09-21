"""Combine news-driven signals with price momentum to surface uptrend candidates."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional

import pandas as pd

try:  # pragma: no cover - optional dependency
    import yfinance as yf
except ImportError:  # pragma: no cover - fallback stub
    yf = None


@dataclass
class PriceMetrics:
    symbol: str
    price_change_pct: float
    momentum_score: float
    trend_bias: float
    summary: Dict[str, Any]


class UptrendSelector:
    """Rank stocks likely to rise by blending news, fundamentals, and price action."""

    def __init__(
        self,
        news_signal_engine: Any,
        *,
        price_fetcher: Optional[Callable[[str, str], pd.DataFrame]] = None,
    ) -> None:
        self.news_signal_engine = news_signal_engine
        self.price_fetcher = price_fetcher or self._default_price_fetcher

    # ------------------------------------------------------------------
    # Public APIs
    # ------------------------------------------------------------------
    def select_candidates(
        self,
        symbols: Optional[Iterable[str]] = None,
        *,
        lookback_days: int = 3,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Generate news signals then rank candidates."""
        if not self.news_signal_engine:
            return []

        symbols_iter = symbols
        auto_discover = symbols_iter is None

        signals = self.news_signal_engine.generate_news_signals(  # type: ignore[attr-defined]
            symbols_iter,
            lookback_days=lookback_days,
            auto_discover=auto_discover,
            discover_top_n=max(top_n * 2, 10),
        )
        return self.rank_from_signals(signals, top_n=top_n)

    def rank_from_signals(
        self,
        signals: Iterable[Dict[str, Any]],
        *,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Combine existing news signals with price metrics and rank."""
        ranked: List[Dict[str, Any]] = []

        for signal in signals or []:
            symbol = signal.get('symbol')
            if not symbol:
                continue

            price_metrics = self._compute_price_metrics(symbol)
            if price_metrics is None:
                continue

            composite = self._blend_scores(
                news_score=float(signal.get('composite_score', 0.0)),
                momentum=price_metrics.momentum_score,
                trend=price_metrics.trend_bias,
                fundamental=float(signal.get('fundamental_tilt', 0.0)),
            )

            profile = {
                'symbol': symbol,
                'final_score': round(composite, 2),
                'news_score': round(float(signal.get('composite_score', 0.0)), 2),
                'momentum_score': round(price_metrics.momentum_score, 2),
                'trend_bias': round(price_metrics.trend_bias, 2),
                'price_change_pct': round(price_metrics.price_change_pct, 2),
                'news_sentiment': round(float(signal.get('news_sentiment', 0.0)), 3),
                'fundamental_tilt': round(float(signal.get('fundamental_tilt', 0.0)), 3),
                'confidence': float(signal.get('confidence', 0.0)),
                'news_count': int(signal.get('news_count', 0)),
                'headlines': signal.get('headlines', [])[:3],
                'event_tags': signal.get('event_tags', [])[:4],
                'top_keywords': signal.get('top_keywords', [])[:5],
            }
            profile.update(price_metrics.summary)
            ranked.append(profile)

        ranked.sort(key=lambda item: item['final_score'], reverse=True)
        return ranked[:top_n]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _compute_price_metrics(self, symbol: str) -> Optional[PriceMetrics]:
        try:
            df = self.price_fetcher(symbol, '2mo')
        except Exception:  # pragma: no cover - external dependency failures
            return None
        if df is None or df.empty:
            return None

        closes = df['Close'].dropna()
        if len(closes) < 6:
            return None

        last_close = float(closes.iloc[-1])
        prior_close = float(closes.iloc[-6])
        pct_change = ((last_close / prior_close) - 1.0) * 100.0

        recent_returns = closes.pct_change().tail(5)
        avg_daily = float(recent_returns.mean(skipna=True) or 0.0) * 100.0

        ma_window = closes.rolling(20).mean().iloc[-1] if len(closes) >= 20 else closes.mean()
        ma_ratio = (last_close / float(ma_window) - 1.0) * 100.0 if ma_window else 0.0

        momentum_score = self._normalize_percentage(pct_change)
        trend_bias = self._normalize_percentage(ma_ratio, center=0.5)

        summary = {
            'last_close': round(last_close, 2),
            'avg_daily_change_pct': round(avg_daily, 2),
            'ma_trend_pct': round(ma_ratio, 2),
        }

        return PriceMetrics(
            symbol=symbol,
            price_change_pct=pct_change,
            momentum_score=momentum_score,
            trend_bias=trend_bias,
            summary=summary,
        )

    @staticmethod
    def _normalize_percentage(value: float, *, center: float = 0.0) -> float:
        base = value - center
        scaled = (base + 5.0) / 15.0  # -5% -> 0, +10% -> 1
        return max(0.0, min(scaled * 100.0, 100.0))

    @staticmethod
    def _blend_scores(*, news_score: float, momentum: float, trend: float, fundamental: float) -> float:
        news_component = max(0.0, min(news_score, 100.0))
        fundamental_component = (fundamental + 1.0) / 2.0 * 100.0
        composite = (
            news_component * 0.55
            + momentum * 0.25
            + trend * 0.15
            + fundamental_component * 0.05
        )
        return max(0.0, min(composite, 100.0))

    @staticmethod
    def _default_price_fetcher(symbol: str, period: str = '2mo') -> pd.DataFrame:
        if yf is None:
            raise RuntimeError('yfinance is not available')
        return yf.Ticker(symbol).history(period=period)
