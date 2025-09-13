import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class StockForecastAnalyzer:
    """銘柄の今後の動向分析と予想を行うクラス"""
    
    def __init__(self):
        self.forecast_results = {}
    
    def calculate_technical_indicators(self, stock_data: pd.DataFrame) -> Dict:
        """技術分析指標を計算"""
        if stock_data is None or stock_data.empty:
            return {}
        
        try:
            # 移動平均線
            stock_data['MA5'] = stock_data['Close'].rolling(window=5).mean()
            stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
            stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
            
            # RSI (相対力指数)
            delta = stock_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            stock_data['RSI'] = rsi
            
            # MACD
            exp1 = stock_data['Close'].ewm(span=12).mean()
            exp2 = stock_data['Close'].ewm(span=26).mean()
            stock_data['MACD'] = exp1 - exp2
            stock_data['MACD_Signal'] = stock_data['MACD'].ewm(span=9).mean()
            stock_data['MACD_Histogram'] = stock_data['MACD'] - stock_data['MACD_Signal']
            
            # ボリンジャーバンド
            stock_data['BB_Middle'] = stock_data['Close'].rolling(window=20).mean()
            bb_std = stock_data['Close'].rolling(window=20).std()
            stock_data['BB_Upper'] = stock_data['BB_Middle'] + (bb_std * 2)
            stock_data['BB_Lower'] = stock_data['BB_Middle'] - (bb_std * 2)
            
            # 最新の値
            latest = stock_data.iloc[-1]
            
            return {
                'ma5': latest['MA5'],
                'ma20': latest['MA20'],
                'ma50': latest['MA50'],
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'macd_signal': latest['MACD_Signal'],
                'macd_histogram': latest['MACD_Histogram'],
                'bb_upper': latest['BB_Upper'],
                'bb_middle': latest['BB_Middle'],
                'bb_lower': latest['BB_Lower'],
                'current_price': latest['Close']
            }
        except Exception as e:
            print(f"技術指標計算エラー: {e}")
            return {}
    
    def analyze_technical_trend(self, indicators: Dict) -> Dict:
        """技術分析によるトレンド分析"""
        if not indicators:
            return {'trend': 'neutral', 'score': 0, 'reasons': []}
        
        score = 0
        reasons = []
        
        current_price = indicators['current_price']
        ma5 = indicators.get('ma5', 0)
        ma20 = indicators.get('ma20', 0)
        ma50 = indicators.get('ma50', 0)
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_histogram = indicators.get('macd_histogram', 0)
        
        # 移動平均線分析
        if current_price > ma5 > ma20 > ma50:
            score += 3
            reasons.append("✅ 上昇トレンド: 価格が全移動平均線を上回る")
        elif current_price < ma5 < ma20 < ma50:
            score -= 3
            reasons.append("❌ 下降トレンド: 価格が全移動平均線を下回る")
        elif current_price > ma20:
            score += 1
            reasons.append("📈 中期的に上昇傾向")
        elif current_price < ma20:
            score -= 1
            reasons.append("📉 中期的に下降傾向")
        
        # RSI分析
        if rsi < 30:
            score += 2
            reasons.append("🔄 売られすぎ: RSIが30を下回る（反発期待）")
        elif rsi > 70:
            score -= 2
            reasons.append("⚠️ 買われすぎ: RSIが70を上回る（調整リスク）")
        elif 40 <= rsi <= 60:
            score += 1
            reasons.append("⚖️ バランス良好: RSIが適正水準")
        
        # MACD分析
        if macd > macd_signal and macd_histogram > 0:
            score += 2
            reasons.append("📊 買いシグナル: MACDがシグナル線を上抜け")
        elif macd < macd_signal and macd_histogram < 0:
            score -= 2
            reasons.append("📊 売りシグナル: MACDがシグナル線を下抜け")
        
        # ボリンジャーバンド分析
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        if current_price > bb_upper:
            score -= 1
            reasons.append("📈 ボリンジャーバンド上限突破（過熱感）")
        elif current_price < bb_lower:
            score += 1
            reasons.append("📉 ボリンジャーバンド下限突破（反発期待）")
        
        # トレンド判定
        if score >= 3:
            trend = 'strong_bullish'
        elif score >= 1:
            trend = 'bullish'
        elif score <= -3:
            trend = 'strong_bearish'
        elif score <= -1:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'trend': trend,
            'score': score,
            'reasons': reasons
        }
    
    def analyze_fundamental_strength(self, metrics: Dict) -> Dict:
        """ファンダメンタル分析による強度評価"""
        if not metrics:
            return {'strength': 'neutral', 'score': 0, 'reasons': []}
        
        score = 0
        reasons = []
        
        per = metrics.get('per', 0)
        pbr = metrics.get('pbr', 0)
        roe = metrics.get('roe', 0)
        debt_ratio = metrics.get('debt_ratio', 0)
        dividend_yield = metrics.get('dividend_yield', 0)
        
        # PER分析
        if 0 < per < 15:
            score += 2
            reasons.append("💰 割安: PERが15倍未満")
        elif 15 <= per <= 25:
            score += 1
            reasons.append("⚖️ 適正: PERが適正水準")
        elif per > 30:
            score -= 1
            reasons.append("💸 割高: PERが30倍超")
        
        # PBR分析
        if 0 < pbr < 1:
            score += 2
            reasons.append("🏢 資産割安: PBRが1倍未満")
        elif 1 <= pbr <= 2:
            score += 1
            reasons.append("⚖️ 適正: PBRが適正水準")
        elif pbr > 3:
            score -= 1
            reasons.append("💸 資産割高: PBRが3倍超")
        
        # ROE分析
        if roe > 15:
            score += 2
            reasons.append("📈 高収益性: ROEが15%超")
        elif roe > 10:
            score += 1
            reasons.append("📊 良好収益: ROEが10%超")
        elif roe < 5:
            score -= 1
            reasons.append("📉 低収益性: ROEが5%未満")
        
        # 負債比率分析
        if debt_ratio < 30:
            score += 1
            reasons.append("🛡️ 健全財務: 負債比率が30%未満")
        elif debt_ratio > 60:
            score -= 1
            reasons.append("⚠️ 高負債: 負債比率が60%超")
        
        # 配当利回り分析
        if dividend_yield > 3:
            score += 1
            reasons.append("💵 高配当: 配当利回りが3%超")
        elif dividend_yield > 1:
            score += 0.5
            reasons.append("💰 配当あり: 配当利回りが1%超")
        
        # 強度判定
        if score >= 4:
            strength = 'very_strong'
        elif score >= 2:
            strength = 'strong'
        elif score <= -2:
            strength = 'weak'
        else:
            strength = 'neutral'
        
        return {
            'strength': strength,
            'score': score,
            'reasons': reasons
        }
    
    def analyze_market_environment(self, symbol: str) -> Dict:
        """市場環境分析"""
        try:
            # 日経平均の取得
            nikkei = yf.Ticker("^N225")
            nikkei_data = nikkei.history(period="1mo")
            
            if nikkei_data.empty:
                return {'environment': 'neutral', 'score': 0, 'reasons': []}
            
            # 日経平均の動向
            latest_nikkei = nikkei_data['Close'].iloc[-1]
            month_ago_nikkei = nikkei_data['Close'].iloc[0]
            nikkei_change = (latest_nikkei - month_ago_nikkei) / month_ago_nikkei * 100
            
            score = 0
            reasons = []
            
            if nikkei_change > 5:
                score += 2
                reasons.append("📈 市場好調: 日経平均が1ヶ月で5%上昇")
            elif nikkei_change > 2:
                score += 1
                reasons.append("📊 市場堅調: 日経平均が上昇傾向")
            elif nikkei_change < -5:
                score -= 2
                reasons.append("📉 市場調整: 日経平均が1ヶ月で5%下落")
            elif nikkei_change < -2:
                score -= 1
                reasons.append("⚠️ 市場軟調: 日経平均が下降傾向")
            
            # ボラティリティ分析
            nikkei_volatility = nikkei_data['Close'].pct_change().std() * np.sqrt(252) * 100
            if nikkei_volatility < 15:
                score += 1
                reasons.append("🛡️ 市場安定: ボラティリティが低水準")
            elif nikkei_volatility > 25:
                score -= 1
                reasons.append("⚡ 市場不安定: ボラティリティが高水準")
            
            # 環境判定
            if score >= 2:
                environment = 'favorable'
            elif score <= -2:
                environment = 'unfavorable'
            else:
                environment = 'neutral'
            
            return {
                'environment': environment,
                'score': score,
                'reasons': reasons,
                'nikkei_change': nikkei_change,
                'volatility': nikkei_volatility
            }
        except Exception as e:
            print(f"市場環境分析エラー: {e}")
            return {'environment': 'neutral', 'score': 0, 'reasons': []}
    
    def generate_forecast(self, symbol: str, stock_data: pd.DataFrame, metrics: Dict) -> Dict:
        """総合的な予想を生成"""
        # 技術分析
        indicators = self.calculate_technical_indicators(stock_data)
        technical_analysis = self.analyze_technical_trend(indicators)
        
        # ファンダメンタル分析
        fundamental_analysis = self.analyze_fundamental_strength(metrics)
        
        # 市場環境分析
        market_analysis = self.analyze_market_environment(symbol)
        
        # 総合スコア計算
        total_score = (
            technical_analysis['score'] * 0.4 +
            fundamental_analysis['score'] * 0.4 +
            market_analysis['score'] * 0.2
        )
        
        # 予想判定
        if total_score >= 3:
            forecast = 'strong_bullish'
            direction = '上昇'
            confidence = min(90, 60 + total_score * 5)
        elif total_score >= 1:
            forecast = 'bullish'
            direction = '上昇'
            confidence = min(80, 50 + total_score * 5)
        elif total_score <= -3:
            forecast = 'strong_bearish'
            direction = '下落'
            confidence = min(90, 60 + abs(total_score) * 5)
        elif total_score <= -1:
            forecast = 'bearish'
            direction = '下落'
            confidence = min(80, 50 + abs(total_score) * 5)
        else:
            forecast = 'neutral'
            direction = '横ばい'
            confidence = 50
        
        # 推奨アクション
        if forecast in ['strong_bullish', 'bullish']:
            action = '買い推奨'
        elif forecast in ['strong_bearish', 'bearish']:
            action = '売り推奨'
        else:
            action = '様子見'
        
        # リスク要因
        risk_factors = []
        if technical_analysis['score'] < -1:
            risk_factors.append("技術的に弱い")
        if fundamental_analysis['score'] < -1:
            risk_factors.append("ファンダメンタルが弱い")
        if market_analysis['score'] < -1:
            risk_factors.append("市場環境が不利")
        
        return {
            'symbol': symbol,
            'forecast': forecast,
            'direction': direction,
            'confidence': confidence,
            'action': action,
            'total_score': total_score,
            'technical_analysis': technical_analysis,
            'fundamental_analysis': fundamental_analysis,
            'market_analysis': market_analysis,
            'risk_factors': risk_factors,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def analyze_multiple_stocks(self, stock_data_dict: Dict, metrics_dict: Dict) -> List[Dict]:
        """複数銘柄の動向分析"""
        forecasts = []
        
        for symbol, stock_data in stock_data_dict.items():
            if symbol in metrics_dict:
                metrics = metrics_dict[symbol]
                forecast = self.generate_forecast(symbol, stock_data['data'], metrics)
                forecasts.append(forecast)
        
        # 信頼度順でソート
        forecasts.sort(key=lambda x: x['confidence'], reverse=True)
        
        return forecasts
