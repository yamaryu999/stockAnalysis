import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class ProfitMaximizer:
    """利益最大化に特化したアナライザー"""
    
    def __init__(self):
        self.strategies = {
            'momentum': self._momentum_strategy,
            'mean_reversion': self._mean_reversion_strategy,
            'breakout': self._breakout_strategy,
            'scalping': self._scalping_strategy,
            'swing': self._swing_strategy
        }
    
    def _calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """サポート・レジスタンスレベルを計算"""
        highs = data['High'].rolling(window=window).max()
        lows = data['Low'].rolling(window=window).min()
        
        # 最近の高値・安値
        recent_high = highs.iloc[-1]
        recent_low = lows.iloc[-1]
        
        # 重要な価格レベル
        current_price = data['Close'].iloc[-1]
        
        # サポート・レジスタンスレベル
        resistance_levels = []
        support_levels = []
        
        # 過去の高値・安値を分析
        for i in range(len(data) - window, len(data)):
            if data['High'].iloc[i] == highs.iloc[i]:
                resistance_levels.append(data['High'].iloc[i])
            if data['Low'].iloc[i] == lows.iloc[i]:
                support_levels.append(data['Low'].iloc[i])
        
        # 最も重要なレベルを選択
        key_resistance = max(resistance_levels) if resistance_levels else current_price * 1.05
        key_support = min(support_levels) if support_levels else current_price * 0.95
        
        return {
            'resistance': key_resistance,
            'support': key_support,
            'current_price': current_price,
            'recent_high': recent_high,
            'recent_low': recent_low
        }
    
    def _momentum_strategy(self, data: pd.DataFrame) -> Dict:
        """モメンタム戦略"""
        # 価格モメンタム
        price_change_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100
        price_change_10d = (data['Close'].iloc[-1] / data['Close'].iloc[-11] - 1) * 100
        
        # 出来高モメンタム
        volume_ma = data['Volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = data['Volume'].iloc[-1] / volume_ma
        
        # エントリー条件
        entry_conditions = []
        if price_change_5d > 3 and price_change_10d > 5:
            entry_conditions.append("強い上昇モメンタム")
        if volume_ratio > 1.5:
            entry_conditions.append("出来高急増")
        
        # エグジット条件
        exit_conditions = []
        if price_change_5d < -2:
            exit_conditions.append("モメンタム減退")
        if volume_ratio < 0.8:
            exit_conditions.append("出来高減少")
        
        # 目標価格（リスクリワード比 1:2）
        current_price = data['Close'].iloc[-1]
        risk = current_price * 0.02  # 2%のリスク
        target_price = current_price + (risk * 2)  # 2倍のリターン
        
        return {
            'strategy': 'momentum',
            'entry_conditions': entry_conditions,
            'exit_conditions': exit_conditions,
            'target_price': target_price,
            'stop_loss': current_price - risk,
            'risk_reward_ratio': 2.0,
            'confidence': min(len(entry_conditions) * 0.3, 1.0)
        }
    
    def _mean_reversion_strategy(self, data: pd.DataFrame) -> Dict:
        """平均回帰戦略"""
        # 移動平均からの乖離
        ma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
        current_price = data['Close'].iloc[-1]
        
        deviation_20 = (current_price - ma_20) / ma_20 * 100
        deviation_50 = (current_price - ma_50) / ma_50 * 100
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # エントリー条件
        entry_conditions = []
        if deviation_20 < -5:  # 20日移動平均から5%以上下回る
            entry_conditions.append("移動平均乖離（買い場）")
        if current_rsi < 30:
            entry_conditions.append("RSI売られすぎ")
        
        # エグジット条件
        exit_conditions = []
        if deviation_20 > 2:  # 20日移動平均に回帰
            exit_conditions.append("移動平均回帰")
        if current_rsi > 70:
            exit_conditions.append("RSI買われすぎ")
        
        # 目標価格
        target_price = ma_20  # 20日移動平均まで
        stop_loss = current_price * 0.95  # 5%のストップロス
        
        return {
            'strategy': 'mean_reversion',
            'entry_conditions': entry_conditions,
            'exit_conditions': exit_conditions,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'risk_reward_ratio': abs(target_price - current_price) / abs(current_price - stop_loss),
            'confidence': min(len(entry_conditions) * 0.4, 1.0)
        }
    
    def _breakout_strategy(self, data: pd.DataFrame) -> Dict:
        """ブレイクアウト戦略"""
        # サポート・レジスタンスレベル
        levels = self._calculate_support_resistance(data)
        
        current_price = levels['current_price']
        resistance = levels['resistance']
        support = levels['support']
        
        # 出来高分析
        volume_ma = data['Volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = data['Volume'].iloc[-1] / volume_ma
        
        # エントリー条件
        entry_conditions = []
        if current_price > resistance * 1.01:  # レジスタンス突破
            entry_conditions.append("レジスタンス突破")
        if volume_ratio > 2.0:
            entry_conditions.append("出来高急増")
        
        # エグジット条件
        exit_conditions = []
        if current_price < resistance * 0.99:  # レジスタンス下回り
            exit_conditions.append("レジスタンス下回り")
        if volume_ratio < 1.0:
            exit_conditions.append("出来高減少")
        
        # 目標価格（ブレイクアウト幅の1.5倍）
        breakout_range = resistance - support
        target_price = resistance + (breakout_range * 1.5)
        stop_loss = resistance * 0.98  # レジスタンス直下
        
        return {
            'strategy': 'breakout',
            'entry_conditions': entry_conditions,
            'exit_conditions': exit_conditions,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'risk_reward_ratio': (target_price - current_price) / (current_price - stop_loss),
            'confidence': min(len(entry_conditions) * 0.5, 1.0)
        }
    
    def _scalping_strategy(self, data: pd.DataFrame) -> Dict:
        """スキャルピング戦略"""
        # 短期ボラティリティ
        volatility_5d = data['Close'].pct_change().rolling(window=5).std().iloc[-1]
        volatility_20d = data['Close'].pct_change().rolling(window=20).std().iloc[-1]
        
        # 価格変動
        price_change_1d = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
        
        # エントリー条件
        entry_conditions = []
        if volatility_5d > volatility_20d * 1.2:  # ボラティリティ上昇
            entry_conditions.append("ボラティリティ上昇")
        if abs(price_change_1d) > 1:  # 1%以上の変動
            entry_conditions.append("価格変動拡大")
        
        # エグジット条件
        exit_conditions = []
        if abs(price_change_1d) < 0.5:  # 変動縮小
            exit_conditions.append("価格変動縮小")
        if volatility_5d < volatility_20d * 0.8:
            exit_conditions.append("ボラティリティ低下")
        
        # 目標価格（小さな利幅）
        current_price = data['Close'].iloc[-1]
        target_price = current_price * 1.005  # 0.5%の利幅
        stop_loss = current_price * 0.998  # 0.2%のストップロス
        
        return {
            'strategy': 'scalping',
            'entry_conditions': entry_conditions,
            'exit_conditions': exit_conditions,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'risk_reward_ratio': 2.5,
            'confidence': min(len(entry_conditions) * 0.6, 1.0)
        }
    
    def _swing_strategy(self, data: pd.DataFrame) -> Dict:
        """スイング戦略"""
        # トレンド分析
        ma_10 = data['Close'].rolling(window=10).mean().iloc[-1]
        ma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
        
        current_price = data['Close'].iloc[-1]
        
        # エントリー条件
        entry_conditions = []
        if ma_10 > ma_20 > ma_50:  # 上昇トレンド
            entry_conditions.append("上昇トレンド確認")
        if current_price > ma_10:  # 短期移動平均上
            entry_conditions.append("短期移動平均上")
        
        # エグジット条件
        exit_conditions = []
        if ma_10 < ma_20:  # トレンド転換
            exit_conditions.append("トレンド転換")
        if current_price < ma_20:  # 中期移動平均下
            exit_conditions.append("中期移動平均下")
        
        # 目標価格（トレンド継続想定）
        trend_strength = (ma_10 - ma_20) / ma_20 * 100
        target_price = current_price * (1 + trend_strength * 0.1)
        stop_loss = ma_20 * 0.98  # 20日移動平均の2%下
        
        return {
            'strategy': 'swing',
            'entry_conditions': entry_conditions,
            'exit_conditions': exit_conditions,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'risk_reward_ratio': (target_price - current_price) / (current_price - stop_loss),
            'confidence': min(len(entry_conditions) * 0.4, 1.0)
        }
    
    def analyze_profit_opportunities(self, data: pd.DataFrame) -> Dict:
        """利益機会を分析"""
        if data is None or data.empty or len(data) < 50:
            return {'error': 'データが不足しています'}
        
        results = {}
        
        # 各戦略を実行
        for strategy_name, strategy_func in self.strategies.items():
            try:
                result = strategy_func(data)
                results[strategy_name] = result
            except Exception as e:
                results[strategy_name] = {'error': str(e)}
        
        # 最適戦略を選択
        valid_strategies = {k: v for k, v in results.items() if 'error' not in v}
        if valid_strategies:
            best_strategy = max(valid_strategies.items(), key=lambda x: x[1]['confidence'])
            results['best_strategy'] = best_strategy
        
        return results
    
    def analyze_multiple_stocks(self, stock_data_dict: Dict) -> Dict:
        """複数銘柄の利益機会分析"""
        results = {}
        
        for symbol, data in stock_data_dict.items():
            if data and data['data'] is not None and not data['data'].empty:
                try:
                    opportunities = self.analyze_profit_opportunities(data['data'])
                    results[symbol] = opportunities
                except Exception as e:
                    results[symbol] = {'error': str(e)}
        
        return results
    
    def create_profit_chart(self, data: pd.DataFrame, profit_result: Dict) -> go.Figure:
        """利益機会のチャートを作成"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('価格とエントリー・エグジットポイント', '戦略別信頼度'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
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
        ma_20 = data['Close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=ma_20,
                mode='lines',
                name='MA20',
                line=dict(color='orange', dash='dash')
            ),
            row=1, col=1
        )
        
        # 最適戦略のエントリー・エグジットポイント
        if 'best_strategy' in profit_result:
            best_strategy = profit_result['best_strategy'][1]
            current_price = data['Close'].iloc[-1]
            
            # エントリーポイント
            fig.add_hline(
                y=current_price,
                line_dash="dash",
                line_color="green",
                annotation_text="エントリー",
                row=1, col=1
            )
            
            # 目標価格
            if 'target_price' in best_strategy:
                fig.add_hline(
                    y=best_strategy['target_price'],
                    line_dash="dash",
                    line_color="blue",
                    annotation_text="目標価格",
                    row=1, col=1
                )
            
            # ストップロス
            if 'stop_loss' in best_strategy:
                fig.add_hline(
                    y=best_strategy['stop_loss'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="ストップロス",
                    row=1, col=1
                )
        
        # 戦略別信頼度
        if 'best_strategy' not in profit_result:
            strategies = [k for k, v in profit_result.items() if 'error' not in v and 'confidence' in v]
            confidences = [profit_result[k]['confidence'] for k in strategies]
            
            fig.add_trace(
                go.Bar(
                    x=strategies,
                    y=confidences,
                    name='信頼度',
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title='利益最大化分析',
            height=600,
            showlegend=True
        )
        
        return fig
