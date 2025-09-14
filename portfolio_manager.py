import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

class PortfolioManager:
    """
    ポートフォリオ管理機能
    
    ポートフォリオの構築、最適化、リバランスを行います。
    """
    
    def __init__(self, data_file: str = "portfolio_data.json"):
        self.data_file = data_file
        self.portfolios = self._load_portfolios()
        self.performance_tracker = None  # PerformanceTrackerのインスタンスを後で設定
    
    def _load_portfolios(self) -> List[Dict]:
        """ポートフォリオデータを読み込み"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('portfolios', [])
            except Exception as e:
                print(f"ポートフォリオデータ読み込みエラー: {e}")
                return []
        return []
    
    def _save_portfolios(self):
        """ポートフォリオデータを保存"""
        try:
            data = {
                'portfolios': self.portfolios,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"ポートフォリオデータ保存エラー: {e}")
    
    def create_portfolio(self, name: str, description: str = "", strategy: str = "balanced") -> str:
        """
        新しいポートフォリオを作成
        
        Args:
            name: ポートフォリオ名
            description: 説明
            strategy: 投資戦略
            
        Returns:
            ポートフォリオID
        """
        portfolio_id = f"portfolio_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        portfolio = {
            'id': portfolio_id,
            'name': name,
            'description': description,
            'strategy': strategy,
            'created_at': datetime.now(),
            'last_updated': datetime.now(),
            'positions': [],
            'target_allocation': {},
            'rebalance_rules': {
                'frequency': 'monthly',
                'threshold': 0.05,  # 5%の偏差でリバランス
                'min_weight': 0.01,  # 最小1%
                'max_weight': 0.4    # 最大40%
            },
            'performance': {
                'total_return': 0,
                'annualized_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        }
        
        self.portfolios.append(portfolio)
        self._save_portfolios()
        
        return portfolio_id
    
    def add_position(self, portfolio_id: str, symbol: str, weight: float, 
                    target_price: float = None, notes: str = "") -> bool:
        """
        ポートフォリオにポジションを追加
        
        Args:
            portfolio_id: ポートフォリオID
            symbol: 銘柄コード
            weight: 目標ウェイト
            target_price: 目標価格
            notes: メモ
            
        Returns:
            成功可否
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return False
        
        # 既存のポジションを更新または新規追加
        existing_position = None
        for pos in portfolio['positions']:
            if pos['symbol'] == symbol:
                existing_position = pos
                break
        
        if existing_position:
            existing_position['weight'] = weight
            existing_position['target_price'] = target_price
            existing_position['notes'] = notes
            existing_position['updated_at'] = datetime.now()
        else:
            position = {
                'symbol': symbol,
                'weight': weight,
                'target_price': target_price,
                'notes': notes,
                'added_at': datetime.now(),
                'updated_at': datetime.now()
            }
            portfolio['positions'].append(position)
        
        portfolio['last_updated'] = datetime.now()
        self._save_portfolios()
        
        return True
    
    def remove_position(self, portfolio_id: str, symbol: str) -> bool:
        """ポートフォリオからポジションを削除"""
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return False
        
        portfolio['positions'] = [pos for pos in portfolio['positions'] if pos['symbol'] != symbol]
        portfolio['last_updated'] = datetime.now()
        self._save_portfolios()
        
        return True
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """ポートフォリオを取得"""
        for portfolio in self.portfolios:
            if portfolio['id'] == portfolio_id:
                return portfolio
        return None
    
    def get_all_portfolios(self) -> List[Dict]:
        """全ポートフォリオを取得"""
        return self.portfolios
    
    def update_portfolio_performance(self, portfolio_id: str, performance_data: Dict) -> bool:
        """ポートフォリオのパフォーマンスを更新"""
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return False
        
        portfolio['performance'].update(performance_data)
        portfolio['last_updated'] = datetime.now()
        self._save_portfolios()
        
        return True
    
    def calculate_portfolio_metrics(self, portfolio_id: str, current_prices: Dict[str, float]) -> Dict:
        """
        ポートフォリオのメトリクスを計算
        
        Args:
            portfolio_id: ポートフォリオID
            current_prices: 現在価格の辞書
            
        Returns:
            ポートフォリオメトリクス
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return {}
        
        positions = portfolio['positions']
        if not positions:
            return {
                'total_weight': 0,
                'diversification_score': 0,
                'risk_score': 0,
                'expected_return': 0,
                'current_allocation': {},
                'deviation_from_target': {}
            }
        
        # 現在のアロケーションを計算
        current_allocation = {}
        total_weight = 0
        
        for position in positions:
            symbol = position['symbol']
            weight = position['weight']
            current_allocation[symbol] = weight
            total_weight += weight
        
        # 目標アロケーションからの偏差を計算
        target_allocation = portfolio.get('target_allocation', {})
        deviation_from_target = {}
        
        for symbol, current_weight in current_allocation.items():
            target_weight = target_allocation.get(symbol, current_weight)
            deviation = abs(current_weight - target_weight)
            deviation_from_target[symbol] = {
                'current': current_weight,
                'target': target_weight,
                'deviation': deviation,
                'deviation_pct': (deviation / target_weight * 100) if target_weight > 0 else 0
            }
        
        # 分散化スコアを計算（エントロピー）
        weights = list(current_allocation.values())
        if weights:
            weights = np.array(weights)
            weights = weights / weights.sum()  # 正規化
            entropy = -np.sum(weights * np.log(weights + 1e-10))
            max_entropy = np.log(len(weights))
            diversification_score = entropy / max_entropy if max_entropy > 0 else 0
        else:
            diversification_score = 0
        
        # リスクスコアを計算（簡易版）
        risk_score = 1 - diversification_score  # 分散化が低いほどリスクが高い
        
        # 期待リターンを計算（簡易版）
        expected_return = 0.08  # 仮の期待リターン8%
        
        return {
            'total_weight': total_weight,
            'diversification_score': diversification_score,
            'risk_score': risk_score,
            'expected_return': expected_return,
            'current_allocation': current_allocation,
            'deviation_from_target': deviation_from_target,
            'position_count': len(positions)
        }
    
    def suggest_rebalance(self, portfolio_id: str, current_prices: Dict[str, float]) -> Dict:
        """
        リバランス提案を生成
        
        Args:
            portfolio_id: ポートフォリオID
            current_prices: 現在価格の辞書
            
        Returns:
            リバランス提案
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return {}
        
        metrics = self.calculate_portfolio_metrics(portfolio_id, current_prices)
        rebalance_rules = portfolio.get('rebalance_rules', {})
        threshold = rebalance_rules.get('threshold', 0.05)
        
        rebalance_needed = False
        rebalance_actions = []
        
        for symbol, deviation_data in metrics['deviation_from_target'].items():
            if deviation_data['deviation'] > threshold:
                rebalance_needed = True
                
                current_weight = deviation_data['current']
                target_weight = deviation_data['target']
                deviation = deviation_data['deviation']
                
                if current_weight > target_weight:
                    action = 'SELL'
                    amount = deviation
                else:
                    action = 'BUY'
                    amount = deviation
                
                rebalance_actions.append({
                    'symbol': symbol,
                    'action': action,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'adjustment': amount,
                    'reason': f"目標ウェイトから{deviation:.1%}偏差"
                })
        
        return {
            'rebalance_needed': rebalance_needed,
            'threshold': threshold,
            'actions': rebalance_actions,
            'total_adjustments': len(rebalance_actions),
            'portfolio_metrics': metrics
        }
    
    def optimize_portfolio(self, portfolio_id: str, risk_tolerance: float = 0.5) -> Dict:
        """
        ポートフォリオ最適化（簡易版）
        
        Args:
            portfolio_id: ポートフォリオID
            risk_tolerance: リスク許容度 (0-1)
            
        Returns:
            最適化結果
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return {}
        
        positions = portfolio['positions']
        if not positions:
            return {}
        
        # 簡易的な最適化（等ウェイト）
        n_positions = len(positions)
        optimal_weight = 1.0 / n_positions
        
        # リスク許容度に基づく調整
        if risk_tolerance < 0.3:  # 保守的
            # より分散化を重視
            max_weight = 0.2
        elif risk_tolerance > 0.7:  # アグレッシブ
            # 集中投資を許容
            max_weight = 0.4
        else:  # バランス型
            max_weight = 0.3
        
        # 最適化されたウェイトを計算
        optimized_weights = {}
        for position in positions:
            symbol = position['symbol']
            # 簡易的な最適化：等ウェイト + リスク調整
            optimized_weights[symbol] = min(optimal_weight, max_weight)
        
        # 正規化
        total_weight = sum(optimized_weights.values())
        if total_weight > 0:
            for symbol in optimized_weights:
                optimized_weights[symbol] /= total_weight
        
        return {
            'optimized_weights': optimized_weights,
            'risk_tolerance': risk_tolerance,
            'max_weight': max_weight,
            'diversification_improvement': len(positions) / 10.0,  # 簡易的な改善度
            'expected_risk_reduction': 0.1  # 仮のリスク削減率
        }
    
    def generate_portfolio_report(self, portfolio_id: str, current_prices: Dict[str, float]) -> str:
        """ポートフォリオレポートを生成"""
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return "ポートフォリオが見つかりません。"
        
        metrics = self.calculate_portfolio_metrics(portfolio_id, current_prices)
        rebalance_suggestion = self.suggest_rebalance(portfolio_id, current_prices)
        
        report = f"""
# ポートフォリオレポート

## 基本情報
- ポートフォリオ名: {portfolio['name']}
- 戦略: {portfolio['strategy']}
- 作成日: {portfolio['created_at'].strftime('%Y年%m月%d日')}
- 最終更新: {portfolio['last_updated'].strftime('%Y年%m月%d日')}

## ポートフォリオ構成
- 総ポジション数: {metrics['position_count']}銘柄
- 総ウェイト: {metrics['total_weight']:.1%}
- 分散化スコア: {metrics['diversification_score']:.2f}
- リスクスコア: {metrics['risk_score']:.2f}
- 期待リターン: {metrics['expected_return']:.1%}

## 現在のアロケーション
"""
        
        for symbol, weight in metrics['current_allocation'].items():
            report += f"- {symbol}: {weight:.1%}\n"
        
        report += "\n## リバランス提案\n"
        
        if rebalance_suggestion['rebalance_needed']:
            report += f"リバランスが必要です（閾値: {rebalance_suggestion['threshold']:.1%}）\n\n"
            
            for action in rebalance_suggestion['actions']:
                report += f"### {action['symbol']}\n"
                report += f"- アクション: {action['action']}\n"
                report += f"- 現在ウェイト: {action['current_weight']:.1%}\n"
                report += f"- 目標ウェイト: {action['target_weight']:.1%}\n"
                report += f"- 調整量: {action['adjustment']:.1%}\n"
                report += f"- 理由: {action['reason']}\n\n"
        else:
            report += "現在のアロケーションは適切です。リバランスは不要です。\n"
        
        # パフォーマンス情報
        performance = portfolio.get('performance', {})
        if performance:
            report += "\n## パフォーマンス\n"
            report += f"- 総リターン: {performance.get('total_return', 0):.2f}%\n"
            report += f"- 年率リターン: {performance.get('annualized_return', 0):.2f}%\n"
            report += f"- ボラティリティ: {performance.get('volatility', 0):.2f}%\n"
            report += f"- シャープレシオ: {performance.get('sharpe_ratio', 0):.2f}\n"
            report += f"- 最大ドローダウン: {performance.get('max_drawdown', 0):.2f}%\n"
        
        return report
    
    def delete_portfolio(self, portfolio_id: str) -> bool:
        """ポートフォリオを削除"""
        original_count = len(self.portfolios)
        self.portfolios = [p for p in self.portfolios if p['id'] != portfolio_id]
        
        if len(self.portfolios) < original_count:
            self._save_portfolios()
            return True
        return False
    
    def clone_portfolio(self, portfolio_id: str, new_name: str) -> str:
        """ポートフォリオをクローン"""
        original_portfolio = self.get_portfolio(portfolio_id)
        if not original_portfolio:
            return None
        
        new_portfolio_id = self.create_portfolio(
            name=new_name,
            description=f"{original_portfolio['name']}のコピー",
            strategy=original_portfolio['strategy']
        )
        
        new_portfolio = self.get_portfolio(new_portfolio_id)
        if new_portfolio:
            new_portfolio['positions'] = original_portfolio['positions'].copy()
            new_portfolio['target_allocation'] = original_portfolio.get('target_allocation', {}).copy()
            new_portfolio['rebalance_rules'] = original_portfolio.get('rebalance_rules', {}).copy()
            self._save_portfolios()
        
        return new_portfolio_id
