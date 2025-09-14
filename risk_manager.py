import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class RiskManager:
    """リスク管理に特化したアナライザー"""
    
    def __init__(self):
        self.risk_levels = {
            'conservative': {'max_loss': 0.01, 'max_position': 0.05},  # 1%損失、5%ポジション
            'moderate': {'max_loss': 0.02, 'max_position': 0.10},      # 2%損失、10%ポジション
            'aggressive': {'max_loss': 0.05, 'max_position': 0.20}     # 5%損失、20%ポジション
        }
    
    def _calculate_volatility(self, data: pd.DataFrame, window: int = 20) -> float:
        """ボラティリティを計算"""
        returns = data['Close'].pct_change().dropna()
        return returns.rolling(window=window).std().iloc[-1]
    
    def _calculate_atr(self, data: pd.DataFrame, window: int = 14) -> float:
        """ATR (Average True Range) を計算"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(window=window).mean().iloc[-1]
    
    def _calculate_support_resistance(self, data: pd.DataFrame) -> Dict:
        """サポート・レジスタンスレベルを計算"""
        # 最近の高値・安値
        recent_high = data['High'].rolling(window=20).max().iloc[-1]
        recent_low = data['Low'].rolling(window=20).min().iloc[-1]
        current_price = data['Close'].iloc[-1]
        
        # 重要な価格レベル
        levels = []
        for i in range(len(data) - 20, len(data)):
            if data['High'].iloc[i] == recent_high:
                levels.append(recent_high)
            if data['Low'].iloc[i] == recent_low:
                levels.append(recent_low)
        
        return {
            'resistance': recent_high,
            'support': recent_low,
            'current_price': current_price
        }
    
    def calculate_stop_loss(self, data: pd.DataFrame, risk_level: str = 'moderate') -> Dict:
        """ストップロス価格を計算"""
        if data is None or data.empty or len(data) < 20:
            return {'error': 'データが不足しています'}
        
        current_price = data['Close'].iloc[-1]
        atr = self._calculate_atr(data)
        volatility = self._calculate_volatility(data)
        levels = self._calculate_support_resistance(data)
        
        # リスクレベル設定
        max_loss_ratio = self.risk_levels[risk_level]['max_loss']
        
        # 複数のストップロス戦略
        stop_losses = {}
        
        # 1. 固定パーセンテージストップロス
        stop_losses['percentage'] = {
            'price': current_price * (1 - max_loss_ratio),
            'method': '固定パーセンテージ',
            'description': f'{max_loss_ratio*100:.1f}%の損失でストップロス'
        }
        
        # 2. ATRベースストップロス
        atr_multiplier = 2.0  # ATRの2倍
        stop_losses['atr'] = {
            'price': current_price - (atr * atr_multiplier),
            'method': 'ATRベース',
            'description': f'ATRの{atr_multiplier}倍下でストップロス'
        }
        
        # 3. サポートレベルストップロス
        support_buffer = current_price * 0.01  # 1%のバッファ
        stop_losses['support'] = {
            'price': levels['support'] - support_buffer,
            'method': 'サポートレベル',
            'description': 'サポートレベル下でストップロス'
        }
        
        # 4. 移動平均ストップロス
        ma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        stop_losses['moving_average'] = {
            'price': ma_20 * 0.98,  # 20日移動平均の2%下
            'method': '移動平均',
            'description': '20日移動平均の2%下でストップロス'
        }
        
        # 最適なストップロスを選択（最も保守的なものを選択）
        best_stop_loss = min(stop_losses.items(), key=lambda x: x[1]['price'])
        
        return {
            'current_price': current_price,
            'stop_losses': stop_losses,
            'recommended_stop_loss': best_stop_loss,
            'atr': atr,
            'volatility': volatility,
            'risk_level': risk_level
        }
    
    def calculate_take_profit(self, data: pd.DataFrame, entry_price: float, risk_level: str = 'moderate') -> Dict:
        """テイクプロフィット価格を計算"""
        if data is None or data.empty or len(data) < 20:
            return {'error': 'データが不足しています'}
        
        current_price = data['Close'].iloc[-1]
        atr = self._calculate_atr(data)
        levels = self._calculate_support_resistance(data)
        
        # リスクリワード比
        risk_reward_ratios = {
            'conservative': 1.5,
            'moderate': 2.0,
            'aggressive': 3.0
        }
        
        target_ratio = risk_reward_ratios[risk_level]
        
        # 複数のテイクプロフィット戦略
        take_profits = {}
        
        # 1. リスクリワード比ベース
        risk_amount = current_price - entry_price  # エントリー価格からのリスク
        take_profits['risk_reward'] = {
            'price': current_price + (risk_amount * target_ratio),
            'method': 'リスクリワード比',
            'description': f'{target_ratio}:1のリスクリワード比'
        }
        
        # 2. ATRベース
        atr_multiplier = 3.0  # ATRの3倍
        take_profits['atr'] = {
            'price': current_price + (atr * atr_multiplier),
            'method': 'ATRベース',
            'description': f'ATRの{atr_multiplier}倍上でテイクプロフィット'
        }
        
        # 3. レジスタンスレベル
        resistance_buffer = current_price * 0.01  # 1%のバッファ
        take_profits['resistance'] = {
            'price': levels['resistance'] - resistance_buffer,
            'method': 'レジスタンスレベル',
            'description': 'レジスタンスレベルでテイクプロフィット'
        }
        
        # 4. 移動平均ベース
        ma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
        take_profits['moving_average'] = {
            'price': ma_50 * 1.05,  # 50日移動平均の5%上
            'method': '移動平均',
            'description': '50日移動平均の5%上でテイクプロフィット'
        }
        
        # 最適なテイクプロフィットを選択（最も現実的なものを選択）
        # 現在価格から最も近い適度な価格を選択
        valid_take_profits = {k: v for k, v in take_profits.items() if v['price'] > current_price}
        if valid_take_profits:
            best_take_profit = min(valid_take_profits.items(), key=lambda x: abs(x[1]['price'] - current_price * 1.1))
        else:
            best_take_profit = list(take_profits.items())[0]
        
        return {
            'current_price': current_price,
            'entry_price': entry_price,
            'take_profits': take_profits,
            'recommended_take_profit': best_take_profit,
            'risk_reward_ratio': target_ratio
        }
    
    def calculate_position_size(self, account_balance: float, entry_price: float, stop_loss_price: float, risk_level: str = 'moderate') -> Dict:
        """ポジションサイズを計算"""
        max_loss_ratio = self.risk_levels[risk_level]['max_loss']
        max_position_ratio = self.risk_levels[risk_level]['max_position']
        
        # リスク金額
        risk_per_share = abs(entry_price - stop_loss_price)
        max_risk_amount = account_balance * max_loss_ratio
        
        # 最大ポジションサイズ
        max_position_amount = account_balance * max_position_ratio
        
        # リスクベースのポジションサイズ
        risk_based_shares = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 0
        risk_based_amount = risk_based_shares * entry_price
        
        # ポジション制限ベースのサイズ
        position_based_amount = max_position_amount
        position_based_shares = int(position_based_amount / entry_price)
        
        # より保守的なサイズを選択
        recommended_shares = min(risk_based_shares, position_based_shares)
        recommended_amount = recommended_shares * entry_price
        
        return {
            'account_balance': account_balance,
            'entry_price': entry_price,
            'stop_loss_price': stop_loss_price,
            'risk_per_share': risk_per_share,
            'max_risk_amount': max_risk_amount,
            'max_position_amount': max_position_amount,
            'risk_based_shares': risk_based_shares,
            'position_based_shares': position_based_shares,
            'recommended_shares': recommended_shares,
            'recommended_amount': recommended_amount,
            'risk_level': risk_level
        }
    
    def analyze_risk_metrics(self, data: pd.DataFrame) -> Dict:
        """リスク指標を分析"""
        if data is None or data.empty or len(data) < 50:
            return {'error': 'データが不足しています'}
        
        # 基本統計
        returns = data['Close'].pct_change().dropna()
        
        # リスク指標
        volatility = returns.std() * np.sqrt(252)  # 年率ボラティリティ
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # 最大ドローダウン
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # VaR (Value at Risk)
        var_95 = np.percentile(returns, 5)  # 95% VaR
        var_99 = np.percentile(returns, 1)  # 99% VaR
        
        # 期待リターン
        expected_return = returns.mean() * 252  # 年率
        
        # リスクスコア（0-100、低いほど安全）
        risk_score = min(100, max(0, (volatility * 10) + (abs(max_drawdown) * 50)))
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'var_99': var_99,
            'expected_return': expected_return,
            'risk_score': risk_score,
            'current_price': data['Close'].iloc[-1]
        }
    
    def comprehensive_risk_analysis(self, data: pd.DataFrame, account_balance: float = 1000000, risk_level: str = 'moderate') -> Dict:
        """包括的なリスク分析"""
        if data is None or data.empty:
            return {'error': 'データが不足しています'}
        
        current_price = data['Close'].iloc[-1]
        
        # ストップロス分析
        stop_loss_analysis = self.calculate_stop_loss(data, risk_level)
        
        # テイクプロフィット分析
        take_profit_analysis = self.calculate_take_profit(data, current_price, risk_level)
        
        # ポジションサイズ分析
        if 'recommended_stop_loss' in stop_loss_analysis:
            stop_loss_price = stop_loss_analysis['recommended_stop_loss'][1]['price']
            position_analysis = self.calculate_position_size(account_balance, current_price, stop_loss_price, risk_level)
        else:
            position_analysis = {'error': 'ストップロス分析に失敗'}
        
        # リスク指標分析
        risk_metrics = self.analyze_risk_metrics(data)
        
        return {
            'current_price': current_price,
            'account_balance': account_balance,
            'risk_level': risk_level,
            'stop_loss_analysis': stop_loss_analysis,
            'take_profit_analysis': take_profit_analysis,
            'position_analysis': position_analysis,
            'risk_metrics': risk_metrics
        }
    
    def analyze_multiple_stocks(self, stock_data_dict: Dict, account_balance: float = 1000000, risk_level: str = 'moderate') -> Dict:
        """複数銘柄のリスク分析"""
        results = {}
        
        for symbol, data in stock_data_dict.items():
            if data and data['data'] is not None and not data['data'].empty:
                try:
                    risk_analysis = self.comprehensive_risk_analysis(data['data'], account_balance, risk_level)
                    results[symbol] = risk_analysis
                except Exception as e:
                    results[symbol] = {'error': str(e)}
        
        return results
    
    def create_risk_chart(self, data: pd.DataFrame, risk_analysis: Dict) -> go.Figure:
        """リスク分析のチャートを作成"""
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('価格とリスク管理レベル', 'リスク指標', 'ドローダウン'),
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
        
        # ストップロス・テイクプロフィットライン
        if 'stop_loss_analysis' in risk_analysis and 'recommended_stop_loss' in risk_analysis['stop_loss_analysis']:
            stop_loss_price = risk_analysis['stop_loss_analysis']['recommended_stop_loss'][1]['price']
            fig.add_hline(
                y=stop_loss_price,
                line_dash="dash",
                line_color="red",
                annotation_text="ストップロス",
                row=1, col=1
            )
        
        if 'take_profit_analysis' in risk_analysis and 'recommended_take_profit' in risk_analysis['take_profit_analysis']:
            take_profit_price = risk_analysis['take_profit_analysis']['recommended_take_profit'][1]['price']
            fig.add_hline(
                y=take_profit_price,
                line_dash="dash",
                line_color="green",
                annotation_text="テイクプロフィット",
                row=1, col=1
            )
        
        # リスク指標
        if 'risk_metrics' in risk_analysis:
            risk_metrics = risk_analysis['risk_metrics']
            
            # ボラティリティ
            volatility_data = data['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=volatility_data,
                    mode='lines',
                    name='ボラティリティ',
                    line=dict(color='orange')
                ),
                row=2, col=1
            )
            
            # ドローダウン
            returns = data['Close'].pct_change().dropna()
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            
            fig.add_trace(
                go.Scatter(
                    x=drawdown.index,
                    y=drawdown,
                    mode='lines',
                    name='ドローダウン',
                    line=dict(color='red'),
                    fill='tonexty'
                ),
                row=3, col=1
            )
        
        fig.update_layout(
            title='リスク管理分析',
            height=800,
            showlegend=True
        )
        
        return fig
