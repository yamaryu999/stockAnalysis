import time

from services.news_signal_engine import NewsSignalEngine


class DummyNewsAnalyzer:
    def analyze_market_news(self, symbols, days_back=7):
        now = time.time()
        results = {}
        for sym in symbols:
            articles = [
                {
                    'title': '決算発表で増益を達成',
                    'summary': 'ガイダンスも上方修正され市場期待が高まる。',
                    'published': now - 3600,
                    'source': 'DummyWire',
                },
                {
                    'title': '業界全体で投資拡大',
                    'summary': 'EV関連投資が強化される見通し。',
                    'published': now - 7200,
                    'source': 'DummyWire',
                },
            ]
            results[sym] = {
                'sentiment': {'score': 0.4, 'confidence': 0.6, 'analyzed_count': 2},
                'keywords': {'keywords': ['増益', '投資'], 'frequency': {'増益': 2}},
                'articles': articles,
                'top_headlines': [article['title'] for article in articles],
                'news_count': len(articles),
                'confidence': 0.6,
                'sources': ['DummyWire'],
            }
        return results

    def discover_trending_symbols(self, days_back=3, top_n=10):
        return ['7203.T', '6758.T'][:top_n]


class DummyDatabase:
    def get_financial_metrics(self, symbol):
        return {
            'roe': 12.0,
            'per': 14.5,
            'dividend_yield': 2.1,
            'debt_ratio': 80.0,
        }


def test_news_signal_engine_generates_ranked_signals():
    engine = NewsSignalEngine(news_analyzer=DummyNewsAnalyzer(), database_manager=DummyDatabase())
    signals = engine.generate_news_signals(['7203.T', '6758.T'], lookback_days=1)

    assert len(signals) == 2
    assert signals[0]['composite_score'] >= signals[1]['composite_score']
    assert 'event_tags' in signals[0]
    assert signals[0]['news_sentiment'] == 0.4


def test_news_signal_engine_auto_discover():
    engine = NewsSignalEngine(news_analyzer=DummyNewsAnalyzer(), database_manager=DummyDatabase())
    signals = engine.generate_news_signals(None, lookback_days=1, auto_discover=True, discover_top_n=2)

    assert len(signals) == 2
