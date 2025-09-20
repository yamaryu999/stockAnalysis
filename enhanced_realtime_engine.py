"""
Enhanced Real-time Analysis Engine
リアルタイム分析エンジンの強化版 - ストリーミング処理、パターン検出、インテリジェントアラート
"""

import asyncio
import websockets
import json
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import yfinance as yf
from enhanced_data_sources import multi_data_source_manager
from advanced_ml_pipeline import advanced_ml_pipeline
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StreamingData:
    """ストリーミングデータ"""
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open_price: Optional[float] = None

@dataclass
class PatternSignal:
    """パターンシグナル"""
    pattern_type: str
    confidence: float
    direction: str  # 'bullish', 'bearish', 'neutral'
    strength: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class AlertSignal:
    """アラートシグナル"""
    alert_id: str
    symbol: str
    alert_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime
    data: Dict[str, Any]
    action_required: bool = False

class StreamingDataProcessor:
    """ストリーミングデータプロセッサー"""
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.data_buffers = {}
        self.logger = logging.getLogger(__name__)
        
    def add_data(self, data: StreamingData):
        """データをバッファに追加"""
        if data.symbol not in self.data_buffers:
            self.data_buffers[data.symbol] = deque(maxlen=self.buffer_size)
        
        self.data_buffers[data.symbol].append(data)
    
    def get_latest_data(self, symbol: str, count: int = 100) -> List[StreamingData]:
        """最新データを取得"""
        if symbol not in self.data_buffers:
            return []
        
        buffer = self.data_buffers[symbol]
        return list(buffer)[-count:] if len(buffer) >= count else list(buffer)
    
    def process_data(self, symbol: str) -> Dict[str, Any]:
        """データを処理して統計情報を生成"""
        data_points = self.get_latest_data(symbol, 100)
        
        if not data_points:
            return {}
        
        prices = [d.price for d in data_points]
        volumes = [d.volume for d in data_points]
        timestamps = [d.timestamp for d in data_points]
        
        # 基本統計
        stats = {
            'current_price': prices[-1],
            'price_change': prices[-1] - prices[0] if len(prices) > 1 else 0,
            'price_change_pct': ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 1 and prices[0] != 0 else 0,
            'volatility': np.std(prices) if len(prices) > 1 else 0,
            'volume_avg': np.mean(volumes) if volumes else 0,
            'volume_trend': self._calculate_volume_trend(volumes),
            'price_trend': self._calculate_price_trend(prices),
            'data_points': len(data_points),
            'time_span': (timestamps[-1] - timestamps[0]).total_seconds() if len(timestamps) > 1 else 0
        }
        
        return stats
    
    def _calculate_volume_trend(self, volumes: List[int]) -> str:
        """出来高トレンドを計算"""
        if len(volumes) < 10:
            return 'neutral'
        
        recent_avg = np.mean(volumes[-5:])
        earlier_avg = np.mean(volumes[-10:-5])
        
        if recent_avg > earlier_avg * 1.2:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_price_trend(self, prices: List[float]) -> str:
        """価格トレンドを計算"""
        if len(prices) < 10:
            return 'neutral'
        
        # 線形回帰の傾きを計算
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        
        if slope > 0.01:
            return 'uptrend'
        elif slope < -0.01:
            return 'downtrend'
        else:
            return 'sideways'

class RealtimePatternDetector:
    """リアルタイムパターン検出器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_cache = {}
        
    def detect_patterns(self, symbol: str, data_points: List[StreamingData]) -> List[PatternSignal]:
        """パターンを検出"""
        if len(data_points) < 20:
            return []
        
        patterns = []
        
        # 価格データを抽出
        prices = [d.price for d in data_points]
        volumes = [d.volume for d in data_points]
        timestamps = [d.timestamp for d in data_points]
        
        # 各種パターンを検出
        patterns.extend(self._detect_support_resistance(prices, timestamps))
        patterns.extend(self._detect_breakout_patterns(prices, volumes, timestamps))
        patterns.extend(self._detect_reversal_patterns(prices, volumes, timestamps))
        patterns.extend(self._detect_volume_patterns(prices, volumes, timestamps))
        patterns.extend(self._detect_volatility_patterns(prices, timestamps))
        
        return patterns
    
    def _detect_support_resistance(self, prices: List[float], 
                                 timestamps: List[datetime]) -> List[PatternSignal]:
        """サポート・レジスタンス検出"""
        patterns = []
        
        if len(prices) < 20:
            return patterns
        
        # ローカル高値・安値を検出
        peaks, _ = self._find_peaks_valleys(prices)
        
        # サポートレベル（安値のクラスタ）
        support_levels = self._find_cluster_levels(prices, peaks, 'min')
        for level, confidence in support_levels:
            if confidence > 0.7:
                patterns.append(PatternSignal(
                    pattern_type='support_level',
                    confidence=confidence,
                    direction='bullish',
                    strength=confidence,
                    timestamp=timestamps[-1],
                    metadata={'level': level, 'type': 'support'}
                ))
        
        # レジスタンスレベル（高値のクラスタ）
        resistance_levels = self._find_cluster_levels(prices, peaks, 'max')
        for level, confidence in resistance_levels:
            if confidence > 0.7:
                patterns.append(PatternSignal(
                    pattern_type='resistance_level',
                    confidence=confidence,
                    direction='bearish',
                    strength=confidence,
                    timestamp=timestamps[-1],
                    metadata={'level': level, 'type': 'resistance'}
                ))
        
        return patterns
    
    def _detect_breakout_patterns(self, prices: List[float], 
                                volumes: List[int], 
                                timestamps: List[datetime]) -> List[PatternSignal]:
        """ブレイクアウトパターン検出"""
        patterns = []
        
        if len(prices) < 30:
            return patterns
        
        # ボラティリティの収縮を検出
        recent_volatility = np.std(prices[-10:])
        earlier_volatility = np.std(prices[-30:-10])
        
        if recent_volatility < earlier_volatility * 0.7:
            # 出来高の増加をチェック
            recent_volume = np.mean(volumes[-5:])
            earlier_volume = np.mean(volumes[-15:-5])
            
            if recent_volume > earlier_volume * 1.5:
                # ブレイクアウトの方向を判定
                price_change = prices[-1] - prices[-10]
                direction = 'bullish' if price_change > 0 else 'bearish'
                
                patterns.append(PatternSignal(
                    pattern_type='breakout',
                    confidence=0.8,
                    direction=direction,
                    strength=abs(price_change) / prices[-10],
                    timestamp=timestamps[-1],
                    metadata={
                        'volatility_contraction': recent_volatility / earlier_volatility,
                        'volume_surge': recent_volume / earlier_volume,
                        'price_change': price_change
                    }
                ))
        
        return patterns
    
    def _detect_reversal_patterns(self, prices: List[float], 
                                volumes: List[int], 
                                timestamps: List[datetime]) -> List[PatternSignal]:
        """反転パターン検出"""
        patterns = []
        
        if len(prices) < 20:
            return patterns
        
        # ハンマー・ドージパターン
        hammer_pattern = self._detect_hammer_pattern(prices[-5:])
        if hammer_pattern:
            patterns.append(PatternSignal(
                pattern_type='hammer',
                confidence=hammer_pattern['confidence'],
                direction='bullish',
                strength=hammer_pattern['strength'],
                timestamp=timestamps[-1],
                metadata=hammer_pattern
            ))
        
        # シューティングスターパターン
        shooting_star = self._detect_shooting_star_pattern(prices[-5:])
        if shooting_star:
            patterns.append(PatternSignal(
                pattern_type='shooting_star',
                confidence=shooting_star['confidence'],
                direction='bearish',
                strength=shooting_star['strength'],
                timestamp=timestamps[-1],
                metadata=shooting_star
            ))
        
        return patterns
    
    def _detect_volume_patterns(self, prices: List[float], 
                              volumes: List[int], 
                              timestamps: List[datetime]) -> List[PatternSignal]:
        """出来高パターン検出"""
        patterns = []
        
        if len(volumes) < 20:
            return patterns
        
        # 出来高スパイク
        recent_volume = volumes[-1]
        avg_volume = np.mean(volumes[-20:])
        
        if recent_volume > avg_volume * 3:
            price_change = prices[-1] - prices[-2] if len(prices) > 1 else 0
            direction = 'bullish' if price_change > 0 else 'bearish'
            
            patterns.append(PatternSignal(
                pattern_type='volume_spike',
                confidence=0.9,
                direction=direction,
                strength=recent_volume / avg_volume,
                timestamp=timestamps[-1],
                metadata={
                    'volume_ratio': recent_volume / avg_volume,
                    'price_change': price_change
                }
            ))
        
        return patterns
    
    def _detect_volatility_patterns(self, prices: List[float], 
                                  timestamps: List[datetime]) -> List[PatternSignal]:
        """ボラティリティパターン検出"""
        patterns = []
        
        if len(prices) < 30:
            return patterns
        
        # ボラティリティクラスタリング
        recent_volatility = np.std(prices[-10:])
        earlier_volatility = np.std(prices[-30:-10])
        
        if recent_volatility > earlier_volatility * 2:
            patterns.append(PatternSignal(
                pattern_type='volatility_expansion',
                confidence=0.8,
                direction='neutral',
                strength=recent_volatility / earlier_volatility,
                timestamp=timestamps[-1],
                metadata={
                    'volatility_ratio': recent_volatility / earlier_volatility,
                    'current_volatility': recent_volatility
                }
            ))
        
        return patterns
    
    def _find_peaks_valleys(self, prices: List[float]) -> Tuple[List[int], List[int]]:
        """ピークとバレーを検出"""
        from scipy.signal import find_peaks
        
        prices_array = np.array(prices)
        
        # ピーク検出
        peaks, _ = find_peaks(prices_array, distance=5, prominence=np.std(prices_array) * 0.5)
        
        # バレー検出
        valleys, _ = find_peaks(-prices_array, distance=5, prominence=np.std(prices_array) * 0.5)
        
        return peaks.tolist(), valleys.tolist()
    
    def _find_cluster_levels(self, prices: List[float], 
                           peaks: List[int], 
                           level_type: str) -> List[Tuple[float, float]]:
        """クラスタレベルを検出"""
        if not peaks:
            return []
        
        # ピーク周辺の価格を取得
        peak_prices = [prices[i] for i in peaks]
        
        # クラスタリング（簡易版）
        clusters = []
        tolerance = np.std(peak_prices) * 0.1
        
        for price in peak_prices:
            found_cluster = False
            for cluster in clusters:
                if abs(price - cluster[0]) <= tolerance:
                    cluster[0] = (cluster[0] + price) / 2  # 平均を更新
                    cluster[1] += 1  # カウントを増加
                    found_cluster = True
                    break
            
            if not found_cluster:
                clusters.append([price, 1])
        
        # 信頼度を計算
        levels = []
        for cluster_price, count in clusters:
            confidence = min(1.0, count / len(peak_prices))
            if confidence > 0.3:  # 閾値
                levels.append((cluster_price, confidence))
        
        return levels
    
    def _detect_hammer_pattern(self, prices: List[float]) -> Optional[Dict[str, Any]]:
        """ハンマーパターン検出"""
        if len(prices) < 5:
            return None
        
        # 簡易的なハンマー検出
        open_price = prices[0]
        close_price = prices[-1]
        high_price = max(prices)
        low_price = min(prices)
        
        body_size = abs(close_price - open_price)
        lower_shadow = min(open_price, close_price) - low_price
        upper_shadow = high_price - max(open_price, close_price)
        
        if lower_shadow > body_size * 2 and upper_shadow < body_size * 0.5:
            return {
                'confidence': 0.8,
                'strength': lower_shadow / body_size,
                'body_size': body_size,
                'lower_shadow': lower_shadow,
                'upper_shadow': upper_shadow
            }
        
        return None
    
    def _detect_shooting_star_pattern(self, prices: List[float]) -> Optional[Dict[str, Any]]:
        """シューティングスターパターン検出"""
        if len(prices) < 5:
            return None
        
        open_price = prices[0]
        close_price = prices[-1]
        high_price = max(prices)
        low_price = min(prices)
        
        body_size = abs(close_price - open_price)
        lower_shadow = min(open_price, close_price) - low_price
        upper_shadow = high_price - max(open_price, close_price)
        
        if upper_shadow > body_size * 2 and lower_shadow < body_size * 0.5:
            return {
                'confidence': 0.8,
                'strength': upper_shadow / body_size,
                'body_size': body_size,
                'lower_shadow': lower_shadow,
                'upper_shadow': upper_shadow
            }
        
        return None

class IntelligentAlertEngine:
    """インテリジェントアラートエンジン"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_rules = {}
        self.alert_history = deque(maxlen=1000)
        
    def add_alert_rule(self, rule_id: str, rule: Dict[str, Any]):
        """アラートルールを追加"""
        self.alert_rules[rule_id] = rule
    
    def generate_alerts(self, symbol: str, patterns: List[PatternSignal], 
                       data_stats: Dict[str, Any]) -> List[AlertSignal]:
        """アラートを生成"""
        alerts = []
        
        # パターンベースのアラート
        for pattern in patterns:
            alert = self._create_pattern_alert(symbol, pattern)
            if alert:
                alerts.append(alert)
        
        # 統計ベースのアラート
        stats_alerts = self._create_stats_alerts(symbol, data_stats)
        alerts.extend(stats_alerts)
        
        # ルールベースのアラート
        rule_alerts = self._evaluate_alert_rules(symbol, data_stats, patterns)
        alerts.extend(rule_alerts)
        
        # アラート履歴に追加
        for alert in alerts:
            self.alert_history.append(alert)
        
        return alerts
    
    def _create_pattern_alert(self, symbol: str, pattern: PatternSignal) -> Optional[AlertSignal]:
        """パターンベースのアラートを作成"""
        severity_map = {
            'breakout': 'high',
            'volume_spike': 'medium',
            'volatility_expansion': 'medium',
            'support_level': 'low',
            'resistance_level': 'low',
            'hammer': 'medium',
            'shooting_star': 'medium'
        }
        
        severity = severity_map.get(pattern.pattern_type, 'low')
        
        if pattern.confidence > 0.7:
            return AlertSignal(
                alert_id=f"{symbol}_{pattern.pattern_type}_{int(time.time())}",
                symbol=symbol,
                alert_type=pattern.pattern_type,
                severity=severity,
                message=f"{symbol}: {pattern.pattern_type} detected (confidence: {pattern.confidence:.2f})",
                timestamp=pattern.timestamp,
                data=pattern.metadata,
                action_required=severity in ['high', 'critical']
            )
        
        return None
    
    def _create_stats_alerts(self, symbol: str, stats: Dict[str, Any]) -> List[AlertSignal]:
        """統計ベースのアラートを作成"""
        alerts = []
        
        # 価格変動アラート
        if abs(stats.get('price_change_pct', 0)) > 5:
            severity = 'high' if abs(stats['price_change_pct']) > 10 else 'medium'
            alerts.append(AlertSignal(
                alert_id=f"{symbol}_price_change_{int(time.time())}",
                symbol=symbol,
                alert_type='price_change',
                severity=severity,
                message=f"{symbol}: Significant price change ({stats['price_change_pct']:.2f}%)",
                timestamp=datetime.now(),
                data=stats,
                action_required=severity == 'high'
            ))
        
        # ボラティリティアラート
        if stats.get('volatility', 0) > 2.0:
            alerts.append(AlertSignal(
                alert_id=f"{symbol}_volatility_{int(time.time())}",
                symbol=symbol,
                alert_type='high_volatility',
                severity='medium',
                message=f"{symbol}: High volatility detected ({stats['volatility']:.2f})",
                timestamp=datetime.now(),
                data=stats,
                action_required=False
            ))
        
        return alerts
    
    def _evaluate_alert_rules(self, symbol: str, stats: Dict[str, Any], 
                            patterns: List[PatternSignal]) -> List[AlertSignal]:
        """アラートルールを評価"""
        alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if rule.get('symbol') != symbol and rule.get('symbol') != '*':
                continue
            
            if self._evaluate_rule_condition(rule, stats, patterns):
                alerts.append(AlertSignal(
                    alert_id=f"{symbol}_{rule_id}_{int(time.time())}",
                    symbol=symbol,
                    alert_type=rule.get('type', 'custom'),
                    severity=rule.get('severity', 'medium'),
                    message=rule.get('message', f"Custom rule triggered: {rule_id}"),
                    timestamp=datetime.now(),
                    data={'rule_id': rule_id, 'stats': stats, 'patterns': [p.pattern_type for p in patterns]},
                    action_required=rule.get('action_required', False)
                ))
        
        return alerts
    
    def _evaluate_rule_condition(self, rule: Dict[str, Any], 
                               stats: Dict[str, Any], 
                               patterns: List[PatternSignal]) -> bool:
        """ルール条件を評価"""
        condition = rule.get('condition', {})
        
        # 価格条件
        if 'price_change_pct' in condition:
            threshold = condition['price_change_pct']
            if not (threshold[0] <= stats.get('price_change_pct', 0) <= threshold[1]):
                return False
        
        # ボラティリティ条件
        if 'volatility' in condition:
            threshold = condition['volatility']
            if stats.get('volatility', 0) < threshold:
                return False
        
        # パターン条件
        if 'patterns' in condition:
            required_patterns = condition['patterns']
            detected_patterns = [p.pattern_type for p in patterns]
            if not any(pattern in detected_patterns for pattern in required_patterns):
                return False
        
        return True

class EnhancedRealtimeAnalysisEngine:
    """強化されたリアルタイム分析エンジン"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_processor = StreamingDataProcessor()
        self.pattern_detector = RealtimePatternDetector()
        self.alert_engine = IntelligentAlertEngine()
        
        self.active_symbols = set()
        self.analysis_results = {}
        self.websocket_connections = {}
        
        # スレッドプール
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # 分析ループの制御
        self.running = False
        self.analysis_thread = None
        
    def start_analysis(self, symbols: List[str]):
        """分析を開始"""
        self.active_symbols.update(symbols)
        self.running = True
        
        if self.analysis_thread is None or not self.analysis_thread.is_alive():
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.start()
        
        self.logger.info(f"リアルタイム分析開始: {symbols}")
    
    def stop_analysis(self):
        """分析を停止"""
        self.running = False
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5)
        
        self.logger.info("リアルタイム分析停止")
    
    def add_symbol(self, symbol: str):
        """シンボルを追加"""
        self.active_symbols.add(symbol)
        self.logger.info(f"シンボル追加: {symbol}")
    
    def remove_symbol(self, symbol: str):
        """シンボルを削除"""
        self.active_symbols.discard(symbol)
        if symbol in self.analysis_results:
            del self.analysis_results[symbol]
        self.logger.info(f"シンボル削除: {symbol}")
    
    def _analysis_loop(self):
        """分析ループ"""
        while self.running:
            try:
                for symbol in list(self.active_symbols):
                    self._analyze_symbol(symbol)
                
                time.sleep(1)  # 1秒間隔で分析
                
            except Exception as e:
                self.logger.error(f"分析ループエラー: {e}")
                time.sleep(5)
    
    def _analyze_symbol(self, symbol: str):
        """シンボルを分析"""
        try:
            # 最新データを取得
            latest_data = self._fetch_latest_data(symbol)
            if not latest_data:
                return
            
            # データをプロセッサーに追加
            self.data_processor.add_data(latest_data)
            
            # データ統計を計算
            data_stats = self.data_processor.process_data(symbol)
            
            # パターンを検出
            data_points = self.data_processor.get_latest_data(symbol, 100)
            patterns = self.pattern_detector.detect_patterns(symbol, data_points)
            
            # アラートを生成
            alerts = self.alert_engine.generate_alerts(symbol, patterns, data_stats)
            
            # 結果を保存
            self.analysis_results[symbol] = {
                'timestamp': datetime.now(),
                'data_stats': data_stats,
                'patterns': [asdict(p) for p in patterns],
                'alerts': [asdict(a) for a in alerts],
                'latest_data': asdict(latest_data)
            }
            
        except Exception as e:
            self.logger.error(f"シンボル分析エラー {symbol}: {e}")
    
    def _fetch_latest_data(self, symbol: str) -> Optional[StreamingData]:
        """最新データを取得"""
        try:
            # Yahoo Financeから最新データを取得
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            return StreamingData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=info.get('regularMarketPrice', 0),
                volume=info.get('regularMarketVolume', 0),
                bid=info.get('bid', None),
                ask=info.get('ask', None),
                high=info.get('dayHigh', None),
                low=info.get('dayLow', None),
                open_price=info.get('open', None)
            )
            
        except Exception as e:
            self.logger.error(f"データ取得エラー {symbol}: {e}")
            return None
    
    def get_analysis_results(self, symbol: str) -> Optional[Dict[str, Any]]:
        """分析結果を取得"""
        return self.analysis_results.get(symbol)
    
    def get_all_results(self) -> Dict[str, Any]:
        """全分析結果を取得"""
        return self.analysis_results.copy()
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[AlertSignal]:
        """アクティブなアラートを取得"""
        alerts = []
        for result in self.analysis_results.values():
            for alert_data in result.get('alerts', []):
                alert = AlertSignal(**alert_data)
                if severity is None or alert.severity == severity:
                    alerts.append(alert)
        
        return alerts
    
    def add_custom_alert_rule(self, rule_id: str, rule: Dict[str, Any]):
        """カスタムアラートルールを追加"""
        self.alert_engine.add_alert_rule(rule_id, rule)
        self.logger.info(f"カスタムアラートルール追加: {rule_id}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクスを取得"""
        return {
            'active_symbols': len(self.active_symbols),
            'total_alerts': len(self.alert_engine.alert_history),
            'analysis_results_count': len(self.analysis_results),
            'running': self.running,
            'timestamp': datetime.now()
        }

# グローバルインスタンス
enhanced_realtime_engine = EnhancedRealtimeAnalysisEngine()
