import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class AdvancedFundamentalAnalyzer:
    """高度なファンダメンタル分析を行うクラス"""
    
    def __init__(self):
        self.industry_averages = self._load_industry_averages()
    
    def _load_industry_averages(self) -> Dict:
        """業界平均値をロード（簡易版）"""
        return {
            'IT・通信': {
                'pe_avg': 25.0, 'pb_avg': 3.5, 'roe_avg': 15.0,
                'debt_ratio_avg': 30.0, 'dividend_yield_avg': 1.5
            },
            '金融': {
                'pe_avg': 12.0, 'pb_avg': 0.8, 'roe_avg': 8.0,
                'debt_ratio_avg': 80.0, 'dividend_yield_avg': 3.0
            },
            '製造業': {
                'pe_avg': 18.0, 'pb_avg': 1.2, 'roe_avg': 12.0,
                'debt_ratio_avg': 40.0, 'dividend_yield_avg': 2.5
            },
            'ヘルスケア': {
                'pe_avg': 30.0, 'pb_avg': 4.0, 'roe_avg': 18.0,
                'debt_ratio_avg': 25.0, 'dividend_yield_avg': 1.0
            },
            '消費財': {
                'pe_avg': 20.0, 'pb_avg': 2.0, 'roe_avg': 14.0,
                'debt_ratio_avg': 35.0, 'dividend_yield_avg': 2.0
            },
            'エネルギー': {
                'pe_avg': 15.0, 'pb_avg': 1.0, 'roe_avg': 10.0,
                'debt_ratio_avg': 50.0, 'dividend_yield_avg': 4.0
            },
            '公益': {
                'pe_avg': 16.0, 'pb_avg': 1.1, 'roe_avg': 8.0,
                'debt_ratio_avg': 60.0, 'dividend_yield_avg': 3.5
            },
            '素材': {
                'pe_avg': 14.0, 'pb_avg': 0.9, 'roe_avg': 9.0,
                'debt_ratio_avg': 45.0, 'dividend_yield_avg': 2.8
            }
        }
    
    def calculate_cash_flow_metrics(self, stock_data: Dict) -> Dict:
        """キャッシュフロー分析を実行"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty:
                return None
            
            # 基本的なキャッシュフロー指標を計算
            # 実際のキャッシュフローデータはyfinanceでは限定的なため、
            # 価格データから推定値を計算
            
            # 価格変動率（流動性の指標として使用）
            price_volatility = data['Close'].pct_change().std() * np.sqrt(252)
            
            # 出来高分析
            avg_volume = data['Volume'].mean()
            volume_volatility = data['Volume'].pct_change().std()
            
            # 流動性スコア（出来高と価格変動の組み合わせ）
            liquidity_score = min(100, (avg_volume / 1000000) * (1 / (price_volatility + 0.01)))
            
            return {
                'price_volatility': price_volatility,
                'avg_volume': avg_volume,
                'volume_volatility': volume_volatility,
                'liquidity_score': liquidity_score,
                'cash_flow_strength': 'high' if liquidity_score > 50 else 'medium' if liquidity_score > 25 else 'low'
            }
            
        except Exception as e:
            print(f"キャッシュフロー分析エラー: {e}")
            return None
    
    def calculate_financial_health_score(self, metrics: Dict) -> Dict:
        """財務健全性スコアを計算（Altman Z-Score風）"""
        try:
            if not metrics:
                return None
            
            # 各指標のスコアを計算（0-100点）
            scores = {}
            
            # PERスコア（適正範囲内で高得点）
            pe_ratio = metrics.get('pe_ratio', 0)
            if 5 <= pe_ratio <= 20:
                scores['pe_score'] = 100 - abs(pe_ratio - 12.5) * 4
            else:
                scores['pe_score'] = max(0, 50 - abs(pe_ratio - 12.5) * 2)
            
            # PBRスコア
            pb_ratio = metrics.get('pb_ratio', 0)
            if 0.5 <= pb_ratio <= 2.0:
                scores['pb_score'] = 100 - abs(pb_ratio - 1.25) * 40
            else:
                scores['pb_score'] = max(0, 50 - abs(pb_ratio - 1.25) * 20)
            
            # ROEスコア
            roe = metrics.get('roe', 0)
            scores['roe_score'] = min(100, roe * 5)  # ROE 20%で満点
            
            # 負債比率スコア（低いほど高得点）
            debt_ratio = metrics.get('debt_to_equity', 0)
            scores['debt_score'] = max(0, 100 - debt_ratio * 2)
            
            # 配当利回リスコア
            dividend_yield = metrics.get('dividend_yield', 0)
            scores['dividend_score'] = min(100, dividend_yield * 25)  # 4%で満点
            
            # 総合スコア計算（重み付き平均）
            weights = {
                'pe_score': 0.2,
                'pb_score': 0.2,
                'roe_score': 0.25,
                'debt_score': 0.2,
                'dividend_score': 0.15
            }
            
            total_score = sum(scores[key] * weights[key] for key in scores.keys())
            
            # 健全性レベル判定
            if total_score >= 80:
                health_level = 'excellent'
                health_desc = '優秀'
            elif total_score >= 65:
                health_level = 'good'
                health_desc = '良好'
            elif total_score >= 50:
                health_level = 'average'
                health_desc = '平均'
            elif total_score >= 35:
                health_level = 'poor'
                health_desc = '要注意'
            else:
                health_level = 'critical'
                health_desc = '危険'
            
            return {
                'total_score': total_score,
                'health_level': health_level,
                'health_description': health_desc,
                'individual_scores': scores,
                'recommendation': self._get_health_recommendation(health_level)
            }
            
        except Exception as e:
            print(f"財務健全性スコア計算エラー: {e}")
            return None
    
    def _get_health_recommendation(self, health_level: str) -> str:
        """健全性レベルに基づく推奨アクション"""
        recommendations = {
            'excellent': '強く推奨 - 優良企業として長期投資に適している',
            'good': '推奨 - 安定した財務基盤を持つ企業',
            'average': '要検討 - 他の要因も考慮して判断',
            'poor': '注意 - 財務状況の改善を要する',
            'critical': '非推奨 - 投資リスクが高い'
        }
        return recommendations.get(health_level, '要検討')
    
    def calculate_industry_comparison(self, metrics: Dict, sector: str) -> Dict:
        """業界比較分析を実行"""
        try:
            if not metrics or not sector:
                return None
            
            industry_avg = self.industry_averages.get(sector, self.industry_averages['製造業'])
            
            comparisons = {}
            
            # 各指標の業界平均との比較
            pe_ratio = metrics.get('pe_ratio', 0)
            pe_avg = industry_avg['pe_avg']
            comparisons['pe_vs_industry'] = {
                'value': pe_ratio,
                'industry_avg': pe_avg,
                'difference': pe_ratio - pe_avg,
                'percentile': self._calculate_percentile(pe_ratio, pe_avg, 'lower_better'),
                'status': 'undervalued' if pe_ratio < pe_avg * 0.8 else 'overvalued' if pe_ratio > pe_avg * 1.2 else 'fair'
            }
            
            pb_ratio = metrics.get('pb_ratio', 0)
            pb_avg = industry_avg['pb_avg']
            comparisons['pb_vs_industry'] = {
                'value': pb_ratio,
                'industry_avg': pb_avg,
                'difference': pb_ratio - pb_avg,
                'percentile': self._calculate_percentile(pb_ratio, pb_avg, 'lower_better'),
                'status': 'undervalued' if pb_ratio < pb_avg * 0.8 else 'overvalued' if pb_ratio > pb_avg * 1.2 else 'fair'
            }
            
            roe = metrics.get('roe', 0)
            roe_avg = industry_avg['roe_avg']
            comparisons['roe_vs_industry'] = {
                'value': roe,
                'industry_avg': roe_avg,
                'difference': roe - roe_avg,
                'percentile': self._calculate_percentile(roe, roe_avg, 'higher_better'),
                'status': 'excellent' if roe > roe_avg * 1.2 else 'poor' if roe < roe_avg * 0.8 else 'average'
            }
            
            debt_ratio = metrics.get('debt_to_equity', 0)
            debt_avg = industry_avg['debt_ratio_avg']
            comparisons['debt_vs_industry'] = {
                'value': debt_ratio,
                'industry_avg': debt_avg,
                'difference': debt_ratio - debt_avg,
                'percentile': self._calculate_percentile(debt_ratio, debt_avg, 'lower_better'),
                'status': 'excellent' if debt_ratio < debt_avg * 0.8 else 'poor' if debt_ratio > debt_avg * 1.2 else 'average'
            }
            
            dividend_yield = metrics.get('dividend_yield', 0)
            div_avg = industry_avg['dividend_yield_avg']
            comparisons['dividend_vs_industry'] = {
                'value': dividend_yield,
                'industry_avg': div_avg,
                'difference': dividend_yield - div_avg,
                'percentile': self._calculate_percentile(dividend_yield, div_avg, 'higher_better'),
                'status': 'excellent' if dividend_yield > div_avg * 1.2 else 'poor' if dividend_yield < div_avg * 0.8 else 'average'
            }
            
            # 総合業界比較スコア
            total_score = sum(comp['percentile'] for comp in comparisons.values()) / len(comparisons)
            
            return {
                'industry': sector,
                'comparisons': comparisons,
                'overall_score': total_score,
                'industry_ranking': self._get_industry_ranking(total_score),
                'competitive_position': self._get_competitive_position(comparisons)
            }
            
        except Exception as e:
            print(f"業界比較分析エラー: {e}")
            return None
    
    def _calculate_percentile(self, value: float, industry_avg: float, direction: str) -> float:
        """業界平均に対するパーセンタイルを計算"""
        if direction == 'lower_better':
            # 低い方が良い指標（PER, PBR, 負債比率）
            if value <= industry_avg * 0.5:
                return 90
            elif value <= industry_avg * 0.8:
                return 75
            elif value <= industry_avg:
                return 60
            elif value <= industry_avg * 1.2:
                return 40
            elif value <= industry_avg * 1.5:
                return 25
            else:
                return 10
        else:
            # 高い方が良い指標（ROE, 配当利回り）
            if value >= industry_avg * 1.5:
                return 90
            elif value >= industry_avg * 1.2:
                return 75
            elif value >= industry_avg:
                return 60
            elif value >= industry_avg * 0.8:
                return 40
            elif value >= industry_avg * 0.5:
                return 25
            else:
                return 10
    
    def _get_industry_ranking(self, score: float) -> str:
        """業界内ランキングを取得"""
        if score >= 80:
            return '業界トップクラス'
        elif score >= 65:
            return '業界上位'
        elif score >= 50:
            return '業界平均'
        elif score >= 35:
            return '業界下位'
        else:
            return '業界最下位'
    
    def _get_competitive_position(self, comparisons: Dict) -> str:
        """競争ポジションを判定"""
        undervalued_count = sum(1 for comp in comparisons.values() 
                              if comp['status'] in ['undervalued', 'excellent'])
        overvalued_count = sum(1 for comp in comparisons.values() 
                             if comp['status'] in ['overvalued', 'poor'])
        
        if undervalued_count >= 3:
            return '競争優位'
        elif overvalued_count >= 3:
            return '競争劣位'
        else:
            return '競争均衡'
    
    def calculate_growth_metrics(self, stock_data: Dict) -> Dict:
        """成長性指標を計算"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 20:
                return None
            
            # 価格成長率（短期・中期・長期）
            current_price = data['Close'].iloc[-1]
            
            # 1ヶ月成長率
            price_1m = data['Close'].iloc[-20] if len(data) >= 20 else data['Close'].iloc[0]
            growth_1m = ((current_price - price_1m) / price_1m) * 100
            
            # 3ヶ月成長率
            price_3m = data['Close'].iloc[-60] if len(data) >= 60 else data['Close'].iloc[0]
            growth_3m = ((current_price - price_3m) / price_3m) * 100
            
            # 6ヶ月成長率
            price_6m = data['Close'].iloc[-120] if len(data) >= 120 else data['Close'].iloc[0]
            growth_6m = ((current_price - price_6m) / price_6m) * 100
            
            # 1年成長率
            price_1y = data['Close'].iloc[0]
            growth_1y = ((current_price - price_1y) / price_1y) * 100
            
            # 成長の一貫性スコア
            growth_rates = [growth_1m, growth_3m, growth_6m, growth_1y]
            positive_growth_count = sum(1 for rate in growth_rates if rate > 0)
            consistency_score = (positive_growth_count / len(growth_rates)) * 100
            
            # 成長トレンド分析
            if all(rate > 0 for rate in growth_rates):
                trend = 'accelerating'
                trend_desc = '加速成長'
            elif growth_1y > growth_6m > growth_3m > growth_1m:
                trend = 'decelerating'
                trend_desc = '減速成長'
            elif growth_1m > growth_3m > growth_6m > growth_1y:
                trend = 'recovering'
                trend_desc = '回復成長'
            else:
                trend = 'volatile'
                trend_desc = '変動成長'
            
            return {
                'growth_1m': growth_1m,
                'growth_3m': growth_3m,
                'growth_6m': growth_6m,
                'growth_1y': growth_1y,
                'consistency_score': consistency_score,
                'trend': trend,
                'trend_description': trend_desc,
                'growth_strength': self._get_growth_strength(growth_1y, consistency_score)
            }
            
        except Exception as e:
            print(f"成長性分析エラー: {e}")
            return None
    
    def _get_growth_strength(self, annual_growth: float, consistency: float) -> str:
        """成長強度を判定"""
        if annual_growth > 20 and consistency > 75:
            return 'very_strong'
        elif annual_growth > 10 and consistency > 60:
            return 'strong'
        elif annual_growth > 0 and consistency > 50:
            return 'moderate'
        elif annual_growth > -10:
            return 'weak'
        else:
            return 'declining'
    
    def comprehensive_fundamental_analysis(self, stock_data: Dict, metrics: Dict, sector: str) -> Dict:
        """包括的なファンダメンタル分析を実行"""
        try:
            # 各分析を実行
            cash_flow_analysis = self.calculate_cash_flow_metrics(stock_data)
            health_analysis = self.calculate_financial_health_score(metrics)
            industry_analysis = self.calculate_industry_comparison(metrics, sector)
            growth_analysis = self.calculate_growth_metrics(stock_data)
            
            # 総合評価スコア計算
            scores = []
            if health_analysis:
                scores.append(health_analysis['total_score'])
            if industry_analysis:
                scores.append(industry_analysis['overall_score'])
            if growth_analysis:
                growth_score = min(100, max(0, growth_analysis['growth_1y'] + 50))
                scores.append(growth_score)
            
            overall_score = sum(scores) / len(scores) if scores else 0
            
            # 投資推奨度
            if overall_score >= 75:
                recommendation = 'strong_buy'
                recommendation_desc = '強く推奨'
            elif overall_score >= 60:
                recommendation = 'buy'
                recommendation_desc = '推奨'
            elif overall_score >= 45:
                recommendation = 'hold'
                recommendation_desc = '保有'
            elif overall_score >= 30:
                recommendation = 'weak_sell'
                recommendation_desc = '弱い売り'
            else:
                recommendation = 'sell'
                recommendation_desc = '売り推奨'
            
            return {
                'overall_score': overall_score,
                'recommendation': recommendation,
                'recommendation_description': recommendation_desc,
                'cash_flow_analysis': cash_flow_analysis,
                'financial_health': health_analysis,
                'industry_comparison': industry_analysis,
                'growth_analysis': growth_analysis,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的ファンダメンタル分析エラー: {e}")
            return None
