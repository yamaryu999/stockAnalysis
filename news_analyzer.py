import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class NewsAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_financial_news(self) -> List[Dict]:
        """金融・経済ニュースを取得"""
        news_data = []
        
        # サンプルニュースデータ（実際のニュース取得が失敗した場合のフォールバック）
        sample_news = [
            {'title': '日経平均、小幅上昇で取引終了', 'source': 'サンプル', 'timestamp': datetime.now()},
            {'title': '米国株価指数、好調な企業業績で上昇', 'source': 'サンプル', 'timestamp': datetime.now()},
            {'title': '円安進行、輸出企業に追い風', 'source': 'サンプル', 'timestamp': datetime.now()},
            {'title': 'AI関連株、技術革新で注目集める', 'source': 'サンプル', 'timestamp': datetime.now()},
            {'title': 'ESG投資、持続可能性重視の流れ加速', 'source': 'サンプル', 'timestamp': datetime.now()}
        ]
        
        try:
            # 日経新聞の経済ニュース
            nikkei_url = "https://www.nikkei.com/markets/"
            response = requests.get(nikkei_url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # ニュースタイトルを抽出（実際のサイト構造に応じて調整が必要）
                news_items = soup.find_all(['h3', 'h4', 'a'], class_=re.compile(r'title|headline|news'))
                for item in news_items[:5]:  # 最新5件
                    title = item.get_text(strip=True)
                    if title and len(title) > 10:
                        news_data.append({
                            'title': title,
                            'source': '日経新聞',
                            'timestamp': datetime.now()
                        })
        except Exception as e:
            print(f"日経新聞ニュース取得エラー: {e}")
        
        try:
            # 東洋経済オンライン
            toyokeizai_url = "https://toyokeizai.net/"
            response = requests.get(toyokeizai_url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                news_items = soup.find_all(['h3', 'h4', 'a'], class_=re.compile(r'title|headline|news'))
                for item in news_items[:3]:  # 最新3件
                    title = item.get_text(strip=True)
                    if title and len(title) > 10:
                        news_data.append({
                            'title': title,
                            'source': '東洋経済',
                            'timestamp': datetime.now()
                        })
        except Exception as e:
            print(f"東洋経済ニュース取得エラー: {e}")
        
        # ニュースが取得できない場合はサンプルデータを使用
        if not news_data:
            news_data = sample_news
        
        return news_data
    
    def analyze_market_sentiment(self, news_data: List[Dict]) -> Dict:
        """市場センチメントを分析（詳細根拠付き）"""
        positive_keywords = [
            '上昇', '好調', '成長', '増益', '好決算', '買い', '推奨', '目標株価',
            '上向き', '改善', '回復', '堅調', '活発', '拡大', '増加', 'プラス',
            '好材料', '追い風', '期待', '楽観', '強気', 'ブレイクスルー', '躍進'
        ]
        
        negative_keywords = [
            '下落', '不調', '減益', '悪決算', '売り', '警戒', 'リスク', '懸念',
            '下向き', '悪化', '減少', '縮小', 'マイナス', '調整', '不安', '危機',
            '悪材料', '逆風', '悲観', '弱気', '減速', '悪化', '困難'
        ]
        
        sector_keywords = {
            'IT・通信': ['IT', 'AI', '人工知能', 'デジタル', 'ソフトウェア', '通信', '5G', 'クラウド'],
            '金融': ['銀行', '証券', '保険', '金融', '金利', '為替', '投資'],
            '製造業': ['自動車', '電機', '機械', '化学', '鉄鋼', '製造', '工場'],
            'エネルギー': ['石油', 'ガス', '電力', 'エネルギー', '再生可能', '太陽光', '風力'],
            'ヘルスケア': ['製薬', '医療', 'バイオ', 'ヘルスケア', '医薬品', '治療'],
            '小売・サービス': ['小売', '流通', 'サービス', '飲食', '観光', 'エンタメ']
        }
        
        positive_news = []
        negative_news = []
        neutral_news = []
        sector_mentions = {}
        sentiment_score = 0
        
        for news in news_data:
            title = news['title']
            title_lower = title.lower()
            matched_positive = []
            matched_negative = []
            
            # ポジティブキーワードチェック
            for keyword in positive_keywords:
                if keyword in title_lower:
                    matched_positive.append(keyword)
                    sentiment_score += 1
            
            # ネガティブキーワードチェック
            for keyword in negative_keywords:
                if keyword in title_lower:
                    matched_negative.append(keyword)
                    sentiment_score -= 1
            
            # セクター分析
            for sector, keywords in sector_keywords.items():
                for keyword in keywords:
                    if keyword in title:
                        sector_mentions[sector] = sector_mentions.get(sector, 0) + 1
            
            # ニュース分類
            if matched_positive and not matched_negative:
                positive_news.append({
                    'title': title,
                    'source': news['source'],
                    'keywords': matched_positive
                })
            elif matched_negative and not matched_positive:
                negative_news.append({
                    'title': title,
                    'source': news['source'],
                    'keywords': matched_negative
                })
            else:
                neutral_news.append({
                    'title': title,
                    'source': news['source'],
                    'keywords': matched_positive + matched_negative
                })
        
        # センチメント判定
        if sentiment_score > 0:
            overall_sentiment = 'positive'
        elif sentiment_score < 0:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # 信頼度計算
        total_news = len(news_data)
        confidence_level = min(abs(sentiment_score) / max(total_news, 1) * 100, 100)
        
        return {
            'sentiment_score': sentiment_score,
            'sector_mentions': sector_mentions,
            'overall_sentiment': overall_sentiment,
            'confidence_level': confidence_level,
            'positive_news': positive_news[:5],  # 上位5件
            'negative_news': negative_news[:5],  # 上位5件
            'neutral_news': neutral_news[:3],    # 上位3件
            'analysis_details': {
                'positive_keywords_found': list(set([kw for news in positive_news for kw in news['keywords']])),
                'negative_keywords_found': list(set([kw for news in negative_news for kw in news['keywords']])),
                'total_news_analyzed': total_news,
                'positive_count': len(positive_news),
                'negative_count': len(negative_news),
                'neutral_count': len(neutral_news)
            }
        }
    
    def get_market_conditions(self) -> Dict:
        """現在の市場状況を分析"""
        conditions = {
            'volatility': 'normal',  # low, normal, high
            'trend': 'sideways',     # bullish, bearish, sideways
            'sector_rotation': 'none',  # tech, value, growth, none
            'risk_level': 'medium'   # low, medium, high
        }
        
        # 実際の実装では、より詳細な市場データ分析を行う
        # ここでは簡易的な例を示す
        
        return conditions
    
    def suggest_screening_criteria(self, sentiment_data: Dict, market_conditions: Dict) -> Dict:
        """市場状況に基づいてスクリーニング条件を提案"""
        
        # 基本条件
        base_criteria = {
            'pe_min': 5.0,
            'pe_max': 20.0,
            'pb_min': 0.5,
            'pb_max': 2.0,
            'roe_min': 10.0,
            'dividend_min': 2.0,
            'debt_max': 50.0
        }
        
        # センチメントに基づく調整
        if sentiment_data['overall_sentiment'] == 'positive':
            # 好材料が多い場合は、やや積極的な条件
            base_criteria['pe_max'] = 25.0
            base_criteria['pb_max'] = 2.5
            base_criteria['roe_min'] = 8.0
        elif sentiment_data['overall_sentiment'] == 'negative':
            # 悪材料が多い場合は、より保守的な条件
            base_criteria['pe_max'] = 15.0
            base_criteria['pb_max'] = 1.5
            base_criteria['roe_min'] = 12.0
            base_criteria['dividend_min'] = 2.5
        
        # 市場状況に基づく調整
        if market_conditions['volatility'] == 'high':
            # 高ボラティリティの場合は、より厳格な条件
            base_criteria['debt_max'] = 40.0
            base_criteria['dividend_min'] = 2.5
        elif market_conditions['volatility'] == 'low':
            # 低ボラティリティの場合は、やや緩い条件
            base_criteria['pe_max'] = 22.0
            base_criteria['pb_max'] = 2.2
        
        # セクター別の推奨
        recommended_sectors = []
        if sentiment_data['sector_mentions']:
            sorted_sectors = sorted(sentiment_data['sector_mentions'].items(), 
                                  key=lambda x: x[1], reverse=True)
            recommended_sectors = [sector for sector, count in sorted_sectors[:3]]
        
        return {
            'criteria': base_criteria,
            'recommended_sectors': recommended_sectors,
            'reasoning': self._generate_reasoning(sentiment_data, market_conditions),
            'investment_strategy': self._suggest_strategy(sentiment_data, market_conditions)
        }
    
    def _generate_reasoning(self, sentiment_data: Dict, market_conditions: Dict) -> str:
        """推奨理由を生成"""
        reasoning_parts = []
        
        if sentiment_data['overall_sentiment'] == 'positive':
            reasoning_parts.append("市場センチメントが良好なため、やや積極的な投資条件を推奨")
        elif sentiment_data['overall_sentiment'] == 'negative':
            reasoning_parts.append("市場センチメントが慎重なため、保守的な投資条件を推奨")
        
        if market_conditions['volatility'] == 'high':
            reasoning_parts.append("市場のボラティリティが高いため、財務健全性を重視")
        
        if sentiment_data['sector_mentions']:
            top_sector = max(sentiment_data['sector_mentions'].items(), key=lambda x: x[1])
            reasoning_parts.append(f"{top_sector[0]}セクターが注目されているため、関連銘柄を検討")
        
        return "。".join(reasoning_parts) + "。"
    
    def _suggest_strategy(self, sentiment_data: Dict, market_conditions: Dict) -> str:
        """投資戦略を提案"""
        if sentiment_data['overall_sentiment'] == 'positive' and market_conditions['volatility'] == 'low':
            return "グロース投資戦略"
        elif sentiment_data['overall_sentiment'] == 'negative' or market_conditions['volatility'] == 'high':
            return "バリュー投資戦略"
        else:
            return "バランス型投資戦略"
    
    def get_current_recommendations(self) -> Dict:
        """現在の推奨条件を取得"""
        try:
            # ニュース取得
            news_data = self.get_financial_news()
            
            # センチメント分析
            sentiment_data = self.analyze_market_sentiment(news_data)
            
            # 市場状況分析
            market_conditions = self.get_market_conditions()
            
            # 推奨条件生成
            recommendations = self.suggest_screening_criteria(sentiment_data, market_conditions)
            
            return {
                'news_data': news_data,
                'sentiment_data': sentiment_data,
                'market_conditions': market_conditions,
                'recommendations': recommendations,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"推奨条件生成エラー: {e}")
            # エラー時はデフォルト条件を返す
            return {
                'news_data': [],
                'sentiment_data': {'overall_sentiment': 'neutral', 'sector_mentions': {}},
                'market_conditions': {'volatility': 'normal', 'trend': 'sideways'},
                'recommendations': {
                    'criteria': {
                        'pe_min': 5.0, 'pe_max': 20.0, 'pb_min': 0.5, 'pb_max': 2.0,
                        'roe_min': 10.0, 'dividend_min': 2.0, 'debt_max': 50.0
                    },
                    'recommended_sectors': [],
                    'reasoning': 'デフォルトのバランス型投資条件を推奨',
                    'investment_strategy': 'バランス型投資戦略'
                },
                'timestamp': datetime.now()
            }
