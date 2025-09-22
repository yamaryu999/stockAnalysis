"""
ニュース分析機能
複数のニュースソースから情報を収集し、センチメント分析を行う
"""

import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import time
import json
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
import warnings
warnings.filterwarnings('ignore')

class NewsAnalyzer:
    """ニュース分析を行うクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache = {}
        self.cache_duration = 3600  # 1時間
        self._company_cache: Dict[str, Optional[str]] = {}
        
        # センチメント分析用の辞書
        self.positive_words = {
            '上昇', '成長', '好調', '改善', '増加', '利益', '成功', '強気', '買い', '推奨',
            'up', 'rise', 'growth', 'profit', 'gain', 'positive', 'bullish', 'buy'
        }
        
        self.negative_words = {
            '下落', '減少', '悪化', '損失', '弱気', '懸念', 'リスク', '問題', '売り', '警戒',
            'down', 'fall', 'loss', 'negative', 'bearish', 'sell', 'risk', 'concern'
        }
    
    def analyze_market_news(self, symbols: List[str], days_back: int = 7) -> Dict:
        """市場ニュースの分析"""
        try:
            results = {}
            
            for symbol in symbols:
                # ニュースデータを取得
                news_data = self._fetch_comprehensive_news(symbol, days_back)
                
                if news_data:
                    # 新しい順にソート
                    sorted_news = sorted(
                        news_data,
                        key=lambda item: item.get('published', 0) or 0,
                        reverse=True
                    )
                    top_headlines = [item.get('title', '') for item in sorted_news[:5]]
                    
                    # センチメント分析
                    sentiment_analysis = self._analyze_sentiment(sorted_news)
                    
                    # キーワード分析
                    keyword_analysis = self._analyze_keywords(sorted_news)
                    
                    # セクター分析
                    sector_analysis = self._analyze_sector_impact(symbol, sorted_news)
                    
                    # 信頼度評価
                    confidence = self._calculate_news_confidence(sorted_news)
                    
                    results[symbol] = {
                        'sentiment': sentiment_analysis,
                        'keywords': keyword_analysis,
                        'sector_impact': sector_analysis,
                        'confidence': confidence,
                        'news_count': len(sorted_news),
                        'sources': list({item.get('source') for item in sorted_news if item.get('source')}),
                        'articles': sorted_news,
                        'top_headlines': top_headlines,
                        'latest_timestamp': sorted_news[0].get('published') if sorted_news else None
                    }
            
            return results
            
        except Exception as e:
            print(f"市場ニュース分析エラー: {e}")
            return {}
    
    def get_sector_news(self, sector: str, days_back: int = 7) -> Dict:
        """セクター別ニュース取得"""
        try:
            # モックサーバーが指定されている場合は優先
            mock_base = os.getenv('NEWS_MOCK_URL')
            if mock_base:
                try:
                    resp = self.session.get(
                        mock_base.rstrip('/') + '/sector',
                        params={'sector': sector, 'days_back': days_back},
                        timeout=5,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    if isinstance(data, dict) and 'news_count' in data:
                        return data
                except Exception:
                    pass

            # セクターキーワードマッピング（実データ）
            sector_keywords = {
                'technology': ['テクノロジー', 'IT', 'ソフトウェア', 'ハードウェア', 'AI', '人工知能', 'technology', 'software'],
                'finance': ['金融', '銀行', '保険', '証券', '投資', 'finance', 'banking', 'investment'],
                'healthcare': ['医療', '製薬', 'バイオ', 'ヘルスケア', 'healthcare', 'pharmaceutical', 'medical'],
                'automotive': ['自動車', '車', 'トヨタ', 'ホンダ', '日産', 'automotive', 'car', 'vehicle'],
                'energy': ['エネルギー', '石油', 'ガス', '電力', '再生可能', 'energy', 'oil', 'gas', 'power']
            }
            
            keywords = sector_keywords.get(sector.lower(), [sector])
            news_data = self._fetch_sector_news(keywords, days_back)
            
            if news_data:
                sentiment = self._analyze_sentiment(news_data)
                keywords_analysis = self._analyze_keywords(news_data)
                
                return {
                    'sector': sector,
                    'sentiment': sentiment,
                    'keywords': keywords_analysis,
                    'news_count': len(news_data),
                    'confidence': self._calculate_news_confidence(news_data)
                }
            
            return {}
            
        except Exception as e:
            print(f"セクターニュース取得エラー: {e}")
            return {}
    
    def get_economic_indicators(self) -> Dict:
        """経済指標の取得と分析"""
        try:
            # モックサーバーが指定されている場合は優先
            mock_base = os.getenv('NEWS_MOCK_URL')
            if mock_base:
                try:
                    resp = self.session.get(
                        mock_base.rstrip('/') + '/indicators',
                        timeout=5,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    if isinstance(data, dict) and data:
                        return data
                except Exception:
                    pass

            indicators = {}
            
            # 日経平均関連ニュース
            nikkei_news = self._fetch_nikkei_news()
            if nikkei_news:
                indicators['nikkei_sentiment'] = self._analyze_sentiment(nikkei_news)
                indicators['nikkei_keywords'] = self._analyze_keywords(nikkei_news)
            
            # 為替関連ニュース
            fx_news = self._fetch_fx_news()
            if fx_news:
                indicators['fx_sentiment'] = self._analyze_sentiment(fx_news)
                indicators['fx_keywords'] = self._analyze_keywords(fx_news)
            
            # 金利関連ニュース
            interest_news = self._fetch_interest_rate_news()
            if interest_news:
                indicators['interest_sentiment'] = self._analyze_sentiment(interest_news)
                indicators['interest_keywords'] = self._analyze_keywords(interest_news)
            
            return indicators
            
        except Exception as e:
            print(f"経済指標取得エラー: {e}")
            return {}

    def discover_trending_symbols(
        self,
        candidates: Optional[List[str]] = None,
        *,
        days_back: int = 3,
        top_n: int = 10,
    ) -> List[str]:
        """ニュース件数とセンチメントから注目銘柄を抽出"""
        try:
            if candidates is None:
                try:
                    from stock_analyzer import JapaneseStockAnalyzer  # noqa: WPS433

                    analyzer = JapaneseStockAnalyzer()
                    candidates = analyzer.get_high_priority_stocks()
                except Exception:
                    candidates = []

            trending = []
            for symbol in candidates[:50]:
                news_items = self._fetch_comprehensive_news(symbol, days_back)
                if not news_items:
                    continue
                sentiment = self._analyze_sentiment(news_items)
                trending.append(
                    {
                        'symbol': symbol,
                        'news_count': len(news_items),
                        'sentiment_score': float(sentiment.get('score', 0.0)),
                    }
                )

            trending.sort(
                key=lambda item: (item['news_count'], item['sentiment_score']),
                reverse=True,
            )
            if trending:
                return [item['symbol'] for item in trending[:top_n]]

            if candidates:
                return candidates[:top_n]

            return ['7203.T', '6758.T', '9984.T'][:top_n]

        except Exception as e:
            print(f"トレンド銘柄抽出エラー: {e}")
            return []
    
    def _fetch_comprehensive_news(self, symbol: str, days_back: int) -> List[Dict]:
        """包括的なニュース取得"""
        try:
            # モックサーバーが指定されている場合は優先
            mock_base = os.getenv('NEWS_MOCK_URL')
            if mock_base:
                try:
                    resp = self.session.get(
                        mock_base.rstrip('/') + '/news',
                        params={'symbol': symbol, 'days_back': days_back},
                        timeout=5,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    if isinstance(data, list):
                        return data
                except Exception:
                    # フォールバックして実データへ
                    pass
            # キャッシュをチェック
            cache_key = f"{symbol}_{days_back}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_duration:
                    return cached_data
            
            news_data = []
            
            # Yahoo Finance ニュース
            yahoo_news = self._fetch_yahoo_news(symbol)
            news_data.extend(yahoo_news)
            
            # Google ニュース
            google_news = self._fetch_google_news(symbol)
            news_data.extend(google_news)
            
            # 日本経済新聞
            nikkei_news = self._fetch_nikkei_company_news(symbol)
            news_data.extend(nikkei_news)
            
            # 重複を除去
            unique_news = self._remove_duplicates(news_data)
            
            # キャッシュに保存
            self.cache[cache_key] = (unique_news, time.time())
            
            return unique_news
            
        except Exception as e:
            print(f"包括的ニュース取得エラー: {e}")
            return []
    
    def _fetch_yahoo_news(self, symbol: str) -> List[Dict]:
        """Yahoo Finance ニュース取得"""
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            news = ticker.news or []

            news_data: List[Dict] = []
            for article in news[:15]:  # 最新15件
                content = article.get('content') if isinstance(article, dict) else None

                title = None
                summary = ''
                url = ''
                provider = 'Yahoo'
                published_raw = None

                if isinstance(content, dict):
                    title = content.get('title') or article.get('title')
                    summary = content.get('summary') or content.get('description') or ''
                    canonical = content.get('canonicalUrl') or {}
                    if isinstance(canonical, dict):
                        url = canonical.get('url', '')
                    if not url:
                        click_through = content.get('clickThroughUrl') or {}
                        if isinstance(click_through, dict):
                            url = click_through.get('url', '')
                    provider_info = content.get('provider') or {}
                    if isinstance(provider_info, dict):
                        provider = provider_info.get('displayName', provider)
                    published_raw = content.get('pubDate') or content.get('displayTime')
                else:
                    title = article.get('title')
                    summary = article.get('summary') or ''
                    url = article.get('link', '')
                    provider = article.get('provider', 'Yahoo')
                    published_raw = article.get('providerPublishTime')

                if not title:
                    continue

                if not url:
                    url = article.get('link', '') if isinstance(article, dict) else ''

                if isinstance(published_raw, (int, float)):
                    published_ts = int(published_raw)
                else:
                    published_dt = pd.to_datetime(published_raw, utc=True, errors='coerce')
                    if pd.isna(published_dt):
                        published_ts = int(time.time())
                    else:
                        published_ts = int(published_dt.timestamp())

                news_data.append({
                    'title': title,
                    'summary': summary,
                    'published': published_ts,
                    'source': 'Yahoo Finance',
                    'url': url,
                    'provider': provider,
                })

            return news_data

        except Exception as e:
            print(f"Yahoo Finance ニュース取得エラー: {e}")
            return []
    
    def _fetch_google_news(self, symbol: str) -> List[Dict]:
        """Google ニュース取得 (RSSベース)"""
        try:
            query = f"{symbol} 株価 ニュース"
            rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=ja&gl=JP&ceid=JP:ja"

            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            channel = root.find('channel')
            if channel is None:
                return []

            news_data: List[Dict] = []
            for item in channel.findall('item')[:10]:  # 最新10件
                title = item.findtext('title') or ''
                link = item.findtext('link') or ''
                description = item.findtext('description') or ''
                pub_date = item.findtext('pubDate')

                if not title:
                    continue

                published_dt = pd.to_datetime(pub_date, utc=True, errors='coerce')
                published_ts = int(published_dt.timestamp()) if not pd.isna(published_dt) else int(time.time())

                news_data.append({
                    'title': title,
                    'summary': BeautifulSoup(description, 'html.parser').get_text().strip(),
                    'published': published_ts,
                    'source': 'Google News',
                    'url': link,
                    'provider': 'Google',
                })

            return news_data

        except Exception as e:
            print(f"Google ニュース取得エラー: {e}")
            return []
    
    def _fetch_nikkei_company_news(self, symbol: str) -> List[Dict]:
        """日本経済新聞 企業ニュース取得"""
        try:
            # 企業名を取得（簡易版）
            company_name = self._get_company_name(symbol)
            if not company_name:
                return []
            
            # Nikkei 検索
            query = f"{company_name} 株価"
            url = f"https://www.nikkei.com/search?keyword={query}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', class_='m-miM09_title')[:5]  # 最新5件
            
            news_data = []
            for article in articles:
                title = article.get_text().strip()
                url = article.get('href', '')
                
                if title and url:
                    news_data.append({
                        'title': title,
                        'summary': '',
                        'published': int(time.time()),
                        'source': '日本経済新聞',
                        'url': urljoin('https://www.nikkei.com', url),
                        'provider': 'Nikkei'
                    })
            
            return news_data
            
        except Exception as e:
            print(f"日本経済新聞取得エラー: {e}")
            return []
    
    def _fetch_sector_news(self, keywords: List[str], days_back: int) -> List[Dict]:
        """セクター別ニュース取得"""
        try:
            news_data = []
            
            for keyword in keywords[:3]:  # 上位3キーワード
                # Google ニュース検索
                query = f"{keyword} 株価 ニュース"
                url = f"https://news.google.com/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('article')[:5]  # 各キーワード5件
                
                for article in articles:
                    title_elem = article.find('h3')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        link_elem = title_elem.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        news_data.append({
                            'title': title,
                            'summary': '',
                            'published': int(time.time()),
                            'source': 'Google News',
                            'url': url,
                            'provider': 'Google',
                            'keyword': keyword
                        })
            
            return news_data
            
        except Exception as e:
            print(f"セクターニュース取得エラー: {e}")
            return []
    
    def _fetch_nikkei_news(self) -> List[Dict]:
        """日経平均関連ニュース取得"""
        try:
            url = "https://www.nikkei.com/markets/kabu/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', class_='m-miM09_title')[:10]
            
            news_data = []
            for article in articles:
                title = article.get_text().strip()
                url = article.get('href', '')
                
                if title and url:
                    news_data.append({
                        'title': title,
                        'summary': '',
                        'published': int(time.time()),
                        'source': '日本経済新聞',
                        'url': urljoin('https://www.nikkei.com', url),
                        'provider': 'Nikkei'
                    })
            
            return news_data
            
        except Exception as e:
            print(f"日経ニュース取得エラー: {e}")
            return []
    
    def _fetch_fx_news(self) -> List[Dict]:
        """為替関連ニュース取得"""
        try:
            url = "https://www.nikkei.com/markets/forex/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('a', class_='m-miM09_title')[:10]
            
            news_data = []
            for article in articles:
                title = article.get_text().strip()
                url = article.get('href', '')
                
                if title and url:
                    news_data.append({
                        'title': title,
                        'summary': '',
                        'published': int(time.time()),
                        'source': '日本経済新聞',
                        'url': urljoin('https://www.nikkei.com', url),
                        'provider': 'Nikkei'
                    })
            
            return news_data
            
        except Exception as e:
            print(f"為替ニュース取得エラー: {e}")
            return []
    
    def _fetch_interest_rate_news(self) -> List[Dict]:
        """金利関連ニュース取得"""
        try:
            query = "金利 日銀 政策金利"
            url = f"https://news.google.com/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article')[:10]
            
            news_data = []
            for article in articles:
                title_elem = article.find('h3')
                if title_elem:
                    title = title_elem.get_text().strip()
                    link_elem = title_elem.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    
                    news_data.append({
                        'title': title,
                        'summary': '',
                        'published': int(time.time()),
                        'source': 'Google News',
                        'url': url,
                        'provider': 'Google'
                    })
            
            return news_data
            
        except Exception as e:
            print(f"金利ニュース取得エラー: {e}")
            return []
    
    def _analyze_sentiment(self, news_data: List[Dict]) -> Dict:
        """センチメント分析"""
        try:
            if not news_data:
                return {'score': 0.0, 'sentiment': 'neutral', 'confidence': 0.0}
            
            total_score = 0
            analyzed_count = 0
            
            for item in news_data:
                text = (item['title'] + ' ' + item['summary']).lower()
                
                positive_count = sum(1 for word in self.positive_words if word in text)
                negative_count = sum(1 for word in self.negative_words if word in text)
                
                if positive_count + negative_count > 0:
                    score = (positive_count - negative_count) / (positive_count + negative_count)
                    total_score += score
                    analyzed_count += 1
            
            if analyzed_count == 0:
                return {'score': 0.0, 'sentiment': 'neutral', 'confidence': 0.0}
            
            avg_score = total_score / analyzed_count
            
            # センチメント判定
            if avg_score > 0.2:
                sentiment = 'positive'
            elif avg_score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # 信頼度計算
            confidence = min(analyzed_count / 10, 1.0)  # 10件で最大信頼度
            
            return {
                'score': avg_score,
                'sentiment': sentiment,
                'confidence': confidence,
                'analyzed_count': analyzed_count
            }
            
        except Exception as e:
            print(f"センチメント分析エラー: {e}")
            return {'score': 0.0, 'sentiment': 'neutral', 'confidence': 0.0}
    
    def _analyze_keywords(self, news_data: List[Dict]) -> Dict:
        """キーワード分析"""
        try:
            if not news_data:
                return {'keywords': [], 'frequency': {}}
            
            # テキストを結合
            texts = [item['title'] + ' ' + item['summary'] for item in news_data]
            combined_text = ' '.join(texts)
            
            # キーワード抽出
            words = re.findall(r'\b\w+\b', combined_text.lower())
            
            # ストップワードを除外
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
                'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
                'a', 'an', 'の', 'に', 'を', 'は', 'が', 'で', 'と', 'も', 'から', 'まで'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # 頻度計算
            word_freq = pd.Series(filtered_words).value_counts()
            top_keywords = word_freq.head(10)
            
            return {
                'keywords': top_keywords.index.tolist(),
                'frequency': top_keywords.to_dict()
            }
            
        except Exception as e:
            print(f"キーワード分析エラー: {e}")
            return {'keywords': [], 'frequency': {}}
    
    def _analyze_sector_impact(self, symbol: str, news_data: List[Dict]) -> Dict:
        """セクター影響分析"""
        try:
            # セクターキーワード
            sector_keywords = {
                'technology': ['テクノロジー', 'IT', 'ソフトウェア', 'ハードウェア', 'AI', '人工知能', 'technology', 'software'],
                'finance': ['金融', '銀行', '保険', '証券', '投資', 'finance', 'banking', 'investment'],
                'healthcare': ['医療', '製薬', 'バイオ', 'ヘルスケア', 'healthcare', 'pharmaceutical', 'medical'],
                'automotive': ['自動車', '車', 'トヨタ', 'ホンダ', '日産', 'automotive', 'car', 'vehicle'],
                'energy': ['エネルギー', '石油', 'ガス', '電力', '再生可能', 'energy', 'oil', 'gas', 'power'],
                'retail': ['小売', '流通', 'EC', 'オンライン', 'retail', 'commerce', 'online'],
                'manufacturing': ['製造', '工場', '生産', 'manufacturing', 'production', 'factory']
            }
            
            sector_mentions = {}
            
            for sector, keywords in sector_keywords.items():
                mentions = 0
                for item in news_data:
                    text = (item['title'] + ' ' + item['summary']).lower()
                    mentions += sum(1 for keyword in keywords if keyword in text)
                
                sector_mentions[sector] = mentions
            
            # 最も言及されたセクター
            top_sector = max(sector_mentions.items(), key=lambda x: x[1])[0] if sector_mentions else None
            
            return {
                'sector_mentions': sector_mentions,
                'top_sector': top_sector,
                'total_mentions': sum(sector_mentions.values())
            }
            
        except Exception as e:
            print(f"セクター影響分析エラー: {e}")
            return {}
    
    def _calculate_news_confidence(self, news_data: List[Dict]) -> float:
        """ニュース信頼度計算"""
        try:
            if not news_data:
                return 0.0
            
            confidence = 0.0
            
            # ニュース数に基づく信頼度
            news_count = len(news_data)
            confidence += min(news_count / 20, 0.4)  # 20件で最大0.4
            
            # ソースの多様性
            sources = set([item['source'] for item in news_data])
            confidence += min(len(sources) / 5, 0.3)  # 5ソースで最大0.3
            
            # プロバイダーの信頼性
            trusted_providers = {'Yahoo Finance', '日本経済新聞', 'Nikkei', 'Google News'}
            trusted_count = sum(1 for item in news_data if item.get('provider', '') in trusted_providers)
            confidence += min(trusted_count / len(news_data), 0.3)  # 信頼できるプロバイダーで最大0.3
            
            return min(confidence, 1.0)
            
        except Exception as e:
            print(f"ニュース信頼度計算エラー: {e}")
            return 0.0
    
    def _remove_duplicates(self, news_data: List[Dict]) -> List[Dict]:
        """重複ニュースの除去"""
        try:
            seen_titles = set()
            unique_news = []
            
            for item in news_data:
                title = item['title'].strip()
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(item)
            
            return unique_news
            
        except Exception as e:
            print(f"重複除去エラー: {e}")
            return news_data

    def get_company_name(self, symbol: str) -> Optional[str]:
        """外部公開用の企業名取得"""
        if symbol in self._company_cache:
            return self._company_cache[symbol]

        name = self._get_company_name(symbol)
        if not name:
            try:
                import yfinance as yf

                info = yf.Ticker(symbol).info
                name = info.get('shortName') or info.get('longName')
            except Exception:
                name = None

        self._company_cache[symbol] = name
        return name

    def _get_company_name(self, symbol: str) -> Optional[str]:
        """銘柄コードから企業名を取得"""
        try:
            # 主要企業のマッピング
            company_mapping = {
                '7203.T': 'トヨタ自動車',
                '6758.T': 'ソニー',
                '9984.T': 'ソフトバンクグループ',
                '9434.T': 'ソフトバンク',
                '6861.T': 'キーエンス',
                '4063.T': '信越化学工業',
                '8306.T': '三菱UFJフィナンシャル・グループ',
                '8316.T': '三井住友フィナンシャルグループ',
                '8035.T': '東京エレクトロン',
                '6954.T': 'ファナック'
            }
            
            return company_mapping.get(symbol)
            
        except Exception as e:
            print(f"企業名取得エラー: {e}")
            return None
