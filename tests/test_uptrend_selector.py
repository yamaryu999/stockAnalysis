import pandas as pd

from services.uptrend_selector import UptrendSelector


class DummyNewsEngine:
    def generate_news_signals(self, symbols=None, lookback_days=3, auto_discover=False, discover_top_n=10, **kwargs):
        return [
            {
                'symbol': symbol,
                'composite_score': 70 + idx * 5,
                'news_sentiment': 0.4,
                'fundamental_tilt': 0.2,
                'confidence': 0.8,
                'news_count': 3,
                'headlines': ['テストヘッドライン'],
                'event_tags': ['決算'],
                'top_keywords': ['成長'],
            }
            for idx, symbol in enumerate(symbols or ['7203.T', '6758.T'])
        ]

    def discover_trending_symbols(self, *, top_n=10, lookback_days=3):
        return ['7203.T', '6758.T'][:top_n]


def dummy_price_fetcher(symbol, period='2mo'):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30, freq='B')
    base = 100 + hash(symbol) % 20
    close = pd.Series(range(len(dates)), index=dates) * 0.5 + base
    data = pd.DataFrame({'Close': close})
    return data


def test_uptrend_selector_rank_from_signals():
    engine = UptrendSelector(DummyNewsEngine(), price_fetcher=dummy_price_fetcher)
    candidates = engine.select_candidates(['7203.T', '6758.T'], top_n=2)

    assert len(candidates) == 2
    assert candidates[0]['final_score'] >= candidates[1]['final_score']
    assert 'price_change_pct' in candidates[0]
    assert 'headlines' in candidates[0]


def test_uptrend_selector_handles_empty_signals():
    engine = UptrendSelector(DummyNewsEngine(), price_fetcher=dummy_price_fetcher)
    ranked = engine.rank_from_signals([], top_n=3)
    assert ranked == []


def test_uptrend_selector_auto_discover():
    engine = UptrendSelector(DummyNewsEngine(), price_fetcher=dummy_price_fetcher)
    candidates = engine.select_candidates(None, top_n=2)
    assert len(candidates) == 2
