import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class TrendAnalyzer:
    """トレンド分析の精度向上を行うクラス"""
    
    def __init__(self):
        pass
    
    def analyze_multiple_timeframes(self, stock_data: Dict) -> Dict:
        """複数時間軸分析を実行"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 50:
                return None
            
            # 日足データから週足、月足を生成
            daily_data = data.copy()
            
            # 週足データ（5日移動平均）
            weekly_data = daily_data.resample('W').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            # 月足データ（20日移動平均）
            monthly_data = daily_data.resample('M').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            # 各時間軸のトレンド分析
            daily_trend = self._analyze_trend_strength(daily_data, 'daily')
            weekly_trend = self._analyze_trend_strength(weekly_data, 'weekly')
            monthly_trend = self._analyze_trend_strength(monthly_data, 'monthly')
            
            # 時間軸の整合性分析
            timeframe_consistency = self._analyze_timeframe_consistency(
                daily_trend, weekly_trend, monthly_trend
            )
            
            return {
                'daily_trend': daily_trend,
                'weekly_trend': weekly_trend,
                'monthly_trend': monthly_trend,
                'timeframe_consistency': timeframe_consistency,
                'overall_trend': self._determine_overall_trend(
                    daily_trend, weekly_trend, monthly_trend
                )
            }
            
        except Exception as e:
            print(f"複数時間軸分析エラー: {e}")
            return None
    
    def _analyze_trend_strength(self, data: pd.DataFrame, timeframe: str) -> Dict:
        """各時間軸のトレンド強度を分析"""
        try:
            if data.empty or len(data) < 10:
                return {'trend': 'neutral', 'strength': 0, 'direction': 'sideways'}
            
            close = data['Close']
            
            # 移動平均線
            ma_short = close.rolling(window=5).mean()
            ma_medium = close.rolling(window=20).mean()
            ma_long = close.rolling(window=50).mean()
            
            # 現在の値
            current_price = close.iloc[-1]
            current_ma_short = ma_short.iloc[-1]
            current_ma_medium = ma_medium.iloc[-1]
            current_ma_long = ma_long.iloc[-1]
            
            # トレンド方向判定
            if current_price > current_ma_short > current_ma_medium > current_ma_long:
                direction = 'uptrend'
                trend_desc = '上昇トレンド'
            elif current_price < current_ma_short < current_ma_medium < current_ma_long:
                direction = 'downtrend'
                trend_desc = '下降トレンド'
            else:
                direction = 'sideways'
                trend_desc = '横ばい'
            
            # トレンド強度計算
            strength = self._calculate_trend_strength(
                close, ma_short, ma_medium, ma_long, direction
            )
            
            # ボラティリティ分析
            volatility = self._calculate_volatility(close)
            
            return {
                'trend': direction,
                'trend_description': trend_desc,
                'strength': strength,
                'strength_level': self._get_strength_level(strength),
                'volatility': volatility,
                'moving_averages': {
                    'short': current_ma_short,
                    'medium': current_ma_medium,
                    'long': current_ma_long
                },
                'price_position': self._get_price_position(
                    current_price, current_ma_short, current_ma_medium, current_ma_long
                )
            }
            
        except Exception as e:
            print(f"トレンド強度分析エラー ({timeframe}): {e}")
            return {'trend': 'neutral', 'strength': 0, 'direction': 'sideways'}
    
    def _calculate_trend_strength(self, close: pd.Series, ma_short: pd.Series, 
                                ma_medium: pd.Series, ma_long: pd.Series, direction: str) -> float:
        """トレンド強度を計算"""
        try:
            # 移動平均線の傾き
            ma_short_slope = ma_short.pct_change().tail(5).mean() * 100
            ma_medium_slope = ma_medium.pct_change().tail(10).mean() * 100
            ma_long_slope = ma_long.pct_change().tail(20).mean() * 100
            
            # 価格の移動平均線からの乖離
            price_deviation = abs(close.iloc[-1] - ma_medium.iloc[-1]) / ma_medium.iloc[-1] * 100
            
            # トレンドの一貫性
            if direction == 'uptrend':
                consistency = 1 if ma_short_slope > 0 and ma_medium_slope > 0 else 0.5
            elif direction == 'downtrend':
                consistency = 1 if ma_short_slope < 0 and ma_medium_slope < 0 else 0.5
            else:
                consistency = 0.3
            
            # 総合強度スコア
            strength = (abs(ma_short_slope) * 0.4 + 
                       abs(ma_medium_slope) * 0.3 + 
                       abs(ma_long_slope) * 0.2 + 
                       price_deviation * 0.1) * consistency
            
            return min(100, max(0, strength * 10))
            
        except Exception as e:
            print(f"トレンド強度計算エラー: {e}")
            return 0
    
    def _calculate_volatility(self, prices: pd.Series) -> Dict:
        """ボラティリティを計算"""
        try:
            # 日次リターン
            returns = prices.pct_change().dropna()
            
            # ボラティリティ指標
            daily_volatility = returns.std() * 100
            annualized_volatility = daily_volatility * np.sqrt(252)
            
            # ボラティリティレベル
            if annualized_volatility > 30:
                vol_level = 'high'
                vol_desc = '高ボラティリティ'
            elif annualized_volatility > 15:
                vol_level = 'medium'
                vol_desc = '中ボラティリティ'
            else:
                vol_level = 'low'
                vol_desc = '低ボラティリティ'
            
            return {
                'daily_volatility': daily_volatility,
                'annualized_volatility': annualized_volatility,
                'level': vol_level,
                'description': vol_desc
            }
            
        except Exception as e:
            print(f"ボラティリティ計算エラー: {e}")
            return {'daily_volatility': 0, 'annualized_volatility': 0, 'level': 'unknown', 'description': '不明'}
    
    def _get_strength_level(self, strength: float) -> str:
        """強度レベルを取得"""
        if strength >= 70:
            return 'very_strong'
        elif strength >= 50:
            return 'strong'
        elif strength >= 30:
            return 'moderate'
        elif strength >= 15:
            return 'weak'
        else:
            return 'very_weak'
    
    def _get_price_position(self, price: float, ma_short: float, ma_medium: float, ma_long: float) -> str:
        """価格の位置を取得"""
        if price > ma_short > ma_medium > ma_long:
            return 'above_all_ma'
        elif price < ma_short < ma_medium < ma_long:
            return 'below_all_ma'
        elif price > ma_short and price > ma_medium:
            return 'above_short_medium'
        elif price < ma_short and price < ma_medium:
            return 'below_short_medium'
        else:
            return 'mixed'
    
    def _analyze_timeframe_consistency(self, daily_trend: Dict, weekly_trend: Dict, monthly_trend: Dict) -> Dict:
        """時間軸の整合性を分析"""
        try:
            trends = [daily_trend.get('trend', 'neutral'), 
                     weekly_trend.get('trend', 'neutral'), 
                     monthly_trend.get('trend', 'neutral')]
            
            # 整合性スコア計算
            if all(trend == 'uptrend' for trend in trends):
                consistency_score = 100
                consistency_level = 'perfect_bullish'
                consistency_desc = '全時間軸で上昇トレンド'
            elif all(trend == 'downtrend' for trend in trends):
                consistency_score = 100
                consistency_level = 'perfect_bearish'
                consistency_desc = '全時間軸で下降トレンド'
            elif trends.count('uptrend') >= 2:
                consistency_score = 70
                consistency_level = 'mostly_bullish'
                consistency_desc = '主に上昇トレンド'
            elif trends.count('downtrend') >= 2:
                consistency_score = 70
                consistency_level = 'mostly_bearish'
                consistency_desc = '主に下降トレンド'
            elif trends.count('sideways') >= 2:
                consistency_score = 50
                consistency_level = 'mostly_sideways'
                consistency_desc = '主に横ばい'
            else:
                consistency_score = 30
                consistency_level = 'mixed'
                consistency_desc = '時間軸でトレンドが混在'
            
            return {
                'score': consistency_score,
                'level': consistency_level,
                'description': consistency_desc,
                'trends': {
                    'daily': daily_trend.get('trend', 'neutral'),
                    'weekly': weekly_trend.get('trend', 'neutral'),
                    'monthly': monthly_trend.get('trend', 'neutral')
                }
            }
            
        except Exception as e:
            print(f"時間軸整合性分析エラー: {e}")
            return {'score': 0, 'level': 'unknown', 'description': '分析不可'}
    
    def _determine_overall_trend(self, daily_trend: Dict, weekly_trend: Dict, monthly_trend: Dict) -> Dict:
        """総合トレンドを決定"""
        try:
            # 重み付きスコア計算（長期トレンドを重視）
            weights = {'daily': 0.2, 'weekly': 0.3, 'monthly': 0.5}
            
            trend_scores = {
                'uptrend': 0,
                'downtrend': 0,
                'sideways': 0
            }
            
            for timeframe, weight in weights.items():
                if timeframe == 'daily':
                    trend = daily_trend.get('trend', 'neutral')
                elif timeframe == 'weekly':
                    trend = weekly_trend.get('trend', 'neutral')
                else:
                    trend = monthly_trend.get('trend', 'neutral')
                
                if trend == 'uptrend':
                    trend_scores['uptrend'] += weight * 100
                elif trend == 'downtrend':
                    trend_scores['downtrend'] += weight * 100
                else:
                    trend_scores['sideways'] += weight * 100
            
            # 最も高いスコアのトレンドを選択
            dominant_trend = max(trend_scores, key=trend_scores.get)
            confidence = trend_scores[dominant_trend]
            
            # トレンド強度
            avg_strength = (daily_trend.get('strength', 0) * 0.2 + 
                           weekly_trend.get('strength', 0) * 0.3 + 
                           monthly_trend.get('strength', 0) * 0.5)
            
            return {
                'trend': dominant_trend,
                'confidence': confidence,
                'strength': avg_strength,
                'description': self._get_trend_description(dominant_trend, confidence, avg_strength)
            }
            
        except Exception as e:
            print(f"総合トレンド決定エラー: {e}")
            return {'trend': 'neutral', 'confidence': 0, 'strength': 0, 'description': '分析不可'}
    
    def _get_trend_description(self, trend: str, confidence: float, strength: float) -> str:
        """トレンドの説明を取得"""
        if trend == 'uptrend':
            if confidence >= 80 and strength >= 60:
                return '強い上昇トレンド'
            elif confidence >= 60:
                return '上昇トレンド'
            else:
                return 'やや上昇傾向'
        elif trend == 'downtrend':
            if confidence >= 80 and strength >= 60:
                return '強い下降トレンド'
            elif confidence >= 60:
                return '下降トレンド'
            else:
                return 'やや下降傾向'
        else:
            return '横ばいトレンド'
    
    def analyze_breakout_patterns(self, stock_data: Dict) -> Dict:
        """ブレイクアウトパターンを分析"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 50:
                return None
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            # 過去の高値・安値を計算
            recent_high = high.tail(20).max()
            recent_low = low.tail(20).min()
            current_price = close.iloc[-1]
            current_volume = volume.iloc[-1]
            avg_volume = volume.tail(20).mean()
            
            # ブレイクアウト判定
            breakout_signals = []
            
            # 高値ブレイクアウト
            if current_price > recent_high * 1.02:  # 2%以上上抜け
                if current_volume > avg_volume * 1.5:  # 出来高も増加
                    breakout_signals.append({
                        'type': 'bullish_breakout',
                        'description': '高値ブレイクアウト（強気）',
                        'strength': 'strong' if current_volume > avg_volume * 2 else 'moderate'
                    })
            
            # 安値ブレイクアウト
            if current_price < recent_low * 0.98:  # 2%以上下抜け
                if current_volume > avg_volume * 1.5:  # 出来高も増加
                    breakout_signals.append({
                        'type': 'bearish_breakout',
                        'description': '安値ブレイクアウト（弱気）',
                        'strength': 'strong' if current_volume > avg_volume * 2 else 'moderate'
                    })
            
            # ボラティリティブレイクアウト
            atr = self._calculate_atr(high, low, close)
            if atr.iloc[-1] > atr.tail(20).mean() * 1.5:
                breakout_signals.append({
                    'type': 'volatility_breakout',
                    'description': 'ボラティリティブレイクアウト',
                    'strength': 'moderate'
                })
            
            return {
                'breakout_signals': breakout_signals,
                'recent_high': recent_high,
                'recent_low': recent_low,
                'current_price': current_price,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1,
                'breakout_potential': self._assess_breakout_potential(close, high, low, volume)
            }
            
        except Exception as e:
            print(f"ブレイクアウトパターン分析エラー: {e}")
            return None
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """ATRを計算"""
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
    
    def _assess_breakout_potential(self, close: pd.Series, high: pd.Series, low: pd.Series, volume: pd.Series) -> Dict:
        """ブレイクアウトの可能性を評価"""
        try:
            # 価格の圧縮状況
            recent_range = (high.tail(10).max() - low.tail(10).min()) / close.tail(10).mean()
            
            # 出来高の変化
            volume_trend = volume.tail(5).mean() / volume.tail(20).mean()
            
            # ブレイクアウト可能性
            if recent_range < 0.05 and volume_trend > 1.2:  # 価格圧縮 + 出来高増加
                potential = 'high'
                potential_desc = '高（価格圧縮中、出来高増加）'
            elif recent_range < 0.08 and volume_trend > 1.0:
                potential = 'medium'
                potential_desc = '中（価格圧縮中）'
            else:
                potential = 'low'
                potential_desc = '低（価格変動中）'
            
            return {
                'level': potential,
                'description': potential_desc,
                'price_compression': recent_range,
                'volume_trend': volume_trend
            }
            
        except Exception as e:
            print(f"ブレイクアウト可能性評価エラー: {e}")
            return {'level': 'unknown', 'description': '評価不可'}
    
    def comprehensive_trend_analysis(self, stock_data: Dict) -> Dict:
        """包括的なトレンド分析を実行"""
        try:
            # 各分析を実行
            multi_timeframe = self.analyze_multiple_timeframes(stock_data)
            breakout_patterns = self.analyze_breakout_patterns(stock_data)
            
            if not multi_timeframe:
                return None
            
            # 総合評価
            overall_trend = multi_timeframe['overall_trend']
            consistency = multi_timeframe['timeframe_consistency']
            
            # 投資推奨
            if (overall_trend['trend'] == 'uptrend' and 
                overall_trend['confidence'] >= 70 and 
                consistency['score'] >= 60):
                recommendation = 'strong_buy'
                recommendation_desc = '強く推奨（強い上昇トレンド）'
            elif (overall_trend['trend'] == 'uptrend' and 
                  overall_trend['confidence'] >= 50):
                recommendation = 'buy'
                recommendation_desc = '推奨（上昇トレンド）'
            elif (overall_trend['trend'] == 'downtrend' and 
                  overall_trend['confidence'] >= 70):
                recommendation = 'sell'
                recommendation_desc = '売り推奨（下降トレンド）'
            elif overall_trend['trend'] == 'sideways':
                recommendation = 'hold'
                recommendation_desc = '保有（横ばいトレンド）'
            else:
                recommendation = 'hold'
                recommendation_desc = '様子見（トレンド不明）'
            
            return {
                'overall_trend': overall_trend,
                'timeframe_consistency': consistency,
                'breakout_patterns': breakout_patterns,
                'recommendation': recommendation,
                'recommendation_description': recommendation_desc,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的トレンド分析エラー: {e}")
            return None
