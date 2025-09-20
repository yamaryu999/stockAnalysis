"""
複数データソース対応システム
複数のAPIプロバイダーから株価データを取得・統合
"""

import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

@dataclass
class StockData:
    """株価データクラス"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open_price: float
    close_price: float
    timestamp: datetime
    source: str
    confidence: float = 1.0

@dataclass
class DataSourceConfig:
    """データソース設定クラス"""
    name: str
    api_key: Optional[str] = None
    base_url: str = ""
    rate_limit: int = 100  # 1分あたりのリクエスト数
    timeout: int = 30
    enabled: bool = True
    priority: int = 1  # 優先度（1が最高）

class DataSource(ABC):
    """データソース基底クラス"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.request_count = 0
        self.last_request_time = 0
        self.session = None
    
    @abstractmethod
    async def fetch_stock_data(self, symbol: str) -> Optional[StockData]:
        """株価データを取得"""
        pass
    
    @abstractmethod
    async def fetch_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """複数銘柄のデータを取得"""
        pass
    
    @abstractmethod
    def get_supported_symbols(self) -> List[str]:
        """サポートされている銘柄一覧を取得"""
        pass
    
    def _check_rate_limit(self):
        """レート制限をチェック"""
        current_time = time.time()
        if current_time - self.last_request_time < 60:  # 1分以内
            if self.request_count >= self.config.rate_limit:
                sleep_time = 60 - (current_time - self.last_request_time)
                self.logger.warning(f"レート制限に達しました。{sleep_time:.1f}秒待機します。")
                time.sleep(sleep_time)
                self.request_count = 0
                self.last_request_time = time.time()
        else:
            self.request_count = 0
            self.last_request_time = current_time
        
        self.request_count += 1
    
    async def _get_session(self):
        """HTTPセッションを取得"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """セッションを閉じる"""
        if self.session:
            await self.session.close()

class YahooFinanceSource(DataSource):
    """Yahoo Finance データソース"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.config.name = "Yahoo Finance"
    
    async def fetch_stock_data(self, symbol: str) -> Optional[StockData]:
        """株価データを取得"""
        try:
            self._check_rate_limit()
            
            # yfinanceを使用してデータを取得
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 履歴データを取得
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = info.get('previousClose', current_price)
            
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
            
            return StockData(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                high=hist['High'].iloc[-1],
                low=hist['Low'].iloc[-1],
                open_price=hist['Open'].iloc[-1],
                close_price=current_price,
                timestamp=datetime.now(),
                source=self.config.name,
                confidence=0.9
            )
            
        except Exception as e:
            self.logger.error(f"Yahoo Finance データ取得エラー {symbol}: {e}")
            return None
    
    async def fetch_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """複数銘柄のデータを取得"""
        results = {}
        
        # 並列処理でデータを取得
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.fetch_stock_data(symbol))
            tasks.append((symbol, task))
        
        for symbol, task in tasks:
            try:
                data = await task
                if data:
                    results[symbol] = data
            except Exception as e:
                self.logger.error(f"複数銘柄取得エラー {symbol}: {e}")
        
        return results
    
    def get_supported_symbols(self) -> List[str]:
        """サポートされている銘柄一覧を取得"""
        # 日本株の主要銘柄
        return [
            "7203.T", "6758.T", "9984.T", "6861.T", "8035.T",
            "4063.T", "9983.T", "8306.T", "9432.T", "9433.T",
            "9434.T", "9437.T", "9982.T", "4503.T", "4502.T",
            "4506.T", "4507.T", "4519.T", "4523.T", "4543.T"
        ]

class AlphaVantageSource(DataSource):
    """Alpha Vantage データソース"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.config.name = "Alpha Vantage"
        self.config.base_url = "https://www.alphavantage.co/query"
    
    async def fetch_stock_data(self, symbol: str) -> Optional[StockData]:
        """株価データを取得"""
        try:
            if not self.config.api_key:
                self.logger.warning("Alpha Vantage APIキーが設定されていません")
                return None
            
            self._check_rate_limit()
            
            session = await self._get_session()
            
            # リアルタイム株価を取得
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol.replace('.T', ''),  # Alpha Vantage用に変換
                'apikey': self.config.api_key
            }
            
            async with session.get(self.config.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        
                        price = float(quote.get('05. price', 0))
                        change = float(quote.get('09. change', 0))
                        change_percent = float(quote.get('10. change percent', '0%').replace('%', ''))
                        volume = int(quote.get('06. volume', 0))
                        high = float(quote.get('03. high', 0))
                        low = float(quote.get('04. low', 0))
                        open_price = float(quote.get('02. open', 0))
                        
                        return StockData(
                            symbol=symbol,
                            price=price,
                            change=change,
                            change_percent=change_percent,
                            volume=volume,
                            high=high,
                            low=low,
                            open_price=open_price,
                            close_price=price,
                            timestamp=datetime.now(),
                            source=self.config.name,
                            confidence=0.8
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage データ取得エラー {symbol}: {e}")
            return None
    
    async def fetch_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """複数銘柄のデータを取得"""
        results = {}
        
        # Alpha Vantageは1リクエストで1銘柄のみ
        for symbol in symbols:
            data = await self.fetch_stock_data(symbol)
            if data:
                results[symbol] = data
        
        return results
    
    def get_supported_symbols(self) -> List[str]:
        """サポートされている銘柄一覧を取得"""
        return [
            "7203", "6758", "9984", "6861", "8035",
            "4063", "9983", "8306", "9432", "9433"
        ]

class IEXCloudSource(DataSource):
    """IEX Cloud データソース"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.config.name = "IEX Cloud"
        self.config.base_url = "https://cloud.iexapis.com/stable"
    
    async def fetch_stock_data(self, symbol: str) -> Optional[StockData]:
        """株価データを取得"""
        try:
            if not self.config.api_key:
                self.logger.warning("IEX Cloud APIキーが設定されていません")
                return None
            
            self._check_rate_limit()
            
            session = await self._get_session()
            
            # 株価データを取得
            url = f"{self.config.base_url}/stock/{symbol}/quote"
            params = {'token': self.config.api_key}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    price = data.get('latestPrice', 0)
                    change = data.get('change', 0)
                    change_percent = data.get('changePercent', 0) * 100
                    volume = data.get('latestVolume', 0)
                    high = data.get('high', 0)
                    low = data.get('low', 0)
                    open_price = data.get('open', 0)
                    
                    return StockData(
                        symbol=symbol,
                        price=price,
                        change=change,
                        change_percent=change_percent,
                        volume=volume,
                        high=high,
                        low=low,
                        open_price=open_price,
                        close_price=price,
                        timestamp=datetime.now(),
                        source=self.config.name,
                        confidence=0.85
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"IEX Cloud データ取得エラー {symbol}: {e}")
            return None
    
    async def fetch_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """複数銘柄のデータを取得"""
        try:
            if not self.config.api_key:
                return {}
            
            self._check_rate_limit()
            
            session = await self._get_session()
            
            # バッチリクエストで複数銘柄を取得
            symbols_str = ','.join(symbols)
            url = f"{self.config.base_url}/stock/market/batch"
            params = {
                'symbols': symbols_str,
                'types': 'quote',
                'token': self.config.api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = {}
                    
                    for symbol, quote_data in data.items():
                        if 'quote' in quote_data:
                            quote = quote_data['quote']
                            
                            results[symbol] = StockData(
                                symbol=symbol,
                                price=quote.get('latestPrice', 0),
                                change=quote.get('change', 0),
                                change_percent=quote.get('changePercent', 0) * 100,
                                volume=quote.get('latestVolume', 0),
                                high=quote.get('high', 0),
                                low=quote.get('low', 0),
                                open_price=quote.get('open', 0),
                                close_price=quote.get('latestPrice', 0),
                                timestamp=datetime.now(),
                                source=self.config.name,
                                confidence=0.85
                            )
                    
                    return results
            
            return {}
            
        except Exception as e:
            self.logger.error(f"IEX Cloud 複数銘柄取得エラー: {e}")
            return {}
    
    def get_supported_symbols(self) -> List[str]:
        """サポートされている銘柄一覧を取得"""
        return [
            "7203", "6758", "9984", "6861", "8035",
            "4063", "9983", "8306", "9432", "9433"
        ]

class MultiDataSourceManager:
    """複数データソース管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_sources: List[DataSource] = []
        self.data_cache: Dict[str, StockData] = {}
        self.cache_ttl = 30  # 秒
        self.last_cache_update = {}
        
        # デフォルトデータソースを初期化
        self._initialize_default_sources()
    
    def _initialize_default_sources(self):
        """デフォルトデータソースを初期化"""
        # Yahoo Finance（常に有効）
        yahoo_config = DataSourceConfig(
            name="Yahoo Finance",
            priority=1,
            rate_limit=1000,
            enabled=True
        )
        self.data_sources.append(YahooFinanceSource(yahoo_config))
        
        # Alpha Vantage（APIキーが必要）
        alpha_config = DataSourceConfig(
            name="Alpha Vantage",
            api_key=None,  # 設定ファイルから読み込み
            priority=2,
            rate_limit=5,  # 無料プランは5リクエスト/分
            enabled=False
        )
        self.data_sources.append(AlphaVantageSource(alpha_config))
        
        # IEX Cloud（APIキーが必要）
        iex_config = DataSourceConfig(
            name="IEX Cloud",
            api_key=None,  # 設定ファイルから読み込み
            priority=3,
            rate_limit=100,
            enabled=False
        )
        self.data_sources.append(IEXCloudSource(iex_config))
    
    def add_data_source(self, data_source: DataSource):
        """データソースを追加"""
        self.data_sources.append(data_source)
        self.logger.info(f"データソースを追加: {data_source.config.name}")
    
    def remove_data_source(self, name: str):
        """データソースを削除"""
        self.data_sources = [ds for ds in self.data_sources if ds.config.name != name]
        self.logger.info(f"データソースを削除: {name}")
    
    def enable_data_source(self, name: str):
        """データソースを有効化"""
        for ds in self.data_sources:
            if ds.config.name == name:
                ds.config.enabled = True
                self.logger.info(f"データソースを有効化: {name}")
                break
    
    def disable_data_source(self, name: str):
        """データソースを無効化"""
        for ds in self.data_sources:
            if ds.config.name == name:
                ds.config.enabled = False
                self.logger.info(f"データソースを無効化: {name}")
                break
    
    def get_enabled_sources(self) -> List[DataSource]:
        """有効なデータソースを取得"""
        return [ds for ds in self.data_sources if ds.config.enabled]
    
    def get_source_by_name(self, name: str) -> Optional[DataSource]:
        """名前でデータソースを取得"""
        for ds in self.data_sources:
            if ds.config.name == name:
                return ds
        return None
    
    async def fetch_stock_data(self, symbol: str, preferred_source: Optional[str] = None) -> Optional[StockData]:
        """株価データを取得（複数ソース対応）"""
        # キャッシュチェック
        cache_key = f"{symbol}_{int(time.time() // self.cache_ttl)}"
        if cache_key in self.data_cache:
            cached_data = self.data_cache[cache_key]
            self.logger.debug(f"キャッシュからデータを取得: {symbol}")
            return cached_data
        
        # 有効なデータソースを優先度順にソート
        enabled_sources = self.get_enabled_sources()
        if preferred_source:
            preferred_ds = self.get_source_by_name(preferred_source)
            if preferred_ds and preferred_ds.config.enabled:
                enabled_sources = [preferred_ds] + [ds for ds in enabled_sources if ds.config.name != preferred_source]
        
        enabled_sources.sort(key=lambda x: x.config.priority)
        
        # 各データソースからデータを取得
        for data_source in enabled_sources:
            try:
                data = await data_source.fetch_stock_data(symbol)
                if data:
                    # キャッシュに保存
                    self.data_cache[cache_key] = data
                    self.last_cache_update[cache_key] = time.time()
                    
                    self.logger.info(f"データを取得: {symbol} from {data_source.config.name}")
                    return data
                    
            except Exception as e:
                self.logger.error(f"データソース {data_source.config.name} でエラー: {e}")
                continue
        
        self.logger.warning(f"すべてのデータソースでデータ取得に失敗: {symbol}")
        return None
    
    async def fetch_multiple_stocks(self, symbols: List[str], preferred_source: Optional[str] = None) -> Dict[str, StockData]:
        """複数銘柄のデータを取得"""
        results = {}
        
        # 並列処理でデータを取得
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self.fetch_stock_data(symbol, preferred_source))
            tasks.append((symbol, task))
        
        for symbol, task in tasks:
            try:
                data = await task
                if data:
                    results[symbol] = data
            except Exception as e:
                self.logger.error(f"複数銘柄取得エラー {symbol}: {e}")
        
        return results
    
    def get_aggregated_data(self, symbol: str) -> Optional[StockData]:
        """複数ソースから集約されたデータを取得"""
        # 各ソースからデータを取得して集約
        all_data = []
        
        for data_source in self.get_enabled_sources():
            try:
                # 同期処理でデータを取得（簡略化）
                data = asyncio.run(data_source.fetch_stock_data(symbol))
                if data:
                    all_data.append(data)
            except Exception as e:
                self.logger.error(f"集約データ取得エラー {data_source.config.name}: {e}")
        
        if not all_data:
            return None
        
        # データを集約（平均値、信頼度重み付き）
        total_confidence = sum(d.confidence for d in all_data)
        
        if total_confidence == 0:
            return all_data[0]  # フォールバック
        
        aggregated = StockData(
            symbol=symbol,
            price=sum(d.price * d.confidence for d in all_data) / total_confidence,
            change=sum(d.change * d.confidence for d in all_data) / total_confidence,
            change_percent=sum(d.change_percent * d.confidence for d in all_data) / total_confidence,
            volume=int(sum(d.volume * d.confidence for d in all_data) / total_confidence),
            high=max(d.high for d in all_data),
            low=min(d.low for d in all_data),
            open_price=sum(d.open_price * d.confidence for d in all_data) / total_confidence,
            close_price=sum(d.close_price * d.confidence for d in all_data) / total_confidence,
            timestamp=datetime.now(),
            source="Aggregated",
            confidence=min(total_confidence / len(all_data), 1.0)
        )
        
        return aggregated
    
    def get_source_statistics(self) -> Dict[str, Any]:
        """データソース統計を取得"""
        stats = {}
        
        for data_source in self.data_sources:
            stats[data_source.config.name] = {
                'enabled': data_source.config.enabled,
                'priority': data_source.config.priority,
                'rate_limit': data_source.config.rate_limit,
                'request_count': data_source.request_count,
                'supported_symbols_count': len(data_source.get_supported_symbols())
            }
        
        return stats
    
    async def cleanup(self):
        """リソースをクリーンアップ"""
        for data_source in self.data_sources:
            await data_source.close()
        
        self.logger.info("データソースリソースをクリーンアップしました")

# グローバルインスタンス
multi_data_source_manager = MultiDataSourceManager()

# 設定ファイルからAPIキーを読み込む関数
def load_api_keys_from_config():
    """設定ファイルからAPIキーを読み込み"""
    try:
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        api_keys = config.get('api_keys', {})
        
        # Alpha Vantage
        alpha_source = multi_data_source_manager.get_source_by_name("Alpha Vantage")
        if alpha_source and 'alpha_vantage' in api_keys:
            alpha_source.config.api_key = api_keys['alpha_vantage']
            alpha_source.config.enabled = True
        
        # IEX Cloud
        iex_source = multi_data_source_manager.get_source_by_name("IEX Cloud")
        if iex_source and 'iex_cloud' in api_keys:
            iex_source.config.api_key = api_keys['iex_cloud']
            iex_source.config.enabled = True
        
        logging.info("APIキーを設定ファイルから読み込みました")
        
    except Exception as e:
        logging.error(f"APIキー読み込みエラー: {e}")

# 初期化時にAPIキーを読み込み
load_api_keys_from_config()