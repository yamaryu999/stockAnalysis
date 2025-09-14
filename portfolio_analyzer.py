import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class PortfolioAnalyzer:
    """ポートフォリオ分析を行うクラス"""
    
    def __init__(self):
        self.risk_free_rate = 0.01  # リスクフリーレート（1%）
    
    def calculate_portfolio_metrics(self, stock_data_dict: Dict, weights: Optional[Dict] = None) -> Dict:
        """ポートフォリオ指標を計算"""
        try:
            if not stock_data_dict or len(stock_data_dict) < 2:
                return None
            
            # リターンデータを準備
            returns_data = {}
            symbols = list(stock_data_dict.keys())
            
            for symbol, stock_data in stock_data_dict.items():
                if stock_data and stock_data.get('data') is not None:
                    data = stock_data['data']
                    if not data.empty:
                        returns = data['Close'].pct_change().dropna()
                        returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return None
            
            # 共通の日付でデータを揃える
            common_dates = None
            for symbol, returns in returns_data.items():
                if common_dates is None:
                    common_dates = returns.index
                else:
                    common_dates = common_dates.intersection(returns.index)
            
            if len(common_dates) < 20:
                return None
            
            # データを揃える
            aligned_returns = {}
            for symbol, returns in returns_data.items():
                aligned_returns[symbol] = returns.loc[common_dates]
            
            # リターンマトリックス
            returns_matrix = pd.DataFrame(aligned_returns)
            
            # 等重みポートフォリオ（重みが指定されていない場合）
            if weights is None:
                weights = {symbol: 1.0 / len(symbols) for symbol in symbols}
            
            # 重みベクトル
            weight_vector = np.array([weights.get(symbol, 0) for symbol in symbols])
            
            # ポートフォリオリターン
            portfolio_returns = returns_matrix.dot(weight_vector)
            
            # ポートフォリオ指標計算
            portfolio_metrics = self._calculate_portfolio_statistics(portfolio_returns, returns_matrix, weight_vector)
            
            return {
                'portfolio_returns': portfolio_returns,
                'portfolio_metrics': portfolio_metrics,
                'weights': weights,
                'symbols': symbols,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"ポートフォリオ指標計算エラー: {e}")
            return None
    
    def _calculate_portfolio_statistics(self, portfolio_returns: pd.Series, 
                                      returns_matrix: pd.DataFrame, 
                                      weights: np.ndarray) -> Dict:
        """ポートフォリオ統計を計算"""
        try:
            # 基本統計
            mean_return = portfolio_returns.mean() * 252  # 年率
            volatility = portfolio_returns.std() * np.sqrt(252)  # 年率ボラティリティ
            
            # シャープレシオ
            sharpe_ratio = (mean_return - self.risk_free_rate) / volatility if volatility > 0 else 0
            
            # 最大ドローダウン
            cumulative = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # VaR（95%信頼区間）
            var_95 = -np.percentile(portfolio_returns, 5)
            
            # 共分散行列
            cov_matrix = returns_matrix.cov() * 252  # 年率
            
            # ポートフォリオ分散
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            portfolio_volatility_calc = np.sqrt(portfolio_variance)
            
            return {
                'annual_return': mean_return,
                'annual_volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'portfolio_variance': portfolio_variance,
                'portfolio_volatility_calc': portfolio_volatility_calc
            }
            
        except Exception as e:
            print(f"ポートフォリオ統計計算エラー: {e}")
            return {}
    
    def calculate_correlation_analysis(self, stock_data_dict: Dict) -> Dict:
        """相関分析を実行"""
        try:
            if not stock_data_dict or len(stock_data_dict) < 2:
                return None
            
            # リターンデータを準備
            returns_data = {}
            
            for symbol, stock_data in stock_data_dict.items():
                if stock_data and stock_data.get('data') is not None:
                    data = stock_data['data']
                    if not data.empty:
                        returns = data['Close'].pct_change().dropna()
                        returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return None
            
            # 共通の日付でデータを揃える
            common_dates = None
            for symbol, returns in returns_data.items():
                if common_dates is None:
                    common_dates = returns.index
                else:
                    common_dates = common_dates.intersection(returns.index)
            
            if len(common_dates) < 20:
                return None
            
            # データを揃える
            aligned_returns = {}
            for symbol, returns in returns_data.items():
                aligned_returns[symbol] = returns.loc[common_dates]
            
            # リターンマトリックス
            returns_matrix = pd.DataFrame(aligned_returns)
            
            # 相関行列
            correlation_matrix = returns_matrix.corr()
            
            # 平均相関
            symbols = list(returns_data.keys())
            correlations = []
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    corr = correlation_matrix.loc[symbols[i], symbols[j]]
                    if not np.isnan(corr):
                        correlations.append(corr)
            
            avg_correlation = np.mean(correlations) if correlations else 0
            
            # 相関の解釈
            correlation_interpretation = self._interpret_correlation(avg_correlation)
            
            # 分散投資効果
            diversification_benefit = self._calculate_diversification_benefit(correlation_matrix, symbols)
            
            return {
                'correlation_matrix': correlation_matrix,
                'average_correlation': avg_correlation,
                'correlation_interpretation': correlation_interpretation,
                'diversification_benefit': diversification_benefit,
                'symbols': symbols,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"相関分析エラー: {e}")
            return None
    
    def _interpret_correlation(self, avg_correlation: float) -> Dict:
        """相関の解釈"""
        if avg_correlation > 0.8:
            return {
                'level': 'very_high',
                'description': '非常に高い相関',
                'diversification_effect': 'low',
                'recommendation': '分散投資効果が低い'
            }
        elif avg_correlation > 0.6:
            return {
                'level': 'high',
                'description': '高い相関',
                'diversification_effect': 'moderate',
                'recommendation': '分散投資効果が中程度'
            }
        elif avg_correlation > 0.4:
            return {
                'level': 'moderate',
                'description': '中程度の相関',
                'diversification_effect': 'good',
                'recommendation': '適度な分散投資効果'
            }
        elif avg_correlation > 0.2:
            return {
                'level': 'low',
                'description': '低い相関',
                'diversification_effect': 'high',
                'recommendation': '高い分散投資効果'
            }
        else:
            return {
                'level': 'very_low',
                'description': '非常に低い相関',
                'diversification_effect': 'very_high',
                'recommendation': '非常に高い分散投資効果'
            }
    
    def _calculate_diversification_benefit(self, correlation_matrix: pd.DataFrame, symbols: List[str]) -> Dict:
        """分散投資効果を計算"""
        try:
            # 各銘柄の個別リスク
            individual_risks = []
            for symbol in symbols:
                # 簡易的な個別リスク（標準偏差）
                individual_risk = correlation_matrix.loc[symbol, symbol]  # 自己相関は1
                individual_risks.append(individual_risk)
            
            # 等重みポートフォリオの理論的リスク
            avg_individual_risk = np.mean(individual_risks)
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            
            # 分散投資効果
            diversification_ratio = 1 / np.sqrt(len(symbols))
            correlation_adjustment = 1 + (len(symbols) - 1) * avg_correlation
            portfolio_risk = avg_individual_risk * np.sqrt(correlation_adjustment / len(symbols))
            
            # 分散投資効果の測定
            diversification_benefit = (avg_individual_risk - portfolio_risk) / avg_individual_risk * 100
            
            return {
                'individual_risk': avg_individual_risk,
                'portfolio_risk': portfolio_risk,
                'diversification_benefit_percentage': diversification_benefit,
                'risk_reduction': avg_individual_risk - portfolio_risk
            }
            
        except Exception as e:
            print(f"分散投資効果計算エラー: {e}")
            return {'diversification_benefit_percentage': 0, 'risk_reduction': 0}
    
    def optimize_portfolio(self, stock_data_dict: Dict, target_return: Optional[float] = None) -> Dict:
        """ポートフォリオ最適化を実行"""
        try:
            if not stock_data_dict or len(stock_data_dict) < 2:
                return None
            
            # リターンデータを準備
            returns_data = {}
            symbols = list(stock_data_dict.keys())
            
            for symbol, stock_data in stock_data_dict.items():
                if stock_data and stock_data.get('data') is not None:
                    data = stock_data['data']
                    if not data.empty:
                        returns = data['Close'].pct_change().dropna()
                        returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return None
            
            # 共通の日付でデータを揃える
            common_dates = None
            for symbol, returns in returns_data.items():
                if common_dates is None:
                    common_dates = returns.index
                else:
                    common_dates = common_dates.intersection(returns.index)
            
            if len(common_dates) < 20:
                return None
            
            # データを揃える
            aligned_returns = {}
            for symbol, returns in returns_data.items():
                aligned_returns[symbol] = returns.loc[common_dates]
            
            # リターンマトリックス
            returns_matrix = pd.DataFrame(aligned_returns)
            
            # 平均リターンと共分散行列
            mean_returns = returns_matrix.mean() * 252  # 年率
            cov_matrix = returns_matrix.cov() * 252  # 年率
            
            # 最適化実行
            if target_return is None:
                # 最大シャープレシオポートフォリオ
                optimal_weights = self._maximize_sharpe_ratio(mean_returns, cov_matrix)
            else:
                # 目標リターンでの最小分散ポートフォリオ
                optimal_weights = self._minimize_variance_target_return(mean_returns, cov_matrix, target_return)
            
            if optimal_weights is None:
                return None
            
            # 最適化されたポートフォリオの指標
            optimal_portfolio = self.calculate_portfolio_metrics(stock_data_dict, dict(zip(symbols, optimal_weights)))
            
            return {
                'optimal_weights': dict(zip(symbols, optimal_weights)),
                'portfolio_metrics': optimal_portfolio['portfolio_metrics'] if optimal_portfolio else {},
                'optimization_type': 'max_sharpe' if target_return is None else 'min_variance_target_return',
                'target_return': target_return,
                'symbols': symbols,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"ポートフォリオ最適化エラー: {e}")
            return None
    
    def _maximize_sharpe_ratio(self, mean_returns: pd.Series, cov_matrix: pd.DataFrame) -> Optional[np.ndarray]:
        """最大シャープレシオポートフォリオを計算"""
        try:
            n_assets = len(mean_returns)
            
            # 目的関数（負のシャープレシオを最小化）
            def negative_sharpe_ratio(weights):
                portfolio_return = np.dot(weights, mean_returns)
                portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                portfolio_volatility = np.sqrt(portfolio_variance)
                return -(portfolio_return - self.risk_free_rate) / portfolio_volatility
            
            # 制約条件
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # 重みの合計が1
            
            # 境界条件（各重みが0以上1以下）
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # 初期値（等重み）
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # 最適化実行
            result = minimize(negative_sharpe_ratio, initial_weights, 
                            method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                return result.x
            else:
                return None
                
        except Exception as e:
            print(f"最大シャープレシオ計算エラー: {e}")
            return None
    
    def _minimize_variance_target_return(self, mean_returns: pd.Series, cov_matrix: pd.DataFrame, 
                                       target_return: float) -> Optional[np.ndarray]:
        """目標リターンでの最小分散ポートフォリオを計算"""
        try:
            n_assets = len(mean_returns)
            
            # 目的関数（ポートフォリオ分散を最小化）
            def portfolio_variance(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            # 制約条件
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # 重みの合計が1
                {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) - target_return}  # 目標リターン
            ]
            
            # 境界条件
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # 初期値
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # 最適化実行
            result = minimize(portfolio_variance, initial_weights, 
                            method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                return result.x
            else:
                return None
                
        except Exception as e:
            print(f"最小分散ポートフォリオ計算エラー: {e}")
            return None
    
    def calculate_efficient_frontier(self, stock_data_dict: Dict, num_portfolios: int = 100) -> Dict:
        """効率的フロンティアを計算"""
        try:
            if not stock_data_dict or len(stock_data_dict) < 2:
                return None
            
            # リターンデータを準備
            returns_data = {}
            symbols = list(stock_data_dict.keys())
            
            for symbol, stock_data in stock_data_dict.items():
                if stock_data and stock_data.get('data') is not None:
                    data = stock_data['data']
                    if not data.empty:
                        returns = data['Close'].pct_change().dropna()
                        returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return None
            
            # 共通の日付でデータを揃える
            common_dates = None
            for symbol, returns in returns_data.items():
                if common_dates is None:
                    common_dates = returns.index
                else:
                    common_dates = common_dates.intersection(returns.index)
            
            if len(common_dates) < 20:
                return None
            
            # データを揃える
            aligned_returns = {}
            for symbol, returns in returns_data.items():
                aligned_returns[symbol] = returns.loc[common_dates]
            
            # リターンマトリックス
            returns_matrix = pd.DataFrame(aligned_returns)
            
            # 平均リターンと共分散行列
            mean_returns = returns_matrix.mean() * 252
            cov_matrix = returns_matrix.cov() * 252
            
            # 効率的フロンティアの計算
            target_returns = np.linspace(mean_returns.min(), mean_returns.max(), num_portfolios)
            efficient_portfolios = []
            
            for target_return in target_returns:
                optimal_weights = self._minimize_variance_target_return(mean_returns, cov_matrix, target_return)
                if optimal_weights is not None:
                    portfolio_return = np.dot(optimal_weights, mean_returns)
                    portfolio_variance = np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
                    portfolio_volatility = np.sqrt(portfolio_variance)
                    sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                    
                    efficient_portfolios.append({
                        'return': portfolio_return,
                        'volatility': portfolio_volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'weights': dict(zip(symbols, optimal_weights))
                    })
            
            if not efficient_portfolios:
                return None
            
            # 最大シャープレシオポートフォリオ
            max_sharpe_portfolio = max(efficient_portfolios, key=lambda x: x['sharpe_ratio'])
            
            # 最小分散ポートフォリオ
            min_volatility_portfolio = min(efficient_portfolios, key=lambda x: x['volatility'])
            
            return {
                'efficient_portfolios': efficient_portfolios,
                'max_sharpe_portfolio': max_sharpe_portfolio,
                'min_volatility_portfolio': min_volatility_portfolio,
                'target_returns': target_returns.tolist(),
                'symbols': symbols,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"効率的フロンティア計算エラー: {e}")
            return None
    
    def comprehensive_portfolio_analysis(self, stock_data_dict: Dict, weights: Optional[Dict] = None) -> Dict:
        """包括的なポートフォリオ分析を実行"""
        try:
            # 各分析を実行
            portfolio_metrics = self.calculate_portfolio_metrics(stock_data_dict, weights)
            correlation_analysis = self.calculate_correlation_analysis(stock_data_dict)
            optimization_result = self.optimize_portfolio(stock_data_dict)
            efficient_frontier = self.calculate_efficient_frontier(stock_data_dict)
            
            if not portfolio_metrics:
                return None
            
            # 総合評価
            portfolio_performance = portfolio_metrics['portfolio_metrics']
            
            # 投資推奨
            if portfolio_performance.get('sharpe_ratio', 0) > 1.0:
                recommendation = 'excellent'
                recommendation_desc = '優秀なポートフォリオ'
            elif portfolio_performance.get('sharpe_ratio', 0) > 0.5:
                recommendation = 'good'
                recommendation_desc = '良好なポートフォリオ'
            elif portfolio_performance.get('sharpe_ratio', 0) > 0:
                recommendation = 'average'
                recommendation_desc = '平均的なポートフォリオ'
            else:
                recommendation = 'poor'
                recommendation_desc = '改善が必要なポートフォリオ'
            
            return {
                'recommendation': recommendation,
                'recommendation_description': recommendation_desc,
                'portfolio_metrics': portfolio_metrics,
                'correlation_analysis': correlation_analysis,
                'optimization_result': optimization_result,
                'efficient_frontier': efficient_frontier,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的ポートフォリオ分析エラー: {e}")
            return None
