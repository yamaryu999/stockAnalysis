import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')

class ShortTermPredictor:
    """短期予測（1日〜1週間）に特化したアナライザー"""
    
    def __init__(self):
        self.models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'LinearRegression': LinearRegression()
        }
        self.scaler = StandardScaler()
        self.feature_importance = {}
    
    def _calculate_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """技術指標を計算"""
        df = data.copy()
        
        # 移動平均
        df['MA_5'] = df['Close'].rolling(window=5).mean()
        df['MA_10'] = df['Close'].rolling(window=10).mean()
        df['MA_20'] = df['Close'].rolling(window=20).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # ボリンジャーバンド
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # 出来高指標
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # 価格変動率
        df['Price_Change_1d'] = df['Close'].pct_change(1)
        df['Price_Change_3d'] = df['Close'].pct_change(3)
        df['Price_Change_5d'] = df['Close'].pct_change(5)
        
        # ボラティリティ
        df['Volatility_5d'] = df['Price_Change_1d'].rolling(window=5).std()
        df['Volatility_10d'] = df['Price_Change_1d'].rolling(window=10).std()
        
        # 高値・安値比率
        df['High_Low_Ratio'] = df['High'] / df['Low']
        df['Close_High_Ratio'] = df['Close'] / df['High']
        df['Close_Low_Ratio'] = df['Close'] / df['Low']
        
        return df
    
    def _prepare_features(self, data: pd.DataFrame, lookback_days: int = 30) -> Tuple[np.ndarray, np.ndarray]:
        """特徴量を準備"""
        df = self._calculate_technical_features(data)
        
        # 特徴量リスト
        feature_columns = [
            'MA_5', 'MA_10', 'MA_20', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'BB_Width', 'BB_Position', 'Volume_Ratio', 'Price_Change_1d', 'Price_Change_3d',
            'Price_Change_5d', 'Volatility_5d', 'Volatility_10d', 'High_Low_Ratio',
            'Close_High_Ratio', 'Close_Low_Ratio'
        ]
        
        # 欠損値を処理
        df = df.dropna()
        
        if len(df) < lookback_days + 5:
            return None, None
        
        # 特徴量とターゲットを準備
        X = []
        y = []
        
        for i in range(lookback_days, len(df) - 5):
            # 過去の特徴量
            features = df[feature_columns].iloc[i-lookback_days:i].values.flatten()
            X.append(features)
            
            # 未来の価格変動率（1日後、3日後、5日後）
            future_returns = [
                df['Close'].iloc[i+1] / df['Close'].iloc[i] - 1,  # 1日後
                df['Close'].iloc[i+3] / df['Close'].iloc[i] - 1,  # 3日後
                df['Close'].iloc[i+5] / df['Close'].iloc[i] - 1   # 5日後
            ]
            y.append(future_returns)
        
        return np.array(X), np.array(y)
    
    def train_models(self, data: pd.DataFrame) -> Dict:
        """モデルを訓練"""
        X, y = self._prepare_features(data)
        
        if X is None or len(X) == 0:
            return {'error': 'データが不足しています'}
        
        # データを標準化
        X_scaled = self.scaler.fit_transform(X)
        
        results = {}
        
        for name, model in self.models.items():
            try:
                # 各予測期間に対してモデルを訓練
                model_results = {}
                for i, period in enumerate(['1日後', '3日後', '5日後']):
                    y_period = y[:, i]
                    
                    # モデルを訓練
                    model.fit(X_scaled, y_period)
                    
                    # 予測
                    y_pred = model.predict(X_scaled)
                    
                    # 評価指標
                    mse = mean_squared_error(y_period, y_pred)
                    mae = mean_absolute_error(y_period, y_pred)
                    
                    model_results[period] = {
                        'model': model,
                        'mse': mse,
                        'mae': mae,
                        'predictions': y_pred
                    }
                
                results[name] = model_results
                
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results
    
    def predict_short_term(self, data: pd.DataFrame, days_ahead: int = 1) -> Dict:
        """短期予測を実行"""
        # 最新の特徴量を取得
        df = self._calculate_technical_features(data)
        df = df.dropna()
        
        if len(df) < 30:
            return {'error': 'データが不足しています'}
        
        # 最新の特徴量
        feature_columns = [
            'MA_5', 'MA_10', 'MA_20', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'BB_Width', 'BB_Position', 'Volume_Ratio', 'Price_Change_1d', 'Price_Change_3d',
            'Price_Change_5d', 'Volatility_5d', 'Volatility_10d', 'High_Low_Ratio',
            'Close_High_Ratio', 'Close_Low_Ratio'
        ]
        
        latest_features = df[feature_columns].iloc[-30:].values.flatten()
        latest_features = latest_features.reshape(1, -1)
        latest_features_scaled = self.scaler.transform(latest_features)
        
        current_price = df['Close'].iloc[-1]
        
        predictions = {}
        
        for model_name, model in self.models.items():
            try:
                # 価格変動率を予測
                return_prediction = model.predict(latest_features_scaled)[0]
                
                # 価格を予測
                predicted_price = current_price * (1 + return_prediction)
                
                predictions[model_name] = {
                    'predicted_price': predicted_price,
                    'predicted_return': return_prediction,
                    'confidence': min(abs(return_prediction) * 10, 1.0)  # 簡易的な信頼度
                }
                
            except Exception as e:
                predictions[model_name] = {'error': str(e)}
        
        # アンサンブル予測
        valid_predictions = [p for p in predictions.values() if 'error' not in p]
        if valid_predictions:
            avg_price = np.mean([p['predicted_price'] for p in valid_predictions])
            avg_return = np.mean([p['predicted_return'] for p in valid_predictions])
            avg_confidence = np.mean([p['confidence'] for p in valid_predictions])
            
            predictions['Ensemble'] = {
                'predicted_price': avg_price,
                'predicted_return': avg_return,
                'confidence': avg_confidence
            }
        
        return {
            'current_price': current_price,
            'predictions': predictions,
            'days_ahead': days_ahead,
            'analysis_date': df.index[-1]
        }
    
    def analyze_multiple_stocks(self, stock_data_dict: Dict) -> Dict:
        """複数銘柄の短期予測分析"""
        results = {}
        
        for symbol, data in stock_data_dict.items():
            if data and data['data'] is not None and not data['data'].empty:
                try:
                    prediction = self.predict_short_term(data['data'])
                    results[symbol] = prediction
                except Exception as e:
                    results[symbol] = {'error': str(e)}
        
        return results
    
    def create_prediction_chart(self, data: pd.DataFrame, prediction_result: Dict) -> go.Figure:
        """予測結果のチャートを作成"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('価格予測', '技術指標'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # 価格チャート
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='実際の価格',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # 予測価格
        if 'predictions' in prediction_result:
            current_price = prediction_result['current_price']
            for model_name, pred in prediction_result['predictions'].items():
                if 'predicted_price' in pred:
                    fig.add_trace(
                        go.Scatter(
                            x=[data.index[-1], data.index[-1] + pd.Timedelta(days=1)],
                            y=[current_price, pred['predicted_price']],
                            mode='lines+markers',
                            name=f'{model_name}予測',
                            line=dict(dash='dash')
                        ),
                        row=1, col=1
                    )
        
        # RSI
        df_with_indicators = self._calculate_technical_features(data)
        fig.add_trace(
            go.Scatter(
                x=df_with_indicators.index,
                y=df_with_indicators['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='orange')
            ),
            row=2, col=1
        )
        
        # RSIの基準線
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        fig.update_layout(
            title='短期予測分析',
            height=600,
            showlegend=True
        )
        
        return fig
