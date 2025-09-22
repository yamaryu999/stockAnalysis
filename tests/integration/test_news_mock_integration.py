"""Integration tests for NewsAnalyzer with mock server.

Skips when NEWS_MOCK_URL is not provided.
"""

from __future__ import annotations

import os
import pytest

from news_analyzer import NewsAnalyzer


pytestmark = pytest.mark.integration


@pytest.fixture()
def ensure_mock_url() -> str:
    url = os.getenv("NEWS_MOCK_URL")
    if not url:
        pytest.skip("NEWS_MOCK_URL not set; skipping integration test")
    return url


def test_analyze_market_news_with_mock(ensure_mock_url):
    analyzer = NewsAnalyzer()
    symbols = ["7203.T"]
    result = analyzer.analyze_market_news(symbols, days_back=3)
    assert "7203.T" in result
    info = result["7203.T"]
    assert info.get("news_count", 0) > 0
    # Articles should come from mock
    assert any(a.get("source") == "Mock News" for a in info.get("articles", []))


def test_get_sector_news_with_mock(ensure_mock_url):
    analyzer = NewsAnalyzer()
    data = analyzer.get_sector_news("technology", days_back=3)
    assert data.get("sector") == "technology"
    assert data.get("news_count", 0) > 0
    assert "sentiment" in data and "keywords" in data


def test_get_economic_indicators_with_mock(ensure_mock_url):
    analyzer = NewsAnalyzer()
    indicators = analyzer.get_economic_indicators()
    assert "nikkei_sentiment" in indicators
    assert "fx_sentiment" in indicators
    assert "interest_sentiment" in indicators

