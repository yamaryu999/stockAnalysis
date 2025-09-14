import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class TradingSignalAnalyzer:
    """トレーディングシグナル分析に特化したアナライザー"""
    
    def __init__(self):
        self.signal_weights = {
            'technical': 0.4,
            'momentum': 0.3,
            'volume': 0.2,
            'volatility': 0.1
        }
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """技術指標を計算"""
        df = data.copy()
        
        # 移動平均
        df['MA_5'] = df['Close'].rolling(window=5).mean()
        df['MA_10'] = df['Close'].rolling(window=10).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # ボリンジャーバンド
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # ストキャスティクス
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
        df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
        
        # ウィリアムズ%R
        df['Williams_R'] = -100 * ((high_14 - df['Close']) / (high_14 - low_14))
        
        return df
    
    def _generate_technical_signals(self, df: pd.DataFrame) -> Dict:
        """技術分析シグナルを生成"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'neutral_signals': []
        }
        
        latest = df.iloc[-1]
        
        # 移動平均クロスオーバー
        if latest['MA_5'] > latest['MA_10'] > latest['MA_20']:
            signals['buy_signals'].append({
                'type': 'MA_Cross',
                'strength': 0.7,
                'description': '短期移動平均が中期移動平均を上抜け'
            })
        elif latest['MA_5'] < latest['MA_10'] < latest['MA_20']:
            signals['sell_signals'].append({
                'type': 'MA_Cross',
                'strength': 0.7,
                'description': '短期移動平均が中期移動平均を下抜け'
            })
        
        # RSIシグナル
        if latest['RSI'] < 30:
            signals['buy_signals'].append({
                'type': 'RSI_Oversold',
                'strength': 0.8,
                'description': f'RSIが売られすぎ圏 ({latest["RSI"]:.1f})'
            })
        elif latest['RSI'] > 70:
            signals['sell_signals'].append({
                'type': 'RSI_Overbought',
                'strength': 0.8,
                'description': f'RSIが買われすぎ圏 ({latest["RSI"]:.1f})'
            })
        
        # MACDシグナル
        if latest['MACD'] > latest['MACD_Signal'] and df.iloc[-2]['MACD'] <= df.iloc[-2]['MACD_Signal']:
            signals['buy_signals'].append({
                'type': 'MACD_Bullish',
                'strength': 0.6,
                'description': 'MACDがシグナル線を上抜け'
            })
        elif latest['MACD'] < latest['MACD_Signal'] and df.iloc[-2]['MACD'] >= df.iloc[-2]['MACD_Signal']:
            signals['sell_signals'].append({
                'type': 'MACD_Bearish',
                'strength': 0.6,
                'description': 'MACDがシグナル線を下抜け'
            })
        
        # ボリンジャーバンドシグナル
        if latest['Close'] <= latest['BB_Lower']:
            signals['buy_signals'].append({
                'type': 'BB_Oversold',
                'strength': 0.5,
                'description': '価格がボリンジャーバンド下限にタッチ'
            })
        elif latest['Close'] >= latest['BB_Upper']:
            signals['sell_signals'].append({
                'type': 'BB_Overbought',
                'strength': 0.5,
                'description': '価格がボリンジャーバンド上限にタッチ'
            })
        
        # ストキャスティクスシグナル
        if latest['Stoch_K'] < 20 and latest['Stoch_D'] < 20:
            signals['buy_signals'].append({
                'type': 'Stoch_Oversold',
                'strength': 0.6,
                'description': 'ストキャスティクスが売られすぎ圏'
            })
        elif latest['Stoch_K'] > 80 and latest['Stoch_D'] > 80:
            signals['sell_signals'].append({
                'type': 'Stoch_Overbought',
                'strength': 0.6,
                'description': 'ストキャスティクスが買われすぎ圏'
            })
        
        return signals
    
    def _generate_momentum_signals(self, df: pd.DataFrame) -> Dict:
        """モメンタムシグナルを生成"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'neutral_signals': []
        }
        
        latest = df.iloc[-1]
        
        # 価格モメンタム
        price_change_5d = (latest['Close'] / df.iloc[-6]['Close'] - 1) * 100
        price_change_10d = (latest['Close'] / df.iloc[-11]['Close'] - 1) * 100
        
        if price_change_5d > 5 and price_change_10d > 10:
            signals['buy_signals'].append({
                'type': 'Strong_Momentum',
                'strength': 0.8,
                'description': f'強い上昇モメンタム (5日: +{price_change_5d:.1f}%, 10日: +{price_change_10d:.1f}%)'
            })
        elif price_change_5d < -5 and price_change_10d < -10:
            signals['sell_signals'].append({
                'type': 'Strong_Downward_Momentum',
                'strength': 0.8,
                'description': f'強い下落モメンタム (5日: {price_change_5d:.1f}%, 10日: {price_change_10d:.1f}%)'
            })
        
        # ボラティリティブレイクアウト
        volatility_20d = df['Close'].pct_change().rolling(window=20).std().iloc[-1]
        if volatility_20d > df['Close'].pct_change().rolling(window=20).std().mean() * 1.5:
            if price_change_5d > 0:
                signals['buy_signals'].append({
                    'type': 'Volatility_Breakout_Up',
                    'strength': 0.6,
                    'description': '上向きボラティリティブレイクアウト'
                })
            else:
                signals['sell_signals'].append({
                    'type': 'Volatility_Breakout_Down',
                    'strength': 0.6,
                    'description': '下向きボラティリティブレイクアウト'
                })
        
        return signals
    
    def _generate_volume_signals(self, df: pd.DataFrame) -> Dict:
        """出来高シグナルを生成"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'neutral_signals': []
        }
        
        latest = df.iloc[-1]
        
        # 出来高移動平均
        volume_ma_20 = df['Volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = latest['Volume'] / volume_ma_20
        
        # 価格変動と出来高の関係
        price_change = (latest['Close'] / df.iloc[-2]['Close'] - 1) * 100
        
        if volume_ratio > 2.0 and price_change > 2:
            signals['buy_signals'].append({
                'type': 'Volume_Price_Breakout',
                'strength': 0.9,
                'description': f'出来高急増と価格上昇 (出来高比: {volume_ratio:.1f}x, 価格変動: +{price_change:.1f}%)'
            })
        elif volume_ratio > 2.0 and price_change < -2:
            signals['sell_signals'].append({
                'type': 'Volume_Price_Breakdown',
                'strength': 0.9,
                'description': f'出来高急増と価格下落 (出来高比: {volume_ratio:.1f}x, 価格変動: {price_change:.1f}%)'
            })
        
        # 出来高減少による反転シグナル
        if volume_ratio < 0.5 and abs(price_change) < 1:
            signals['neutral_signals'].append({
                'type': 'Low_Volume_Consolidation',
                'strength': 0.3,
                'description': '出来高減少による調整局面'
            })
        
        return signals
    
    def _generate_volatility_signals(self, df: pd.DataFrame) -> Dict:
        """ボラティリティシグナルを生成"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'neutral_signals': []
        }
        
        # ATR (Average True Range)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=14).mean().iloc[-1]
        
        # ボラティリティの変化
        volatility_5d = df['Close'].pct_change().rolling(window=5).std().iloc[-1]
        volatility_20d = df['Close'].pct_change().rolling(window=20).std().iloc[-1]
        
        if volatility_5d < volatility_20d * 0.7:
            signals['buy_signals'].append({
                'type': 'Low_Volatility_Entry',
                'strength': 0.4,
                'description': '低ボラティリティによるエントリー機会'
            })
        elif volatility_5d > volatility_20d * 1.5:
            signals['sell_signals'].append({
                'type': 'High_Volatility_Exit',
                'strength': 0.6,
                'description': '高ボラティリティによるリスク回避'
            })
        
        return signals
    
    def generate_trading_signals(self, data: pd.DataFrame) -> Dict:
        """総合的なトレーディングシグナルを生成"""
        if data is None or data.empty or len(data) < 50:
            return {'error': 'データが不足しています'}
        
        # 技術指標を計算
        df = self._calculate_technical_indicators(data)
        df = df.dropna()
        
        if len(df) < 20:
            return {'error': '十分なデータがありません'}
        
        # 各カテゴリのシグナルを生成
        technical_signals = self._generate_technical_signals(df)
        momentum_signals = self._generate_momentum_signals(df)
        volume_signals = self._generate_volume_signals(df)
        volatility_signals = self._generate_volatility_signals(df)
        
        # シグナルを統合
        all_buy_signals = []
        all_sell_signals = []
        all_neutral_signals = []
        
        # 技術分析シグナル
        for signal in technical_signals['buy_signals']:
            signal['weight'] = self.signal_weights['technical']
            all_buy_signals.append(signal)
        for signal in technical_signals['sell_signals']:
            signal['weight'] = self.signal_weights['technical']
            all_sell_signals.append(signal)
        
        # モメンタムシグナル
        for signal in momentum_signals['buy_signals']:
            signal['weight'] = self.signal_weights['momentum']
            all_buy_signals.append(signal)
        for signal in momentum_signals['sell_signals']:
            signal['weight'] = self.signal_weights['momentum']
            all_sell_signals.append(signal)
        
        # 出来高シグナル
        for signal in volume_signals['buy_signals']:
            signal['weight'] = self.signal_weights['volume']
            all_buy_signals.append(signal)
        for signal in volume_signals['sell_signals']:
            signal['weight'] = self.signal_weights['volume']
            all_sell_signals.append(signal)
        
        # ボラティリティシグナル
        for signal in volatility_signals['buy_signals']:
            signal['weight'] = self.signal_weights['volatility']
            all_buy_signals.append(signal)
        for signal in volatility_signals['sell_signals']:
            signal['weight'] = self.signal_weights['volatility']
            all_sell_signals.append(signal)
        
        # 総合スコアを計算
        buy_score = sum(signal['strength'] * signal['weight'] for signal in all_buy_signals)
        sell_score = sum(signal['strength'] * signal['weight'] for signal in all_sell_signals)
        
        # 総合判定
        if buy_score > sell_score and buy_score > 0.5:
            overall_signal = 'BUY'
            confidence = min(buy_score, 1.0)
        elif sell_score > buy_score and sell_score > 0.5:
            overall_signal = 'SELL'
            confidence = min(sell_score, 1.0)
        else:
            overall_signal = 'HOLD'
            confidence = 0.3
        
        return {
            'overall_signal': overall_signal,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'buy_signals': all_buy_signals,
            'sell_signals': all_sell_signals,
            'neutral_signals': all_neutral_signals,
            'current_price': df['Close'].iloc[-1],
            'analysis_date': df.index[-1]
        }
    
    def analyze_multiple_stocks(self, stock_data_dict: Dict) -> Dict:
        """複数銘柄のトレーディングシグナル分析"""
        results = {}
        
        for symbol, data in stock_data_dict.items():
            if data and data['data'] is not None and not data['data'].empty:
                try:
                    signals = self.generate_trading_signals(data['data'])
                    results[symbol] = signals
                except Exception as e:
                    results[symbol] = {'error': str(e)}
        
        return results
    
    def create_signal_chart(self, data: pd.DataFrame, signal_result: Dict) -> go.Figure:
        """シグナル結果のチャートを作成"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('価格とシグナル', 'RSI', 'MACD'),
            vertical_spacing=0.1,
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # 価格チャート
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='価格',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # 移動平均
        df_with_indicators = self._calculate_technical_indicators(data)
        fig.add_trace(
            go.Scatter(
                x=df_with_indicators.index,
                y=df_with_indicators['MA_20'],
                mode='lines',
                name='MA20',
                line=dict(color='orange', dash='dash')
            ),
            row=1, col=1
        )
        
        # シグナル表示
        if 'overall_signal' in signal_result:
            signal = signal_result['overall_signal']
            current_price = signal_result.get('current_price', data['Close'].iloc[-1])
            
            if signal == 'BUY':
                fig.add_annotation(
                    x=data.index[-1],
                    y=current_price,
                    text="🟢 BUY",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="green",
                    row=1, col=1
                )
            elif signal == 'SELL':
                fig.add_annotation(
                    x=data.index[-1],
                    y=current_price,
                    text="🔴 SELL",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="red",
                    row=1, col=1
                )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=df_with_indicators.index,
                y=df_with_indicators['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        
        # RSIの基準線
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(
                x=df_with_indicators.index,
                y=df_with_indicators['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue')
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_with_indicators.index,
                y=df_with_indicators['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red')
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            title='トレーディングシグナル分析',
            height=800,
            showlegend=True
        )
        
        return fig
