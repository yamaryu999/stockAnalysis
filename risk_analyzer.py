import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class RiskAnalyzer:
    """リスク分析を行うクラス"""
    
    def __init__(self):
        self.risk_free_rate = 0.01  # リスクフリーレート（1%）
        self.market_risk_premium = 0.06  # マーケットリスクプレミアム（6%）
    
    def calculate_var(self, stock_data: Dict, confidence_levels: List[float] = [0.95, 0.99]) -> Dict:
        """VaR（Value at Risk）を計算"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 30:
                return None
            
            close = data['Close']
            returns = close.pct_change().dropna()
            
            if len(returns) < 20:
                return None
            
            var_results = {}
            
            for confidence in confidence_levels:
                # パラメトリック法（正規分布仮定）
                mean_return = returns.mean()
                std_return = returns.std()
                z_score = stats.norm.ppf(1 - confidence)
                var_parametric = -(mean_return + z_score * std_return)
                
                # ヒストリカル法
                var_historical = -np.percentile(returns, (1 - confidence) * 100)
                
                # モンテカルロ法（簡易版）
                var_monte_carlo = self._calculate_monte_carlo_var(returns, confidence)
                
                var_results[f'var_{int(confidence*100)}'] = {
                    'parametric': var_parametric,
                    'historical': var_historical,
                    'monte_carlo': var_monte_carlo,
                    'average': (var_parametric + var_historical + var_monte_carlo) / 3
                }
            
            # 最大ドローダウン
            max_drawdown = self._calculate_max_drawdown(close)
            
            # シャープレシオ
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            
            return {
                'var_results': var_results,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'volatility': std_return * np.sqrt(252),  # 年率ボラティリティ
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"VaR計算エラー: {e}")
            return None
    
    def _calculate_monte_carlo_var(self, returns: pd.Series, confidence: float, simulations: int = 10000) -> float:
        """モンテカルロ法によるVaR計算"""
        try:
            mean_return = returns.mean()
            std_return = returns.std()
            
            # モンテカルロシミュレーション
            simulated_returns = np.random.normal(mean_return, std_return, simulations)
            
            # VaR計算
            var = -np.percentile(simulated_returns, (1 - confidence) * 100)
            
            return var
        except Exception as e:
            print(f"モンテカルロVaR計算エラー: {e}")
            return 0
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> Dict:
        """最大ドローダウンを計算"""
        try:
            # 累積リターン
            cumulative = (1 + prices.pct_change()).cumprod()
            
            # ローリング最大値
            rolling_max = cumulative.expanding().max()
            
            # ドローダウン
            drawdown = (cumulative - rolling_max) / rolling_max
            
            # 最大ドローダウン
            max_dd = drawdown.min()
            max_dd_date = drawdown.idxmin()
            
            # ドローダウン期間
            dd_duration = self._calculate_drawdown_duration(drawdown)
            
            return {
                'max_drawdown': max_dd,
                'max_drawdown_date': max_dd_date,
                'average_drawdown_duration': dd_duration,
                'current_drawdown': drawdown.iloc[-1] if not drawdown.empty else 0
            }
            
        except Exception as e:
            print(f"最大ドローダウン計算エラー: {e}")
            return {'max_drawdown': 0, 'max_drawdown_date': None, 'average_drawdown_duration': 0, 'current_drawdown': 0}
    
    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> float:
        """ドローダウン期間を計算"""
        try:
            in_drawdown = drawdown < 0
            drawdown_periods = []
            current_period = 0
            
            for is_dd in in_drawdown:
                if is_dd:
                    current_period += 1
                else:
                    if current_period > 0:
                        drawdown_periods.append(current_period)
                    current_period = 0
            
            if current_period > 0:
                drawdown_periods.append(current_period)
            
            return np.mean(drawdown_periods) if drawdown_periods else 0
            
        except Exception as e:
            print(f"ドローダウン期間計算エラー: {e}")
            return 0
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """シャープレシオを計算"""
        try:
            excess_returns = returns - self.risk_free_rate / 252  # 日次リスクフリーレート
            return excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        except Exception as e:
            print(f"シャープレシオ計算エラー: {e}")
            return 0
    
    def calculate_beta_analysis(self, stock_data: Dict) -> Dict:
        """ベータ分析を実行"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 30:
                return None
            
            # 日経平均のデータを取得
            start_date = data.index[0]
            end_date = data.index[-1]
            
            try:
                nikkei = yf.download('^N225', start=start_date, end=end_date, progress=False)
                
                if nikkei.empty:
                    return None
                
                # リターン計算
                stock_returns = data['Close'].pct_change().dropna()
                nikkei_returns = nikkei['Close'].pct_change().dropna()
                
                # 共通の日付でデータを揃える
                common_dates = stock_returns.index.intersection(nikkei_returns.index)
                if len(common_dates) < 20:
                    return None
                
                stock_returns_aligned = stock_returns.loc[common_dates]
                nikkei_returns_aligned = nikkei_returns.loc[common_dates]
                
                # ベータ計算
                covariance = np.cov(stock_returns_aligned, nikkei_returns_aligned)[0, 1]
                nikkei_variance = np.var(nikkei_returns_aligned)
                
                beta = covariance / nikkei_variance if nikkei_variance > 0 else 1.0
                
                # アルファ計算
                alpha = stock_returns_aligned.mean() - (self.risk_free_rate / 252 + beta * (nikkei_returns_aligned.mean() - self.risk_free_rate / 252))
                
                # 相関係数
                correlation = np.corrcoef(stock_returns_aligned, nikkei_returns_aligned)[0, 1]
                
                # 決定係数（R²）
                r_squared = correlation ** 2
                
                # ベータの解釈
                beta_interpretation = self._interpret_beta(beta)
                
                # システマティックリスクとアンシステマティックリスク
                stock_variance = np.var(stock_returns_aligned)
                systematic_risk = (beta ** 2) * nikkei_variance
                unsystematic_risk = stock_variance - systematic_risk
                
                return {
                    'beta': beta,
                    'alpha': alpha,
                    'correlation': correlation,
                    'r_squared': r_squared,
                    'beta_interpretation': beta_interpretation,
                    'systematic_risk': systematic_risk,
                    'unsystematic_risk': unsystematic_risk,
                    'risk_breakdown': {
                        'systematic_percentage': (systematic_risk / stock_variance) * 100 if stock_variance > 0 else 0,
                        'unsystematic_percentage': (unsystematic_risk / stock_variance) * 100 if stock_variance > 0 else 0
                    },
                    'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            except Exception as e:
                print(f"日経平均データ取得エラー: {e}")
                return None
                
        except Exception as e:
            print(f"ベータ分析エラー: {e}")
            return None
    
    def _interpret_beta(self, beta: float) -> Dict:
        """ベータ値を解釈"""
        if beta > 1.5:
            return {
                'level': 'very_high',
                'description': '非常に高い市場感応度',
                'risk_level': 'high',
                'characteristics': '市場の変動に対して非常に敏感に反応'
            }
        elif beta > 1.2:
            return {
                'level': 'high',
                'description': '高い市場感応度',
                'risk_level': 'high',
                'characteristics': '市場の変動に対して敏感に反応'
            }
        elif beta > 0.8:
            return {
                'level': 'moderate',
                'description': '中程度の市場感応度',
                'risk_level': 'medium',
                'characteristics': '市場の変動に対して適度に反応'
            }
        elif beta > 0.5:
            return {
                'level': 'low',
                'description': '低い市場感応度',
                'risk_level': 'low',
                'characteristics': '市場の変動に対して鈍感'
            }
        else:
            return {
                'level': 'very_low',
                'description': '非常に低い市場感応度',
                'risk_level': 'very_low',
                'characteristics': '市場の変動に対して非常に鈍感'
            }
    
    def calculate_liquidity_risk(self, stock_data: Dict) -> Dict:
        """流動性リスクを評価"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 20:
                return None
            
            volume = data['Volume']
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            # 出来高分析
            avg_volume = volume.mean()
            volume_volatility = volume.std() / avg_volume if avg_volume > 0 else 0
            
            # 最近の出来高トレンド
            recent_volume = volume.tail(10).mean()
            volume_trend = (recent_volume - avg_volume) / avg_volume if avg_volume > 0 else 0
            
            # 価格インパクト（簡易版）
            price_impact = self._calculate_price_impact(close, volume)
            
            # スプレッド推定（高値-安値の比率）
            daily_range = (high - low) / close
            avg_spread = daily_range.mean()
            
            # 流動性スコア計算
            liquidity_score = self._calculate_liquidity_score(
                avg_volume, volume_volatility, volume_trend, price_impact, avg_spread
            )
            
            return {
                'avg_volume': avg_volume,
                'volume_volatility': volume_volatility,
                'volume_trend': volume_trend,
                'price_impact': price_impact,
                'estimated_spread': avg_spread,
                'liquidity_score': liquidity_score,
                'liquidity_level': self._get_liquidity_level(liquidity_score),
                'risk_factors': self._identify_liquidity_risks(
                    avg_volume, volume_volatility, volume_trend, price_impact
                ),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"流動性リスク分析エラー: {e}")
            return None
    
    def _calculate_price_impact(self, close: pd.Series, volume: pd.Series) -> float:
        """価格インパクトを計算（簡易版）"""
        try:
            # 出来高と価格変動の相関
            price_change = close.pct_change().abs()
            volume_change = volume.pct_change()
            
            # 共通の日付でデータを揃える
            common_dates = price_change.index.intersection(volume_change.index)
            if len(common_dates) < 10:
                return 0
            
            price_change_aligned = price_change.loc[common_dates]
            volume_change_aligned = volume_change.loc[common_dates]
            
            # 相関係数
            correlation = np.corrcoef(price_change_aligned, volume_change_aligned)[0, 1]
            
            return abs(correlation) if not np.isnan(correlation) else 0
            
        except Exception as e:
            print(f"価格インパクト計算エラー: {e}")
            return 0
    
    def _calculate_liquidity_score(self, avg_volume: float, volume_volatility: float, 
                                 volume_trend: float, price_impact: float, spread: float) -> float:
        """流動性スコアを計算"""
        try:
            score = 50  # ベーススコア
            
            # 出来高スコア（高いほど良い）
            if avg_volume > 1000000:
                score += 20
            elif avg_volume > 500000:
                score += 15
            elif avg_volume > 100000:
                score += 10
            elif avg_volume > 50000:
                score += 5
            
            # 出来高安定性スコア（低いボラティリティほど良い）
            if volume_volatility < 0.5:
                score += 15
            elif volume_volatility < 1.0:
                score += 10
            elif volume_volatility < 2.0:
                score += 5
            
            # 出来高トレンドスコア（増加傾向ほど良い）
            if volume_trend > 0.2:
                score += 10
            elif volume_trend > 0:
                score += 5
            elif volume_trend < -0.2:
                score -= 10
            
            # 価格インパクトスコア（低いほど良い）
            if price_impact < 0.3:
                score += 10
            elif price_impact < 0.5:
                score += 5
            elif price_impact > 0.7:
                score -= 10
            
            # スプレッドスコア（低いほど良い）
            if spread < 0.02:
                score += 10
            elif spread < 0.05:
                score += 5
            elif spread > 0.1:
                score -= 10
            
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"流動性スコア計算エラー: {e}")
            return 50
    
    def _get_liquidity_level(self, score: float) -> str:
        """流動性レベルを取得"""
        if score >= 80:
            return 'very_high'
        elif score >= 65:
            return 'high'
        elif score >= 50:
            return 'medium'
        elif score >= 35:
            return 'low'
        else:
            return 'very_low'
    
    def _identify_liquidity_risks(self, avg_volume: float, volume_volatility: float, 
                                volume_trend: float, price_impact: float) -> List[str]:
        """流動性リスク要因を特定"""
        risks = []
        
        if avg_volume < 100000:
            risks.append('低出来高')
        
        if volume_volatility > 2.0:
            risks.append('出来高の不安定性')
        
        if volume_trend < -0.2:
            risks.append('出来高減少傾向')
        
        if price_impact > 0.7:
            risks.append('高い価格インパクト')
        
        return risks
    
    def calculate_credit_risk(self, metrics: Dict) -> Dict:
        """信用リスクを評価"""
        try:
            if not metrics:
                return None
            
            # 財務健全性指標
            debt_ratio = metrics.get('debt_to_equity', 0)
            roe = metrics.get('roe', 0)
            pe_ratio = metrics.get('pe_ratio', 0)
            pb_ratio = metrics.get('pb_ratio', 0)
            
            # 信用スコア計算
            credit_score = 50  # ベーススコア
            
            # 負債比率スコア（低いほど良い）
            if debt_ratio < 30:
                credit_score += 20
            elif debt_ratio < 50:
                credit_score += 15
            elif debt_ratio < 70:
                credit_score += 10
            elif debt_ratio > 100:
                credit_score -= 20
            
            # ROEスコア（高いほど良い）
            if roe > 15:
                credit_score += 20
            elif roe > 10:
                credit_score += 15
            elif roe > 5:
                credit_score += 10
            elif roe < 0:
                credit_score -= 20
            
            # PERスコア（適正範囲内で高得点）
            if 5 <= pe_ratio <= 20:
                credit_score += 15
            elif 3 <= pe_ratio <= 30:
                credit_score += 10
            elif pe_ratio > 50:
                credit_score -= 15
            
            # PBRスコア（適正範囲内で高得点）
            if 0.5 <= pb_ratio <= 2.0:
                credit_score += 15
            elif 0.3 <= pb_ratio <= 3.0:
                credit_score += 10
            elif pb_ratio > 5.0:
                credit_score -= 10
            
            # 信用リスクレベル
            if credit_score >= 80:
                risk_level = 'very_low'
                risk_desc = '非常に低い'
                rating = 'AAA'
            elif credit_score >= 65:
                risk_level = 'low'
                risk_desc = '低い'
                rating = 'AA'
            elif credit_score >= 50:
                risk_level = 'medium'
                risk_desc = '中程度'
                rating = 'BBB'
            elif credit_score >= 35:
                risk_level = 'high'
                risk_desc = '高い'
                rating = 'BB'
            else:
                risk_level = 'very_high'
                risk_desc = '非常に高い'
                rating = 'B'
            
            return {
                'credit_score': credit_score,
                'risk_level': risk_level,
                'risk_description': risk_desc,
                'credit_rating': rating,
                'risk_factors': self._identify_credit_risks(debt_ratio, roe, pe_ratio, pb_ratio),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"信用リスク分析エラー: {e}")
            return None
    
    def _identify_credit_risks(self, debt_ratio: float, roe: float, pe_ratio: float, pb_ratio: float) -> List[str]:
        """信用リスク要因を特定"""
        risks = []
        
        if debt_ratio > 100:
            risks.append('過度な負債')
        elif debt_ratio > 70:
            risks.append('高負債比率')
        
        if roe < 0:
            risks.append('赤字経営')
        elif roe < 5:
            risks.append('低収益性')
        
        if pe_ratio > 50:
            risks.append('過度に高いPER')
        elif pe_ratio < 0:
            risks.append('赤字によるPER異常')
        
        if pb_ratio > 5:
            risks.append('過度に高いPBR')
        
        return risks
    
    def comprehensive_risk_analysis(self, stock_data: Dict, metrics: Dict) -> Dict:
        """包括的なリスク分析を実行"""
        try:
            # 各リスク分析を実行
            var_analysis = self.calculate_var(stock_data)
            beta_analysis = self.calculate_beta_analysis(stock_data)
            liquidity_analysis = self.calculate_liquidity_risk(stock_data)
            credit_analysis = self.calculate_credit_risk(metrics)
            
            # 総合リスクスコア計算
            risk_scores = []
            
            if var_analysis:
                # VaRベースのリスクスコア
                var_95 = var_analysis['var_results'].get('var_95', {}).get('average', 0)
                risk_scores.append(min(100, max(0, 50 - var_95 * 1000)))
            
            if beta_analysis:
                # ベータベースのリスクスコア
                beta = beta_analysis['beta']
                beta_risk_score = 50 + (abs(beta - 1) * 20)
                risk_scores.append(min(100, max(0, beta_risk_score)))
            
            if liquidity_analysis:
                # 流動性ベースのリスクスコア（逆転）
                liquidity_score = liquidity_analysis['liquidity_score']
                liquidity_risk_score = 100 - liquidity_score
                risk_scores.append(liquidity_risk_score)
            
            if credit_analysis:
                # 信用リスクスコア（逆転）
                credit_score = credit_analysis['credit_score']
                credit_risk_score = 100 - credit_score
                risk_scores.append(credit_risk_score)
            
            overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 50
            
            # 総合リスクレベル
            if overall_risk_score >= 80:
                overall_risk_level = 'very_high'
                overall_risk_desc = '非常に高い'
                recommendation = 'avoid'
                recommendation_desc = '投資回避推奨'
            elif overall_risk_score >= 65:
                overall_risk_level = 'high'
                overall_risk_desc = '高い'
                recommendation = 'caution'
                recommendation_desc = '慎重な投資'
            elif overall_risk_score >= 50:
                overall_risk_level = 'medium'
                overall_risk_desc = '中程度'
                recommendation = 'moderate'
                recommendation_desc = '適度な投資'
            elif overall_risk_score >= 35:
                overall_risk_level = 'low'
                overall_risk_desc = '低い'
                recommendation = 'favorable'
                recommendation_desc = '投資に適している'
            else:
                overall_risk_level = 'very_low'
                overall_risk_desc = '非常に低い'
                recommendation = 'excellent'
                recommendation_desc = '優良投資先'
            
            return {
                'overall_risk_score': overall_risk_score,
                'overall_risk_level': overall_risk_level,
                'overall_risk_description': overall_risk_desc,
                'recommendation': recommendation,
                'recommendation_description': recommendation_desc,
                'var_analysis': var_analysis,
                'beta_analysis': beta_analysis,
                'liquidity_analysis': liquidity_analysis,
                'credit_analysis': credit_analysis,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的リスク分析エラー: {e}")
            return None
