from typing import Dict, List
from datetime import datetime

class InvestmentStrategies:
    def __init__(self):
        self.strategies = {
            'value': {
                'name': 'バリュー投資（割安株重視）',
                'description': 'PER・PBRが低く、配当利回りが高い割安株を重視',
                'criteria': {
                    'pe_min': 3.0,
                    'pe_max': 15.0,
                    'pb_min': 0.3,
                    'pb_max': 1.5,
                    'roe_min': 8.0,
                    'dividend_min': 2.5,
                    'debt_max': 50.0
                },
                'priority_factors': ['PER', 'PBR', '配当利回り', '財務健全性'],
                'suitable_for': '長期投資、安定収益重視'
            },
            'growth': {
                'name': 'グロース投資（成長株重視）',
                'description': '売上・利益成長率が高く、将来性のある成長株を重視',
                'criteria': {
                    'pe_min': 10.0,
                    'pe_max': 30.0,
                    'pb_min': 1.0,
                    'pb_max': 3.0,
                    'roe_min': 15.0,
                    'dividend_min': 1.0,
                    'debt_max': 70.0
                },
                'priority_factors': ['ROE', '成長率', '将来性', '競争優位性'],
                'suitable_for': '中長期投資、成長期待重視'
            },
            'dividend': {
                'name': '配当投資（インカムゲイン重視）',
                'description': '安定した配当利回りと継続的な配当支払いを重視',
                'criteria': {
                    'pe_min': 5.0,
                    'pe_max': 20.0,
                    'pb_min': 0.5,
                    'pb_max': 2.0,
                    'roe_min': 10.0,
                    'dividend_min': 3.0,
                    'debt_max': 40.0
                },
                'priority_factors': ['配当利回り', '配当継続性', '財務安定性', 'キャッシュフロー'],
                'suitable_for': '長期投資、安定収入重視'
            },
            'balanced': {
                'name': 'バランス型投資',
                'description': 'バリューとグロースのバランスを取った投資',
                'criteria': {
                    'pe_min': 5.0,
                    'pe_max': 20.0,
                    'pb_min': 0.5,
                    'pb_max': 2.0,
                    'roe_min': 10.0,
                    'dividend_min': 2.0,
                    'debt_max': 50.0
                },
                'priority_factors': ['バランス', 'リスク管理', '分散投資', '安定性'],
                'suitable_for': '中長期投資、リスク分散重視'
            },
            'defensive': {
                'name': 'ディフェンシブ投資（防御的投資）',
                'description': '景気変動に強い安定した企業を重視',
                'criteria': {
                    'pe_min': 8.0,
                    'pe_max': 18.0,
                    'pb_min': 0.8,
                    'pb_max': 1.8,
                    'roe_min': 8.0,
                    'dividend_min': 2.5,
                    'debt_max': 30.0
                },
                'priority_factors': ['財務健全性', '事業安定性', '配当継続性', 'リスク管理'],
                'suitable_for': '長期投資、リスク回避重視'
            },
            'aggressive': {
                'name': 'アグレッシブ投資（積極的投資）',
                'description': '高いリターンを狙う積極的な投資',
                'criteria': {
                    'pe_min': 5.0,
                    'pe_max': 35.0,
                    'pb_min': 0.5,
                    'pb_max': 4.0,
                    'roe_min': 12.0,
                    'dividend_min': 0.5,
                    'debt_max': 80.0
                },
                'priority_factors': ['成長性', 'ROE', '将来性', 'リターン'],
                'suitable_for': '中短期投資、高リターン重視'
            }
        }
    
    def get_strategy(self, strategy_name: str) -> Dict:
        """指定された投資戦略を取得"""
        return self.strategies.get(strategy_name, self.strategies['balanced'])
    
    def get_all_strategies(self) -> Dict:
        """すべての投資戦略を取得"""
        return self.strategies
    
    def suggest_strategy_by_market_conditions(self, market_conditions: Dict) -> str:
        """市場状況に基づいて投資戦略を提案"""
        volatility = market_conditions.get('volatility', 'normal')
        trend = market_conditions.get('trend', 'sideways')
        risk_level = market_conditions.get('risk_level', 'medium')
        
        if risk_level == 'high' or volatility == 'high':
            return 'defensive'
        elif trend == 'bullish' and volatility == 'low':
            return 'growth'
        elif trend == 'bearish':
            return 'value'
        elif volatility == 'low' and risk_level == 'low':
            return 'aggressive'
        else:
            return 'balanced'
    
    def get_sector_recommendations(self, strategy_name: str) -> List[str]:
        """投資戦略に基づくセクター推奨"""
        sector_recommendations = {
            'value': ['金融', 'エネルギー', '素材', '公益'],
            'growth': ['IT・通信', 'ヘルスケア', '消費財', 'テクノロジー'],
            'dividend': ['公益', '金融', 'エネルギー', '通信'],
            'balanced': ['IT・通信', '金融', '製造業', 'ヘルスケア'],
            'defensive': ['公益', 'ヘルスケア', '消費財', '通信'],
            'aggressive': ['IT・通信', 'バイオテクノロジー', '新興技術', 'グロース']
        }
        
        return sector_recommendations.get(strategy_name, sector_recommendations['balanced'])
    
    def get_risk_profile(self, strategy_name: str) -> Dict:
        """投資戦略のリスクプロファイル"""
        risk_profiles = {
            'value': {'risk_level': 'medium', 'expected_return': 'medium', 'volatility': 'low'},
            'growth': {'risk_level': 'high', 'expected_return': 'high', 'volatility': 'high'},
            'dividend': {'risk_level': 'low', 'expected_return': 'low', 'volatility': 'low'},
            'balanced': {'risk_level': 'medium', 'expected_return': 'medium', 'volatility': 'medium'},
            'defensive': {'risk_level': 'low', 'expected_return': 'low', 'volatility': 'low'},
            'aggressive': {'risk_level': 'high', 'expected_return': 'high', 'volatility': 'high'}
        }
        
        return risk_profiles.get(strategy_name, risk_profiles['balanced'])
    
    def get_time_horizon(self, strategy_name: str) -> str:
        """投資戦略に適した投資期間"""
        time_horizons = {
            'value': '長期（3-5年以上）',
            'growth': '中長期（2-5年）',
            'dividend': '長期（5年以上）',
            'balanced': '中長期（2-5年）',
            'defensive': '長期（3-5年以上）',
            'aggressive': '中短期（1-3年）'
        }
        
        return time_horizons.get(strategy_name, '中長期（2-5年）')
    
    def get_portfolio_allocation_suggestion(self, strategy_name: str) -> Dict:
        """投資戦略に基づくポートフォリオ配分提案"""
        allocations = {
            'value': {
                'large_cap': 60,
                'mid_cap': 30,
                'small_cap': 10,
                'sector_diversification': '高',
                'geographic_diversification': '中'
            },
            'growth': {
                'large_cap': 40,
                'mid_cap': 40,
                'small_cap': 20,
                'sector_diversification': '中',
                'geographic_diversification': '高'
            },
            'dividend': {
                'large_cap': 80,
                'mid_cap': 15,
                'small_cap': 5,
                'sector_diversification': '高',
                'geographic_diversification': '中'
            },
            'balanced': {
                'large_cap': 50,
                'mid_cap': 35,
                'small_cap': 15,
                'sector_diversification': '高',
                'geographic_diversification': '高'
            },
            'defensive': {
                'large_cap': 70,
                'mid_cap': 25,
                'small_cap': 5,
                'sector_diversification': '高',
                'geographic_diversification': '中'
            },
            'aggressive': {
                'large_cap': 30,
                'mid_cap': 40,
                'small_cap': 30,
                'sector_diversification': '中',
                'geographic_diversification': '高'
            }
        }
        
        return allocations.get(strategy_name, allocations['balanced'])
