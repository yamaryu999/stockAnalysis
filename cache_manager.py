import pickle
import os
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import logging
import threading
from functools import wraps
import psutil
from performance_optimizer import performance_timer, memory_efficient

class CacheManager:
    """データキャッシュ管理クラス"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl  # デフォルトTTL（秒）
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # キャッシュディレクトリの作成
        os.makedirs(cache_dir, exist_ok=True)
        
        # メモリキャッシュ（高速アクセス用）
        self._memory_cache = {}
        self._memory_cache_ttl = {}
        
        # メモリ使用量制限（MB）
        self.max_memory_cache_mb = 100
        self.current_memory_cache_mb = 0
        
        # キャッシュ統計
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'file_hits': 0,
            'evictions': 0
        }
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """キャッシュキーを生成"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """キャッシュファイルのパスを取得"""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """キャッシュが期限切れかチェック"""
        return time.time() - timestamp > ttl
    
    @performance_timer
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """キャッシュからデータを取得（最適化版）"""
        if ttl is None:
            ttl = self.default_ttl
        
        with self._lock:
            # メモリキャッシュから取得を試行
            if key in self._memory_cache:
                if not self._is_expired(self._memory_cache_ttl[key], ttl):
                    self.cache_stats['hits'] += 1
                    self.cache_stats['memory_hits'] += 1
                    self.logger.debug(f"メモリキャッシュから取得: {key}")
                    return self._memory_cache[key]
                else:
                    # 期限切れの場合は削除
                    del self._memory_cache[key]
                    del self._memory_cache_ttl[key]
            
            # ファイルキャッシュから取得を試行
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    if not self._is_expired(cache_data['timestamp'], ttl):
                        # メモリキャッシュにも保存（容量チェック付き）
                        self._add_to_memory_cache(key, cache_data['data'], cache_data['timestamp'])
                        
                        self.cache_stats['hits'] += 1
                        self.cache_stats['file_hits'] += 1
                        self.logger.debug(f"ファイルキャッシュから取得: {key}")
                        return cache_data['data']
                    else:
                        # 期限切れの場合は削除
                        os.remove(cache_path)
                        self.logger.debug(f"期限切れキャッシュを削除: {key}")
                        
                except Exception as e:
                    self.logger.error(f"キャッシュ読み込みエラー {key}: {e}")
                    # 破損したキャッシュファイルを削除
                    try:
                        os.remove(cache_path)
                    except:
                        pass
            
            self.cache_stats['misses'] += 1
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """キャッシュにデータを保存"""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            timestamp = time.time()
            cache_data = {
                'data': data,
                'timestamp': timestamp,
                'ttl': ttl
            }
            
            with self._lock:
                # メモリキャッシュに保存
                self._memory_cache[key] = data
                self._memory_cache_ttl[key] = timestamp
                
                # ファイルキャッシュに保存
                cache_path = self._get_cache_path(key)
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                self.logger.debug(f"キャッシュに保存: {key}")
                return True
                
        except Exception as e:
            self.logger.error(f"キャッシュ保存エラー {key}: {e}")
            return False
    
    def _add_to_memory_cache(self, key: str, data: Any, timestamp: float):
        """メモリキャッシュにデータを追加（容量管理付き）"""
        try:
            # データサイズを推定
            data_size_mb = self._estimate_data_size(data)
            
            # 容量チェック
            if self.current_memory_cache_mb + data_size_mb > self.max_memory_cache_mb:
                self._evict_memory_cache()
            
            # メモリキャッシュに追加
            self._memory_cache[key] = data
            self._memory_cache_ttl[key] = timestamp
            self.current_memory_cache_mb += data_size_mb
            
        except Exception as e:
            self.logger.error(f"メモリキャッシュ追加エラー: {e}")
    
    def _estimate_data_size(self, data: Any) -> float:
        """データサイズを推定（MB）"""
        try:
            import sys
            size_bytes = sys.getsizeof(data)
            return size_bytes / (1024 * 1024)  # MB
        except:
            return 0.1  # デフォルト値
    
    def _evict_memory_cache(self):
        """メモリキャッシュから古いデータを削除"""
        try:
            if not self._memory_cache:
                return
            
            # 最も古いデータを削除
            oldest_key = min(self._memory_cache_ttl.keys(), 
                           key=lambda k: self._memory_cache_ttl[k])
            
            del self._memory_cache[oldest_key]
            del self._memory_cache_ttl[oldest_key]
            self.cache_stats['evictions'] += 1
            
            self.logger.debug(f"メモリキャッシュから削除: {oldest_key}")
            
        except Exception as e:
            self.logger.error(f"メモリキャッシュ削除エラー: {e}")
    
    def get_cache_stats(self) -> Dict:
        """キャッシュ統計を取得"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests,
            'memory_hits': self.cache_stats['memory_hits'],
            'file_hits': self.cache_stats['file_hits'],
            'misses': self.cache_stats['misses'],
            'evictions': self.cache_stats['evictions'],
            'memory_cache_size_mb': round(self.current_memory_cache_mb, 2),
            'memory_cache_items': len(self._memory_cache)
        }
    
    def optimize_cache(self) -> bool:
        """キャッシュ最適化を実行"""
        try:
            # 期限切れファイルの削除
            self._cleanup_expired_files()
            
            # メモリキャッシュの最適化
            self._optimize_memory_cache()
            
            self.logger.info("キャッシュ最適化が完了しました")
            return True
            
        except Exception as e:
            self.logger.error(f"キャッシュ最適化エラー: {e}")
            return False
    
    def _cleanup_expired_files(self):
        """期限切れファイルを削除"""
        try:
            current_time = time.time()
            removed_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        with open(file_path, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        if self._is_expired(cache_data['timestamp'], cache_data.get('ttl', self.default_ttl)):
                            os.remove(file_path)
                            removed_count += 1
                            
                    except Exception as e:
                        # 破損したファイルを削除
                        os.remove(file_path)
                        removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"期限切れキャッシュファイルを削除: {removed_count}件")
                
        except Exception as e:
            self.logger.error(f"期限切れファイル削除エラー: {e}")
    
    def _optimize_memory_cache(self):
        """メモリキャッシュの最適化"""
        try:
            # 期限切れデータの削除
            current_time = time.time()
            expired_keys = []
            
            for key, timestamp in self._memory_cache_ttl.items():
                if self._is_expired(timestamp, self.default_ttl):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_cache[key]
                del self._memory_cache_ttl[key]
            
            if expired_keys:
                self.logger.info(f"期限切れメモリキャッシュを削除: {len(expired_keys)}件")
                
        except Exception as e:
            self.logger.error(f"メモリキャッシュ最適化エラー: {e}")
    
    def delete(self, key: str) -> bool:
        """キャッシュを削除"""
        try:
            with self._lock:
                # メモリキャッシュから削除
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    del self._memory_cache_ttl[key]
                
                # ファイルキャッシュから削除
                cache_path = self._get_cache_path(key)
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                
                self.logger.debug(f"キャッシュを削除: {key}")
                return True
                
        except Exception as e:
            self.logger.error(f"キャッシュ削除エラー {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """全キャッシュをクリア"""
        try:
            with self._lock:
                # メモリキャッシュをクリア
                self._memory_cache.clear()
                self._memory_cache_ttl.clear()
                
                # ファイルキャッシュをクリア
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, filename))
                
                self.logger.info("全キャッシュをクリアしました")
                return True
                
        except Exception as e:
            self.logger.error(f"キャッシュクリアエラー: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """期限切れキャッシュをクリーンアップ"""
        cleaned_count = 0
        
        try:
            with self._lock:
                # メモリキャッシュのクリーンアップ
                expired_keys = []
                for key, timestamp in self._memory_cache_ttl.items():
                    if self._is_expired(timestamp, self.default_ttl):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._memory_cache[key]
                    del self._memory_cache_ttl[key]
                    cleaned_count += 1
                
                # ファイルキャッシュのクリーンアップ
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        cache_path = os.path.join(self.cache_dir, filename)
                        try:
                            with open(cache_path, 'rb') as f:
                                cache_data = pickle.load(f)
                            
                            if self._is_expired(cache_data['timestamp'], cache_data.get('ttl', self.default_ttl)):
                                os.remove(cache_path)
                                cleaned_count += 1
                                
                        except Exception as e:
                            self.logger.error(f"キャッシュファイル処理エラー {filename}: {e}")
                            # 破損したファイルは削除
                            try:
                                os.remove(cache_path)
                                cleaned_count += 1
                            except:
                                pass
            
            if cleaned_count > 0:
                self.logger.info(f"{cleaned_count}個の期限切れキャッシュをクリーンアップしました")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"キャッシュクリーンアップエラー: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """キャッシュ統計情報を取得"""
        try:
            with self._lock:
                stats = {
                    'memory_cache_size': len(self._memory_cache),
                    'file_cache_count': 0,
                    'total_cache_size_mb': 0
                }
                
                # ファイルキャッシュの統計
                total_size = 0
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.cache'):
                        cache_path = os.path.join(self.cache_dir, filename)
                        stats['file_cache_count'] += 1
                        total_size += os.path.getsize(cache_path)
                
                stats['total_cache_size_mb'] = total_size / (1024 * 1024)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"キャッシュ統計取得エラー: {e}")
            return {}
    
    def cached(self, ttl: Optional[int] = None, key_prefix: str = ""):
        """デコレータ: 関数の結果をキャッシュ"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # キャッシュキーを生成
                cache_key = f"{key_prefix}{func.__name__}_{self._generate_cache_key(*args, **kwargs)}"
                
                # キャッシュから取得を試行
                cached_result = self.get(cache_key, ttl)
                if cached_result is not None:
                    return cached_result
                
                # 関数を実行して結果をキャッシュ
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator

# グローバルキャッシュマネージャーインスタンス
cache_manager = CacheManager()

# 便利なデコレータ
def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """関数の結果をキャッシュするデコレータ"""
    return cache_manager.cached(ttl, key_prefix)

# 特定用途のキャッシュマネージャー
class StockDataCache:
    """株価データ専用キャッシュ"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.stock_ttl = 1800  # 30分
        self.metrics_ttl = 3600  # 1時間
        self.analysis_ttl = 7200  # 2時間
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[Any]:
        """株価データをキャッシュから取得"""
        key = f"stock_data_{symbol}_{period}"
        return self.cache.get(key, self.stock_ttl)
    
    def set_stock_data(self, symbol: str, data: Any, period: str = "1y") -> bool:
        """株価データをキャッシュに保存"""
        key = f"stock_data_{symbol}_{period}"
        return self.cache.set(key, data, self.stock_ttl)
    
    def get_financial_metrics(self, symbol: str) -> Optional[Any]:
        """財務指標をキャッシュから取得"""
        key = f"financial_metrics_{symbol}"
        return self.cache.get(key, self.metrics_ttl)
    
    def set_financial_metrics(self, symbol: str, data: Any) -> bool:
        """財務指標をキャッシュに保存"""
        key = f"financial_metrics_{symbol}"
        return self.cache.set(key, data, self.metrics_ttl)
    
    def get_analysis_result(self, analysis_type: str, symbol: str) -> Optional[Any]:
        """分析結果をキャッシュから取得"""
        key = f"analysis_{analysis_type}_{symbol}"
        return self.cache.get(key, self.analysis_ttl)
    
    def set_analysis_result(self, analysis_type: str, symbol: str, data: Any) -> bool:
        """分析結果をキャッシュに保存"""
        key = f"analysis_{analysis_type}_{symbol}"
        return self.cache.set(key, data, self.analysis_ttl)
    
    def invalidate_stock_data(self, symbol: str) -> bool:
        """株価データのキャッシュを無効化"""
        # 複数の期間のキャッシュを削除
        periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        success = True
        for period in periods:
            key = f"stock_data_{symbol}_{period}"
            if not self.cache.delete(key):
                success = False
        return success
    
    def invalidate_financial_metrics(self, symbol: str) -> bool:
        """財務指標のキャッシュを無効化"""
        key = f"financial_metrics_{symbol}"
        return self.cache.delete(key)
    
    def invalidate_analysis_result(self, analysis_type: str, symbol: str) -> bool:
        """分析結果のキャッシュを無効化"""
        key = f"analysis_{analysis_type}_{symbol}"
        return self.cache.delete(key)

# グローバル株価データキャッシュインスタンス
stock_cache = StockDataCache(cache_manager)
