"""
パフォーマンス最適化モジュール
データベースクエリ最適化、メモリ使用量削減、非同期処理の実装
"""

import asyncio
import aiohttp
import psutil
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pandas as pd
import numpy as np
from functools import wraps, lru_cache
import gc
import weakref
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

@dataclass
class PerformanceMetrics:
    """パフォーマンスメトリクス"""
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: datetime

class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.max_history = 1000
        
    def get_current_metrics(self) -> PerformanceMetrics:
        """現在のパフォーマンスメトリクスを取得"""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = PerformanceMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                memory_available=memory.available / (1024**3),  # GB
                disk_usage=disk.percent,
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
                
            return metrics
            
        except Exception as e:
            self.logger.error(f"パフォーマンスメトリクス取得エラー: {e}")
            return None
    
    def get_memory_usage(self) -> Dict[str, float]:
        """メモリ使用量の詳細を取得"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total / (1024**3),
                'available': memory.available / (1024**3),
                'used': memory.used / (1024**3),
                'percent': memory.percent,
                'cached': memory.cached / (1024**3) if hasattr(memory, 'cached') else 0,
                'buffers': memory.buffers / (1024**3) if hasattr(memory, 'buffers') else 0
            }
        except Exception as e:
            self.logger.error(f"メモリ使用量取得エラー: {e}")
            return {}
    
    def optimize_memory(self):
        """メモリ最適化を実行"""
        try:
            # ガベージコレクション実行
            collected = gc.collect()
            self.logger.info(f"ガベージコレクション実行: {collected}オブジェクト回収")
            
            # メモリ使用量をログ出力
            memory_info = self.get_memory_usage()
            self.logger.info(f"メモリ使用量: {memory_info}")
            
        except Exception as e:
            self.logger.error(f"メモリ最適化エラー: {e}")

class QueryOptimizer:
    """データベースクエリ最適化クラス"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.query_cache = {}
        self.query_stats = {}
    
    def optimize_query(self, query: str, params: tuple = None) -> str:
        """クエリを最適化"""
        try:
            # 基本的なクエリ最適化
            optimized_query = self._apply_basic_optimizations(query)
            
            # インデックスヒントの追加
            optimized_query = self._add_index_hints(optimized_query)
            
            # クエリ統計を記録
            self._record_query_stats(query, optimized_query)
            
            return optimized_query
            
        except Exception as e:
            self.logger.error(f"クエリ最適化エラー: {e}")
            return query
    
    def _apply_basic_optimizations(self, query: str) -> str:
        """基本的なクエリ最適化を適用"""
        # SELECT * を避ける
        if 'SELECT *' in query.upper():
            self.logger.warning("SELECT * の使用を検出。具体的なカラム名の使用を推奨")
        
        # LIMIT句の追加（適切な場合）
        if 'SELECT' in query.upper() and 'LIMIT' not in query.upper():
            if 'ORDER BY' not in query.upper():
                self.logger.warning("ORDER BY句なしでLIMIT句の使用を検出")
        
        return query
    
    def _add_index_hints(self, query: str) -> str:
        """インデックスヒントを追加"""
        # SQLiteではインデックスヒントは限定的だが、
        # クエリプランの最適化を提案
        return query
    
    def _record_query_stats(self, original_query: str, optimized_query: str):
        """クエリ統計を記録"""
        query_hash = hash(original_query)
        if query_hash not in self.query_stats:
            self.query_stats[query_hash] = {
                'original': original_query,
                'optimized': optimized_query,
                'execution_count': 0,
                'total_time': 0,
                'avg_time': 0
            }
        
        self.query_stats[query_hash]['execution_count'] += 1

class AsyncDataProcessor:
    """非同期データ処理クラス"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        self.session = None
    
    async def __aenter__(self):
        """非同期コンテキストマネージャーの開始"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了"""
        if self.session:
            await self.session.close()
    
    async def fetch_data_async(self, urls: List[str]) -> List[Dict]:
        """非同期でデータを取得"""
        if not self.session:
            raise RuntimeError("AsyncDataProcessorは非同期コンテキスト内で使用してください")
        
        tasks = []
        for url in urls:
            task = self._fetch_single_url(url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # エラーをフィルタリング
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"データ取得エラー: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _fetch_single_url(self, url: str) -> Dict:
        """単一URLからデータを取得"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {'url': url, 'data': data, 'status': 'success'}
                else:
                    return {'url': url, 'data': None, 'status': f'error_{response.status}'}
        except Exception as e:
            return {'url': url, 'data': None, 'status': f'error_{str(e)}'}

class MemoryOptimizer:
    """メモリ最適化クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weak_refs = weakref.WeakValueDictionary()
        self.memory_threshold = 80  # メモリ使用率の閾値（%）
    
    def optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrameのメモリ使用量を最適化"""
        try:
            original_memory = df.memory_usage(deep=True).sum() / 1024**2  # MB
            
            # 数値型の最適化
            for col in df.select_dtypes(include=['int64']).columns:
                if df[col].min() >= 0:
                    if df[col].max() < 255:
                        df[col] = df[col].astype('uint8')
                    elif df[col].max() < 65535:
                        df[col] = df[col].astype('uint16')
                    elif df[col].max() < 4294967295:
                        df[col] = df[col].astype('uint32')
                else:
                    if df[col].min() > -128 and df[col].max() < 127:
                        df[col] = df[col].astype('int8')
                    elif df[col].min() > -32768 and df[col].max() < 32767:
                        df[col] = df[col].astype('int16')
                    elif df[col].min() > -2147483648 and df[col].max() < 2147483647:
                        df[col] = df[col].astype('int32')
            
            # 浮動小数点型の最適化
            for col in df.select_dtypes(include=['float64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
            
            # カテゴリカル型の最適化
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.5:  # ユニーク値が50%未満
                    df[col] = df[col].astype('category')
            
            optimized_memory = df.memory_usage(deep=True).sum() / 1024**2  # MB
            reduction = (original_memory - optimized_memory) / original_memory * 100
            
            self.logger.info(f"DataFrame最適化: {original_memory:.2f}MB → {optimized_memory:.2f}MB ({reduction:.1f}%削減)")
            
            return df
            
        except Exception as e:
            self.logger.error(f"DataFrame最適化エラー: {e}")
            return df
    
    def check_memory_usage(self) -> bool:
        """メモリ使用率をチェック"""
        try:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.memory_threshold:
                self.logger.warning(f"メモリ使用率が閾値を超過: {memory_percent:.1f}% > {self.memory_threshold}%")
                return True
            return False
        except Exception as e:
            self.logger.error(f"メモリ使用率チェックエラー: {e}")
            return False
    
    def cleanup_memory(self):
        """メモリクリーンアップを実行"""
        try:
            # ガベージコレクション
            collected = gc.collect()
            
            # 弱参照のクリーンアップ
            self.weak_refs.clear()
            
            self.logger.info(f"メモリクリーンアップ完了: {collected}オブジェクト回収")
            
        except Exception as e:
            self.logger.error(f"メモリクリーンアップエラー: {e}")

def performance_timer(func: Callable) -> Callable:
    """パフォーマンス計測デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} 実行時間: {execution_time:.3f}秒")
        
        return result
    return wrapper

def memory_efficient(func: Callable) -> Callable:
    """メモリ効率化デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        optimizer = MemoryOptimizer()
        
        # 実行前のメモリチェック
        if optimizer.check_memory_usage():
            optimizer.cleanup_memory()
        
        result = func(*args, **kwargs)
        
        # 実行後のメモリクリーンアップ
        optimizer.cleanup_memory()
        
        return result
    return wrapper

@lru_cache(maxsize=128)
def cached_calculation(func: Callable, *args, **kwargs):
    """計算結果をキャッシュするデコレータ"""
    return func(*args, **kwargs)

class BatchProcessor:
    """バッチ処理クラス"""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def process_in_batches(self, data: List[Any], process_func: Callable) -> List[Any]:
        """データをバッチで処理"""
        results = []
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            self.logger.info(f"バッチ処理: {i//self.batch_size + 1}/{(len(data)-1)//self.batch_size + 1}")
            
            # 並列処理でバッチを処理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                batch_results = list(executor.map(process_func, batch))
                results.extend(batch_results)
        
        return results
    
    def process_with_progress(self, data: List[Any], process_func: Callable, 
                           progress_callback: Optional[Callable] = None) -> List[Any]:
        """プログレス表示付きでバッチ処理"""
        results = []
        total = len(data)
        
        for i, item in enumerate(data):
            result = process_func(item)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results

# グローバルインスタンス
performance_monitor = PerformanceMonitor()
memory_optimizer = MemoryOptimizer()