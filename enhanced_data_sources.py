"""
Enhanced Multi-Data Source Management System
複数のデータソースを統合し、信頼性と可用性を向上させるシステム
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import aiohttp
from cache_manager import cache_manager
from error_handler import handle_errors, retry_on_error

@dataclass
class DataSourceConfig:
    """データソース設定"""
    name: str
    api_key: Optional[str] = None
    rate_limit: int = 1000
    timeout: int = 30
    max_retries: int = 3
    priority: int = 1
    enabled: bool = True

@dataclass
class StockData:
    """株価データクラス"""
    symbol: str
    data: pd.DataFrame
    source: str
    timestamp: datetime
    confidence: float
    metadata: Dict[str, Any]

class DataSource(ABC):
    """データソースの抽象基底クラス"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StockAnalysisTool/1.0'
        })
        self.last_request_time = 0
        self.request_count = 0
    
    @abstractmethod
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[StockData]:
        """株価データを取得"""
        pass
    
    @abstractmethod
    def get_financial_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """財務指標を取得"""
        pass
    
    @abstractmethod
    def get_news_data(self, symbol: str, days_back: int = 7) -> Optional[List[Dict]]:
        """ニュースデータを取得"""
        pass
    
    def _rate_limit_check(self):
        """レート制限チェック"""
        current_time = time.time()
        if current_time - self.last_request_time < (60 / self.config.rate_limit):
            time.sleep((60 / self.config.rate_limit) - (current_time - self.last_request_time))
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """データの妥当性をチェック"""
        if data is None or data.empty:
            return False
        
        # 必要な列が存在するかチェック
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        # データの範囲チェック
        if data['Close'].isna().sum() > len(data) * 0.5:
            return False
        
        return True
    
    def _calculate_confidence(self, data: pd.DataFrame) -> float:
        """データの信頼度を計算"""
        if not self._validate_data(data):
            return 0.0
        
        confidence = 1.0
        
        # 欠損値の割合に基づく信頼度調整
        missing_ratio = data.isna().sum().sum() / (len(data) * len(data.columns))
        confidence *= (1 - missing_ratio)
        
        # データの新しさに基づく信頼度調整
        if not data.empty:
            last_date = data.index[-1]
            days_old = (datetime.now() - last_date).days
            if days_old > 7:
                confidence *= max(0.5, 1 - (days_old - 7) * 0.1)
        
        return max(0.0, min(1.0, confidence))

class YahooFinanceSource(DataSource):
    """Yahoo Finance データソース"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.name = "Yahoo Finance"
    
    @retry_on_error(max_retries=3)
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[StockData]:
        """Yahoo Financeから株価データを取得"""
        try:
            self._rate_limit_check()
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if not self._validate_data(data):
                return None
            
            confidence = self._calculate_confidence(data)
            
            return StockData(
                symbol=symbol,
                data=data,
                source=self.name,
                timestamp=datetime.now(),
                confidence=confidence,
                metadata={
                    'period': period,
                    'data_points': len(data),
                    'currency': 'JPY'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Yahoo Finance データ取得エラー {symbol}: {e}")
            return None
    
    def get_financial_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """財務指標を取得"""
        try:
            self._rate_limit_check()
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            metrics = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'roe': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio')
            }
            
            return {k: v for k, v in metrics.items() if v is not None}
            
        except Exception as e:
            self.logger.error(f"財務指標取得エラー {symbol}: {e}")
            return None
    
    def get_news_data(self, symbol: str, days_back: int = 7) -> Optional[List[Dict]]:
        """ニュースデータを取得"""
        try:
            self._rate_limit_check()
            
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return []
            
            # 日付フィルタリング
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filtered_news = []
            
            for item in news:
                try:
                    pub_date = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                    if pub_date >= cutoff_date:
                        filtered_news.append({
                            'title': item.get('title', ''),
                            'summary': item.get('summary', ''),
                            'url': item.get('link', ''),
                            'source': item.get('publisher', ''),
                            'published_at': pub_date,
                            'sentiment': item.get('sentiment', 'neutral')
                        })
                except:
                    continue
            
            return filtered_news
            
        except Exception as e:
            self.logger.error(f"ニュース取得エラー {symbol}: {e}")
            return []

class AlphaVantageSource(DataSource):
    """Alpha Vantage データソース"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.name = "Alpha Vantage"
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[StockData]:
        """Alpha Vantageから株価データを取得"""
        if not self.config.api_key:
            self.logger.warning("Alpha Vantage APIキーが設定されていません")
            return None
        
        try:
            self._rate_limit_check()
            
            # 期間に応じた出力サイズを設定
            outputsize = "full" if period in ["2y", "5y", "max"] else "compact"
            
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.config.api_key,
                'outputsize': outputsize
            }
            
            response = self.session.get(self.base_url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data:
                self.logger.error(f"Alpha Vantage エラー: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                self.logger.warning(f"Alpha Vantage レート制限: {data['Note']}")
                return None
            
            # データをDataFrameに変換
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                return None
            
            df_data = []
            for date, values in time_series.items():
                df_data.append({
                    'Date': pd.to_datetime(date),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # 期間でフィルタリング
            if period != "max":
                end_date = datetime.now()
                if period == "1y":
                    start_date = end_date - timedelta(days=365)
                elif period == "6mo":
                    start_date = end_date - timedelta(days=180)
                elif period == "3mo":
                    start_date = end_date - timedelta(days=90)
                elif period == "1mo":
                    start_date = end_date - timedelta(days=30)
                else:
                    start_date = end_date - timedelta(days=365)
                
                df = df[df.index >= start_date]
            
            if not self._validate_data(df):
                return None
            
            confidence = self._calculate_confidence(df)
            
            return StockData(
                symbol=symbol,
                data=df,
                source=self.name,
                timestamp=datetime.now(),
                confidence=confidence,
                metadata={
                    'period': period,
                    'data_points': len(df),
                    'currency': 'USD'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage データ取得エラー {symbol}: {e}")
            return None
    
    def get_financial_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """財務指標を取得"""
        if not self.config.api_key:
            return None
        
        try:
            self._rate_limit_check()
            
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.config.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data:
                return None
            
            metrics = {
                'market_cap': self._safe_float(data.get('MarketCapitalization')),
                'pe_ratio': self._safe_float(data.get('PERatio')),
                'pb_ratio': self._safe_float(data.get('PriceToBookRatio')),
                'dividend_yield': self._safe_float(data.get('DividendYield')),
                'roe': self._safe_float(data.get('ReturnOnEquityTTM')),
                'debt_to_equity': self._safe_float(data.get('DebtToEquity')),
                'current_ratio': self._safe_float(data.get('CurrentRatio')),
                'quick_ratio': self._safe_float(data.get('QuickRatio'))
            }
            
            return {k: v for k, v in metrics.items() if v is not None}
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage 財務指標取得エラー {symbol}: {e}")
            return None
    
    def get_news_data(self, symbol: str, days_back: int = 7) -> Optional[List[Dict]]:
        """ニュースデータを取得"""
        if not self.config.api_key:
            return None
        
        try:
            self._rate_limit_check()
            
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': self.config.api_key,
                'limit': 50
            }
            
            response = self.session.get(self.base_url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Error Message' in data:
                return None
            
            news_items = data.get('feed', [])
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            filtered_news = []
            for item in news_items:
                try:
                    pub_date = datetime.fromisoformat(item['time_published'].replace('Z', '+00:00'))
                    if pub_date >= cutoff_date:
                        filtered_news.append({
                            'title': item.get('title', ''),
                            'summary': item.get('summary', ''),
                            'url': item.get('url', ''),
                            'source': item.get('source', ''),
                            'published_at': pub_date,
                            'sentiment': item.get('overall_sentiment_score', 0)
                        })
                except:
                    continue
            
            return filtered_news
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage ニュース取得エラー {symbol}: {e}")
            return None
    
    def _safe_float(self, value: str) -> Optional[float]:
        """安全にfloatに変換"""
        try:
            return float(value) if value and value != 'None' else None
        except (ValueError, TypeError):
            return None

class IEXCloudSource(DataSource):
    """IEX Cloud データソース"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.name = "IEX Cloud"
        self.base_url = "https://cloud.iexapis.com/stable"
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[StockData]:
        """IEX Cloudから株価データを取得"""
        if not self.config.api_key:
            self.logger.warning("IEX Cloud APIキーが設定されていません")
            return None
        
        try:
            self._rate_limit_check()
            
            # 期間に応じた範囲を設定
            range_map = {
                "1mo": "1m",
                "3mo": "3m",
                "6mo": "6m",
                "1y": "1y",
                "2y": "2y",
                "5y": "5y",
                "max": "max"
            }
            
            range_param = range_map.get(period, "1y")
            
            url = f"{self.base_url}/stock/{symbol}/chart/{range_param}"
            params = {
                'token': self.config.api_key
            }
            
            response = self.session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return None
            
            # データをDataFrameに変換
            df_data = []
            for item in data:
                df_data.append({
                    'Date': pd.to_datetime(item['date']),
                    'Open': item.get('open'),
                    'High': item.get('high'),
                    'Low': item.get('low'),
                    'Close': item.get('close'),
                    'Volume': item.get('volume', 0)
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            if not self._validate_data(df):
                return None
            
            confidence = self._calculate_confidence(df)
            
            return StockData(
                symbol=symbol,
                data=df,
                source=self.name,
                timestamp=datetime.now(),
                confidence=confidence,
                metadata={
                    'period': period,
                    'data_points': len(df),
                    'currency': 'USD'
                }
            )
            
        except Exception as e:
            self.logger.error(f"IEX Cloud データ取得エラー {symbol}: {e}")
            return None
    
    def get_financial_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """財務指標を取得"""
        if not self.config.api_key:
            return None
        
        try:
            self._rate_limit_check()
            
            url = f"{self.base_url}/stock/{symbol}/stats"
            params = {
                'token': self.config.api_key
            }
            
            response = self.session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            metrics = {
                'market_cap': data.get('marketcap'),
                'pe_ratio': data.get('peRatio'),
                'pb_ratio': data.get('priceToBook'),
                'dividend_yield': data.get('dividendYield'),
                'roe': data.get('returnOnEquity'),
                'debt_to_equity': data.get('debtToEquity'),
                'current_ratio': data.get('currentRatio'),
                'quick_ratio': data.get('quickRatio')
            }
            
            return {k: v for k, v in metrics.items() if v is not None}
            
        except Exception as e:
            self.logger.error(f"IEX Cloud 財務指標取得エラー {symbol}: {e}")
            return None
    
    def get_news_data(self, symbol: str, days_back: int = 7) -> Optional[List[Dict]]:
        """ニュースデータを取得"""
        if not self.config.api_key:
            return None
        
        try:
            self._rate_limit_check()
            
            url = f"{self.base_url}/stock/{symbol}/news/last/50"
            params = {
                'token': self.config.api_key
            }
            
            response = self.session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            filtered_news = []
            
            for item in data:
                try:
                    pub_date = datetime.fromisoformat(item['datetime'].replace('Z', '+00:00'))
                    if pub_date >= cutoff_date:
                        filtered_news.append({
                            'title': item.get('headline', ''),
                            'summary': item.get('summary', ''),
                            'url': item.get('url', ''),
                            'source': item.get('source', ''),
                            'published_at': pub_date,
                            'sentiment': 'neutral'  # IEX Cloudはセンチメント情報を提供しない
                        })
                except:
                    continue
            
            return filtered_news
            
        except Exception as e:
            self.logger.error(f"IEX Cloud ニュース取得エラー {symbol}: {e}")
            return None

class MultiDataSourceManager:
    """複数データソース管理クラス"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.sources = {}
        self.fallback_cache = {}
        self.data_quality_threshold = 0.7
        
        # 設定ファイルからデータソース設定を読み込み
        self._load_config(config_file)
        self._initialize_sources()
    
    def _load_config(self, config_file: str):
        """設定ファイルを読み込み"""
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.api_keys = config.get('api_keys', {})
            self.data_sources_config = config.get('data_sources', {})
            
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            self.api_keys = {}
            self.data_sources_config = {}
    
    def _initialize_sources(self):
        """データソースを初期化"""
        # Yahoo Finance (常に有効)
        yahoo_config = DataSourceConfig(
            name="yahoo_finance",
            rate_limit=self.data_sources_config.get('yahoo_finance', {}).get('rate_limit', 1000),
            priority=1,
            enabled=True
        )
        self.sources['yahoo_finance'] = YahooFinanceSource(yahoo_config)
        
        # Alpha Vantage
        if self.data_sources_config.get('alpha_vantage', {}).get('enabled', False):
            alpha_config = DataSourceConfig(
                name="alpha_vantage",
                api_key=self.api_keys.get('alpha_vantage'),
                rate_limit=self.data_sources_config.get('alpha_vantage', {}).get('rate_limit', 5),
                priority=2,
                enabled=True
            )
            self.sources['alpha_vantage'] = AlphaVantageSource(alpha_config)
        
        # IEX Cloud
        if self.data_sources_config.get('iex_cloud', {}).get('enabled', False):
            iex_config = DataSourceConfig(
                name="iex_cloud",
                api_key=self.api_keys.get('iex_cloud'),
                rate_limit=self.data_sources_config.get('iex_cloud', {}).get('rate_limit', 100),
                priority=3,
                enabled=True
            )
            self.sources['iex_cloud'] = IEXCloudSource(iex_config)
        
        # 優先度順にソート
        self.sources = dict(sorted(self.sources.items(), 
                                 key=lambda x: x[1].config.priority))
    
    def get_stock_data(self, symbol: str, period: str = "1y", 
                      fallback: bool = True) -> Optional[StockData]:
        """複数ソースから株価データを取得"""
        cache_key = f"stock_data_{symbol}_{period}"
        
        # キャッシュから取得を試行
        cached_data = cache_manager.get(cache_key, ttl=1800)  # 30分キャッシュ
        if cached_data:
            self.logger.debug(f"キャッシュからデータ取得: {symbol}")
            return cached_data
        
        best_data = None
        best_confidence = 0.0
        
        # 各データソースからデータを取得
        for source_name, source in self.sources.items():
            if not source.config.enabled:
                continue
            
            try:
                data = source.get_stock_data(symbol, period)
                if data and data.confidence > best_confidence:
                    best_data = data
                    best_confidence = data.confidence
                    
                    # 信頼度が閾値を超えた場合は早期終了
                    if data.confidence >= self.data_quality_threshold:
                        break
                        
            except Exception as e:
                self.logger.warning(f"{source_name} データ取得エラー {symbol}: {e}")
                continue
        
        # フォールバック処理
        if not best_data and fallback:
            best_data = self._get_fallback_data(symbol, period)
        
        # キャッシュに保存
        if best_data:
            cache_manager.set(cache_key, best_data, ttl=1800)
        
        return best_data
    
    def get_financial_metrics(self, symbol: str, 
                            fallback: bool = True) -> Optional[Dict[str, Any]]:
        """複数ソースから財務指標を取得"""
        cache_key = f"financial_metrics_{symbol}"
        
        # キャッシュから取得を試行
        cached_metrics = cache_manager.get(cache_key, ttl=3600)  # 1時間キャッシュ
        if cached_metrics:
            return cached_metrics
        
        all_metrics = {}
        
        # 各データソースから財務指標を取得
        for source_name, source in self.sources.items():
            if not source.config.enabled:
                continue
            
            try:
                metrics = source.get_financial_metrics(symbol)
                if metrics:
                    # メトリクスを統合（後から取得した値で上書き）
                    all_metrics.update(metrics)
                    
            except Exception as e:
                self.logger.warning(f"{source_name} 財務指標取得エラー {symbol}: {e}")
                continue
        
        # キャッシュに保存
        if all_metrics:
            cache_manager.set(cache_key, all_metrics, ttl=3600)
        
        return all_metrics if all_metrics else None
    
    def get_news_data(self, symbol: str, days_back: int = 7,
                     fallback: bool = True) -> List[Dict]:
        """複数ソースからニュースデータを取得"""
        cache_key = f"news_data_{symbol}_{days_back}"
        
        # キャッシュから取得を試行
        cached_news = cache_manager.get(cache_key, ttl=1800)  # 30分キャッシュ
        if cached_news:
            return cached_news
        
        all_news = []
        seen_urls = set()
        
        # 各データソースからニュースを取得
        for source_name, source in self.sources.items():
            if not source.config.enabled:
                continue
            
            try:
                news = source.get_news_data(symbol, days_back)
                if news:
                    for item in news:
                        # 重複チェック
                        if item.get('url') not in seen_urls:
                            all_news.append(item)
                            seen_urls.add(item.get('url'))
                            
            except Exception as e:
                self.logger.warning(f"{source_name} ニュース取得エラー {symbol}: {e}")
                continue
        
        # 日付順にソート
        all_news.sort(key=lambda x: x.get('published_at', datetime.min), reverse=True)
        
        # キャッシュに保存
        if all_news:
            cache_manager.set(cache_key, all_news, ttl=1800)
        
        return all_news
    
    def _get_fallback_data(self, symbol: str, period: str) -> Optional[StockData]:
        """フォールバックデータを取得"""
        # キャッシュから古いデータを取得
        cache_key = f"fallback_{symbol}_{period}"
        fallback_data = self.fallback_cache.get(cache_key)
        
        if fallback_data:
            # データが古すぎる場合は無効
            if (datetime.now() - fallback_data.timestamp).days > 7:
                return None
            return fallback_data
        
        return None
    
    def get_data_quality_report(self, symbol: str) -> Dict[str, Any]:
        """データ品質レポートを生成"""
        report = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'sources': {},
            'overall_quality': 0.0
        }
        
        total_confidence = 0.0
        active_sources = 0
        
        for source_name, source in self.sources.items():
            if not source.config.enabled:
                continue
            
            try:
                data = source.get_stock_data(symbol, "1mo")
                if data:
                    report['sources'][source_name] = {
                        'confidence': data.confidence,
                        'data_points': len(data.data),
                        'last_update': data.timestamp,
                        'status': 'active'
                    }
                    total_confidence += data.confidence
                    active_sources += 1
                else:
                    report['sources'][source_name] = {
                        'confidence': 0.0,
                        'data_points': 0,
                        'last_update': None,
                        'status': 'failed'
                    }
                    
            except Exception as e:
                report['sources'][source_name] = {
                    'confidence': 0.0,
                    'data_points': 0,
                    'last_update': None,
                    'status': f'error: {str(e)}'
                }
        
        if active_sources > 0:
            report['overall_quality'] = total_confidence / active_sources
        
        return report
    
    def optimize_data_sources(self):
        """データソースの最適化"""
        # 使用頻度に基づく優先度調整
        # エラー率に基づく無効化
        # レート制限の動的調整
        
        for source_name, source in self.sources.items():
            if hasattr(source, 'request_count'):
                # エラー率が高い場合は一時的に無効化
                if source.request_count > 100 and hasattr(source, 'error_count'):
                    error_rate = source.error_count / source.request_count
                    if error_rate > 0.1:  # 10%以上のエラー率
                        source.config.enabled = False
                        self.logger.warning(f"{source_name} を一時的に無効化 (エラー率: {error_rate:.2%})")

# グローバルインスタンス
multi_data_source_manager = MultiDataSourceManager()
