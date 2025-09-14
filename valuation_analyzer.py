import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class ValuationAnalyzer:
    """企業価値評価を行うクラス"""
    
    def __init__(self):
        self.risk_free_rate = 0.01  # リスクフリーレート（1%）
        self.market_risk_premium = 0.06  # マーケットリスクプレミアム（6%）
    
    def calculate_dcf_valuation(self, stock_data: Dict, metrics: Dict) -> Dict:
        """DCF（割引キャッシュフロー）モデルによる企業価値評価"""
        try:
            if not stock_data or not metrics:
                return None
            
            data = stock_data['data']
            if data.empty:
                return None
            
            # 現在価格と基本情報
            current_price = data['Close'].iloc[-1]
            market_cap = metrics.get('market_cap', 0)
            
            # 成長率の推定（過去の価格変動から）
            price_growth_rates = []
            for period in [20, 60, 120]:  # 1ヶ月、3ヶ月、6ヶ月
                if len(data) >= period:
                    old_price = data['Close'].iloc[-period]
                    growth_rate = (current_price - old_price) / old_price
                    price_growth_rates.append(growth_rate)
            
            # 平均成長率
            avg_growth_rate = np.mean(price_growth_rates) if price_growth_rates else 0.05
            
            # 将来成長率の設定（保守的）
            short_term_growth = min(0.15, max(0.02, avg_growth_rate * 0.8))  # 短期成長率
            long_term_growth = 0.03  # 長期成長率（3%）
            
            # 割引率の計算（CAPMモデル）
            beta = self._estimate_beta(data)
            discount_rate = self.risk_free_rate + beta * self.market_risk_premium
            
            # 将来キャッシュフローの推定
            years = 10
            cash_flows = []
            
            # 現在のキャッシュフロー（市場価値の5%と仮定）
            current_cash_flow = market_cap * 0.05
            
            for year in range(1, years + 1):
                if year <= 5:
                    # 短期成長率適用
                    growth = short_term_growth
                else:
                    # 長期成長率適用
                    growth = long_term_growth
                
                future_cash_flow = current_cash_flow * ((1 + growth) ** year)
                discounted_cash_flow = future_cash_flow / ((1 + discount_rate) ** year)
                cash_flows.append(discounted_cash_flow)
            
            # 企業価値計算
            present_value = sum(cash_flows)
            terminal_value = (cash_flows[-1] * (1 + long_term_growth)) / (discount_rate - long_term_growth)
            terminal_value_discounted = terminal_value / ((1 + discount_rate) ** years)
            
            total_enterprise_value = present_value + terminal_value_discounted
            
            # 1株当たりの理論価格
            shares_outstanding = market_cap / current_price if current_price > 0 else 1
            theoretical_price = total_enterprise_value / shares_outstanding
            
            # 割安・割高判定
            price_ratio = theoretical_price / current_price if current_price > 0 else 1
            
            if price_ratio > 1.2:
                valuation_status = 'undervalued'
                valuation_desc = '割安'
            elif price_ratio < 0.8:
                valuation_status = 'overvalued'
                valuation_desc = '割高'
            else:
                valuation_status = 'fair'
                valuation_desc = '適正'
            
            return {
                'theoretical_price': theoretical_price,
                'current_price': current_price,
                'price_ratio': price_ratio,
                'valuation_status': valuation_status,
                'valuation_description': valuation_desc,
                'enterprise_value': total_enterprise_value,
                'discount_rate': discount_rate,
                'beta': beta,
                'growth_assumptions': {
                    'short_term_growth': short_term_growth,
                    'long_term_growth': long_term_growth
                },
                'margin_of_safety': (price_ratio - 1) * 100
            }
            
        except Exception as e:
            print(f"DCF評価エラー: {e}")
            return None
    
    def _estimate_beta(self, data: pd.DataFrame) -> float:
        """ベータ値を推定（日経平均との相関から）"""
        try:
            if len(data) < 20:
                return 1.0
            
            # 日経平均のデータを取得
            nikkei = yf.download('^N225', start=data.index[0], end=data.index[-1], progress=False)
            
            if nikkei.empty:
                return 1.0
            
            # リターン計算
            stock_returns = data['Close'].pct_change().dropna()
            nikkei_returns = nikkei['Close'].pct_change().dropna()
            
            # 共通の日付でデータを揃える
            common_dates = stock_returns.index.intersection(nikkei_returns.index)
            if len(common_dates) < 10:
                return 1.0
            
            stock_returns_aligned = stock_returns.loc[common_dates]
            nikkei_returns_aligned = nikkei_returns.loc[common_dates]
            
            # ベータ計算
            covariance = np.cov(stock_returns_aligned, nikkei_returns_aligned)[0, 1]
            nikkei_variance = np.var(nikkei_returns_aligned)
            
            beta = covariance / nikkei_variance if nikkei_variance > 0 else 1.0
            
            # ベータ値を合理的な範囲に制限
            return max(0.1, min(3.0, beta))
            
        except Exception as e:
            print(f"ベータ推定エラー: {e}")
            return 1.0
    
    def calculate_relative_valuation(self, metrics: Dict, sector: str) -> Dict:
        """相対価値評価を実行"""
        try:
            if not metrics:
                return None
            
            # 業界平均倍率（簡易版）
            industry_multiples = {
                'IT・通信': {'pe_avg': 25.0, 'pb_avg': 3.5, 'ps_avg': 5.0},
                '金融': {'pe_avg': 12.0, 'pb_avg': 0.8, 'ps_avg': 2.0},
                '製造業': {'pe_avg': 18.0, 'pb_avg': 1.2, 'ps_avg': 1.5},
                'ヘルスケア': {'pe_avg': 30.0, 'pb_avg': 4.0, 'ps_avg': 8.0},
                '消費財': {'pe_avg': 20.0, 'pb_avg': 2.0, 'ps_avg': 2.5},
                'エネルギー': {'pe_avg': 15.0, 'pb_avg': 1.0, 'ps_avg': 1.0},
                '公益': {'pe_avg': 16.0, 'pb_avg': 1.1, 'ps_avg': 1.2},
                '素材': {'pe_avg': 14.0, 'pb_avg': 0.9, 'ps_avg': 1.0}
            }
            
            industry_avg = industry_multiples.get(sector, industry_multiples['製造業'])
            
            # 現在の倍率
            current_pe = metrics.get('pe_ratio', 0)
            current_pb = metrics.get('pb_ratio', 0)
            current_price = metrics.get('current_price', 0)
            
            # 理論価格計算
            # PERベース
            if current_pe > 0 and industry_avg['pe_avg'] > 0:
                # EPS推定（現在価格 / PER）
                estimated_eps = current_price / current_pe
                fair_price_pe = estimated_eps * industry_avg['pe_avg']
            else:
                fair_price_pe = current_price
            
            # PBRベース
            if current_pb > 0 and industry_avg['pb_avg'] > 0:
                # BPS推定（現在価格 / PBR）
                estimated_bps = current_price / current_pb
                fair_price_pb = estimated_bps * industry_avg['pb_avg']
            else:
                fair_price_pb = current_price
            
            # 平均理論価格
            fair_price_avg = (fair_price_pe + fair_price_pb) / 2
            
            # 割安・割高判定
            if fair_price_avg > current_price * 1.2:
                relative_status = 'undervalued'
                relative_desc = '業界平均より割安'
            elif fair_price_avg < current_price * 0.8:
                relative_status = 'overvalued'
                relative_desc = '業界平均より割高'
            else:
                relative_status = 'fair'
                relative_desc = '業界平均と同等'
            
            return {
                'fair_price_pe': fair_price_pe,
                'fair_price_pb': fair_price_pb,
                'fair_price_avg': fair_price_avg,
                'current_price': current_price,
                'relative_status': relative_status,
                'relative_description': relative_desc,
                'pe_vs_industry': current_pe / industry_avg['pe_avg'] if industry_avg['pe_avg'] > 0 else 1,
                'pb_vs_industry': current_pb / industry_avg['pb_avg'] if industry_avg['pb_avg'] > 0 else 1,
                'industry_averages': industry_avg
            }
            
        except Exception as e:
            print(f"相対価値評価エラー: {e}")
            return None
    
    def calculate_dividend_sustainability(self, metrics: Dict, stock_data: Dict) -> Dict:
        """配当持続可能性分析"""
        try:
            if not metrics or not stock_data:
                return None
            
            dividend_yield = metrics.get('dividend_yield', 0)
            roe = metrics.get('roe', 0)
            debt_ratio = metrics.get('debt_to_equity', 0)
            pe_ratio = metrics.get('pe_ratio', 0)
            
            # 配当持続可能性スコア計算
            sustainability_score = 0
            
            # ROEスコア（高いほど配当余力あり）
            if roe > 15:
                sustainability_score += 30
            elif roe > 10:
                sustainability_score += 20
            elif roe > 5:
                sustainability_score += 10
            
            # 負債比率スコア（低いほど安定）
            if debt_ratio < 30:
                sustainability_score += 25
            elif debt_ratio < 50:
                sustainability_score += 15
            elif debt_ratio < 70:
                sustainability_score += 10
            
            # 配当利回リスコア（適正範囲内で高得点）
            if 2 <= dividend_yield <= 4:
                sustainability_score += 25
            elif 1 <= dividend_yield <= 5:
                sustainability_score += 15
            elif dividend_yield > 5:
                sustainability_score += 5  # 高すぎる配当は持続性に疑問
            
            # PERスコア（適正範囲内で高得点）
            if 10 <= pe_ratio <= 20:
                sustainability_score += 20
            elif 5 <= pe_ratio <= 30:
                sustainability_score += 10
            
            # 持続可能性レベル判定
            if sustainability_score >= 80:
                sustainability_level = 'very_high'
                sustainability_desc = '非常に高い'
            elif sustainability_score >= 65:
                sustainability_level = 'high'
                sustainability_desc = '高い'
            elif sustainability_score >= 50:
                sustainability_level = 'moderate'
                sustainability_desc = '中程度'
            elif sustainability_score >= 35:
                sustainability_level = 'low'
                sustainability_desc = '低い'
            else:
                sustainability_level = 'very_low'
                sustainability_desc = '非常に低い'
            
            # 配当カバレッジ比率（推定）
            # 配当利回りから配当支払い額を推定し、利益に対する比率を計算
            estimated_dividend_payout_ratio = dividend_yield * pe_ratio / 100 if pe_ratio > 0 else 0
            
            return {
                'sustainability_score': sustainability_score,
                'sustainability_level': sustainability_level,
                'sustainability_description': sustainability_desc,
                'estimated_payout_ratio': estimated_dividend_payout_ratio,
                'dividend_risk_factors': self._identify_dividend_risks(metrics),
                'recommendation': self._get_dividend_recommendation(sustainability_level)
            }
            
        except Exception as e:
            print(f"配当持続可能性分析エラー: {e}")
            return None
    
    def _identify_dividend_risks(self, metrics: Dict) -> List[str]:
        """配当リスク要因を特定"""
        risks = []
        
        if metrics.get('debt_to_equity', 0) > 60:
            risks.append('高負債比率')
        
        if metrics.get('roe', 0) < 5:
            risks.append('低収益性')
        
        if metrics.get('dividend_yield', 0) > 6:
            risks.append('過度に高い配当利回り')
        
        if metrics.get('pe_ratio', 0) > 30:
            risks.append('高PER（収益性の疑問）')
        
        return risks
    
    def _get_dividend_recommendation(self, sustainability_level: str) -> str:
        """配当持続可能性に基づく推奨"""
        recommendations = {
            'very_high': '配当投資に最適 - 安定した配当継続が期待できる',
            'high': '配当投資に適している - 継続的な配当が期待できる',
            'moderate': '配当投資に注意 - 他の要因も考慮が必要',
            'low': '配当投資に慎重 - 配当カットのリスクあり',
            'very_low': '配当投資非推奨 - 配当持続性に重大な懸念'
        }
        return recommendations.get(sustainability_level, '要検討')
    
    def comprehensive_valuation_analysis(self, stock_data: Dict, metrics: Dict, sector: str) -> Dict:
        """包括的な企業価値評価を実行"""
        try:
            # 各評価手法を実行
            dcf_analysis = self.calculate_dcf_valuation(stock_data, metrics)
            relative_analysis = self.calculate_relative_valuation(metrics, sector)
            dividend_analysis = self.calculate_dividend_sustainability(metrics, stock_data)
            
            # 総合評価スコア計算
            scores = []
            
            if dcf_analysis:
                # DCF評価スコア
                price_ratio = dcf_analysis['price_ratio']
                if price_ratio > 1.2:
                    dcf_score = 90
                elif price_ratio > 1.0:
                    dcf_score = 70
                elif price_ratio > 0.8:
                    dcf_score = 50
                else:
                    dcf_score = 30
                scores.append(dcf_score)
            
            if relative_analysis:
                # 相対評価スコア
                if relative_analysis['relative_status'] == 'undervalued':
                    relative_score = 85
                elif relative_analysis['relative_status'] == 'fair':
                    relative_score = 60
                else:
                    relative_score = 35
                scores.append(relative_score)
            
            if dividend_analysis:
                # 配当持続可能性スコア
                scores.append(dividend_analysis['sustainability_score'])
            
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
                'dcf_analysis': dcf_analysis,
                'relative_analysis': relative_analysis,
                'dividend_analysis': dividend_analysis,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的企業価値評価エラー: {e}")
            return None
