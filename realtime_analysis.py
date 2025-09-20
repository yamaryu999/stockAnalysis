"""
リアルタイム分析システム
ストリーミングデータのリアルタイム分析機能
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
import logging
from dataclasses import dataclass
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
from collections import deque
import json

@dataclass
class RealtimeAnalysisResult:
    """リアルタイム分析結果クラス"""
    symbol: str
    timestamp: datetime
    analysis_type: str
    result: Dict[str, Any]
    confidence: float
    signal: str  # 'buy', 'sell', 'hold'
    strength: float
    metadata: Dict[str, Any]

@dataclass
class StreamingData:
    """ストリーミングデータクラス"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None

class TechnicalIndicatorCalculator:
    """テクニカル指標計算クラス"""
    
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.logger = logging.getLogger(__name__)
    
    def calculate_rsi(self, prices: deque) -> float:
        """RSIを計算"""
        try:
            if len(prices) < 2:
                return 50.0
            
            prices_list = list(prices)
            deltas = [prices_list[i] - prices_list[i-1] for i in range(1, len(prices_list))]
            
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = sum(gains[-self.window_size:]) / min(len(gains), self.window_size)
            avg_loss = sum(losses[-self.window_size:]) / min(len(losses), self.window_size)
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            self.logger.error(f"RSI計算エラー: {e}")
            return 50.0
    
    def calculate_moving_average(self, prices: deque, period: int) -> float:
        """移動平均を計算"""
        try:
            if len(prices) < period:
                return prices[-1] if prices else 0.0
            
            return sum(list(prices)[-period:]) / period
            
        except Exception as e:
            self.logger.error(f"移動平均計算エラー: {e}")
            return 0.0
    
    def calculate_bollinger_bands(self, prices: deque, period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """ボリンジャーバンドを計算"""
        try:
            if len(prices) < period:
                price = prices[-1] if prices else 0.0
                return price, price, price
            
            prices_list = list(prices)[-period:]
            ma = sum(prices_list) / period
            variance = sum((p - ma) ** 2 for p in prices_list) / period
            std = np.sqrt(variance)
            
            upper = ma + (std * std_dev)
            lower = ma - (std * std_dev)
            
            return upper, ma, lower
            
        except Exception as e:
            self.logger.error(f"ボリンジャーバンド計算エラー: {e}")
            price = prices[-1] if prices else 0.0
            return price, price, price
    
    def calculate_macd(self, prices: deque, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """MACDを計算"""
        try:
            if len(prices) < slow:
                return 0.0, 0.0, 0.0
            
            prices_list = list(prices)
            
            # EMA計算
            def calculate_ema(data, period):
                if len(data) < period:
                    return data[-1] if data else 0.0
                
                multiplier = 2 / (period + 1)
                ema = data[0]
                
                for price in data[1:]:
                    ema = (price * multiplier) + (ema * (1 - multiplier))
                
                return ema
            
            ema_fast = calculate_ema(prices_list, fast)
            ema_slow = calculate_ema(prices_list, slow)
            macd_line = ema_fast - ema_slow
            
            # MACDシグナルライン（簡易版）
            macd_signal = macd_line * 0.9  # 簡易的なシグナルライン
            
            histogram = macd_line - macd_signal
            
            return macd_line, macd_signal, histogram
            
        except Exception as e:
            self.logger.error(f"MACD計算エラー: {e}")
            return 0.0, 0.0, 0.0
    
    def calculate_stochastic(self, highs: deque, lows: deque, closes: deque, k_period: int = 14) -> Tuple[float, float]:
        """ストキャスティクスを計算"""
        try:
            if len(highs) < k_period or len(lows) < k_period or len(closes) < k_period:
                return 50.0, 50.0
            
            highs_list = list(highs)[-k_period:]
            lows_list = list(lows)[-k_period:]
            closes_list = list(closes)[-k_period:]
            
            current_close = closes_list[-1]
            highest_high = max(highs_list)
            lowest_low = min(lows_list)
            
            if highest_high == lowest_low:
                return 50.0, 50.0
            
            k_percent = 100 * ((current_close - lowest_low) / (highest_high - lowest_low))
            
            # Dライン（簡易版）
            d_percent = k_percent * 0.8
            
            return k_percent, d_percent
            
        except Exception as e:
            self.logger.error(f"ストキャスティクス計算エラー: {e}")
            return 50.0, 50.0

class RealtimeAnalyzer:
    """リアルタイム分析クラス"""
    
    def __init__(self, symbol: str, analysis_interval: int = 5):
        self.symbol = symbol
        self.analysis_interval = analysis_interval
        self.logger = logging.getLogger(__name__)
        
        # データバッファ
        self.price_buffer = deque(maxlen=100)
        self.volume_buffer = deque(maxlen=100)
        self.high_buffer = deque(maxlen=100)
        self.low_buffer = deque(maxlen=100)
        
        # 分析結果
        self.latest_analysis = None
        self.analysis_history = deque(maxlen=50)
        
        # テクニカル指標計算器
        self.indicator_calculator = TechnicalIndicatorCalculator()
        
        # コールバック
        self.analysis_callbacks = []
        
        # 実行状態
        self.is_running = False
        self.analysis_thread = None
        
        # 分析設定
        self.analysis_config = {
            'rsi_enabled': True,
            'ma_enabled': True,
            'bollinger_enabled': True,
            'macd_enabled': True,
            'stochastic_enabled': True,
            'volume_analysis': True,
            'trend_analysis': True
        }
    
    def add_analysis_callback(self, callback: Callable[[RealtimeAnalysisResult], None]):
        """分析結果のコールバックを追加"""
        self.analysis_callbacks.append(callback)
    
    def update_data(self, data: StreamingData):
        """データを更新"""
        try:
            self.price_buffer.append(data.price)
            self.volume_buffer.append(data.volume)
            
            if data.high:
                self.high_buffer.append(data.high)
            if data.low:
                self.low_buffer.append(data.low)
            
            # バッファが十分に満たされたら分析を実行
            if len(self.price_buffer) >= 20:
                self._perform_analysis()
                
        except Exception as e:
            self.logger.error(f"データ更新エラー: {e}")
    
    def _perform_analysis(self):
        """分析を実行"""
        try:
            analysis_result = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'indicators': {},
                'signals': {},
                'trend': {},
                'volume': {}
            }
            
            # テクニカル指標を計算
            if self.analysis_config['rsi_enabled']:
                rsi = self.indicator_calculator.calculate_rsi(self.price_buffer)
                analysis_result['indicators']['rsi'] = rsi
                analysis_result['signals']['rsi'] = self._get_rsi_signal(rsi)
            
            if self.analysis_config['ma_enabled']:
                ma_5 = self.indicator_calculator.calculate_moving_average(self.price_buffer, 5)
                ma_20 = self.indicator_calculator.calculate_moving_average(self.price_buffer, 20)
                analysis_result['indicators']['ma_5'] = ma_5
                analysis_result['indicators']['ma_20'] = ma_20
                analysis_result['signals']['ma'] = self._get_ma_signal(ma_5, ma_20)
            
            if self.analysis_config['bollinger_enabled']:
                bb_upper, bb_middle, bb_lower = self.indicator_calculator.calculate_bollinger_bands(self.price_buffer)
                analysis_result['indicators']['bb_upper'] = bb_upper
                analysis_result['indicators']['bb_middle'] = bb_middle
                analysis_result['indicators']['bb_lower'] = bb_lower
                analysis_result['signals']['bollinger'] = self._get_bollinger_signal(
                    self.price_buffer[-1], bb_upper, bb_lower
                )
            
            if self.analysis_config['macd_enabled']:
                macd, macd_signal, macd_hist = self.indicator_calculator.calculate_macd(self.price_buffer)
                analysis_result['indicators']['macd'] = macd
                analysis_result['indicators']['macd_signal'] = macd_signal
                analysis_result['indicators']['macd_histogram'] = macd_hist
                analysis_result['signals']['macd'] = self._get_macd_signal(macd, macd_signal)
            
            if self.analysis_config['stochastic_enabled'] and self.high_buffer and self.low_buffer:
                stoch_k, stoch_d = self.indicator_calculator.calculate_stochastic(
                    self.high_buffer, self.low_buffer, self.price_buffer
                )
                analysis_result['indicators']['stoch_k'] = stoch_k
                analysis_result['indicators']['stoch_d'] = stoch_d
                analysis_result['signals']['stochastic'] = self._get_stochastic_signal(stoch_k, stoch_d)
            
            # ボリューム分析
            if self.analysis_config['volume_analysis']:
                volume_analysis = self._analyze_volume()
                analysis_result['volume'] = volume_analysis
            
            # トレンド分析
            if self.analysis_config['trend_analysis']:
                trend_analysis = self._analyze_trend()
                analysis_result['trend'] = trend_analysis
            
            # 総合シグナルを生成
            overall_signal = self._generate_overall_signal(analysis_result['signals'])
            analysis_result['overall_signal'] = overall_signal
            
            # 分析結果を作成
            result = RealtimeAnalysisResult(
                symbol=self.symbol,
                timestamp=analysis_result['timestamp'],
                analysis_type='realtime_technical',
                result=analysis_result,
                confidence=self._calculate_confidence(analysis_result),
                signal=overall_signal['signal'],
                strength=overall_signal['strength'],
                metadata={
                    'data_points': len(self.price_buffer),
                    'analysis_config': self.analysis_config
                }
            )
            
            # 結果を保存
            self.latest_analysis = result
            self.analysis_history.append(result)
            
            # コールバックを実行
            for callback in self.analysis_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"コールバック実行エラー: {e}")
            
        except Exception as e:
            self.logger.error(f"分析実行エラー: {e}")
    
    def _get_rsi_signal(self, rsi: float) -> Dict[str, Any]:
        """RSIシグナルを生成"""
        if rsi < 30:
            return {'signal': 'buy', 'strength': min(1.0, (30 - rsi) / 30), 'description': 'RSI過売り'}
        elif rsi > 70:
            return {'signal': 'sell', 'strength': min(1.0, (rsi - 70) / 30), 'description': 'RSI過買い'}
        else:
            return {'signal': 'hold', 'strength': 0.0, 'description': 'RSI中立'}
    
    def _get_ma_signal(self, ma_5: float, ma_20: float) -> Dict[str, Any]:
        """移動平均シグナルを生成"""
        current_price = self.price_buffer[-1]
        
        if current_price > ma_5 > ma_20:
            return {'signal': 'buy', 'strength': 0.7, 'description': '価格が移動平均を上回る'}
        elif current_price < ma_5 < ma_20:
            return {'signal': 'sell', 'strength': 0.7, 'description': '価格が移動平均を下回る'}
        else:
            return {'signal': 'hold', 'strength': 0.3, 'description': '移動平均中立'}
    
    def _get_bollinger_signal(self, price: float, upper: float, lower: float) -> Dict[str, Any]:
        """ボリンジャーバンドシグナルを生成"""
        if price <= lower:
            return {'signal': 'buy', 'strength': min(1.0, (lower - price) / lower), 'description': 'ボリンジャーバンド下限'}
        elif price >= upper:
            return {'signal': 'sell', 'strength': min(1.0, (price - upper) / upper), 'description': 'ボリンジャーバンド上限'}
        else:
            return {'signal': 'hold', 'strength': 0.0, 'description': 'ボリンジャーバンド内'}
    
    def _get_macd_signal(self, macd: float, macd_signal: float) -> Dict[str, Any]:
        """MACDシグナルを生成"""
        if macd > macd_signal:
            return {'signal': 'buy', 'strength': min(1.0, abs(macd - macd_signal) / abs(macd_signal) if macd_signal != 0 else 0), 'description': 'MACD上抜け'}
        else:
            return {'signal': 'sell', 'strength': min(1.0, abs(macd - macd_signal) / abs(macd_signal) if macd_signal != 0 else 0), 'description': 'MACD下抜け'}
    
    def _get_stochastic_signal(self, k: float, d: float) -> Dict[str, Any]:
        """ストキャスティクスシグナルを生成"""
        if k < 20 and d < 20:
            return {'signal': 'buy', 'strength': min(1.0, (20 - k) / 20), 'description': 'ストキャスティクス過売り'}
        elif k > 80 and d > 80:
            return {'signal': 'sell', 'strength': min(1.0, (k - 80) / 20), 'description': 'ストキャスティクス過買い'}
        else:
            return {'signal': 'hold', 'strength': 0.0, 'description': 'ストキャスティクス中立'}
    
    def _analyze_volume(self) -> Dict[str, Any]:
        """ボリューム分析"""
        try:
            if len(self.volume_buffer) < 10:
                return {'status': 'insufficient_data'}
            
            current_volume = self.volume_buffer[-1]
            avg_volume = sum(list(self.volume_buffer)[-10:]) / 10
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            return {
                'current_volume': current_volume,
                'average_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'status': 'high' if volume_ratio > 1.5 else 'low' if volume_ratio < 0.5 else 'normal'
            }
            
        except Exception as e:
            self.logger.error(f"ボリューム分析エラー: {e}")
            return {'status': 'error'}
    
    def _analyze_trend(self) -> Dict[str, Any]:
        """トレンド分析"""
        try:
            if len(self.price_buffer) < 20:
                return {'status': 'insufficient_data'}
            
            prices = list(self.price_buffer)[-20:]
            
            # 線形回帰でトレンドを計算
            x = np.arange(len(prices))
            y = np.array(prices)
            
            # 簡易的な線形回帰
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # トレンドの強さを計算
            trend_strength = abs(slope) / np.std(y) if np.std(y) > 0 else 0
            
            return {
                'slope': slope,
                'trend': 'up' if slope > 0 else 'down' if slope < 0 else 'sideways',
                'strength': min(1.0, trend_strength),
                'status': 'strong' if trend_strength > 0.5 else 'weak'
            }
            
        except Exception as e:
            self.logger.error(f"トレンド分析エラー: {e}")
            return {'status': 'error'}
    
    def _generate_overall_signal(self, signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """総合シグナルを生成"""
        try:
            buy_signals = []
            sell_signals = []
            hold_signals = []
            
            for signal_name, signal_data in signals.items():
                signal_type = signal_data['signal']
                strength = signal_data['strength']
                
                if signal_type == 'buy':
                    buy_signals.append(strength)
                elif signal_type == 'sell':
                    sell_signals.append(strength)
                else:
                    hold_signals.append(strength)
            
            # 重み付き平均で総合シグナルを決定
            buy_strength = sum(buy_signals) / len(buy_signals) if buy_signals else 0
            sell_strength = sum(sell_signals) / len(sell_signals) if sell_signals else 0
            
            if buy_strength > sell_strength and buy_strength > 0.3:
                return {'signal': 'buy', 'strength': buy_strength, 'description': '複数指標で買いシグナル'}
            elif sell_strength > buy_strength and sell_strength > 0.3:
                return {'signal': 'sell', 'strength': sell_strength, 'description': '複数指標で売りシグナル'}
            else:
                return {'signal': 'hold', 'strength': max(buy_strength, sell_strength), 'description': '中立'}
            
        except Exception as e:
            self.logger.error(f"総合シグナル生成エラー: {e}")
            return {'signal': 'hold', 'strength': 0.0, 'description': 'エラー'}
    
    def _calculate_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """分析の信頼度を計算"""
        try:
            confidence_factors = []
            
            # データポイント数による信頼度
            data_points = len(self.price_buffer)
            data_confidence = min(1.0, data_points / 50)
            confidence_factors.append(data_confidence)
            
            # シグナルの一貫性による信頼度
            signals = analysis_result.get('signals', {})
            if signals:
                signal_strengths = [signal.get('strength', 0) for signal in signals.values()]
                consistency = np.std(signal_strengths) if len(signal_strengths) > 1 else 0
                consistency_confidence = max(0, 1 - consistency)
                confidence_factors.append(consistency_confidence)
            
            # ボリューム分析による信頼度
            volume_analysis = analysis_result.get('volume', {})
            if volume_analysis.get('status') == 'normal':
                confidence_factors.append(0.8)
            elif volume_analysis.get('status') == 'high':
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.6)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
        except Exception as e:
            self.logger.error(f"信頼度計算エラー: {e}")
            return 0.5
    
    def get_latest_analysis(self) -> Optional[RealtimeAnalysisResult]:
        """最新の分析結果を取得"""
        return self.latest_analysis
    
    def get_analysis_history(self) -> List[RealtimeAnalysisResult]:
        """分析履歴を取得"""
        return list(self.analysis_history)
    
    def update_config(self, config: Dict[str, Any]):
        """分析設定を更新"""
        self.analysis_config.update(config)
        self.logger.info(f"分析設定を更新: {config}")

class RealtimeAnalysisManager:
    """リアルタイム分析管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzers: Dict[str, RealtimeAnalyzer] = {}
        self.data_queue = queue.Queue()
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # グローバルコールバック
        self.global_callbacks = []
    
    def add_symbol(self, symbol: str, analysis_interval: int = 5) -> bool:
        """分析対象銘柄を追加"""
        try:
            if symbol in self.analyzers:
                self.logger.warning(f"銘柄は既に分析中です: {symbol}")
                return False
            
            analyzer = RealtimeAnalyzer(symbol, analysis_interval)
            analyzer.add_analysis_callback(self._on_analysis_result)
            
            self.analyzers[symbol] = analyzer
            
            self.logger.info(f"分析対象銘柄を追加: {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"銘柄追加エラー: {e}")
            return False
    
    def remove_symbol(self, symbol: str) -> bool:
        """分析対象銘柄を削除"""
        try:
            if symbol in self.analyzers:
                del self.analyzers[symbol]
                self.logger.info(f"分析対象銘柄を削除: {symbol}")
                return True
            else:
                self.logger.warning(f"分析対象銘柄が見つかりません: {symbol}")
                return False
                
        except Exception as e:
            self.logger.error(f"銘柄削除エラー: {e}")
            return False
    
    def update_data(self, symbol: str, data: StreamingData):
        """データを更新"""
        try:
            if symbol in self.analyzers:
                self.analyzers[symbol].update_data(data)
            else:
                self.logger.warning(f"分析対象銘柄が見つかりません: {symbol}")
                
        except Exception as e:
            self.logger.error(f"データ更新エラー: {e}")
    
    def get_analysis_result(self, symbol: str) -> Optional[RealtimeAnalysisResult]:
        """分析結果を取得"""
        try:
            if symbol in self.analyzers:
                return self.analyzers[symbol].get_latest_analysis()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"分析結果取得エラー: {e}")
            return None
    
    def get_all_analysis_results(self) -> Dict[str, RealtimeAnalysisResult]:
        """全銘柄の分析結果を取得"""
        try:
            results = {}
            for symbol, analyzer in self.analyzers.items():
                result = analyzer.get_latest_analysis()
                if result:
                    results[symbol] = result
            
            return results
            
        except Exception as e:
            self.logger.error(f"全分析結果取得エラー: {e}")
            return {}
    
    def add_global_callback(self, callback: Callable[[RealtimeAnalysisResult], None]):
        """グローバルコールバックを追加"""
        self.global_callbacks.append(callback)
    
    def _on_analysis_result(self, result: RealtimeAnalysisResult):
        """分析結果のコールバック"""
        try:
            for callback in self.global_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"グローバルコールバック実行エラー: {e}")
                    
        except Exception as e:
            self.logger.error(f"分析結果コールバックエラー: {e}")
    
    def update_analyzer_config(self, symbol: str, config: Dict[str, Any]) -> bool:
        """分析設定を更新"""
        try:
            if symbol in self.analyzers:
                self.analyzers[symbol].update_config(config)
                self.logger.info(f"分析設定を更新: {symbol}")
                return True
            else:
                self.logger.warning(f"分析対象銘柄が見つかりません: {symbol}")
                return False
                
        except Exception as e:
            self.logger.error(f"分析設定更新エラー: {e}")
            return False
    
    def get_manager_status(self) -> Dict[str, Any]:
        """管理システムの状態を取得"""
        try:
            return {
                'total_symbols': len(self.analyzers),
                'symbols': list(self.analyzers.keys()),
                'is_running': self.is_running,
                'global_callbacks': len(self.global_callbacks)
            }
            
        except Exception as e:
            self.logger.error(f"状態取得エラー: {e}")
            return {}

# グローバルインスタンス
realtime_analysis_manager = RealtimeAnalysisManager()