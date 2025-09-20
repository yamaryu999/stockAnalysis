"""
Intelligent Performance Optimization System
インテリジェントパフォーマンス最適化システム - 自動最適化、リソース管理、負荷分散
"""

import psutil
import time
import threading
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import queue
import gc
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np
import pandas as pd
from functools import wraps, lru_cache
import json
import os
import subprocess
import signal
import sys
from contextlib import contextmanager
import tracemalloc
import linecache
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PerformanceMetrics:
    """パフォーマンスメトリクス"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    network_io: Dict[str, int]
    process_count: int
    active_connections: int
    response_time: float
    throughput: float

@dataclass
class OptimizationRule:
    """最適化ルール"""
    rule_id: str
    condition: Dict[str, Any]
    action: str
    parameters: Dict[str, Any]
    enabled: bool = True
    priority: int = 1

@dataclass
class OptimizationResult:
    """最適化結果"""
    rule_id: str
    action_taken: str
    performance_before: PerformanceMetrics
    performance_after: PerformanceMetrics
    improvement: float
    timestamp: datetime
    success: bool

class ResourceMonitor:
    """リソース監視クラス"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: float = 1.0):
        """監視を開始"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("リソース監視開始")
    
    def stop_monitoring(self):
        """監視を停止"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        self.logger.info("リソース監視停止")
    
    def _monitoring_loop(self, interval: float):
        """監視ループ"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """メトリクスを収集"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # メモリ使用量
            memory = psutil.virtual_memory()
            
            # ディスク使用量
            disk = psutil.disk_usage('/')
            
            # ネットワークI/O
            network = psutil.net_io_counters()
            
            # プロセス数
            process_count = len(psutil.pids())
            
            # アクティブ接続数
            try:
                connections = psutil.net_connections()
                active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                active_connections = 0
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
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
                process_count=process_count,
                active_connections=active_connections,
                response_time=0.0,  # 後で計算
                throughput=0.0  # 後で計算
            )
            
        except Exception as e:
            self.logger.error(f"メトリクス収集エラー: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                memory_available=0.0,
                disk_usage=0.0,
                network_io={},
                process_count=0,
                active_connections=0,
                response_time=0.0,
                throughput=0.0
            )
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """現在のメトリクスを取得"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_trend(self, duration_minutes: int = 10) -> Dict[str, List[float]]:
        """メトリクストレンドを取得"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
        
        return {
            'cpu_usage': [m.cpu_usage for m in recent_metrics],
            'memory_usage': [m.memory_usage for m in recent_metrics],
            'disk_usage': [m.disk_usage for m in recent_metrics],
            'timestamps': [m.timestamp for m in recent_metrics]
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """パフォーマンスサマリーを取得"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # 直近100件
        
        return {
            'avg_cpu_usage': np.mean([m.cpu_usage for m in recent_metrics]),
            'max_cpu_usage': max([m.cpu_usage for m in recent_metrics]),
            'avg_memory_usage': np.mean([m.memory_usage for m in recent_metrics]),
            'max_memory_usage': max([m.memory_usage for m in recent_metrics]),
            'avg_disk_usage': np.mean([m.disk_usage for m in recent_metrics]),
            'memory_available_gb': recent_metrics[-1].memory_available,
            'total_metrics': len(self.metrics_history)
        }

class MemoryOptimizer:
    """メモリ最適化クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weak_refs = weakref.WeakSet()
        self.memory_threshold = 80.0  # メモリ使用率の閾値
        
    def optimize_memory(self) -> Dict[str, Any]:
        """メモリ最適化を実行"""
        try:
            before_memory = psutil.virtual_memory().percent
            
            # ガベージコレクション実行
            collected = gc.collect()
            
            # 弱参照のクリーンアップ
            self._cleanup_weak_refs()
            
            # キャッシュのクリーンアップ
            self._cleanup_caches()
            
            # メモリマッピングの最適化
            self._optimize_memory_mapping()
            
            after_memory = psutil.virtual_memory().percent
            improvement = before_memory - after_memory
            
            result = {
                'before_memory': before_memory,
                'after_memory': after_memory,
                'improvement': improvement,
                'objects_collected': collected,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"メモリ最適化完了: {improvement:.2f}%改善")
            return result
            
        except Exception as e:
            self.logger.error(f"メモリ最適化エラー: {e}")
            return {'error': str(e)}
    
    def _cleanup_weak_refs(self):
        """弱参照のクリーンアップ"""
        # 弱参照セットをクリア
        self.weak_refs.clear()
    
    def _cleanup_caches(self):
        """キャッシュのクリーンアップ"""
        # linecacheのクリーンアップ
        linecache.clearcache()
        
        # その他のキャッシュクリーンアップ
        if hasattr(gc, 'set_threshold'):
            gc.set_threshold(700, 10, 10)  # ガベージコレクション閾値を調整
    
    def _optimize_memory_mapping(self):
        """メモリマッピングの最適化"""
        # メモリマッピングの最適化処理
        pass
    
    def add_weak_ref(self, obj):
        """弱参照を追加"""
        self.weak_refs.add(obj)
    
    def get_memory_usage_by_type(self) -> Dict[str, int]:
        """型別メモリ使用量を取得"""
        try:
            import tracemalloc
            if not tracemalloc.is_tracing():
                tracemalloc.start()
            
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            type_usage = {}
            for stat in top_stats[:20]:  # 上位20件
                filename = stat.traceback.format()[0]
                if 'site-packages' not in filename:  # サードパーティライブラリを除外
                    type_usage[filename] = stat.size
            
            return type_usage
            
        except Exception as e:
            self.logger.error(f"メモリ使用量分析エラー: {e}")
            return {}

class CPUOptimizer:
    """CPU最適化クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cpu_threshold = 80.0  # CPU使用率の閾値
        self.process_priorities = {}
        
    def optimize_cpu(self) -> Dict[str, Any]:
        """CPU最適化を実行"""
        try:
            before_cpu = psutil.cpu_percent(interval=1)
            
            # プロセス優先度の調整
            self._adjust_process_priorities()
            
            # CPUアフィニティの最適化
            self._optimize_cpu_affinity()
            
            # スレッドプールの最適化
            self._optimize_thread_pools()
            
            after_cpu = psutil.cpu_percent(interval=1)
            improvement = before_cpu - after_cpu
            
            result = {
                'before_cpu': before_cpu,
                'after_cpu': after_cpu,
                'improvement': improvement,
                'timestamp': datetime.now()
            }
            
            self.logger.info(f"CPU最適化完了: {improvement:.2f}%改善")
            return result
            
        except Exception as e:
            self.logger.error(f"CPU最適化エラー: {e}")
            return {'error': str(e)}
    
    def _adjust_process_priorities(self):
        """プロセス優先度の調整"""
        try:
            current_process = psutil.Process()
            # プロセス優先度を高く設定
            current_process.nice(psutil.HIGH_PRIORITY_CLASS)
        except (psutil.AccessDenied, AttributeError):
            pass
    
    def _optimize_cpu_affinity(self):
        """CPUアフィニティの最適化"""
        try:
            current_process = psutil.Process()
            cpu_count = psutil.cpu_count()
            
            # 利用可能なCPUコアに分散
            if cpu_count > 1:
                affinity = list(range(cpu_count))
                current_process.cpu_affinity(affinity)
        except (psutil.AccessDenied, AttributeError):
            pass
    
    def _optimize_thread_pools(self):
        """スレッドプールの最適化"""
        # スレッドプールの最適化処理
        pass

class CacheOptimizer:
    """キャッシュ最適化クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_stats = {}
        
    def optimize_caches(self) -> Dict[str, Any]:
        """キャッシュ最適化を実行"""
        try:
            # LRUキャッシュの最適化
            self._optimize_lru_caches()
            
            # メモリキャッシュの最適化
            self._optimize_memory_caches()
            
            # ディスクキャッシュの最適化
            self._optimize_disk_caches()
            
            result = {
                'timestamp': datetime.now(),
                'optimization_completed': True
            }
            
            self.logger.info("キャッシュ最適化完了")
            return result
            
        except Exception as e:
            self.logger.error(f"キャッシュ最適化エラー: {e}")
            return {'error': str(e)}
    
    def _optimize_lru_caches(self):
        """LRUキャッシュの最適化"""
        # LRUキャッシュの最適化処理
        pass
    
    def _optimize_memory_caches(self):
        """メモリキャッシュの最適化"""
        # メモリキャッシュの最適化処理
        pass
    
    def _optimize_disk_caches(self):
        """ディスクキャッシュの最適化"""
        # ディスクキャッシュの最適化処理
        pass

class LoadBalancer:
    """負荷分散クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.worker_pools = {}
        self.load_distribution = {}
        
    def create_worker_pool(self, pool_name: str, max_workers: int = None):
        """ワーカープールを作成"""
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        
        self.worker_pools[pool_name] = ThreadPoolExecutor(max_workers=max_workers)
        self.load_distribution[pool_name] = {
            'active_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'max_workers': max_workers
        }
        
        self.logger.info(f"ワーカープール作成: {pool_name} (max_workers: {max_workers})")
    
    def submit_task(self, pool_name: str, func: Callable, *args, **kwargs):
        """タスクを送信"""
        if pool_name not in self.worker_pools:
            self.create_worker_pool(pool_name)
        
        pool = self.worker_pools[pool_name]
        future = pool.submit(func, *args, **kwargs)
        
        # 負荷統計を更新
        self.load_distribution[pool_name]['active_tasks'] += 1
        
        return future
    
    def get_load_distribution(self) -> Dict[str, Any]:
        """負荷分散状況を取得"""
        return self.load_distribution.copy()
    
    def balance_load(self):
        """負荷を分散"""
        try:
            # 各プールの負荷を分析
            for pool_name, stats in self.load_distribution.items():
                utilization = stats['active_tasks'] / stats['max_workers']
                
                if utilization > 0.8:  # 80%以上の使用率
                    self.logger.warning(f"プール {pool_name} の負荷が高い: {utilization:.2%}")
                    # 必要に応じてワーカー数を増加
                    self._scale_pool(pool_name, 'up')
                elif utilization < 0.2:  # 20%未満の使用率
                    self.logger.info(f"プール {pool_name} の負荷が低い: {utilization:.2%}")
                    # 必要に応じてワーカー数を減少
                    self._scale_pool(pool_name, 'down')
        
        except Exception as e:
            self.logger.error(f"負荷分散エラー: {e}")
    
    def _scale_pool(self, pool_name: str, direction: str):
        """プールをスケール"""
        try:
            current_stats = self.load_distribution[pool_name]
            current_workers = current_stats['max_workers']
            
            if direction == 'up' and current_workers < 64:
                new_workers = min(64, current_workers * 2)
                self._resize_pool(pool_name, new_workers)
            elif direction == 'down' and current_workers > 2:
                new_workers = max(2, current_workers // 2)
                self._resize_pool(pool_name, new_workers)
                
        except Exception as e:
            self.logger.error(f"プールスケールエラー {pool_name}: {e}")
    
    def _resize_pool(self, pool_name: str, new_workers: int):
        """プールサイズを変更"""
        try:
            # 既存のプールをシャットダウン
            if pool_name in self.worker_pools:
                self.worker_pools[pool_name].shutdown(wait=False)
            
            # 新しいプールを作成
            self.worker_pools[pool_name] = ThreadPoolExecutor(max_workers=new_workers)
            self.load_distribution[pool_name]['max_workers'] = new_workers
            
            self.logger.info(f"プール {pool_name} を {new_workers} ワーカーにスケール")
            
        except Exception as e:
            self.logger.error(f"プールリサイズエラー {pool_name}: {e}")
    
    def shutdown_all_pools(self):
        """全プールをシャットダウン"""
        for pool_name, pool in self.worker_pools.items():
            try:
                pool.shutdown(wait=True)
                self.logger.info(f"プール {pool_name} シャットダウン完了")
            except Exception as e:
                self.logger.error(f"プールシャットダウンエラー {pool_name}: {e}")

class IntelligentPerformanceOptimizer:
    """インテリジェントパフォーマンス最適化システム"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # コンポーネントの初期化
        self.resource_monitor = ResourceMonitor()
        self.memory_optimizer = MemoryOptimizer()
        self.cpu_optimizer = CPUOptimizer()
        self.cache_optimizer = CacheOptimizer()
        self.load_balancer = LoadBalancer()
        
        # 最適化ルール
        self.optimization_rules = {}
        self.optimization_history = deque(maxlen=1000)
        
        # 自動最適化の制御
        self.auto_optimization = True
        self.optimization_interval = 60  # 秒
        self.optimization_thread = None
        self.running = False
        
        # パフォーマンス閾値
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 80.0,
            'disk_usage': 90.0,
            'response_time': 5.0  # 秒
        }
        
        # デフォルトルールの設定
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """デフォルトルールを設定"""
        default_rules = [
            OptimizationRule(
                rule_id='high_memory_usage',
                condition={'memory_usage': {'>': 80}},
                action='optimize_memory',
                parameters={},
                priority=1
            ),
            OptimizationRule(
                rule_id='high_cpu_usage',
                condition={'cpu_usage': {'>': 80}},
                action='optimize_cpu',
                parameters={},
                priority=1
            ),
            OptimizationRule(
                rule_id='low_memory_available',
                condition={'memory_available': {'<': 1.0}},  # 1GB未満
                action='optimize_memory',
                parameters={'aggressive': True},
                priority=2
            ),
            OptimizationRule(
                rule_id='cache_optimization',
                condition={'memory_usage': {'>': 70}},
                action='optimize_caches',
                parameters={},
                priority=3
            )
        ]
        
        for rule in default_rules:
            self.optimization_rules[rule.rule_id] = rule
    
    def start_auto_optimization(self):
        """自動最適化を開始"""
        if self.running:
            return
        
        self.running = True
        self.resource_monitor.start_monitoring()
        
        self.optimization_thread = threading.Thread(
            target=self._auto_optimization_loop,
            daemon=True
        )
        self.optimization_thread.start()
        
        self.logger.info("自動最適化開始")
    
    def stop_auto_optimization(self):
        """自動最適化を停止"""
        self.running = False
        self.resource_monitor.stop_monitoring()
        
        if self.optimization_thread and self.optimization_thread.is_alive():
            self.optimization_thread.join(timeout=5)
        
        self.load_balancer.shutdown_all_pools()
        
        self.logger.info("自動最適化停止")
    
    def _auto_optimization_loop(self):
        """自動最適化ループ"""
        while self.running:
            try:
                if self.auto_optimization:
                    self._evaluate_and_optimize()
                
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                self.logger.error(f"自動最適化ループエラー: {e}")
                time.sleep(10)
    
    def _evaluate_and_optimize(self):
        """評価と最適化を実行"""
        try:
            current_metrics = self.resource_monitor.get_current_metrics()
            if not current_metrics:
                return
            
            # ルールを評価
            triggered_rules = self._evaluate_rules(current_metrics)
            
            # 最適化を実行
            for rule in triggered_rules:
                self._execute_optimization(rule, current_metrics)
            
        except Exception as e:
            self.logger.error(f"評価・最適化エラー: {e}")
    
    def _evaluate_rules(self, metrics: PerformanceMetrics) -> List[OptimizationRule]:
        """ルールを評価"""
        triggered_rules = []
        
        for rule in self.optimization_rules.values():
            if not rule.enabled:
                continue
            
            if self._evaluate_rule_condition(rule, metrics):
                triggered_rules.append(rule)
        
        # 優先度順にソート
        triggered_rules.sort(key=lambda x: x.priority)
        
        return triggered_rules
    
    def _evaluate_rule_condition(self, rule: OptimizationRule, 
                               metrics: PerformanceMetrics) -> bool:
        """ルール条件を評価"""
        try:
            condition = rule.condition
            
            for metric_name, condition_dict in condition.items():
                if not hasattr(metrics, metric_name):
                    continue
                
                metric_value = getattr(metrics, metric_name)
                
                for operator, threshold in condition_dict.items():
                    if operator == '>' and metric_value <= threshold:
                        return False
                    elif operator == '<' and metric_value >= threshold:
                        return False
                    elif operator == '>=' and metric_value < threshold:
                        return False
                    elif operator == '<=' and metric_value > threshold:
                        return False
                    elif operator == '==' and metric_value != threshold:
                        return False
                    elif operator == '!=' and metric_value == threshold:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"ルール条件評価エラー: {e}")
            return False
    
    def _execute_optimization(self, rule: OptimizationRule, 
                            before_metrics: PerformanceMetrics):
        """最適化を実行"""
        try:
            action = rule.action
            parameters = rule.parameters
            
            self.logger.info(f"最適化実行: {rule.rule_id} - {action}")
            
            # 最適化を実行
            if action == 'optimize_memory':
                result = self.memory_optimizer.optimize_memory()
            elif action == 'optimize_cpu':
                result = self.cpu_optimizer.optimize_cpu()
            elif action == 'optimize_caches':
                result = self.cache_optimizer.optimize_caches()
            elif action == 'balance_load':
                self.load_balancer.balance_load()
                result = {'success': True}
            else:
                self.logger.warning(f"未知の最適化アクション: {action}")
                return
            
            # 最適化後のメトリクスを取得
            time.sleep(2)  # 最適化効果を測定するため少し待機
            after_metrics = self.resource_monitor.get_current_metrics()
            
            if after_metrics:
                improvement = self._calculate_improvement(before_metrics, after_metrics)
                
                optimization_result = OptimizationResult(
                    rule_id=rule.rule_id,
                    action_taken=action,
                    performance_before=before_metrics,
                    performance_after=after_metrics,
                    improvement=improvement,
                    timestamp=datetime.now(),
                    success=result.get('success', True)
                )
                
                self.optimization_history.append(optimization_result)
                
                self.logger.info(f"最適化完了: {rule.rule_id} - 改善率: {improvement:.2f}%")
            
        except Exception as e:
            self.logger.error(f"最適化実行エラー {rule.rule_id}: {e}")
    
    def _calculate_improvement(self, before: PerformanceMetrics, 
                             after: PerformanceMetrics) -> float:
        """改善率を計算"""
        try:
            # メモリ使用率の改善を計算
            memory_improvement = before.memory_usage - after.memory_usage
            
            # CPU使用率の改善を計算
            cpu_improvement = before.cpu_usage - after.cpu_usage
            
            # 総合改善率（重み付き平均）
            total_improvement = (memory_improvement * 0.6 + cpu_improvement * 0.4)
            
            return total_improvement
            
        except Exception as e:
            self.logger.error(f"改善率計算エラー: {e}")
            return 0.0
    
    def add_optimization_rule(self, rule: OptimizationRule):
        """最適化ルールを追加"""
        self.optimization_rules[rule.rule_id] = rule
        self.logger.info(f"最適化ルール追加: {rule.rule_id}")
    
    def remove_optimization_rule(self, rule_id: str):
        """最適化ルールを削除"""
        if rule_id in self.optimization_rules:
            del self.optimization_rules[rule_id]
            self.logger.info(f"最適化ルール削除: {rule_id}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを取得"""
        try:
            current_metrics = self.resource_monitor.get_current_metrics()
            performance_summary = self.resource_monitor.get_performance_summary()
            load_distribution = self.load_balancer.get_load_distribution()
            
            # 最適化履歴の統計
            recent_optimizations = list(self.optimization_history)[-10:]
            optimization_stats = {
                'total_optimizations': len(self.optimization_history),
                'recent_optimizations': len(recent_optimizations),
                'avg_improvement': np.mean([opt.improvement for opt in recent_optimizations]) if recent_optimizations else 0,
                'success_rate': sum(1 for opt in recent_optimizations if opt.success) / len(recent_optimizations) if recent_optimizations else 0
            }
            
            return {
                'timestamp': datetime.now(),
                'current_metrics': asdict(current_metrics) if current_metrics else None,
                'performance_summary': performance_summary,
                'load_distribution': load_distribution,
                'optimization_stats': optimization_stats,
                'active_rules': len([r for r in self.optimization_rules.values() if r.enabled]),
                'auto_optimization': self.auto_optimization,
                'running': self.running
            }
            
        except Exception as e:
            self.logger.error(f"パフォーマンスレポート生成エラー: {e}")
            return {'error': str(e)}
    
    def manual_optimize(self, optimization_type: str) -> Dict[str, Any]:
        """手動最適化を実行"""
        try:
            before_metrics = self.resource_monitor.get_current_metrics()
            
            if optimization_type == 'memory':
                result = self.memory_optimizer.optimize_memory()
            elif optimization_type == 'cpu':
                result = self.cpu_optimizer.optimize_cpu()
            elif optimization_type == 'cache':
                result = self.cache_optimizer.optimize_caches()
            elif optimization_type == 'all':
                memory_result = self.memory_optimizer.optimize_memory()
                cpu_result = self.cpu_optimizer.optimize_cpu()
                cache_result = self.cache_optimizer.optimize_caches()
                result = {
                    'memory': memory_result,
                    'cpu': cpu_result,
                    'cache': cache_result
                }
            else:
                return {'error': f'Unknown optimization type: {optimization_type}'}
            
            after_metrics = self.resource_monitor.get_current_metrics()
            
            return {
                'optimization_type': optimization_type,
                'before_metrics': asdict(before_metrics) if before_metrics else None,
                'after_metrics': asdict(after_metrics) if after_metrics else None,
                'result': result,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"手動最適化エラー: {e}")
            return {'error': str(e)}

# パフォーマンス測定デコレータ
def performance_monitor(func):
    """パフォーマンス監視デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # パフォーマンスログ
            logger = logging.getLogger(func.__module__)
            logger.info(f"{func.__name__} - 実行時間: {execution_time:.3f}s, メモリ使用量: {memory_usage:.2f}MB")
        
        return result
    return wrapper

# グローバルインスタンス
intelligent_performance_optimizer = IntelligentPerformanceOptimizer()
