import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class PersonalizationAnalyzer:
    """パーソナライズ機能を提供するクラス"""
    
    def __init__(self):
        self.user_preferences = {}
        self.investment_history = {}
        self.risk_profile = {}
    
    def analyze_user_behavior(self, user_interactions: Dict) -> Dict:
        """ユーザー行動を分析"""
        try:
            if not user_interactions:
                return self._get_default_preferences()
            
            # 投資戦略の選択傾向
            strategy_preferences = self._analyze_strategy_preferences(user_interactions)
            
            # 銘柄選択の傾向
            stock_preferences = self._analyze_stock_preferences(user_interactions)
            
            # リスク許容度の分析
            risk_tolerance = self._analyze_risk_tolerance(user_interactions)
            
            # 投資期間の傾向
            investment_horizon = self._analyze_investment_horizon(user_interactions)
            
            # セクター選好
            sector_preferences = self._analyze_sector_preferences(user_interactions)
            
            return {
                'strategy_preferences': strategy_preferences,
                'stock_preferences': stock_preferences,
                'risk_tolerance': risk_tolerance,
                'investment_horizon': investment_horizon,
                'sector_preferences': sector_preferences,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"ユーザー行動分析エラー: {e}")
            return self._get_default_preferences()
    
    def _analyze_strategy_preferences(self, interactions: Dict) -> Dict:
        """投資戦略の選好を分析"""
        try:
            strategy_counts = interactions.get('strategy_selections', {})
            
            if not strategy_counts:
                return {'preferred_strategy': 'balanced', 'confidence': 0.5}
            
            # 最も選択された戦略
            preferred_strategy = max(strategy_counts, key=strategy_counts.get)
            total_selections = sum(strategy_counts.values())
            confidence = strategy_counts[preferred_strategy] / total_selections if total_selections > 0 else 0.5
            
            return {
                'preferred_strategy': preferred_strategy,
                'confidence': confidence,
                'strategy_distribution': strategy_counts
            }
            
        except Exception as e:
            print(f"戦略選好分析エラー: {e}")
            return {'preferred_strategy': 'balanced', 'confidence': 0.5}
    
    def _analyze_stock_preferences(self, interactions: Dict) -> Dict:
        """銘柄選択の傾向を分析"""
        try:
            selected_stocks = interactions.get('selected_stocks', [])
            
            if not selected_stocks:
                return {'preferred_characteristics': {}, 'confidence': 0.5}
            
            # 選択された銘柄の特徴を分析
            characteristics = {
                'avg_pe': 0,
                'avg_pb': 0,
                'avg_roe': 0,
                'avg_dividend_yield': 0,
                'avg_debt_ratio': 0
            }
            
            for stock in selected_stocks:
                if isinstance(stock, dict):
                    characteristics['avg_pe'] += stock.get('pe_ratio', 0)
                    characteristics['avg_pb'] += stock.get('pb_ratio', 0)
                    characteristics['avg_roe'] += stock.get('roe', 0)
                    characteristics['avg_dividend_yield'] += stock.get('dividend_yield', 0)
                    characteristics['avg_debt_ratio'] += stock.get('debt_to_equity', 0)
            
            # 平均値を計算
            if selected_stocks:
                for key in characteristics:
                    characteristics[key] /= len(selected_stocks)
            
            return {
                'preferred_characteristics': characteristics,
                'confidence': min(1.0, len(selected_stocks) / 10),  # 10銘柄で最大信頼度
                'selection_count': len(selected_stocks)
            }
            
        except Exception as e:
            print(f"銘柄選好分析エラー: {e}")
            return {'preferred_characteristics': {}, 'confidence': 0.5}
    
    def _analyze_risk_tolerance(self, interactions: Dict) -> Dict:
        """リスク許容度を分析"""
        try:
            risk_indicators = interactions.get('risk_indicators', {})
            
            if not risk_indicators:
                return {'risk_level': 'medium', 'confidence': 0.5}
            
            # リスク指標を集計
            risk_score = 0
            total_indicators = 0
            
            # 高リスク銘柄の選択傾向
            high_risk_selections = risk_indicators.get('high_risk_selections', 0)
            total_selections = risk_indicators.get('total_selections', 1)
            risk_score += (high_risk_selections / total_selections) * 50
            
            # ボラティリティ許容度
            volatility_tolerance = risk_indicators.get('volatility_tolerance', 0.5)
            risk_score += volatility_tolerance * 30
            
            # 損失許容度
            loss_tolerance = risk_indicators.get('loss_tolerance', 0.5)
            risk_score += loss_tolerance * 20
            
            # リスクレベルを決定
            if risk_score >= 70:
                risk_level = 'high'
            elif risk_score >= 40:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'confidence': min(1.0, total_selections / 20)  # 20回の選択で最大信頼度
            }
            
        except Exception as e:
            print(f"リスク許容度分析エラー: {e}")
            return {'risk_level': 'medium', 'confidence': 0.5}
    
    def _analyze_investment_horizon(self, interactions: Dict) -> Dict:
        """投資期間の傾向を分析"""
        try:
            holding_periods = interactions.get('holding_periods', [])
            
            if not holding_periods:
                return {'preferred_horizon': 'medium', 'confidence': 0.5}
            
            # 平均保有期間を計算
            avg_holding_period = np.mean(holding_periods) if holding_periods else 365
            
            # 投資期間を分類
            if avg_holding_period <= 30:
                horizon = 'short'
            elif avg_holding_period <= 365:
                horizon = 'medium'
            else:
                horizon = 'long'
            
            return {
                'preferred_horizon': horizon,
                'avg_holding_period': avg_holding_period,
                'confidence': min(1.0, len(holding_periods) / 10)
            }
            
        except Exception as e:
            print(f"投資期間分析エラー: {e}")
            return {'preferred_horizon': 'medium', 'confidence': 0.5}
    
    def _analyze_sector_preferences(self, interactions: Dict) -> Dict:
        """セクター選好を分析"""
        try:
            sector_selections = interactions.get('sector_selections', {})
            
            if not sector_selections:
                return {'preferred_sectors': [], 'confidence': 0.5}
            
            # 最も選択されたセクター
            sorted_sectors = sorted(sector_selections.items(), key=lambda x: x[1], reverse=True)
            preferred_sectors = [sector for sector, count in sorted_sectors[:3]]  # 上位3セクター
            
            total_selections = sum(sector_selections.values())
            confidence = min(1.0, total_selections / 20)
            
            return {
                'preferred_sectors': preferred_sectors,
                'sector_distribution': sector_selections,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"セクター選好分析エラー: {e}")
            return {'preferred_sectors': [], 'confidence': 0.5}
    
    def _get_default_preferences(self) -> Dict:
        """デフォルトの選好を取得"""
        return {
            'strategy_preferences': {'preferred_strategy': 'balanced', 'confidence': 0.5},
            'stock_preferences': {'preferred_characteristics': {}, 'confidence': 0.5},
            'risk_tolerance': {'risk_level': 'medium', 'confidence': 0.5},
            'investment_horizon': {'preferred_horizon': 'medium', 'confidence': 0.5},
            'sector_preferences': {'preferred_sectors': [], 'confidence': 0.5}
        }
    
    def generate_personalized_recommendations(self, user_behavior: Dict, available_stocks: List[Dict]) -> Dict:
        """パーソナライズされた推奨を生成"""
        try:
            if not available_stocks:
                return {'recommendations': [], 'reasoning': '利用可能な銘柄がありません'}
            
            # ユーザーの選好に基づいてスコアリング
            scored_stocks = []
            
            for stock in available_stocks:
                score = self._calculate_personalization_score(stock, user_behavior)
                scored_stocks.append({
                    'stock': stock,
                    'personalization_score': score,
                    'match_reasons': self._get_match_reasons(stock, user_behavior)
                })
            
            # スコアでソート
            scored_stocks.sort(key=lambda x: x['personalization_score'], reverse=True)
            
            # 上位推奨を選択
            top_recommendations = scored_stocks[:10]  # 上位10銘柄
            
            return {
                'recommendations': top_recommendations,
                'total_analyzed': len(available_stocks),
                'personalization_confidence': self._calculate_personalization_confidence(user_behavior),
                'reasoning': self._generate_recommendation_reasoning(user_behavior, top_recommendations)
            }
            
        except Exception as e:
            print(f"パーソナライズ推奨生成エラー: {e}")
            return {'recommendations': [], 'reasoning': '推奨生成に失敗しました'}
    
    def _calculate_personalization_score(self, stock: Dict, user_behavior: Dict) -> float:
        """パーソナライズスコアを計算"""
        try:
            score = 0
            total_weight = 0
            
            # 戦略選好スコア
            strategy_prefs = user_behavior.get('strategy_preferences', {})
            if strategy_prefs.get('confidence', 0) > 0.3:
                strategy_score = self._get_strategy_match_score(stock, strategy_prefs)
                score += strategy_score * strategy_prefs.get('confidence', 0.5) * 0.3
                total_weight += 0.3
            
            # 銘柄特徴選好スコア
            stock_prefs = user_behavior.get('stock_preferences', {})
            if stock_prefs.get('confidence', 0) > 0.3:
                characteristics_score = self._get_characteristics_match_score(stock, stock_prefs)
                score += characteristics_score * stock_prefs.get('confidence', 0.5) * 0.25
                total_weight += 0.25
            
            # リスク許容度スコア
            risk_tolerance = user_behavior.get('risk_tolerance', {})
            if risk_tolerance.get('confidence', 0) > 0.3:
                risk_score = self._get_risk_match_score(stock, risk_tolerance)
                score += risk_score * risk_tolerance.get('confidence', 0.5) * 0.2
                total_weight += 0.2
            
            # セクター選好スコア
            sector_prefs = user_behavior.get('sector_preferences', {})
            if sector_prefs.get('confidence', 0) > 0.3:
                sector_score = self._get_sector_match_score(stock, sector_prefs)
                score += sector_score * sector_prefs.get('confidence', 0.5) * 0.15
                total_weight += 0.15
            
            # 投資期間スコア
            horizon = user_behavior.get('investment_horizon', {})
            if horizon.get('confidence', 0) > 0.3:
                horizon_score = self._get_horizon_match_score(stock, horizon)
                score += horizon_score * horizon.get('confidence', 0.5) * 0.1
                total_weight += 0.1
            
            # 正規化
            if total_weight > 0:
                score = score / total_weight
            else:
                score = 0.5  # デフォルトスコア
            
            return max(0, min(1, score))
            
        except Exception as e:
            print(f"パーソナライズスコア計算エラー: {e}")
            return 0.5
    
    def _get_strategy_match_score(self, stock: Dict, strategy_prefs: Dict) -> float:
        """戦略マッチスコアを計算"""
        try:
            preferred_strategy = strategy_prefs.get('preferred_strategy', 'balanced')
            
            # 戦略に応じたスコア計算
            if preferred_strategy == 'value':
                # バリュー投資: 低PER、低PBR、高配当
                pe_score = 1 - min(1, stock.get('pe_ratio', 20) / 30)
                pb_score = 1 - min(1, stock.get('pb_ratio', 2) / 3)
                dividend_score = min(1, stock.get('dividend_yield', 0) / 5)
                return (pe_score + pb_score + dividend_score) / 3
                
            elif preferred_strategy == 'growth':
                # グロース投資: 高ROE、適度なPER
                roe_score = min(1, stock.get('roe', 0) / 20)
                pe_score = 1 - abs(stock.get('pe_ratio', 15) - 15) / 15
                return (roe_score + pe_score) / 2
                
            elif preferred_strategy == 'dividend':
                # 配当投資: 高配当、低負債
                dividend_score = min(1, stock.get('dividend_yield', 0) / 5)
                debt_score = 1 - min(1, stock.get('debt_to_equity', 50) / 100)
                return (dividend_score + debt_score) / 2
                
            else:  # balanced
                # バランス型: 全体的なバランス
                return 0.5
            
        except Exception as e:
            print(f"戦略マッチスコア計算エラー: {e}")
            return 0.5
    
    def _get_characteristics_match_score(self, stock: Dict, stock_prefs: Dict) -> float:
        """銘柄特徴マッチスコアを計算"""
        try:
            preferred = stock_prefs.get('preferred_characteristics', {})
            if not preferred:
                return 0.5
            
            score = 0
            count = 0
            
            # 各指標の類似度を計算
            for metric, preferred_value in preferred.items():
                if metric in stock and preferred_value > 0:
                    stock_value = stock[metric]
                    similarity = 1 - abs(stock_value - preferred_value) / max(stock_value, preferred_value, 1)
                    score += max(0, similarity)
                    count += 1
            
            return score / count if count > 0 else 0.5
            
        except Exception as e:
            print(f"特徴マッチスコア計算エラー: {e}")
            return 0.5
    
    def _get_risk_match_score(self, stock: Dict, risk_tolerance: Dict) -> float:
        """リスクマッチスコアを計算"""
        try:
            risk_level = risk_tolerance.get('risk_level', 'medium')
            
            # 銘柄のリスクレベルを推定
            pe_ratio = stock.get('pe_ratio', 15)
            debt_ratio = stock.get('debt_to_equity', 50)
            roe = stock.get('roe', 10)
            
            # リスクスコア計算
            risk_score = 0
            if pe_ratio > 25:
                risk_score += 0.3
            if debt_ratio > 70:
                risk_score += 0.3
            if roe < 5:
                risk_score += 0.4
            
            # ユーザーのリスク許容度とマッチング
            if risk_level == 'high':
                return 1 - abs(risk_score - 0.7)  # 高リスク銘柄を好む
            elif risk_level == 'low':
                return 1 - abs(risk_score - 0.2)  # 低リスク銘柄を好む
            else:  # medium
                return 1 - abs(risk_score - 0.5)  # 中リスク銘柄を好む
            
        except Exception as e:
            print(f"リスクマッチスコア計算エラー: {e}")
            return 0.5
    
    def _get_sector_match_score(self, stock: Dict, sector_prefs: Dict) -> float:
        """セクターマッチスコアを計算"""
        try:
            preferred_sectors = sector_prefs.get('preferred_sectors', [])
            stock_sector = stock.get('sector', '')
            
            if not preferred_sectors or not stock_sector:
                return 0.5
            
            return 1.0 if stock_sector in preferred_sectors else 0.0
            
        except Exception as e:
            print(f"セクターマッチスコア計算エラー: {e}")
            return 0.5
    
    def _get_horizon_match_score(self, stock: Dict, horizon: Dict) -> float:
        """投資期間マッチスコアを計算"""
        try:
            preferred_horizon = horizon.get('preferred_horizon', 'medium')
            
            # 投資期間に応じた銘柄の適性
            dividend_yield = stock.get('dividend_yield', 0)
            pe_ratio = stock.get('pe_ratio', 15)
            
            if preferred_horizon == 'long':
                # 長期投資: 高配当、安定性重視
                return min(1, dividend_yield / 3 + (1 - min(1, pe_ratio / 20)))
            elif preferred_horizon == 'short':
                # 短期投資: 成長性重視
                roe = stock.get('roe', 10)
                return min(1, roe / 20)
            else:  # medium
                # 中期投資: バランス
                return 0.5
            
        except Exception as e:
            print(f"投資期間マッチスコア計算エラー: {e}")
            return 0.5
    
    def _get_match_reasons(self, stock: Dict, user_behavior: Dict) -> List[str]:
        """マッチ理由を取得"""
        try:
            reasons = []
            
            # 戦略マッチ
            strategy_prefs = user_behavior.get('strategy_preferences', {})
            if strategy_prefs.get('confidence', 0) > 0.3:
                preferred_strategy = strategy_prefs.get('preferred_strategy', 'balanced')
                reasons.append(f"{preferred_strategy}戦略に適合")
            
            # セクターマッチ
            sector_prefs = user_behavior.get('sector_preferences', {})
            if sector_prefs.get('confidence', 0) > 0.3:
                preferred_sectors = sector_prefs.get('preferred_sectors', [])
                stock_sector = stock.get('sector', '')
                if stock_sector in preferred_sectors:
                    reasons.append(f"好みのセクター: {stock_sector}")
            
            # リスクマッチ
            risk_tolerance = user_behavior.get('risk_tolerance', {})
            if risk_tolerance.get('confidence', 0) > 0.3:
                risk_level = risk_tolerance.get('risk_level', 'medium')
                reasons.append(f"リスク許容度に適合: {risk_level}")
            
            return reasons
            
        except Exception as e:
            print(f"マッチ理由取得エラー: {e}")
            return []
    
    def _calculate_personalization_confidence(self, user_behavior: Dict) -> float:
        """パーソナライズ信頼度を計算"""
        try:
            confidences = []
            
            for key, value in user_behavior.items():
                if isinstance(value, dict) and 'confidence' in value:
                    confidences.append(value['confidence'])
            
            return np.mean(confidences) if confidences else 0.5
            
        except Exception as e:
            print(f"パーソナライズ信頼度計算エラー: {e}")
            return 0.5
    
    def _generate_recommendation_reasoning(self, user_behavior: Dict, recommendations: List[Dict]) -> str:
        """推奨理由を生成"""
        try:
            reasoning_parts = []
            
            # 戦略選好
            strategy_prefs = user_behavior.get('strategy_preferences', {})
            if strategy_prefs.get('confidence', 0) > 0.3:
                preferred_strategy = strategy_prefs.get('preferred_strategy', 'balanced')
                reasoning_parts.append(f"あなたの好みの{preferred_strategy}戦略に基づいて")
            
            # リスク許容度
            risk_tolerance = user_behavior.get('risk_tolerance', {})
            if risk_tolerance.get('confidence', 0) > 0.3:
                risk_level = risk_tolerance.get('risk_level', 'medium')
                reasoning_parts.append(f"{risk_level}リスクレベルに適合する")
            
            # セクター選好
            sector_prefs = user_behavior.get('sector_preferences', {})
            if sector_prefs.get('confidence', 0) > 0.3:
                preferred_sectors = sector_prefs.get('preferred_sectors', [])
                if preferred_sectors:
                    reasoning_parts.append(f"好みのセクター({', '.join(preferred_sectors)})を含む")
            
            if reasoning_parts:
                return "これらの銘柄は" + "、".join(reasoning_parts) + "銘柄として推奨します。"
            else:
                return "一般的な投資基準に基づいて推奨します。"
            
        except Exception as e:
            print(f"推奨理由生成エラー: {e}")
            return "パーソナライズされた推奨を生成しました。"
