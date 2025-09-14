import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class FundamentalScreener:
    """
    ファンダメンタルズ分析に基づく銘柄選定機能
    
    包括的な財務指標分析により、投資価値の高い銘柄を選定します。
    """
    
    def __init__(self):
        # 業界別ベンチマーク（日本市場の平均値）
        self.industry_benchmarks = {
            'Technology': {
                'pe_ratio': 25.0,
                'pb_ratio': 2.5,
                'roe': 12.0,
                'roa': 8.0,
                'debt_to_equity': 0.3,
                'current_ratio': 2.0,
                'profit_margin': 8.0,
                'revenue_growth': 5.0
            },
            'Healthcare': {
                'pe_ratio': 30.0,
                'pb_ratio': 3.0,
                'roe': 15.0,
                'roa': 10.0,
                'debt_to_equity': 0.2,
                'current_ratio': 2.5,
                'profit_margin': 12.0,
                'revenue_growth': 8.0
            },
            'Financial Services': {
                'pe_ratio': 12.0,
                'pb_ratio': 0.8,
                'roe': 8.0,
                'roa': 1.0,
                'debt_to_equity': 2.0,
                'current_ratio': 1.2,
                'profit_margin': 15.0,
                'revenue_growth': 3.0
            },
            'Consumer Cyclical': {
                'pe_ratio': 18.0,
                'pb_ratio': 1.5,
                'roe': 10.0,
                'roa': 6.0,
                'debt_to_equity': 0.5,
                'current_ratio': 1.8,
                'profit_margin': 6.0,
                'revenue_growth': 4.0
            },
            'Industrials': {
                'pe_ratio': 20.0,
                'pb_ratio': 1.8,
                'roe': 11.0,
                'roa': 7.0,
                'debt_to_equity': 0.4,
                'current_ratio': 1.5,
                'profit_margin': 7.0,
                'revenue_growth': 3.0
            },
            'Materials': {
                'pe_ratio': 15.0,
                'pb_ratio': 1.2,
                'roe': 9.0,
                'roa': 5.0,
                'debt_to_equity': 0.6,
                'current_ratio': 1.3,
                'profit_margin': 5.0,
                'revenue_growth': 2.0
            },
            'Energy': {
                'pe_ratio': 12.0,
                'pb_ratio': 1.0,
                'roe': 8.0,
                'roa': 4.0,
                'debt_to_equity': 0.8,
                'current_ratio': 1.2,
                'profit_margin': 4.0,
                'revenue_growth': 1.0
            },
            'Utilities': {
                'pe_ratio': 16.0,
                'pb_ratio': 1.3,
                'roe': 7.0,
                'roa': 3.0,
                'debt_to_equity': 1.0,
                'current_ratio': 1.1,
                'profit_margin': 8.0,
                'revenue_growth': 2.0
            },
            'Consumer Defensive': {
                'pe_ratio': 22.0,
                'pb_ratio': 2.0,
                'roe': 12.0,
                'roa': 8.0,
                'debt_to_equity': 0.3,
                'current_ratio': 2.2,
                'profit_margin': 9.0,
                'revenue_growth': 3.0
            },
            'Communication Services': {
                'pe_ratio': 28.0,
                'pb_ratio': 2.8,
                'roe': 13.0,
                'roa': 9.0,
                'debt_to_equity': 0.4,
                'current_ratio': 1.8,
                'profit_margin': 10.0,
                'revenue_growth': 6.0
            }
        }
        
        # デフォルトベンチマーク（全業界平均）
        self.default_benchmark = {
            'pe_ratio': 20.0,
            'pb_ratio': 1.8,
            'roe': 10.0,
            'roa': 6.0,
            'debt_to_equity': 0.5,
            'current_ratio': 1.8,
            'profit_margin': 7.0,
            'revenue_growth': 4.0
        }
    
    def analyze_fundamentals(self, stock_data: Dict) -> Dict:
        """
        包括的なファンダメンタルズ分析を実行
        
        Args:
            stock_data: 株価データと基本情報
            
        Returns:
            分析結果の辞書
        """
        if not stock_data or not stock_data.get('info'):
            return None
            
        info = stock_data['info']
        data = stock_data['data']
        
        # 基本財務指標の計算
        fundamentals = self._calculate_basic_metrics(info, data)
        
        # 高度な財務指標の計算
        advanced_metrics = self._calculate_advanced_metrics(info, data)
        
        # 業界比較分析
        industry_analysis = self._analyze_industry_comparison(fundamentals, info.get('sector', 'Unknown'))
        
        # 総合スコア計算
        total_score = self._calculate_total_score(fundamentals, advanced_metrics, industry_analysis)
        
        # グレード評価
        grade = self._assign_grade(total_score)
        
        # 投資推奨度
        recommendation = self._generate_recommendation(total_score, fundamentals, advanced_metrics)
        
        return {
            'symbol': stock_data['symbol'],
            'company_name': info.get('longName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'fundamentals': fundamentals,
            'advanced_metrics': advanced_metrics,
            'industry_analysis': industry_analysis,
            'total_score': total_score,
            'grade': grade,
            'recommendation': recommendation,
            'analysis_date': pd.Timestamp.now()
        }
    
    def _calculate_basic_metrics(self, info: Dict, data: pd.DataFrame) -> Dict:
        """基本財務指標を計算"""
        current_price = data['Close'].iloc[-1] if not data.empty else 0
        
        return {
            'current_price': current_price,
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'dividend_yield': (info.get('dividendYield', 0) * 100) if info.get('dividendYield') else 0,
            'roe': (info.get('returnOnEquity', 0) * 100) if info.get('returnOnEquity') else 0,
            'roa': (info.get('returnOnAssets', 0) * 100) if info.get('returnOnAssets') else 0,
            'debt_to_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'profit_margin': (info.get('profitMargins', 0) * 100) if info.get('profitMargins') else 0,
            'revenue_growth': (info.get('revenueGrowth', 0) * 100) if info.get('revenueGrowth') else 0,
            'earnings_growth': (info.get('earningsGrowth', 0) * 100) if info.get('earningsGrowth') else 0,
            'beta': info.get('beta', 1.0)
        }
    
    def _calculate_advanced_metrics(self, info: Dict, data: pd.DataFrame) -> Dict:
        """高度な財務指標を計算"""
        # フリーキャッシュフロー利回り
        fcf_yield = 0
        if info.get('freeCashflow') and info.get('marketCap'):
            fcf_yield = (info['freeCashflow'] / info['marketCap']) * 100
        
        # 配当性向
        payout_ratio = 0
        if info.get('dividendRate') and info.get('trailingEps'):
            payout_ratio = (info['dividendRate'] / info['trailingEps']) * 100
        
        # 自己資本比率
        equity_ratio = 0
        if info.get('totalStockholderEquity') and info.get('totalAssets'):
            equity_ratio = (info['totalStockholderEquity'] / info['totalAssets']) * 100
        
        # 総資産回転率
        asset_turnover = 0
        if info.get('totalRevenue') and info.get('totalAssets'):
            asset_turnover = info['totalRevenue'] / info['totalAssets']
        
        # 在庫回転率
        inventory_turnover = 0
        if info.get('totalRevenue') and info.get('inventory'):
            inventory_turnover = info['totalRevenue'] / info['inventory']
        
        # 売上債権回転率
        receivables_turnover = 0
        if info.get('totalRevenue') and info.get('netReceivables'):
            receivables_turnover = info['totalRevenue'] / info['netReceivables']
        
        return {
            'fcf_yield': fcf_yield,
            'payout_ratio': payout_ratio,
            'equity_ratio': equity_ratio,
            'asset_turnover': asset_turnover,
            'inventory_turnover': inventory_turnover,
            'receivables_turnover': receivables_turnover,
            'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
            'ev_ebitda': info.get('enterpriseToEbitda', 0),
            'ev_sales': info.get('enterpriseToRevenue', 0)
        }
    
    def _analyze_industry_comparison(self, fundamentals: Dict, sector: str) -> Dict:
        """業界比較分析を実行"""
        # 業界ベンチマークを取得
        benchmark = self.industry_benchmarks.get(sector, self.default_benchmark)
        
        comparison = {}
        
        # 各指標の業界比較
        for metric, value in fundamentals.items():
            if metric in benchmark and value > 0:
                benchmark_value = benchmark[metric]
                if benchmark_value > 0:
                    comparison[f"{metric}_vs_industry"] = (value / benchmark_value) * 100
                else:
                    comparison[f"{metric}_vs_industry"] = 100
            else:
                comparison[f"{metric}_vs_industry"] = 100
        
        # 業界内での相対的な位置
        industry_rank = self._calculate_industry_rank(fundamentals, benchmark)
        comparison['industry_rank'] = industry_rank
        
        return comparison
    
    def _calculate_industry_rank(self, fundamentals: Dict, benchmark: Dict) -> str:
        """業界内での相対的な位置を計算"""
        above_benchmark = 0
        total_metrics = 0
        
        for metric, value in fundamentals.items():
            if metric in benchmark and value > 0:
                total_metrics += 1
                if value > benchmark[metric]:
                    above_benchmark += 1
        
        if total_metrics == 0:
            return "不明"
        
        ratio = above_benchmark / total_metrics
        
        if ratio >= 0.8:
            return "業界トップ"
        elif ratio >= 0.6:
            return "業界上位"
        elif ratio >= 0.4:
            return "業界平均"
        elif ratio >= 0.2:
            return "業界下位"
        else:
            return "業界最下位"
    
    def _calculate_total_score(self, fundamentals: Dict, advanced_metrics: Dict, industry_analysis: Dict) -> float:
        """総合スコアを計算（100点満点）"""
        score = 0
        max_score = 100
        
        # 収益性指標（30点）
        profitability_score = 0
        if fundamentals['roe'] > 0:
            profitability_score += min(10, fundamentals['roe'] / 2)  # ROE (10点)
        if fundamentals['roa'] > 0:
            profitability_score += min(10, fundamentals['roa'] / 1.5)  # ROA (10点)
        if fundamentals['profit_margin'] > 0:
            profitability_score += min(10, fundamentals['profit_margin'] / 2)  # 利益率 (10点)
        
        # 成長性指標（25点）
        growth_score = 0
        if fundamentals['revenue_growth'] > 0:
            growth_score += min(15, fundamentals['revenue_growth'] / 2)  # 売上成長率 (15点)
        if fundamentals['earnings_growth'] > 0:
            growth_score += min(10, fundamentals['earnings_growth'] / 3)  # 利益成長率 (10点)
        
        # 財務健全性指標（25点）
        financial_health_score = 0
        if fundamentals['debt_to_equity'] > 0:
            # 負債比率が低いほど高得点
            financial_health_score += max(0, 15 - fundamentals['debt_to_equity'] * 10)  # 負債比率 (15点)
        if fundamentals['current_ratio'] > 0:
            # 流動比率が適切な範囲にあるほど高得点
            if 1.5 <= fundamentals['current_ratio'] <= 3.0:
                financial_health_score += 10  # 流動比率 (10点)
            else:
                financial_health_score += max(0, 10 - abs(fundamentals['current_ratio'] - 2.0) * 2)
        
        # バリュエーション指標（20点）
        valuation_score = 0
        if fundamentals['pe_ratio'] > 0 and fundamentals['pe_ratio'] < 30:
            # PERが適切な範囲にあるほど高得点
            if 10 <= fundamentals['pe_ratio'] <= 20:
                valuation_score += 10  # PER (10点)
            else:
                valuation_score += max(0, 10 - abs(fundamentals['pe_ratio'] - 15) * 0.5)
        
        if fundamentals['pb_ratio'] > 0 and fundamentals['pb_ratio'] < 5:
            # PBRが適切な範囲にあるほど高得点
            if 1.0 <= fundamentals['pb_ratio'] <= 2.0:
                valuation_score += 10  # PBR (10点)
            else:
                valuation_score += max(0, 10 - abs(fundamentals['pb_ratio'] - 1.5) * 3)
        
        # 総合スコア
        total_score = profitability_score + growth_score + financial_health_score + valuation_score
        
        return min(max_score, max(0, total_score))
    
    def _assign_grade(self, score: float) -> str:
        """スコアに基づいてグレードを付与"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        elif score >= 30:
            return "D+"
        elif score >= 20:
            return "D"
        else:
            return "F"
    
    def _generate_recommendation(self, score: float, fundamentals: Dict, advanced_metrics: Dict) -> Dict:
        """投資推奨度を生成"""
        if score >= 80:
            recommendation = "強力買い"
            confidence = "高"
        elif score >= 60:
            recommendation = "買い"
            confidence = "中"
        elif score >= 40:
            recommendation = "中立"
            confidence = "中"
        elif score >= 20:
            recommendation = "売り"
            confidence = "中"
        else:
            recommendation = "強力売り"
            confidence = "高"
        
        # 推奨理由
        reasons = []
        
        if fundamentals['roe'] > 15:
            reasons.append("高いROE")
        if fundamentals['revenue_growth'] > 10:
            reasons.append("高い成長率")
        if fundamentals['debt_to_equity'] < 0.3:
            reasons.append("健全な財務体質")
        if fundamentals['pe_ratio'] < 15 and fundamentals['pe_ratio'] > 0:
            reasons.append("割安なバリュエーション")
        if fundamentals['dividend_yield'] > 3:
            reasons.append("高い配当利回り")
        
        if not reasons:
            reasons.append("総合的な分析結果")
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'reasons': reasons,
            'target_price': self._calculate_target_price(fundamentals),
            'risk_level': self._assess_risk_level(fundamentals, advanced_metrics)
        }
    
    def _calculate_target_price(self, fundamentals: Dict) -> float:
        """目標価格を計算"""
        current_price = fundamentals['current_price']
        
        # 簡易的な目標価格計算（PERベース）
        if fundamentals['pe_ratio'] > 0 and fundamentals['pe_ratio'] < 30:
            # 適正PERを15と仮定
            fair_pe = 15
            if fundamentals['pe_ratio'] < fair_pe:
                # 割安の場合、適正価格まで上昇を期待
                target_price = current_price * (fair_pe / fundamentals['pe_ratio'])
            else:
                # 割高の場合、適正価格まで下落の可能性
                target_price = current_price * (fair_pe / fundamentals['pe_ratio'])
        else:
            target_price = current_price
        
        return target_price
    
    def _assess_risk_level(self, fundamentals: Dict, advanced_metrics: Dict) -> str:
        """リスクレベルを評価"""
        risk_score = 0
        
        # 負債比率によるリスク
        if fundamentals['debt_to_equity'] > 1.0:
            risk_score += 3
        elif fundamentals['debt_to_equity'] > 0.5:
            risk_score += 1
        
        # 流動比率によるリスク
        if fundamentals['current_ratio'] < 1.0:
            risk_score += 3
        elif fundamentals['current_ratio'] < 1.5:
            risk_score += 1
        
        # ベータによるリスク
        if fundamentals['beta'] > 1.5:
            risk_score += 2
        elif fundamentals['beta'] > 1.2:
            risk_score += 1
        
        # 成長率の変動性によるリスク
        if abs(fundamentals['revenue_growth']) > 20:
            risk_score += 2
        elif abs(fundamentals['revenue_growth']) > 10:
            risk_score += 1
        
        if risk_score <= 2:
            return "低"
        elif risk_score <= 4:
            return "中"
        else:
            return "高"
    
    def screen_stocks_by_fundamentals(self, stocks_data: Dict, min_score: float = 60.0) -> pd.DataFrame:
        """
        ファンダメンタルズ分析に基づいて銘柄をスクリーニング
        
        Args:
            stocks_data: 株価データの辞書
            min_score: 最小スコア（デフォルト: 60.0）
            
        Returns:
            スクリーニング結果のDataFrame
        """
        results = []
        
        for stock_name, stock_data in stocks_data.items():
            if stock_data:
                analysis = self.analyze_fundamentals(stock_data)
                if analysis and analysis['total_score'] >= min_score:
                    # DataFrame用のデータを準備
                    result = {
                        'symbol': analysis['symbol'],
                        'company_name': analysis['company_name'],
                        'sector': analysis['sector'],
                        'industry': analysis['industry'],
                        'current_price': analysis['fundamentals']['current_price'],
                        'market_cap': analysis['fundamentals']['market_cap'],
                        'pe_ratio': analysis['fundamentals']['pe_ratio'],
                        'pb_ratio': analysis['fundamentals']['pb_ratio'],
                        'roe': analysis['fundamentals']['roe'],
                        'roa': analysis['fundamentals']['roa'],
                        'debt_to_equity': analysis['fundamentals']['debt_to_equity'],
                        'current_ratio': analysis['fundamentals']['current_ratio'],
                        'profit_margin': analysis['fundamentals']['profit_margin'],
                        'revenue_growth': analysis['fundamentals']['revenue_growth'],
                        'dividend_yield': analysis['fundamentals']['dividend_yield'],
                        'beta': analysis['fundamentals']['beta'],
                        'total_score': analysis['total_score'],
                        'grade': analysis['grade'],
                        'recommendation': analysis['recommendation']['recommendation'],
                        'confidence': analysis['recommendation']['confidence'],
                        'target_price': analysis['recommendation']['target_price'],
                        'risk_level': analysis['recommendation']['risk_level'],
                        'industry_rank': analysis['industry_analysis']['industry_rank']
                    }
                    results.append(result)
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # スコア順でソート
        df = df.sort_values('total_score', ascending=False)
        
        return df
    
    def generate_fundamental_report(self, analysis_results: List[Dict]) -> str:
        """ファンダメンタルズ分析レポートを生成"""
        if not analysis_results:
            return "分析対象の銘柄が見つかりませんでした。"
        
        report = f"""
# ファンダメンタルズ分析レポート
生成日時: {pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M')}

## 分析サマリー
- 分析対象銘柄数: {len(analysis_results)}銘柄
- 平均スコア: {np.mean([r['total_score'] for r in analysis_results]):.1f}点
- 最高スコア: {max([r['total_score'] for r in analysis_results]):.1f}点
- 最低スコア: {min([r['total_score'] for r in analysis_results]):.1f}点

## グレード分布
"""
        
        # グレード分布を計算
        grades = [r['grade'] for r in analysis_results]
        grade_counts = pd.Series(grades).value_counts().sort_index()
        
        for grade, count in grade_counts.items():
            report += f"- {grade}級: {count}銘柄\n"
        
        report += "\n## おすすめ銘柄（スコア上位5銘柄）\n"
        
        # スコア上位5銘柄
        top_stocks = sorted(analysis_results, key=lambda x: x['total_score'], reverse=True)[:5]
        
        for i, stock in enumerate(top_stocks, 1):
            report += f"""
### {i}. {stock['company_name']} ({stock['symbol']})
- **総合スコア**: {stock['total_score']:.1f}点 ({stock['grade']}級)
- **投資推奨**: {stock['recommendation']['recommendation']} (信頼度: {stock['recommendation']['confidence']})
- **現在価格**: ¥{stock['fundamentals']['current_price']:,.0f}
- **目標価格**: ¥{stock['recommendation']['target_price']:,.0f}
- **リスクレベル**: {stock['recommendation']['risk_level']}
- **業界内ランク**: {stock['industry_analysis']['industry_rank']}

#### 主要財務指標
- PER: {stock['fundamentals']['pe_ratio']:.2f}
- PBR: {stock['fundamentals']['pb_ratio']:.2f}
- ROE: {stock['fundamentals']['roe']:.2f}%
- ROA: {stock['fundamentals']['roa']:.2f}%
- 負債比率: {stock['fundamentals']['debt_to_equity']:.2f}
- 流動比率: {stock['fundamentals']['current_ratio']:.2f}
- 利益率: {stock['fundamentals']['profit_margin']:.2f}%
- 売上成長率: {stock['fundamentals']['revenue_growth']:.2f}%
- 配当利回り: {stock['fundamentals']['dividend_yield']:.2f}%

#### 推奨理由
"""
            for reason in stock['recommendation']['reasons']:
                report += f"- {reason}\n"
        
        return report
