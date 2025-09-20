"""
Advanced Visualization System
高度な可視化システム - インタラクティブチャート、3D可視化、アニメーション、カスタムダッシュボード
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
import json
import streamlit as st
from scipy import stats
import talib
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ChartConfig:
    """チャート設定"""
    title: str
    width: int = 800
    height: int = 600
    theme: str = 'plotly_white'
    show_legend: bool = True
    show_grid: bool = True
    animation: bool = False
    interactive: bool = True

@dataclass
class ColorScheme:
    """カラースキーム"""
    primary: str = '#1f77b4'
    secondary: str = '#ff7f0e'
    success: str = '#2ca02c'
    danger: str = '#d62728'
    warning: str = '#ff7f0e'
    info: str = '#17a2b8'
    light: str = '#f8f9fa'
    dark: str = '#343a40'

class AdvancedChartGenerator:
    """高度なチャート生成クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.color_scheme = ColorScheme()
        self.default_config = ChartConfig(
            title="Stock Analysis Chart",
            width=800,
            height=600
        )
    
    def create_candlestick_chart(self, data: pd.DataFrame, 
                               config: ChartConfig = None) -> go.Figure:
        """ローソク足チャートを作成"""
        try:
            config = config or self.default_config
            
            fig = go.Figure(data=go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color=self.color_scheme.success,
                decreasing_line_color=self.color_scheme.danger
            ))
            
            # レイアウト設定
            fig.update_layout(
                title=config.title,
                xaxis_title='Date',
                yaxis_title='Price',
                template=config.theme,
                width=config.width,
                height=config.height,
                showlegend=config.show_legend,
                xaxis_rangeslider_visible=False
            )
            
            # グリッド設定
            if config.show_grid:
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            
            return fig
            
        except Exception as e:
            self.logger.error(f"ローソク足チャート作成エラー: {e}")
            return go.Figure()
    
    def create_volume_chart(self, data: pd.DataFrame, 
                          config: ChartConfig = None) -> go.Figure:
        """出来高チャートを作成"""
        try:
            config = config or self.default_config
            
            # 出来高の色を価格変動に基づいて設定
            colors = []
            for i in range(len(data)):
                if i == 0:
                    colors.append(self.color_scheme.primary)
                else:
                    if data['Close'].iloc[i] >= data['Close'].iloc[i-1]:
                        colors.append(self.color_scheme.success)
                    else:
                        colors.append(self.color_scheme.danger)
            
            fig = go.Figure(data=go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title='Date',
                yaxis_title='Volume',
                template=config.theme,
                width=config.width,
                height=config.height,
                showlegend=config.show_legend
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"出来高チャート作成エラー: {e}")
            return go.Figure()
    
    def create_technical_indicators_chart(self, data: pd.DataFrame,
                                        indicators: List[str] = None,
                                        config: ChartConfig = None) -> go.Figure:
        """テクニカル指標チャートを作成"""
        try:
            config = config or self.default_config
            indicators = indicators or ['SMA_20', 'SMA_50', 'RSI', 'MACD']
            
            # サブプロットを作成
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('Price with Moving Averages', 'RSI', 'MACD'),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # 価格と移動平均
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Close'], name='Close', 
                          line=dict(color=self.color_scheme.primary)),
                row=1, col=1
            )
            
            if 'SMA_20' in indicators and 'SMA_20' in data.columns:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['SMA_20'], name='SMA 20',
                              line=dict(color=self.color_scheme.secondary, dash='dash')),
                    row=1, col=1
                )
            
            if 'SMA_50' in indicators and 'SMA_50' in data.columns:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50',
                              line=dict(color=self.color_scheme.warning, dash='dash')),
                    row=1, col=1
                )
            
            # RSI
            if 'RSI' in indicators and 'RSI' in data.columns:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['RSI'], name='RSI',
                              line=dict(color=self.color_scheme.info)),
                    row=2, col=1
                )
                
                # RSIの過買い・過売りライン
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            # MACD
            if 'MACD' in indicators and 'MACD' in data.columns:
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['MACD'], name='MACD',
                              line=dict(color=self.color_scheme.primary)),
                    row=3, col=1
                )
                
                if 'MACD_Signal' in data.columns:
                    fig.add_trace(
                        go.Scatter(x=data.index, y=data['MACD_Signal'], name='MACD Signal',
                                  line=dict(color=self.color_scheme.secondary)),
                        row=3, col=1
                    )
                
                if 'MACD_Histogram' in data.columns:
                    colors = ['green' if val >= 0 else 'red' for val in data['MACD_Histogram']]
                    fig.add_trace(
                        go.Bar(x=data.index, y=data['MACD_Histogram'], name='MACD Histogram',
                              marker_color=colors, opacity=0.7),
                        row=3, col=1
                    )
            
            fig.update_layout(
                title=config.title,
                template=config.theme,
                width=config.width,
                height=config.height * 1.5,
                showlegend=config.show_legend
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"テクニカル指標チャート作成エラー: {e}")
            return go.Figure()
    
    def create_correlation_heatmap(self, data: pd.DataFrame,
                                 config: ChartConfig = None) -> go.Figure:
        """相関ヒートマップを作成"""
        try:
            config = config or self.default_config
            
            # 相関行列を計算
            correlation_matrix = data.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=config.title,
                template=config.theme,
                width=config.width,
                height=config.height
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"相関ヒートマップ作成エラー: {e}")
            return go.Figure()
    
    def create_3d_surface_chart(self, data: pd.DataFrame,
                              x_col: str, y_col: str, z_col: str,
                              config: ChartConfig = None) -> go.Figure:
        """3Dサーフェスチャートを作成"""
        try:
            config = config or self.default_config
            
            fig = go.Figure(data=go.Surface(
                x=data[x_col],
                y=data[y_col],
                z=data[z_col],
                colorscale='Viridis',
                opacity=0.8
            ))
            
            fig.update_layout(
                title=config.title,
                scene=dict(
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    zaxis_title=z_col
                ),
                template=config.theme,
                width=config.width,
                height=config.height
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"3Dサーフェスチャート作成エラー: {e}")
            return go.Figure()
    
    def create_animated_chart(self, data: pd.DataFrame,
                            animation_column: str = 'Date',
                            config: ChartConfig = None) -> go.Figure:
        """アニメーションチャートを作成"""
        try:
            config = config or self.default_config
            
            fig = px.scatter(
                data, x='Close', y='Volume',
                animation_frame=animation_column,
                size='Volume',
                color='Close',
                hover_name=data.index,
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                title=config.title,
                template=config.theme,
                width=config.width,
                height=config.height
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"アニメーションチャート作成エラー: {e}")
            return go.Figure()
    
    def create_risk_return_scatter(self, data: pd.DataFrame,
                                 config: ChartConfig = None) -> go.Figure:
        """リスク・リターンスキャッタープロットを作成"""
        try:
            config = config or self.default_config
            
            # リターンとリスクを計算
            returns = data['Close'].pct_change().dropna()
            risk = returns.rolling(window=20).std()
            expected_return = returns.rolling(window=20).mean()
            
            fig = go.Figure(data=go.Scatter(
                x=risk,
                y=expected_return,
                mode='markers',
                marker=dict(
                    size=10,
                    color=expected_return,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Expected Return")
                ),
                text=data.index,
                hovertemplate='<b>%{text}</b><br>' +
                             'Risk: %{x:.4f}<br>' +
                             'Expected Return: %{y:.4f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title='Risk (Standard Deviation)',
                yaxis_title='Expected Return',
                template=config.theme,
                width=config.width,
                height=config.height
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"リスク・リターンスキャッタープロット作成エラー: {e}")
            return go.Figure()
    
    def create_portfolio_performance_chart(self, portfolio_data: Dict[str, pd.DataFrame],
                                         benchmark_data: pd.DataFrame = None,
                                         config: ChartConfig = None) -> go.Figure:
        """ポートフォリオパフォーマンスチャートを作成"""
        try:
            config = config or self.default_config
            
            fig = go.Figure()
            
            # 各資産の累積リターンを計算
            for asset_name, asset_data in portfolio_data.items():
                cumulative_return = (1 + asset_data['Close'].pct_change()).cumprod()
                fig.add_trace(go.Scatter(
                    x=asset_data.index,
                    y=cumulative_return,
                    mode='lines',
                    name=asset_name,
                    line=dict(width=2)
                ))
            
            # ベンチマークを追加
            if benchmark_data is not None:
                benchmark_cumulative = (1 + benchmark_data['Close'].pct_change()).cumprod()
                fig.add_trace(go.Scatter(
                    x=benchmark_data.index,
                    y=benchmark_cumulative,
                    mode='lines',
                    name='Benchmark',
                    line=dict(width=3, dash='dash', color='black')
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title='Date',
                yaxis_title='Cumulative Return',
                template=config.theme,
                width=config.width,
                height=config.height,
                showlegend=config.show_legend
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"ポートフォリオパフォーマンスチャート作成エラー: {e}")
            return go.Figure()

class InteractiveDashboard:
    """インタラクティブダッシュボードクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chart_generator = AdvancedChartGenerator()
        self.dashboard_configs = {}
    
    def create_market_overview_dashboard(self, market_data: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
        """市場概要ダッシュボードを作成"""
        try:
            dashboard = {}
            
            # 市場全体のパフォーマンス
            if 'market_index' in market_data:
                config = ChartConfig(
                    title="Market Index Performance",
                    width=800,
                    height=400
                )
                dashboard['market_performance'] = self.chart_generator.create_candlestick_chart(
                    market_data['market_index'], config
                )
            
            # セクター別パフォーマンス
            if 'sector_performance' in market_data:
                config = ChartConfig(
                    title="Sector Performance",
                    width=800,
                    height=400
                )
                dashboard['sector_performance'] = self._create_sector_performance_chart(
                    market_data['sector_performance'], config
                )
            
            # 出来高分析
            if 'volume_analysis' in market_data:
                config = ChartConfig(
                    title="Volume Analysis",
                    width=800,
                    height=400
                )
                dashboard['volume_analysis'] = self.chart_generator.create_volume_chart(
                    market_data['volume_analysis'], config
                )
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"市場概要ダッシュボード作成エラー: {e}")
            return {}
    
    def create_stock_analysis_dashboard(self, stock_data: pd.DataFrame,
                                      financial_metrics: Dict[str, Any] = None) -> Dict[str, go.Figure]:
        """株式分析ダッシュボードを作成"""
        try:
            dashboard = {}
            
            # 価格チャート
            config = ChartConfig(
                title="Stock Price Analysis",
                width=800,
                height=400
            )
            dashboard['price_chart'] = self.chart_generator.create_candlestick_chart(
                stock_data, config
            )
            
            # テクニカル指標
            config = ChartConfig(
                title="Technical Indicators",
                width=800,
                height=600
            )
            dashboard['technical_indicators'] = self.chart_generator.create_technical_indicators_chart(
                stock_data, config=config
            )
            
            # 出来高分析
            config = ChartConfig(
                title="Volume Analysis",
                width=800,
                height=400
            )
            dashboard['volume_chart'] = self.chart_generator.create_volume_chart(
                stock_data, config
            )
            
            # リスク・リターン分析
            config = ChartConfig(
                title="Risk-Return Analysis",
                width=800,
                height=400
            )
            dashboard['risk_return'] = self.chart_generator.create_risk_return_scatter(
                stock_data, config
            )
            
            # 財務指標（利用可能な場合）
            if financial_metrics:
                dashboard['financial_metrics'] = self._create_financial_metrics_chart(
                    financial_metrics
                )
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"株式分析ダッシュボード作成エラー: {e}")
            return {}
    
    def create_portfolio_dashboard(self, portfolio_data: Dict[str, pd.DataFrame],
                                 portfolio_weights: Dict[str, float] = None) -> Dict[str, go.Figure]:
        """ポートフォリオダッシュボードを作成"""
        try:
            dashboard = {}
            
            # ポートフォリオパフォーマンス
            config = ChartConfig(
                title="Portfolio Performance",
                width=800,
                height=400
            )
            dashboard['portfolio_performance'] = self.chart_generator.create_portfolio_performance_chart(
                portfolio_data, config=config
            )
            
            # 資産配分（利用可能な場合）
            if portfolio_weights:
                dashboard['asset_allocation'] = self._create_asset_allocation_chart(
                    portfolio_weights
                )
            
            # 相関分析
            if len(portfolio_data) > 1:
                combined_data = pd.concat([data['Close'] for data in portfolio_data.values()], axis=1)
                combined_data.columns = list(portfolio_data.keys())
                
                config = ChartConfig(
                    title="Asset Correlation",
                    width=800,
                    height=400
                )
                dashboard['correlation'] = self.chart_generator.create_correlation_heatmap(
                    combined_data, config
                )
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"ポートフォリオダッシュボード作成エラー: {e}")
            return {}
    
    def _create_sector_performance_chart(self, sector_data: pd.DataFrame,
                                       config: ChartConfig) -> go.Figure:
        """セクター別パフォーマンスチャートを作成"""
        try:
            fig = go.Figure()
            
            for column in sector_data.columns:
                fig.add_trace(go.Scatter(
                    x=sector_data.index,
                    y=sector_data[column],
                    mode='lines',
                    name=column,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title='Date',
                yaxis_title='Performance',
                template=config.theme,
                width=config.width,
                height=config.height,
                showlegend=config.show_legend
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"セクター別パフォーマンスチャート作成エラー: {e}")
            return go.Figure()
    
    def _create_financial_metrics_chart(self, metrics: Dict[str, Any]) -> go.Figure:
        """財務指標チャートを作成"""
        try:
            # 財務指標をカテゴリ別に整理
            categories = {
                'Profitability': ['ROE', 'ROA', 'Net_Margin'],
                'Valuation': ['PE_Ratio', 'PB_Ratio', 'PS_Ratio'],
                'Liquidity': ['Current_Ratio', 'Quick_Ratio'],
                'Leverage': ['Debt_to_Equity', 'Debt_to_Assets']
            }
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=list(categories.keys()),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            row_col_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
            
            for i, (category, indicators) in enumerate(categories.items()):
                row, col = row_col_positions[i]
                
                values = []
                labels = []
                for indicator in indicators:
                    if indicator in metrics:
                        values.append(metrics[indicator])
                        labels.append(indicator)
                
                if values:
                    fig.add_trace(
                        go.Bar(x=labels, y=values, name=category, showlegend=False),
                        row=row, col=col
                    )
            
            fig.update_layout(
                title="Financial Metrics Analysis",
                template='plotly_white',
                height=600
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"財務指標チャート作成エラー: {e}")
            return go.Figure()
    
    def _create_asset_allocation_chart(self, weights: Dict[str, float]) -> go.Figure:
        """資産配分チャートを作成"""
        try:
            labels = list(weights.keys())
            values = list(weights.values())
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                textinfo='label+percent',
                textfont_size=12
            )])
            
            fig.update_layout(
                title="Asset Allocation",
                template='plotly_white',
                width=600,
                height=400
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"資産配分チャート作成エラー: {e}")
            return go.Figure()

class AnimationEngine:
    """アニメーションエンジンクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chart_generator = AdvancedChartGenerator()
    
    def create_price_animation(self, data: pd.DataFrame,
                             animation_speed: int = 100) -> go.Figure:
        """価格アニメーションを作成"""
        try:
            # データを時系列でソート
            data_sorted = data.sort_index()
            
            # フレームごとのデータを作成
            frames = []
            for i in range(10, len(data_sorted), 5):  # 5日ごとにフレーム
                frame_data = data_sorted.iloc[:i]
                
                frame = go.Frame(
                    data=[
                        go.Candlestick(
                            x=frame_data.index,
                            open=frame_data['Open'],
                            high=frame_data['High'],
                            low=frame_data['Low'],
                            close=frame_data['Close']
                        )
                    ],
                    name=str(i)
                )
                frames.append(frame)
            
            # 初期データ
            initial_data = data_sorted.iloc[:10]
            fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=initial_data.index,
                        open=initial_data['Open'],
                        high=initial_data['High'],
                        low=initial_data['Low'],
                        close=initial_data['Close']
                    )
                ],
                frames=frames
            )
            
            # アニメーション設定
            fig.update_layout(
                title="Animated Stock Price",
                xaxis_rangeslider_visible=False,
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[None, {"frame": {"duration": animation_speed}}]
                            ),
                            dict(
                                label="Pause",
                                method="animate",
                                args=[[None], {"frame": {"duration": 0}}]
                            )
                        ]
                    )
                ]
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"価格アニメーション作成エラー: {e}")
            return go.Figure()
    
    def create_volume_animation(self, data: pd.DataFrame,
                              animation_speed: int = 100) -> go.Figure:
        """出来高アニメーションを作成"""
        try:
            data_sorted = data.sort_index()
            
            frames = []
            for i in range(10, len(data_sorted), 5):
                frame_data = data_sorted.iloc[:i]
                
                # 出来高の色を価格変動に基づいて設定
                colors = []
                for j in range(len(frame_data)):
                    if j == 0:
                        colors.append('#1f77b4')
                    else:
                        if frame_data['Close'].iloc[j] >= frame_data['Close'].iloc[j-1]:
                            colors.append('#2ca02c')
                        else:
                            colors.append('#d62728')
                
                frame = go.Frame(
                    data=[
                        go.Bar(
                            x=frame_data.index,
                            y=frame_data['Volume'],
                            marker_color=colors
                        )
                    ],
                    name=str(i)
                )
                frames.append(frame)
            
            initial_data = data_sorted.iloc[:10]
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=initial_data.index,
                        y=initial_data['Volume'],
                        marker_color='#1f77b4'
                    )
                ],
                frames=frames
            )
            
            fig.update_layout(
                title="Animated Volume",
                updatemenus=[
                    dict(
                        type="buttons",
                        showactive=False,
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[None, {"frame": {"duration": animation_speed}}]
                            ),
                            dict(
                                label="Pause",
                                method="animate",
                                args=[[None], {"frame": {"duration": 0}}]
                            )
                        ]
                    )
                ]
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"出来高アニメーション作成エラー: {e}")
            return go.Figure()

class CustomDashboardBuilder:
    """カスタムダッシュボードビルダー"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dashboard_generator = InteractiveDashboard()
        self.animation_engine = AnimationEngine()
        self.chart_generator = AdvancedChartGenerator()
    
    def build_dashboard(self, dashboard_config: Dict[str, Any],
                       data: Dict[str, Any]) -> Dict[str, go.Figure]:
        """カスタムダッシュボードを構築"""
        try:
            dashboard = {}
            
            for chart_id, chart_config in dashboard_config.items():
                chart_type = chart_config.get('type')
                chart_data = data.get(chart_config.get('data_key'))
                
                if not chart_data:
                    continue
                
                if chart_type == 'candlestick':
                    dashboard[chart_id] = self.chart_generator.create_candlestick_chart(
                        chart_data, ChartConfig(**chart_config.get('config', {}))
                    )
                elif chart_type == 'volume':
                    dashboard[chart_id] = self.chart_generator.create_volume_chart(
                        chart_data, ChartConfig(**chart_config.get('config', {}))
                    )
                elif chart_type == 'technical_indicators':
                    dashboard[chart_id] = self.chart_generator.create_technical_indicators_chart(
                        chart_data, ChartConfig(**chart_config.get('config', {}))
                    )
                elif chart_type == 'correlation':
                    dashboard[chart_id] = self.chart_generator.create_correlation_heatmap(
                        chart_data, ChartConfig(**chart_config.get('config', {}))
                    )
                elif chart_type == '3d_surface':
                    dashboard[chart_id] = self.chart_generator.create_3d_surface_chart(
                        chart_data,
                        chart_config.get('x_col', 'x'),
                        chart_config.get('y_col', 'y'),
                        chart_config.get('z_col', 'z'),
                        ChartConfig(**chart_config.get('config', {}))
                    )
                elif chart_type == 'animated_price':
                    dashboard[chart_id] = self.animation_engine.create_price_animation(
                        chart_data, chart_config.get('animation_speed', 100)
                    )
                elif chart_type == 'animated_volume':
                    dashboard[chart_id] = self.animation_engine.create_volume_animation(
                        chart_data, chart_config.get('animation_speed', 100)
                    )
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"カスタムダッシュボード構築エラー: {e}")
            return {}
    
    def create_dashboard_template(self, template_name: str) -> Dict[str, Any]:
        """ダッシュボードテンプレートを作成"""
        templates = {
            'market_overview': {
                'market_performance': {
                    'type': 'candlestick',
                    'data_key': 'market_data',
                    'config': {
                        'title': 'Market Performance',
                        'width': 800,
                        'height': 400
                    }
                },
                'sector_analysis': {
                    'type': 'correlation',
                    'data_key': 'sector_data',
                    'config': {
                        'title': 'Sector Correlation',
                        'width': 800,
                        'height': 400
                    }
                }
            },
            'stock_analysis': {
                'price_chart': {
                    'type': 'candlestick',
                    'data_key': 'stock_data',
                    'config': {
                        'title': 'Stock Price',
                        'width': 800,
                        'height': 400
                    }
                },
                'technical_analysis': {
                    'type': 'technical_indicators',
                    'data_key': 'stock_data',
                    'config': {
                        'title': 'Technical Indicators',
                        'width': 800,
                        'height': 600
                    }
                },
                'volume_analysis': {
                    'type': 'volume',
                    'data_key': 'stock_data',
                    'config': {
                        'title': 'Volume Analysis',
                        'width': 800,
                        'height': 400
                    }
                }
            },
            'portfolio_analysis': {
                'performance': {
                    'type': 'candlestick',
                    'data_key': 'portfolio_data',
                    'config': {
                        'title': 'Portfolio Performance',
                        'width': 800,
                        'height': 400
                    }
                },
                'correlation': {
                    'type': 'correlation',
                    'data_key': 'portfolio_correlation',
                    'config': {
                        'title': 'Asset Correlation',
                        'width': 800,
                        'height': 400
                    }
                }
            }
        }
        
        return templates.get(template_name, {})

# グローバルインスタンス
advanced_visualization = {
    'chart_generator': AdvancedChartGenerator(),
    'dashboard': InteractiveDashboard(),
    'animation_engine': AnimationEngine(),
    'dashboard_builder': CustomDashboardBuilder()
}
