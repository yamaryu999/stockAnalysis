"""
高度なAI分析機能
ニュース分析、センチメント分析、パターン認識、予測機能を統合
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

class AdvancedAIAnalyzer:
    """高度なAI分析を行うクラス"""
    
    def __init__(self):
        self.sentiment_model = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.news_cache = {}
        self.pattern_cache = {}
        
    def analyze_market_sentiment(self, symbols: List[str], days_back: int = 7) -> Dict:
        """市場センチメント分析"""
        try:
            sentiment_results = {}
            
            for symbol in symbols:
                # ニュースデータを取得
                news_data = self._fetch_news_data(symbol, days_back)
                
                if news_data:
                    # センチメント分析を実行
                    sentiment_score = self._analyze_sentiment(news_data)
                    
                    # キーワード分析
                    keywords = self._extract_keywords(news_data)
                    
                    # セクター分析
                    sector_impact = self._analyze_sector_impact(symbol, news_data)
                    
                    sentiment_results[symbol] = {
                        'sentiment_score': sentiment_score,
                        'keywords': keywords,
                        'sector_impact': sector_impact,
                        'news_count': len(news_data),
                        'confidence': self._calculate_confidence(news_data)
                    }
            
            return sentiment_results
            
        except Exception as e:
            print(f"センチメント分析エラー: {e}")
            return {}
    
    def detect_trading_patterns(self, symbol: str, period: str = "1y") -> Dict:
        """取引パターン検出"""
        try:
            # 株価データを取得
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return {}
            
            patterns = {}
            
            # サポート・レジスタンスレベル検出
            patterns['support_resistance'] = self._detect_support_resistance(data)
            
            # トレンドライン検出
            patterns['trend_lines'] = self._detect_trend_lines(data)
            
            # チャートパターン検出
            patterns['chart_patterns'] = self._detect_chart_patterns(data)
            
            # ボラティリティパターン
            patterns['volatility_patterns'] = self._analyze_volatility_patterns(data)
            
            # ボリュームパターン
            patterns['volume_patterns'] = self._analyze_volume_patterns(data)
            
            return patterns
            
        except Exception as e:
            print(f"パターン検出エラー: {e}")
            return {}
    
    def predict_price_movement(self, symbol: str, days_ahead: int = 5) -> Dict:
        """価格変動予測"""
        try:
            # 株価データを取得
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2y")
            
            if data.empty or len(data) < 100:
                return {}
            
            # 技術指標を計算
            technical_indicators = self._calculate_technical_indicators(data)
            
            # 価格予測モデル
            price_prediction = self._predict_price(data, technical_indicators, days_ahead)
            
            # リスク評価
            risk_assessment = self._assess_risk(data, technical_indicators)
            
            # 信頼度計算
            confidence = self._calculate_prediction_confidence(data, technical_indicators)
            
            return {
                'predicted_price': price_prediction,
                'risk_assessment': risk_assessment,
                'confidence': confidence,
                'technical_indicators': technical_indicators,
                'recommendation': self._generate_recommendation(price_prediction, risk_assessment, confidence)
            }
            
        except Exception as e:
            print(f"価格予測エラー: {e}")
            return {}
    
    def generate_ai_recommendations(self, symbols: List[str], user_preferences: Dict = None) -> Dict:
        """AI推奨銘柄の生成"""
        try:
            recommendations = {}
            
            for symbol in symbols:
                # 総合スコアを計算
                total_score = 0
                factors = {}
                
                # センチメント分析
                sentiment_data = self.analyze_market_sentiment([symbol])
                if symbol in sentiment_data:
                    sentiment_score = sentiment_data[symbol]['sentiment_score']
                    factors['sentiment'] = sentiment_score
                    total_score += sentiment_score * 0.3
                
                # パターン分析
                patterns = self.detect_trading_patterns(symbol)
                pattern_score = self._calculate_pattern_score(patterns)
                factors['patterns'] = pattern_score
                total_score += pattern_score * 0.2
                
                # 価格予測
                prediction = self.predict_price_movement(symbol)
                if prediction:
                    prediction_score = self._calculate_prediction_score(prediction)
                    factors['prediction'] = prediction_score
                    total_score += prediction_score * 0.3
                
                # リスク評価
                risk_score = self._calculate_risk_score(symbol)
                factors['risk'] = risk_score
                total_score += risk_score * 0.2
                
                # 推奨度を計算
                recommendation_level = self._calculate_recommendation_level(total_score, factors)
                
                recommendations[symbol] = {
                    'total_score': total_score,
                    'factors': factors,
                    'recommendation_level': recommendation_level,
                    'confidence': self._calculate_overall_confidence(factors),
                    'reasoning': self._generate_reasoning(factors, recommendation_level)
                }
            
            # スコア順にソート
            sorted_recommendations = dict(sorted(recommendations.items(), 
                                                key=lambda x: x[1]['total_score'], 
                                                reverse=True))
            
            return sorted_recommendations
            
        except Exception as e:
            print(f"AI推奨生成エラー: {e}")
            return {}
    
    def _fetch_news_data(self, symbol: str, days_back: int) -> List[Dict]:
        """ニュースデータを取得"""
        try:
            # キャッシュをチェック
            cache_key = f"{symbol}_{days_back}"
            if cache_key in self.news_cache:
                return self.news_cache[cache_key]
            
            news_data = []
            
            # Yahoo Finance ニュース
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            for article in news[:20]:  # 最新20件
                if article.get('title') and article.get('summary'):
                    news_data.append({
                        'title': article['title'],
                        'summary': article['summary'],
                        'published': article.get('providerPublishTime', 0),
                        'source': 'Yahoo Finance'
                    })
            
            # キャッシュに保存
            self.news_cache[cache_key] = news_data
            
            return news_data
            
        except Exception as e:
            print(f"ニュース取得エラー: {e}")
            return []
    
    def _analyze_sentiment(self, news_data: List[Dict]) -> float:
        """センチメント分析"""
        try:
            if not news_data:
                return 0.0
            
            # テキストを結合
            texts = [item['title'] + ' ' + item['summary'] for item in news_data]
            
            # 簡単なセンチメント分析（キーワードベース）
            positive_words = ['上昇', '成長', '好調', '改善', '増加', '利益', '成功', '強気']
            negative_words = ['下落', '減少', '悪化', '損失', '弱気', '懸念', 'リスク', '問題']
            
            total_score = 0
            word_count = 0
            
            for text in texts:
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count + negative_count > 0:
                    score = (positive_count - negative_count) / (positive_count + negative_count)
                    total_score += score
                    word_count += 1
            
            return total_score / word_count if word_count > 0 else 0.0
            
        except Exception as e:
            print(f"センチメント分析エラー: {e}")
            return 0.0
    
    def _extract_keywords(self, news_data: List[Dict]) -> List[str]:
        """キーワード抽出"""
        try:
            if not news_data:
                return []
            
            # テキストを結合
            texts = [item['title'] + ' ' + item['summary'] for item in news_data]
            combined_text = ' '.join(texts)
            
            # 簡単なキーワード抽出（頻出単語）
            words = re.findall(r'\b\w+\b', combined_text.lower())
            word_freq = pd.Series(words).value_counts()
            
            # ストップワードを除外
            stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
            
            keywords = word_freq[~word_freq.index.isin(stop_words)].head(10)
            
            return keywords.index.tolist()
            
        except Exception as e:
            print(f"キーワード抽出エラー: {e}")
            return []
    
    def _analyze_sector_impact(self, symbol: str, news_data: List[Dict]) -> Dict:
        """セクター影響分析"""
        try:
            # セクターキーワード
            sector_keywords = {
                'technology': ['テクノロジー', 'IT', 'ソフトウェア', 'ハードウェア', 'AI', '人工知能'],
                'finance': ['金融', '銀行', '保険', '証券', '投資'],
                'healthcare': ['医療', '製薬', 'バイオ', 'ヘルスケア'],
                'automotive': ['自動車', '車', 'トヨタ', 'ホンダ', '日産'],
                'energy': ['エネルギー', '石油', 'ガス', '電力', '再生可能']
            }
            
            sector_mentions = {}
            
            for sector, keywords in sector_keywords.items():
                mentions = 0
                for item in news_data:
                    text = (item['title'] + ' ' + item['summary']).lower()
                    mentions += sum(1 for keyword in keywords if keyword in text)
                
                sector_mentions[sector] = mentions
            
            return sector_mentions
            
        except Exception as e:
            print(f"セクター分析エラー: {e}")
            return {}
    
    def _calculate_confidence(self, news_data: List[Dict]) -> float:
        """信頼度計算"""
        try:
            if not news_data:
                return 0.0
            
            # ニュース数に基づく信頼度
            news_count = len(news_data)
            confidence = min(news_count / 10, 1.0)  # 10件で最大信頼度
            
            return confidence
            
        except Exception as e:
            print(f"信頼度計算エラー: {e}")
            return 0.0
    
    def _detect_support_resistance(self, data: pd.DataFrame) -> Dict:
        """サポート・レジスタンスレベル検出"""
        try:
            highs = data['High'].rolling(window=20).max()
            lows = data['Low'].rolling(window=20).min()
            
            # サポートレベル（過去の安値）
            support_levels = data[data['Low'] == lows]['Low'].dropna().tail(3).tolist()
            
            # レジスタンスレベル（過去の高値）
            resistance_levels = data[data['High'] == highs]['High'].dropna().tail(3).tolist()
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'current_price': data['Close'].iloc[-1],
                'distance_to_support': data['Close'].iloc[-1] - min(support_levels) if support_levels else 0,
                'distance_to_resistance': max(resistance_levels) - data['Close'].iloc[-1] if resistance_levels else 0
            }
            
        except Exception as e:
            print(f"サポート・レジスタンス検出エラー: {e}")
            return {}
    
    def _detect_trend_lines(self, data: pd.DataFrame) -> Dict:
        """トレンドライン検出"""
        try:
            # 簡単なトレンドライン検出
            closes = data['Close'].values
            
            # 移動平均線
            ma_20 = data['Close'].rolling(window=20).mean()
            ma_50 = data['Close'].rolling(window=50).mean()
            
            # トレンド判定
            current_trend = 'sideways'
            if ma_20.iloc[-1] > ma_50.iloc[-1]:
                current_trend = 'uptrend'
            elif ma_20.iloc[-1] < ma_50.iloc[-1]:
                current_trend = 'downtrend'
            
            return {
                'trend': current_trend,
                'ma_20': ma_20.iloc[-1],
                'ma_50': ma_50.iloc[-1],
                'trend_strength': abs(ma_20.iloc[-1] - ma_50.iloc[-1]) / ma_50.iloc[-1]
            }
            
        except Exception as e:
            print(f"トレンドライン検出エラー: {e}")
            return {}
    
    def _detect_chart_patterns(self, data: pd.DataFrame) -> Dict:
        """チャートパターン検出"""
        try:
            patterns = {}
            
            # ヘッドアンドショルダー検出（簡易版）
            highs = data['High'].rolling(window=5).max()
            pattern_points = data[data['High'] == highs]['High'].dropna().tail(5)
            
            if len(pattern_points) >= 3:
                # 簡単なパターン検出
                values = pattern_points.values
                if len(values) >= 3:
                    # 中央が最高値かチェック
                    if values[1] > values[0] and values[1] > values[2]:
                        patterns['head_and_shoulders'] = True
                    else:
                        patterns['head_and_shoulders'] = False
            
            return patterns
            
        except Exception as e:
            print(f"チャートパターン検出エラー: {e}")
            return {}
    
    def _analyze_volatility_patterns(self, data: pd.DataFrame) -> Dict:
        """ボラティリティパターン分析"""
        try:
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # 年率ボラティリティ
            
            # ボラティリティの変化
            recent_volatility = returns.tail(20).std() * np.sqrt(252)
            historical_volatility = returns.std() * np.sqrt(252)
            
            volatility_change = (recent_volatility - historical_volatility) / historical_volatility
            
            return {
                'current_volatility': volatility,
                'recent_volatility': recent_volatility,
                'volatility_change': volatility_change,
                'volatility_trend': 'increasing' if volatility_change > 0.1 else 'decreasing' if volatility_change < -0.1 else 'stable'
            }
            
        except Exception as e:
            print(f"ボラティリティ分析エラー: {e}")
            return {}
    
    def _analyze_volume_patterns(self, data: pd.DataFrame) -> Dict:
        """ボリュームパターン分析"""
        try:
            avg_volume = data['Volume'].mean()
            recent_volume = data['Volume'].tail(5).mean()
            
            volume_ratio = recent_volume / avg_volume
            
            return {
                'average_volume': avg_volume,
                'recent_volume': recent_volume,
                'volume_ratio': volume_ratio,
                'volume_trend': 'high' if volume_ratio > 1.5 else 'low' if volume_ratio < 0.5 else 'normal'
            }
            
        except Exception as e:
            print(f"ボリューム分析エラー: {e}")
            return {}
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """技術指標計算"""
        try:
            indicators = {}
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.iloc[-1]
            
            # MACD
            ema_12 = data['Close'].ewm(span=12).mean()
            ema_26 = data['Close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            indicators['macd'] = macd.iloc[-1]
            indicators['macd_signal'] = signal.iloc[-1]
            
            # ボリンジャーバンド
            sma_20 = data['Close'].rolling(window=20).mean()
            std_20 = data['Close'].rolling(window=20).std()
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            indicators['bb_upper'] = upper_band.iloc[-1]
            indicators['bb_middle'] = sma_20.iloc[-1]
            indicators['bb_lower'] = lower_band.iloc[-1]
            
            return indicators
            
        except Exception as e:
            print(f"技術指標計算エラー: {e}")
            return {}
    
    def _predict_price(self, data: pd.DataFrame, indicators: Dict, days_ahead: int) -> Dict:
        """価格予測"""
        try:
            # 簡単な価格予測（移動平均ベース）
            current_price = data['Close'].iloc[-1]
            ma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
            
            # トレンドに基づく予測
            trend_factor = (ma_20 - ma_50) / ma_50
            
            # ボラティリティを考慮
            volatility = data['Close'].pct_change().std()
            
            predicted_prices = []
            for i in range(1, days_ahead + 1):
                price_change = trend_factor * i * volatility
                predicted_price = current_price * (1 + price_change)
                predicted_prices.append(predicted_price)
            
            return {
                'predicted_prices': predicted_prices,
                'price_change_percent': (predicted_prices[-1] - current_price) / current_price * 100,
                'trend_direction': 'up' if trend_factor > 0 else 'down' if trend_factor < 0 else 'sideways'
            }
            
        except Exception as e:
            print(f"価格予測エラー: {e}")
            return {}
    
    def _assess_risk(self, data: pd.DataFrame, indicators: Dict) -> Dict:
        """リスク評価"""
        try:
            risk_factors = {}
            
            # ボラティリティリスク
            volatility = data['Close'].pct_change().std() * np.sqrt(252)
            risk_factors['volatility_risk'] = 'high' if volatility > 0.3 else 'medium' if volatility > 0.2 else 'low'
            
            # RSIリスク
            rsi = indicators.get('rsi', 50)
            risk_factors['rsi_risk'] = 'high' if rsi > 80 or rsi < 20 else 'medium' if rsi > 70 or rsi < 30 else 'low'
            
            # 総合リスクスコア
            risk_score = 0
            if risk_factors['volatility_risk'] == 'high':
                risk_score += 0.6
            elif risk_factors['volatility_risk'] == 'medium':
                risk_score += 0.3
            
            if risk_factors['rsi_risk'] == 'high':
                risk_score += 0.4
            elif risk_factors['rsi_risk'] == 'medium':
                risk_score += 0.2
            
            overall_risk = 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.3 else 'low'
            
            return {
                'overall_risk': overall_risk,
                'risk_score': risk_score,
                'risk_factors': risk_factors
            }
            
        except Exception as e:
            print(f"リスク評価エラー: {e}")
            return {}
    
    def _calculate_prediction_confidence(self, data: pd.DataFrame, indicators: Dict) -> float:
        """予測信頼度計算"""
        try:
            confidence = 0.5  # ベース信頼度
            
            # データ量に基づく信頼度
            if len(data) > 200:
                confidence += 0.2
            elif len(data) > 100:
                confidence += 0.1
            
            # RSIの信頼度
            rsi = indicators.get('rsi', 50)
            if 30 <= rsi <= 70:
                confidence += 0.1
            
            # MACDの信頼度
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if abs(macd - macd_signal) > 0.01:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            print(f"信頼度計算エラー: {e}")
            return 0.5
    
    def _generate_recommendation(self, prediction: Dict, risk: Dict, confidence: float) -> str:
        """推奨アクション生成"""
        try:
            if not prediction or not risk:
                return "データ不足"
            
            price_change = prediction.get('price_change_percent', 0)
            overall_risk = risk.get('overall_risk', 'medium')
            
            if confidence < 0.6:
                return "信頼度が低いため推奨なし"
            
            if overall_risk == 'high':
                return "リスクが高いため注意が必要"
            
            if price_change > 5:
                return "強気推奨"
            elif price_change > 2:
                return "買い推奨"
            elif price_change < -5:
                return "売り推奨"
            elif price_change < -2:
                return "弱気推奨"
            else:
                return "中立"
                
        except Exception as e:
            print(f"推奨生成エラー: {e}")
            return "エラー"
    
    def _calculate_pattern_score(self, patterns: Dict) -> float:
        """パターンスコア計算"""
        try:
            score = 0.5  # ベーススコア
            
            # トレンドスコア
            trend = patterns.get('trend_lines', {}).get('trend', 'sideways')
            if trend == 'uptrend':
                score += 0.3
            elif trend == 'downtrend':
                score -= 0.3
            
            # ボラティリティスコア
            vol_trend = patterns.get('volatility_patterns', {}).get('volatility_trend', 'stable')
            if vol_trend == 'stable':
                score += 0.1
            
            return max(0, min(1, score))
            
        except Exception as e:
            print(f"パターンスコア計算エラー: {e}")
            return 0.5
    
    def _calculate_prediction_score(self, prediction: Dict) -> float:
        """予測スコア計算"""
        try:
            if not prediction:
                return 0.5
            
            price_change = prediction.get('price_change_percent', 0)
            
            # 価格変動に基づくスコア
            if price_change > 10:
                return 0.9
            elif price_change > 5:
                return 0.8
            elif price_change > 2:
                return 0.7
            elif price_change > 0:
                return 0.6
            elif price_change > -2:
                return 0.4
            elif price_change > -5:
                return 0.3
            else:
                return 0.1
                
        except Exception as e:
            print(f"予測スコア計算エラー: {e}")
            return 0.5
    
    def _calculate_risk_score(self, symbol: str) -> float:
        """リスクスコア計算"""
        try:
            # 簡単なリスクスコア（ボラティリティベース）
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")
            
            if data.empty:
                return 0.5
            
            volatility = data['Close'].pct_change().std() * np.sqrt(252)
            
            # ボラティリティをスコアに変換
            if volatility > 0.4:
                return 0.1  # 高リスク
            elif volatility > 0.3:
                return 0.3  # 中高リスク
            elif volatility > 0.2:
                return 0.5  # 中リスク
            elif volatility > 0.1:
                return 0.7  # 低リスク
            else:
                return 0.9  # 超低リスク
                
        except Exception as e:
            print(f"リスクスコア計算エラー: {e}")
            return 0.5
    
    def _calculate_recommendation_level(self, total_score: float, factors: Dict) -> str:
        """推奨レベル計算"""
        try:
            if total_score > 0.8:
                return "強力推奨"
            elif total_score > 0.6:
                return "推奨"
            elif total_score > 0.4:
                return "中立"
            elif total_score > 0.2:
                return "注意"
            else:
                return "非推奨"
                
        except Exception as e:
            print(f"推奨レベル計算エラー: {e}")
            return "不明"
    
    def _calculate_overall_confidence(self, factors: Dict) -> float:
        """総合信頼度計算"""
        try:
            confidence = 0.5
            
            # 各要因の信頼度を考慮
            for factor, value in factors.items():
                if isinstance(value, (int, float)):
                    confidence += abs(value) * 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            print(f"総合信頼度計算エラー: {e}")
            return 0.5
    
    def _generate_reasoning(self, factors: Dict, recommendation_level: str) -> str:
        """推奨理由生成"""
        try:
            reasoning_parts = []
            
            # センチメント要因
            sentiment = factors.get('sentiment', 0)
            if sentiment > 0.3:
                reasoning_parts.append("市場センチメントが良好")
            elif sentiment < -0.3:
                reasoning_parts.append("市場センチメントが悪化")
            
            # パターン要因
            patterns = factors.get('patterns', 0)
            if patterns > 0.7:
                reasoning_parts.append("技術的パターンが良好")
            elif patterns < 0.3:
                reasoning_parts.append("技術的パターンに懸念")
            
            # 予測要因
            prediction = factors.get('prediction', 0)
            if prediction > 0.7:
                reasoning_parts.append("価格予測が上向き")
            elif prediction < 0.3:
                reasoning_parts.append("価格予測が下向き")
            
            # リスク要因
            risk = factors.get('risk', 0)
            if risk > 0.7:
                reasoning_parts.append("リスクが低い")
            elif risk < 0.3:
                reasoning_parts.append("リスクが高い")
            
            if not reasoning_parts:
                reasoning_parts.append("総合的な分析結果")
            
            return f"{recommendation_level}: {', '.join(reasoning_parts)}"
            
        except Exception as e:
            print(f"推奨理由生成エラー: {e}")
            return f"{recommendation_level}: 分析結果に基づく推奨"