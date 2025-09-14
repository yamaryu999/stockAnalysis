import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class AdvancedTechnicalAnalyzer:
    """高度な技術分析を行うクラス"""
    
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI（相対力指数）を計算"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            print(f"RSI計算エラー: {e}")
            return pd.Series(index=prices.index, dtype=float)
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD（移動平均収束発散）を計算"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
        except Exception as e:
            print(f"MACD計算エラー: {e}")
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict:
        """ボリンジャーバンドを計算"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            # バンドの位置（価格がどのバンドにいるか）
            band_position = (prices - lower_band) / (upper_band - lower_band)
            
            return {
                'upper': upper_band,
                'middle': sma,
                'lower': lower_band,
                'position': band_position
            }
        except Exception as e:
            print(f"ボリンジャーバンド計算エラー: {e}")
            return {'upper': pd.Series(), 'middle': pd.Series(), 'lower': pd.Series(), 'position': pd.Series()}
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict:
        """ストキャスティクスを計算"""
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return {
                'k_percent': k_percent,
                'd_percent': d_percent
            }
        except Exception as e:
            print(f"ストキャスティクス計算エラー: {e}")
            return {'k_percent': pd.Series(), 'd_percent': pd.Series()}
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Williams %Rを計算"""
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            return williams_r
        except Exception as e:
            print(f"Williams %R計算エラー: {e}")
            return pd.Series(index=close.index, dtype=float)
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """ATR（平均真の範囲）を計算"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            print(f"ATR計算エラー: {e}")
            return pd.Series(index=close.index, dtype=float)
    
    def analyze_technical_signals(self, stock_data: Dict) -> Dict:
        """技術分析シグナルを総合分析"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 50:
                return None
            
            # 各指標を計算
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            # RSI
            rsi = self.calculate_rsi(close)
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # MACD
            macd_data = self.calculate_macd(close)
            current_macd = macd_data['macd'].iloc[-1] if not macd_data['macd'].empty else 0
            current_signal = macd_data['signal'].iloc[-1] if not macd_data['signal'].empty else 0
            current_histogram = macd_data['histogram'].iloc[-1] if not macd_data['histogram'].empty else 0
            
            # ボリンジャーバンド
            bb_data = self.calculate_bollinger_bands(close)
            current_price = close.iloc[-1]
            bb_position = bb_data['position'].iloc[-1] if not bb_data['position'].empty else 0.5
            
            # ストキャスティクス
            stoch_data = self.calculate_stochastic(high, low, close)
            current_k = stoch_data['k_percent'].iloc[-1] if not stoch_data['k_percent'].empty else 50
            current_d = stoch_data['d_percent'].iloc[-1] if not stoch_data['d_percent'].empty else 50
            
            # Williams %R
            williams_r = self.calculate_williams_r(high, low, close)
            current_williams = williams_r.iloc[-1] if not williams_r.empty else -50
            
            # ATR
            atr = self.calculate_atr(high, low, close)
            current_atr = atr.iloc[-1] if not atr.empty else 0
            
            # シグナル分析
            signals = self._analyze_signals(
                current_rsi, current_macd, current_signal, current_histogram,
                bb_position, current_k, current_d, current_williams
            )
            
            # 総合スコア計算
            total_score = self._calculate_technical_score(signals)
            
            return {
                'rsi': {
                    'value': current_rsi,
                    'signal': signals['rsi_signal'],
                    'description': self._get_rsi_description(current_rsi)
                },
                'macd': {
                    'macd': current_macd,
                    'signal': current_signal,
                    'histogram': current_histogram,
                    'signal_type': signals['macd_signal'],
                    'description': self._get_macd_description(current_macd, current_signal, current_histogram)
                },
                'bollinger_bands': {
                    'position': bb_position,
                    'signal': signals['bb_signal'],
                    'description': self._get_bb_description(bb_position)
                },
                'stochastic': {
                    'k_percent': current_k,
                    'd_percent': current_d,
                    'signal': signals['stoch_signal'],
                    'description': self._get_stoch_description(current_k, current_d)
                },
                'williams_r': {
                    'value': current_williams,
                    'signal': signals['williams_signal'],
                    'description': self._get_williams_description(current_williams)
                },
                'atr': {
                    'value': current_atr,
                    'volatility': self._get_volatility_level(current_atr, current_price)
                },
                'overall_score': total_score,
                'overall_signal': self._get_overall_signal(total_score),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"技術分析シグナル分析エラー: {e}")
            return None
    
    def _analyze_signals(self, rsi, macd, signal, histogram, bb_pos, k, d, williams) -> Dict:
        """各指標のシグナルを分析"""
        signals = {}
        
        # RSIシグナル
        if rsi > 70:
            signals['rsi_signal'] = 'overbought'
        elif rsi < 30:
            signals['rsi_signal'] = 'oversold'
        else:
            signals['rsi_signal'] = 'neutral'
        
        # MACDシグナル
        if macd > signal and histogram > 0:
            signals['macd_signal'] = 'bullish'
        elif macd < signal and histogram < 0:
            signals['macd_signal'] = 'bearish'
        else:
            signals['macd_signal'] = 'neutral'
        
        # ボリンジャーバンドシグナル
        if bb_pos > 0.8:
            signals['bb_signal'] = 'overbought'
        elif bb_pos < 0.2:
            signals['bb_signal'] = 'oversold'
        else:
            signals['bb_signal'] = 'neutral'
        
        # ストキャスティクスシグナル
        if k > 80 and d > 80:
            signals['stoch_signal'] = 'overbought'
        elif k < 20 and d < 20:
            signals['stoch_signal'] = 'oversold'
        else:
            signals['stoch_signal'] = 'neutral'
        
        # Williams %Rシグナル
        if williams > -20:
            signals['williams_signal'] = 'overbought'
        elif williams < -80:
            signals['williams_signal'] = 'oversold'
        else:
            signals['williams_signal'] = 'neutral'
        
        return signals
    
    def _calculate_technical_score(self, signals: Dict) -> float:
        """技術分析総合スコアを計算"""
        score = 50  # ベーススコア
        
        # 各シグナルの重み付きスコア
        signal_weights = {
            'rsi_signal': 0.25,
            'macd_signal': 0.3,
            'bb_signal': 0.2,
            'stoch_signal': 0.15,
            'williams_signal': 0.1
        }
        
        for signal_name, weight in signal_weights.items():
            signal_value = signals.get(signal_name, 'neutral')
            
            if signal_value == 'bullish' or signal_value == 'oversold':
                score += 15 * weight
            elif signal_value == 'bearish' or signal_value == 'overbought':
                score -= 15 * weight
            # neutralの場合はスコア変更なし
        
        return max(0, min(100, score))
    
    def _get_rsi_description(self, rsi: float) -> str:
        """RSIの説明を取得"""
        if rsi > 70:
            return '買われすぎ（売りシグナル）'
        elif rsi < 30:
            return '売られすぎ（買いシグナル）'
        else:
            return '中立圏'
    
    def _get_macd_description(self, macd: float, signal: float, histogram: float) -> str:
        """MACDの説明を取得"""
        if macd > signal and histogram > 0:
            return '上昇トレンド継続'
        elif macd < signal and histogram < 0:
            return '下降トレンド継続'
        elif macd > signal and histogram < 0:
            return '上昇トレンド弱化'
        elif macd < signal and histogram > 0:
            return '下降トレンド弱化'
        else:
            return 'トレンド不明'
    
    def _get_bb_description(self, position: float) -> str:
        """ボリンジャーバンドの説明を取得"""
        if position > 0.8:
            return '上バンド付近（売りシグナル）'
        elif position < 0.2:
            return '下バンド付近（買いシグナル）'
        else:
            return '中央付近（中立）'
    
    def _get_stoch_description(self, k: float, d: float) -> str:
        """ストキャスティクスの説明を取得"""
        if k > 80 and d > 80:
            return '買われすぎ（売りシグナル）'
        elif k < 20 and d < 20:
            return '売られすぎ（買いシグナル）'
        else:
            return '中立圏'
    
    def _get_williams_description(self, williams: float) -> str:
        """Williams %Rの説明を取得"""
        if williams > -20:
            return '買われすぎ（売りシグナル）'
        elif williams < -80:
            return '売られすぎ（買いシグナル）'
        else:
            return '中立圏'
    
    def _get_volatility_level(self, atr: float, price: float) -> str:
        """ボラティリティレベルを取得"""
        if price > 0:
            volatility_ratio = atr / price
            if volatility_ratio > 0.03:
                return '高ボラティリティ'
            elif volatility_ratio > 0.015:
                return '中ボラティリティ'
            else:
                return '低ボラティリティ'
        return '不明'
    
    def _get_overall_signal(self, score: float) -> str:
        """総合シグナルを取得"""
        if score >= 70:
            return '強気'
        elif score >= 60:
            return 'やや強気'
        elif score >= 40:
            return '中立'
        elif score >= 30:
            return 'やや弱気'
        else:
            return '弱気'
    
    def calculate_support_resistance(self, stock_data: Dict) -> Dict:
        """サポート・レジスタンスレベルを計算"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 20:
                return None
            
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            # ピボットポイント計算
            current_high = high.iloc[-1]
            current_low = low.iloc[-1]
            current_close = close.iloc[-1]
            
            pivot = (current_high + current_low + current_close) / 3
            resistance1 = 2 * pivot - current_low
            support1 = 2 * pivot - current_high
            resistance2 = pivot + (current_high - current_low)
            support2 = pivot - (current_high - current_low)
            
            # 過去の高値・安値
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            
            # 現在価格の位置
            current_price = close.iloc[-1]
            price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
            
            return {
                'pivot_point': pivot,
                'resistance_levels': [resistance1, resistance2],
                'support_levels': [support1, support2],
                'recent_high': recent_high,
                'recent_low': recent_low,
                'current_price': current_price,
                'price_position': price_position,
                'trend_direction': self._get_trend_direction(current_price, pivot)
            }
            
        except Exception as e:
            print(f"サポート・レジスタンス計算エラー: {e}")
            return None
    
    def _get_trend_direction(self, current_price: float, pivot: float) -> str:
        """トレンド方向を判定"""
        if current_price > pivot * 1.02:
            return '上昇トレンド'
        elif current_price < pivot * 0.98:
            return '下降トレンド'
        else:
            return '横ばい'
    
    def comprehensive_technical_analysis(self, stock_data: Dict) -> Dict:
        """包括的な技術分析を実行"""
        try:
            # 各分析を実行
            technical_signals = self.analyze_technical_signals(stock_data)
            support_resistance = self.calculate_support_resistance(stock_data)
            
            if not technical_signals:
                return None
            
            # 総合評価
            overall_score = technical_signals['overall_score']
            overall_signal = technical_signals['overall_signal']
            
            # 投資推奨
            if overall_score >= 70:
                recommendation = 'strong_buy'
                recommendation_desc = '強く推奨（技術的に強気）'
            elif overall_score >= 60:
                recommendation = 'buy'
                recommendation_desc = '推奨（技術的にやや強気）'
            elif overall_score >= 40:
                recommendation = 'hold'
                recommendation_desc = '保有（技術的に中立）'
            elif overall_score >= 30:
                recommendation = 'weak_sell'
                recommendation_desc = '弱い売り（技術的にやや弱気）'
            else:
                recommendation = 'sell'
                recommendation_desc = '売り推奨（技術的に弱気）'
            
            return {
                'overall_score': overall_score,
                'overall_signal': overall_signal,
                'recommendation': recommendation,
                'recommendation_description': recommendation_desc,
                'technical_signals': technical_signals,
                'support_resistance': support_resistance,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的技術分析エラー: {e}")
            return None
