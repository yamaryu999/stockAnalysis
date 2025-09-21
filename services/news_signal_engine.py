"""News-driven signal engine to rank symbols based on recent economic news.

This module combines NewsAnalyzer output with lightweight fundamental metrics to
produce composite scores that can be surfaced in the UI.
"""

from __future__ import annotations

import math
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

try:
    from news_analyzer import NewsAnalyzer
except ImportError:  # pragma: no cover - fallback stub
    NewsAnalyzer = None  # type: ignore

try:
    from database_manager import DatabaseManager
except ImportError:  # pragma: no cover - fallback stub
    DatabaseManager = None  # type: ignore


class NewsSignalEngine:
    """Generate news-driven scores for Japanese stocks."""

    def __init__(
        self,
        news_analyzer: Optional[NewsAnalyzer] = None,
        database_manager: Optional[DatabaseManager] = None,
    ) -> None:
        self.news_analyzer = news_analyzer or (NewsAnalyzer() if NewsAnalyzer else None)
        self.database_manager = database_manager or (DatabaseManager() if DatabaseManager else None)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_news_signals(
        self,
        symbols: Optional[Iterable[str]] = None,
        lookback_days: int = 3,
        min_confidence: float = 0.15,
        auto_discover: bool = False,
        discover_top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """Return ranked news signals for the requested symbols.

        Parameters
        ----------
        symbols:
            List of ticker symbols such as ``['7203.T', '6758.T']``.
        lookback_days:
            How many days of news should be considered.
        min_confidence:
            Minimum sentiment confidence required to keep a signal. Lower values
            include low-volume results; higher values focus on strong coverage.
        """

        symbol_list: List[str] = []
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols if s]
        elif auto_discover:
            symbol_list = self.discover_trending_symbols(lookback_days=lookback_days, top_n=discover_top_n)

        if not symbol_list:
            return []

        news_map: Dict[str, Dict[str, Any]] = {}
        if self.news_analyzer:
            try:
                news_map = self.news_analyzer.analyze_market_news(symbol_list, days_back=lookback_days)
            except Exception:
                news_map = {}

        if not news_map:
            news_map = self._sample_news(symbol_list)

        ranked: List[Dict[str, Any]] = []
        now = time.time()

        for symbol in symbol_list:
            summary = news_map.get(symbol)
            if not summary:
                continue

            sentiment = summary.get('sentiment', {})
            sentiment_score = float(sentiment.get('score', 0.0))
            sentiment_conf = float(sentiment.get('confidence', 0.0))
            if sentiment_conf < min_confidence:
                # retain only if sentiment is extreme despite low confidence
                if abs(sentiment_score) < 0.35:
                    continue

            articles = summary.get('articles', []) or []
            news_intensity = self._compute_news_intensity(articles, now)
            news_momentum = self._compute_news_momentum(articles, now)
            fundamental_tilt = self._fundamental_tilt(symbol)

            composite_score = self._blend_scores(
                sentiment_score=sentiment_score,
                intensity=news_intensity,
                momentum=news_momentum,
                fundamental=fundamental_tilt,
            )

            ranked.append(
                {
                    'symbol': symbol,
                    'composite_score': round(composite_score, 2),
                    'news_sentiment': round(sentiment_score, 3),
                    'news_intensity': round(news_intensity, 3),
                    'news_momentum': round(news_momentum, 3),
                    'fundamental_tilt': round(fundamental_tilt, 3),
                    'confidence': round(sentiment_conf, 3),
                    'news_count': summary.get('news_count', 0),
                    'top_keywords': summary.get('keywords', {}).get('keywords', [])[:5],
                    'headlines': summary.get('top_headlines', [])[:5],
                    'event_tags': self._classify_events(articles),
                }
            )

        ranked.sort(key=lambda item: item['composite_score'], reverse=True)
        return ranked

    def discover_trending_symbols(self, *, top_n: int = 10, lookback_days: int = 3) -> List[str]:
        if not self.news_analyzer:
            return []
        try:
            return self.news_analyzer.discover_trending_symbols(
                days_back=lookback_days,
                top_n=top_n,
            )
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _sample_news(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Provide deterministic sample data when live news is unavailable."""
        now = time.time()
        articles = [
            {
                'title': '日本政府、次世代半導体支援を拡大',
                'summary': '経産省は国内メーカーへの補助金を追加決定。',
                'published': now - 3600,
                'source': 'Sample Source',
            },
            {
                'title': '主要自動車メーカー、EV投資を強化',
                'summary': '電動化戦略の見直しで設備投資を増額。',
                'published': now - 7200,
                'source': 'Sample Source',
            },
        ]
        sample = {}
        for idx, symbol in enumerate(symbols):
            score = 0.35 if idx % 2 == 0 else 0.1
            sample[symbol] = {
                'sentiment': {'score': score, 'confidence': 0.4, 'analyzed_count': 3},
                'keywords': {'keywords': ['成長', '投資', '戦略'], 'frequency': {'成長': 3}},
                'articles': articles,
                'top_headlines': [article['title'] for article in articles],
                'news_count': len(articles),
                'confidence': 0.4,
                'sources': ['Sample Source'],
            }
        return sample

    @staticmethod
    def _compute_news_intensity(articles: List[Dict[str, Any]], now: float) -> float:
        if not articles:
            return 0.0
        # number of fresh articles (within 48h)
        fresh = sum(1 for article in articles if now - float(article.get('published', 0) or 0) < 172800)
        return min(1.0, fresh / 5.0)

    @staticmethod
    def _compute_news_momentum(articles: List[Dict[str, Any]], now: float) -> float:
        if not articles:
            return 0.0
        decay_hours = 12.0
        scores = []
        for article in articles:
            published = float(article.get('published', 0) or 0)
            delta_hours = max(0.0, (now - published) / 3600.0)
            scores.append(math.exp(-delta_hours / decay_hours))
        return min(1.0, sum(scores) / max(len(scores), 1))

    def _fundamental_tilt(self, symbol: str) -> float:
        if not self.database_manager:
            return 0.0
        try:
            metrics = self.database_manager.get_financial_metrics(symbol)
        except Exception:
            metrics = None
        if not metrics:
            return 0.0

        tilt = 0.0
        roe = self._to_float(metrics.get('roe'))
        per = self._to_float(metrics.get('per'))
        dividend = self._to_float(metrics.get('dividend_yield'))
        debt = self._to_float(metrics.get('debt_ratio'))

        if roe is not None:
            tilt += min(roe / 15.0, 1.0) * 0.45
        if per is not None and per > 0:
            tilt += max(0.0, min((20.0 - per) / 20.0, 1.0)) * 0.3
        if dividend is not None:
            tilt += min(dividend / 3.0, 1.0) * 0.2
        if debt is not None and debt > 0:
            tilt -= min(debt / 200.0, 0.25)  # penalise high leverage slightly

        return max(-1.0, min(tilt, 1.0))

    @staticmethod
    def _blend_scores(
        *,
        sentiment_score: float,
        intensity: float,
        momentum: float,
        fundamental: float,
    ) -> float:
        # sentiment (-1..1) -> scale to 0..1
        sentiment_component = (sentiment_score + 1.0) / 2.0
        base = (
            sentiment_component * 0.45
            + intensity * 0.2
            + momentum * 0.2
            + (fundamental + 1.0) / 2.0 * 0.15
        )
        return max(0.0, min(base * 100.0, 100.0))

    @staticmethod
    def _classify_events(articles: List[Dict[str, Any]]) -> List[str]:
        if not articles:
            return []
        event_keywords = {
            '決算': ['決算', 'earnings', 'quarter', '増益', '減益'],
            'ガイダンス': ['上方修正', '下方修正', 'guidance', '見通し'],
            'M&A': ['買収', '合併', 'merger', 'acquisition'],
            '配当': ['配当', 'dividend', '還元'],
            '規制': ['規制', '承認', '認可', 'regulation', 'ban'],
            'マクロ': ['金利', 'インフレ', '為替', '景気', 'GDP', 'BOJ', 'Fed'],
        }
        tags: Dict[str, int] = {}
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            lower = text.lower()
            for tag, keywords in event_keywords.items():
                if any(keyword.lower() in lower for keyword in keywords):
                    tags[tag] = tags.get(tag, 0) + 1
        return sorted(tags, key=lambda key: tags[key], reverse=True)[:4]

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
