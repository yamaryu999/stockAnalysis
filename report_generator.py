"""
レポート生成システム
分析結果のレポート生成・エクスポート機能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
import json
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import yfinance as yf
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ReportSection:
    """レポートセクションクラス"""
    title: str
    content: str
    charts: List[Dict[str, Any]]
    tables: List[pd.DataFrame]
    metrics: Dict[str, Any]
    section_type: str  # 'summary', 'analysis', 'charts', 'recommendations'

@dataclass
class ReportMetadata:
    """レポートメタデータクラス"""
    title: str
    author: str
    generated_at: datetime
    report_type: str
    symbols: List[str]
    period: str
    language: str = 'ja'
    template: str = 'default'

class ChartGenerator:
    """チャート生成クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_price_chart(self, data: pd.DataFrame, symbol: str, 
                          chart_type: str = 'candlestick') -> Dict[str, Any]:
        """価格チャートを作成"""
        try:
            if chart_type == 'candlestick':
                fig = go.Figure(data=go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=symbol
                ))
            elif chart_type == 'line':
                fig = go.Figure(data=go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name=symbol
                ))
            else:
                fig = go.Figure(data=go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name=symbol
                ))
            
            fig.update_layout(
                title=f"{symbol} 価格チャート",
                xaxis_title="日付",
                yaxis_title="価格 (円)",
                template="plotly_dark",
                height=400
            )
            
            return {
                'type': 'plotly',
                'figure': fig,
                'title': f"{symbol} 価格チャート",
                'description': f"{symbol}の価格推移を{chart_type}チャートで表示"
            }
            
        except Exception as e:
            self.logger.error(f"価格チャート作成エラー: {e}")
            return None
    
    def create_volume_chart(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """出来高チャートを作成"""
        try:
            fig = go.Figure(data=go.Bar(
                x=data.index,
                y=data['Volume'],
                name='出来高'
            ))
            
            fig.update_layout(
                title=f"{symbol} 出来高チャート",
                xaxis_title="日付",
                yaxis_title="出来高",
                template="plotly_dark",
                height=300
            )
            
            return {
                'type': 'plotly',
                'figure': fig,
                'title': f"{symbol} 出来高チャート",
                'description': f"{symbol}の出来高推移を表示"
            }
            
        except Exception as e:
            self.logger.error(f"出来高チャート作成エラー: {e}")
            return None
    
    def create_technical_indicators_chart(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """テクニカル指標チャートを作成"""
        try:
            # サブプロットを作成
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('価格と移動平均', 'RSI', 'MACD'),
                vertical_spacing=0.1,
                row_heights=[0.5, 0.25, 0.25]
            )
            
            # 価格と移動平均
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='価格', line=dict(color='white')), row=1, col=1)
            
            # 移動平均を計算
            if len(data) >= 20:
                ma_20 = data['Close'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(x=data.index, y=ma_20, name='MA20', line=dict(color='orange')), row=1, col=1)
            
            if len(data) >= 50:
                ma_50 = data['Close'].rolling(window=50).mean()
                fig.add_trace(go.Scatter(x=data.index, y=ma_50, name='MA50', line=dict(color='red')), row=1, col=1)
            
            # RSIを計算
            if len(data) >= 14:
                rsi = self._calculate_rsi(data['Close'])
                fig.add_trace(go.Scatter(x=data.index, y=rsi, name='RSI', line=dict(color='purple')), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            # MACDを計算
            if len(data) >= 26:
                macd, macd_signal, macd_hist = self._calculate_macd(data['Close'])
                fig.add_trace(go.Scatter(x=data.index, y=macd, name='MACD', line=dict(color='blue')), row=3, col=1)
                fig.add_trace(go.Scatter(x=data.index, y=macd_signal, name='MACD Signal', line=dict(color='red')), row=3, col=1)
                fig.add_trace(go.Bar(x=data.index, y=macd_hist, name='MACD Histogram'), row=3, col=1)
            
            fig.update_layout(
                title=f"{symbol} テクニカル指標",
                template="plotly_dark",
                height=800,
                showlegend=True
            )
            
            return {
                'type': 'plotly',
                'figure': fig,
                'title': f"{symbol} テクニカル指標",
                'description': f"{symbol}のテクニカル指標（移動平均、RSI、MACD）を表示"
            }
            
        except Exception as e:
            self.logger.error(f"テクニカル指標チャート作成エラー: {e}")
            return None
    
    def create_sector_comparison_chart(self, sector_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """セクター比較チャートを作成"""
        try:
            fig = go.Figure()
            
            for sector, data in sector_data.items():
                if not data.empty:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Close'],
                        mode='lines',
                        name=sector
                    ))
            
            fig.update_layout(
                title="セクター別パフォーマンス比較",
                xaxis_title="日付",
                yaxis_title="価格 (円)",
                template="plotly_dark",
                height=400
            )
            
            return {
                'type': 'plotly',
                'figure': fig,
                'title': "セクター別パフォーマンス比較",
                'description': "各セクターのパフォーマンスを比較"
            }
            
        except Exception as e:
            self.logger.error(f"セクター比較チャート作成エラー: {e}")
            return None
    
    def create_performance_metrics_chart(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンス指標チャートを作成"""
        try:
            # メトリクスを棒グラフで表示
            categories = list(metrics.keys())
            values = list(metrics.values())
            
            fig = go.Figure(data=go.Bar(
                x=categories,
                y=values,
                marker_color=['green' if v > 0 else 'red' for v in values]
            ))
            
            fig.update_layout(
                title="パフォーマンス指標",
                xaxis_title="指標",
                yaxis_title="値 (%)",
                template="plotly_dark",
                height=400
            )
            
            return {
                'type': 'plotly',
                'figure': fig,
                'title': "パフォーマンス指標",
                'description': "各種パフォーマンス指標を表示"
            }
            
        except Exception as e:
            self.logger.error(f"パフォーマンス指標チャート作成エラー: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSIを計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACDを計算"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return macd, macd_signal, macd_histogram

class DataAnalyzer:
    """データ分析クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_symbol(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """銘柄を分析"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            info = ticker.info
            
            if data.empty:
                return {'error': 'データが取得できませんでした'}
            
            # 基本統計
            current_price = data['Close'].iloc[-1]
            price_change = current_price - data['Open'].iloc[0]
            price_change_percent = (price_change / data['Open'].iloc[0]) * 100
            
            # ボラティリティ
            daily_returns = data['Close'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100
            
            # 最大ドローダウン
            cumulative_returns = (1 + daily_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            # シャープレシオ
            risk_free_rate = 0.01  # 1%
            excess_returns = daily_returns.mean() * 252 - risk_free_rate
            sharpe_ratio = excess_returns / (daily_returns.std() * np.sqrt(252))
            
            # テクニカル指標
            technical_indicators = self._calculate_technical_indicators(data)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_change': price_change,
                'price_change_percent': price_change_percent,
                'volatility': volatility,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'technical_indicators': technical_indicators,
                'data': data,
                'info': info
            }
            
        except Exception as e:
            self.logger.error(f"銘柄分析エラー {symbol}: {e}")
            return {'error': str(e)}
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """テクニカル指標を計算"""
        try:
            indicators = {}
            
            # RSI
            if len(data) >= 14:
                delta = data['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                indicators['rsi'] = rsi.iloc[-1]
            
            # 移動平均
            if len(data) >= 20:
                indicators['ma_20'] = data['Close'].rolling(window=20).mean().iloc[-1]
            if len(data) >= 50:
                indicators['ma_50'] = data['Close'].rolling(window=50).mean().iloc[-1]
            
            # MACD
            if len(data) >= 26:
                ema_12 = data['Close'].ewm(span=12).mean()
                ema_26 = data['Close'].ewm(span=26).mean()
                macd = ema_12 - ema_26
                macd_signal = macd.ewm(span=9).mean()
                indicators['macd'] = macd.iloc[-1]
                indicators['macd_signal'] = macd_signal.iloc[-1]
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"テクニカル指標計算エラー: {e}")
            return {}

class ReportGenerator:
    """レポート生成クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chart_generator = ChartGenerator()
        self.data_analyzer = DataAnalyzer()
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """テンプレートを読み込み"""
        templates = {
            'default': """
# {title}

**生成日時**: {generated_at}  
**作成者**: {author}  
**分析期間**: {period}  
**対象銘柄**: {symbols}

## エグゼクティブサマリー

{summary}

## 詳細分析

{analysis}

## 推奨事項

{recommendations}

## 免責事項

本レポートは投資アドバイスではありません。投資判断は自己責任で行ってください。
            """,
            'detailed': """
# {title}

## 基本情報
- **生成日時**: {generated_at}
- **作成者**: {author}
- **分析期間**: {period}
- **対象銘柄**: {symbols}

## エグゼクティブサマリー

{summary}

## 市場分析

{market_analysis}

## 個別銘柄分析

{individual_analysis}

## テクニカル分析

{technical_analysis}

## リスク分析

{risk_analysis}

## 推奨事項

{recommendations}

## 付録

{appendix}

## 免責事項

本レポートは投資アドバイスではありません。投資判断は自己責任で行ってください。
            """
        }
        return templates
    
    def generate_report(self, symbols: List[str], period: str = "1y", 
                       report_type: str = "default", language: str = "ja") -> Dict[str, Any]:
        """レポートを生成"""
        try:
            metadata = ReportMetadata(
                title=f"株価分析レポート - {datetime.now().strftime('%Y年%m月%d日')}",
                author="株価分析ツール",
                generated_at=datetime.now(),
                report_type=report_type,
                symbols=symbols,
                period=period,
                language=language
            )
            
            # データを分析
            analysis_results = {}
            for symbol in symbols:
                analysis_results[symbol] = self.data_analyzer.analyze_symbol(symbol, period)
            
            # レポートセクションを生成
            sections = self._generate_sections(analysis_results, metadata)
            
            # レポートを組み立て
            report_content = self._assemble_report(sections, metadata)
            
            return {
                'metadata': metadata,
                'sections': sections,
                'content': report_content,
                'charts': self._extract_charts(sections),
                'tables': self._extract_tables(sections)
            }
            
        except Exception as e:
            self.logger.error(f"レポート生成エラー: {e}")
            return {'error': str(e)}
    
    def _generate_sections(self, analysis_results: Dict[str, Any], 
                          metadata: ReportMetadata) -> List[ReportSection]:
        """レポートセクションを生成"""
        sections = []
        
        # サマリーセクション
        summary_section = self._create_summary_section(analysis_results, metadata)
        sections.append(summary_section)
        
        # 個別分析セクション
        for symbol, result in analysis_results.items():
            if 'error' not in result:
                individual_section = self._create_individual_section(symbol, result, metadata)
                sections.append(individual_section)
        
        # 推奨事項セクション
        recommendations_section = self._create_recommendations_section(analysis_results, metadata)
        sections.append(recommendations_section)
        
        return sections
    
    def _create_summary_section(self, analysis_results: Dict[str, Any], 
                               metadata: ReportMetadata) -> ReportSection:
        """サマリーセクションを作成"""
        try:
            # 全体の統計を計算
            total_symbols = len(analysis_results)
            successful_analyses = len([r for r in analysis_results.values() if 'error' not in r])
            
            if successful_analyses > 0:
                avg_return = np.mean([r['price_change_percent'] for r in analysis_results.values() if 'error' not in r])
                avg_volatility = np.mean([r['volatility'] for r in analysis_results.values() if 'error' not in r])
            else:
                avg_return = 0
                avg_volatility = 0
            
            # サマリーテキスト
            summary_text = f"""
本レポートは{total_symbols}銘柄の分析結果をまとめたものです。

**主要な発見事項:**
- 分析対象銘柄数: {total_symbols}銘柄
- 成功した分析: {successful_analyses}銘柄
- 平均リターン: {avg_return:.2f}%
- 平均ボラティリティ: {avg_volatility:.2f}%

**期間**: {metadata.period}
**分析日時**: {metadata.generated_at.strftime('%Y年%m月%d日 %H:%M')}
            """
            
            # メトリクス
            metrics = {
                '総銘柄数': total_symbols,
                '成功分析数': successful_analyses,
                '平均リターン(%)': avg_return,
                '平均ボラティリティ(%)': avg_volatility
            }
            
            return ReportSection(
                title="エグゼクティブサマリー",
                content=summary_text,
                charts=[],
                tables=[],
                metrics=metrics,
                section_type='summary'
            )
            
        except Exception as e:
            self.logger.error(f"サマリーセクション作成エラー: {e}")
            return ReportSection(
                title="エグゼクティブサマリー",
                content="サマリーの生成中にエラーが発生しました。",
                charts=[],
                tables=[],
                metrics={},
                section_type='summary'
            )
    
    def _create_individual_section(self, symbol: str, result: Dict[str, Any], 
                                 metadata: ReportMetadata) -> ReportSection:
        """個別銘柄セクションを作成"""
        try:
            # 分析結果から情報を抽出
            current_price = result['current_price']
            price_change = result['price_change']
            price_change_percent = result['price_change_percent']
            volatility = result['volatility']
            max_drawdown = result['max_drawdown']
            sharpe_ratio = result['sharpe_ratio']
            
            # テキストコンテンツ
            content = f"""
## {symbol} 分析結果

**現在価格**: ¥{current_price:,.0f}  
**期間変動**: {price_change:+,.0f}円 ({price_change_percent:+.2f}%)  
**ボラティリティ**: {volatility:.2f}%  
**最大ドローダウン**: {max_drawdown:.2f}%  
**シャープレシオ**: {sharpe_ratio:.2f}

### 投資判断
"""
            
            # 投資判断を追加
            if price_change_percent > 10:
                content += "- 強い上昇トレンドを示しています\n"
            elif price_change_percent < -10:
                content += "- 下落トレンドにあります\n"
            else:
                content += "- 横ばい圏での推移です\n"
            
            if volatility > 30:
                content += "- 高ボラティリティ銘柄です\n"
            elif volatility < 15:
                content += "- 低ボラティリティ銘柄です\n"
            else:
                content += "- 中程度のボラティリティです\n"
            
            # チャートを生成
            charts = []
            if 'data' in result and not result['data'].empty:
                price_chart = self.chart_generator.create_price_chart(result['data'], symbol)
                if price_chart:
                    charts.append(price_chart)
                
                volume_chart = self.chart_generator.create_volume_chart(result['data'], symbol)
                if volume_chart:
                    charts.append(volume_chart)
                
                technical_chart = self.chart_generator.create_technical_indicators_chart(result['data'], symbol)
                if technical_chart:
                    charts.append(technical_chart)
            
            # メトリクス
            metrics = {
                '現在価格': current_price,
                '期間変動(%)': price_change_percent,
                'ボラティリティ(%)': volatility,
                '最大ドローダウン(%)': max_drawdown,
                'シャープレシオ': sharpe_ratio
            }
            
            return ReportSection(
                title=f"{symbol} 詳細分析",
                content=content,
                charts=charts,
                tables=[],
                metrics=metrics,
                section_type='analysis'
            )
            
        except Exception as e:
            self.logger.error(f"個別セクション作成エラー {symbol}: {e}")
            return ReportSection(
                title=f"{symbol} 詳細分析",
                content=f"{symbol}の分析中にエラーが発生しました。",
                charts=[],
                tables=[],
                metrics={},
                section_type='analysis'
            )
    
    def _create_recommendations_section(self, analysis_results: Dict[str, Any], 
                                      metadata: ReportMetadata) -> ReportSection:
        """推奨事項セクションを作成"""
        try:
            # 推奨銘柄を選定
            recommendations = []
            
            for symbol, result in analysis_results.items():
                if 'error' not in result:
                    score = 0
                    reasons = []
                    
                    # スコアリング
                    if result['price_change_percent'] > 5:
                        score += 2
                        reasons.append("強い上昇トレンド")
                    
                    if result['volatility'] < 20:
                        score += 1
                        reasons.append("低ボラティリティ")
                    
                    if result['sharpe_ratio'] > 1:
                        score += 2
                        reasons.append("良好なリスク調整リターン")
                    
                    if result['max_drawdown'] > -10:
                        score += 1
                        reasons.append("限定的なドローダウン")
                    
                    if score >= 3:
                        recommendations.append({
                            'symbol': symbol,
                            'score': score,
                            'reasons': reasons,
                            'action': 'BUY'
                        })
                    elif score <= 1:
                        recommendations.append({
                            'symbol': symbol,
                            'score': score,
                            'reasons': reasons,
                            'action': 'SELL'
                        })
                    else:
                        recommendations.append({
                            'symbol': symbol,
                            'score': score,
                            'reasons': reasons,
                            'action': 'HOLD'
                        })
            
            # 推奨事項テキスト
            content = "## 投資推奨事項\n\n"
            
            buy_recommendations = [r for r in recommendations if r['action'] == 'BUY']
            sell_recommendations = [r for r in recommendations if r['action'] == 'SELL']
            hold_recommendations = [r for r in recommendations if r['action'] == 'HOLD']
            
            if buy_recommendations:
                content += "### 🟢 買い推奨銘柄\n"
                for rec in buy_recommendations:
                    content += f"- **{rec['symbol']}**: {', '.join(rec['reasons'])}\n"
            
            if sell_recommendations:
                content += "\n### 🔴 売り推奨銘柄\n"
                for rec in sell_recommendations:
                    content += f"- **{rec['symbol']}**: {', '.join(rec['reasons'])}\n"
            
            if hold_recommendations:
                content += "\n### 🟡 ホールド推奨銘柄\n"
                for rec in hold_recommendations:
                    content += f"- **{rec['symbol']}**: {', '.join(rec['reasons'])}\n"
            
            # 推奨事項テーブル
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                rec_df = rec_df[['symbol', 'action', 'score', 'reasons']]
                rec_df['reasons'] = rec_df['reasons'].apply(lambda x: ', '.join(x))
            else:
                rec_df = pd.DataFrame()
            
            return ReportSection(
                title="投資推奨事項",
                content=content,
                charts=[],
                tables=[rec_df] if not rec_df.empty else [],
                metrics={'推奨銘柄数': len(recommendations)},
                section_type='recommendations'
            )
            
        except Exception as e:
            self.logger.error(f"推奨事項セクション作成エラー: {e}")
            return ReportSection(
                title="投資推奨事項",
                content="推奨事項の生成中にエラーが発生しました。",
                charts=[],
                tables=[],
                metrics={},
                section_type='recommendations'
            )
    
    def _assemble_report(self, sections: List[ReportSection], 
                        metadata: ReportMetadata) -> str:
        """レポートを組み立て"""
        try:
            template = self.templates.get(metadata.template, self.templates['default'])
            
            # セクションコンテンツを結合
            summary_content = ""
            analysis_content = ""
            recommendations_content = ""
            
            for section in sections:
                if section.section_type == 'summary':
                    summary_content = section.content
                elif section.section_type == 'analysis':
                    analysis_content += section.content + "\n\n"
                elif section.section_type == 'recommendations':
                    recommendations_content = section.content
            
            # テンプレートを埋める
            report_content = template.format(
                title=metadata.title,
                generated_at=metadata.generated_at.strftime('%Y年%m月%d日 %H:%M'),
                author=metadata.author,
                period=metadata.period,
                symbols=', '.join(metadata.symbols),
                summary=summary_content,
                analysis=analysis_content,
                recommendations=recommendations_content,
                market_analysis="市場分析は個別銘柄分析に含まれています。",
                individual_analysis=analysis_content,
                technical_analysis="テクニカル分析は個別銘柄分析に含まれています。",
                risk_analysis="リスク分析は個別銘柄分析に含まれています。",
                appendix="詳細なデータは個別銘柄分析セクションを参照してください。"
            )
            
            return report_content
            
        except Exception as e:
            self.logger.error(f"レポート組み立てエラー: {e}")
            return f"レポートの生成中にエラーが発生しました: {e}"
    
    def _extract_charts(self, sections: List[ReportSection]) -> List[Dict[str, Any]]:
        """チャートを抽出"""
        charts = []
        for section in sections:
            charts.extend(section.charts)
        return charts
    
    def _extract_tables(self, sections: List[ReportSection]) -> List[pd.DataFrame]:
        """テーブルを抽出"""
        tables = []
        for section in sections:
            tables.extend(section.tables)
        return tables
    
    def export_report(self, report_data: Dict[str, Any], format: str = 'html', 
                     filename: Optional[str] = None) -> str:
        """レポートをエクスポート"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"stock_report_{timestamp}"
            
            if format == 'html':
                return self._export_html(report_data, filename)
            elif format == 'pdf':
                return self._export_pdf(report_data, filename)
            elif format == 'markdown':
                return self._export_markdown(report_data, filename)
            else:
                raise ValueError(f"未対応のフォーマット: {format}")
                
        except Exception as e:
            self.logger.error(f"レポートエクスポートエラー: {e}")
            return f"エクスポートエラー: {e}"
    
    def _export_html(self, report_data: Dict[str, Any], filename: str) -> str:
        """HTML形式でエクスポート"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['metadata'].title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        h3 {{ color: #888; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #007acc; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    {report_data['content'].replace(chr(10), '<br>')}
</body>
</html>
            """
            
            filepath = f"{filename}.html"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return f"HTMLレポートを保存しました: {filepath}"
            
        except Exception as e:
            self.logger.error(f"HTMLエクスポートエラー: {e}")
            return f"HTMLエクスポートエラー: {e}"
    
    def _export_markdown(self, report_data: Dict[str, Any], filename: str) -> str:
        """Markdown形式でエクスポート"""
        try:
            filepath = f"{filename}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_data['content'])
            
            return f"Markdownレポートを保存しました: {filepath}"
            
        except Exception as e:
            self.logger.error(f"Markdownエクスポートエラー: {e}")
            return f"Markdownエクスポートエラー: {e}"
    
    def _export_pdf(self, report_data: Dict[str, Any], filename: str) -> str:
        """PDF形式でエクスポート（簡易版）"""
        try:
            # HTMLをPDFに変換（簡易版）
            html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{report_data['metadata'].title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    {report_data['content'].replace(chr(10), '<br>')}
</body>
</html>
            """
            
            # PDF生成は外部ライブラリが必要
            return "PDFエクスポートは外部ライブラリが必要です。HTMLまたはMarkdown形式をご利用ください。"
            
        except Exception as e:
            self.logger.error(f"PDFエクスポートエラー: {e}")
            return f"PDFエクスポートエラー: {e}"

# グローバルインスタンス
report_generator = ReportGenerator()