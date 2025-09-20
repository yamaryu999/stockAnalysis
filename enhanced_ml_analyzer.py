"""
強化された機械学習分析システム
より高度なAI分析機能を提供
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import joblib
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MLPrediction:
    """機械学習予測結果クラス"""
    symbol: str
    predicted_price: float
    confidence: float
    prediction_horizon: int  # 日数
    model_name: str
    features_used: List[str]
    timestamp: datetime
    actual_price: Optional[float] = None
    error: Optional[float] = None

@dataclass
class TechnicalIndicator:
    """テクニカル指標クラス"""
    name: str
    value: float
    signal: str  # 'buy', 'sell', 'hold'
    strength: float  # 0-1
    description: str

class FeatureEngineer:
    """特徴量エンジニアリングクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.feature_names = []
    
    def create_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標特徴量を作成"""
        try:
            df = df.copy()
            
            # 移動平均
            df['MA_5'] = df['Close'].rolling(window=5).mean()
            df['MA_10'] = df['Close'].rolling(window=10).mean()
            df['MA_20'] = df['Close'].rolling(window=20).mean()
            df['MA_50'] = df['Close'].rolling(window=50).mean()
            
            # 移動平均の比率
            df['MA_5_ratio'] = df['Close'] / df['MA_5']
            df['MA_10_ratio'] = df['Close'] / df['MA_10']
            df['MA_20_ratio'] = df['Close'] / df['MA_20']
            
            # RSI
            df['RSI'] = self._calculate_rsi(df['Close'])
            
            # MACD
            df['MACD'], df['MACD_signal'] = self._calculate_macd(df['Close'])
            df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
            
            # ボリンジャーバンド
            df['BB_upper'], df['BB_lower'] = self._calculate_bollinger_bands(df['Close'])
            df['BB_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
            
            # ストキャスティクス
            df['Stoch_K'], df['Stoch_D'] = self._calculate_stochastic(df)
            
            # 価格変動率
            df['Price_change_1d'] = df['Close'].pct_change(1)
            df['Price_change_5d'] = df['Close'].pct_change(5)
            df['Price_change_10d'] = df['Close'].pct_change(10)
            
            # ボラティリティ
            df['Volatility_5d'] = df['Price_change_1d'].rolling(window=5).std()
            df['Volatility_10d'] = df['Price_change_1d'].rolling(window=10).std()
            
            # 出来高指標
            df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
            df['Volume_ratio'] = df['Volume'] / df['Volume_MA_5']
            
            # 価格位置
            df['Price_position_5d'] = (df['Close'] - df['Low'].rolling(window=5).min()) / (df['High'].rolling(window=5).max() - df['Low'].rolling(window=5).min())
            df['Price_position_10d'] = (df['Close'] - df['Low'].rolling(window=10).min()) / (df['High'].rolling(window=10).max() - df['Low'].rolling(window=10).min())
            
            return df
            
        except Exception as e:
            self.logger.error(f"テクニカル特徴量作成エラー: {e}")
            return df
    
    def create_fundamental_features(self, df: pd.DataFrame, fundamental_data: Dict) -> pd.DataFrame:
        """ファンダメンタル特徴量を作成"""
        try:
            df = df.copy()
            
            # 基本的な財務指標
            if 'PER' in fundamental_data:
                df['PER'] = fundamental_data['PER']
            if 'PBR' in fundamental_data:
                df['PBR'] = fundamental_data['PBR']
            if 'ROE' in fundamental_data:
                df['ROE'] = fundamental_data['ROE']
            if 'ROA' in fundamental_data:
                df['ROA'] = fundamental_data['ROA']
            if 'Debt_Ratio' in fundamental_data:
                df['Debt_Ratio'] = fundamental_data['Debt_Ratio']
            
            # 市場指標
            df['Market_Cap'] = df['Close'] * fundamental_data.get('Shares_Outstanding', 1)
            df['EV'] = df['Market_Cap'] + fundamental_data.get('Total_Debt', 0) - fundamental_data.get('Cash', 0)
            
            # 成長指標
            if 'Revenue_Growth' in fundamental_data:
                df['Revenue_Growth'] = fundamental_data['Revenue_Growth']
            if 'EPS_Growth' in fundamental_data:
                df['EPS_Growth'] = fundamental_data['EPS_Growth']
            
            return df
            
        except Exception as e:
            self.logger.error(f"ファンダメンタル特徴量作成エラー: {e}")
            return df
    
    def create_market_features(self, df: pd.DataFrame, market_data: Dict) -> pd.DataFrame:
        """市場特徴量を作成"""
        try:
            df = df.copy()
            
            # 市場指数との相関
            if 'Nikkei_225' in market_data:
                df['Nikkei_correlation'] = df['Close'].rolling(window=20).corr(market_data['Nikkei_225'])
            
            # セクター指標
            if 'Sector_PE' in market_data:
                df['Sector_PE_ratio'] = df['PER'] / market_data['Sector_PE']
            
            # 金利影響
            if 'Interest_Rate' in market_data:
                df['Interest_Rate'] = market_data['Interest_Rate']
            
            # 為替影響
            if 'USD_JPY' in market_data:
                df['USD_JPY'] = market_data['USD_JPY']
                df['USD_JPY_change'] = market_data['USD_JPY'].pct_change()
            
            return df
            
        except Exception as e:
            self.logger.error(f"市場特徴量作成エラー: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSIを計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """MACDを計算"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series]:
        """ボリンジャーバンドを計算"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, lower
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """ストキャスティクスを計算"""
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()
        k_percent = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent

class MLModelManager:
    """機械学習モデル管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.feature_engineer = FeatureEngineer()
        self.model_configs = {
            'RandomForest': {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'params': {'n_estimators': [50, 100, 200], 'max_depth': [5, 10, 15]}
            },
            'GradientBoosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 0.2]}
            },
            'LinearRegression': {
                'model': LinearRegression(),
                'params': {}
            },
            'Ridge': {
                'model': Ridge(random_state=42),
                'params': {'alpha': [0.1, 1.0, 10.0]}
            },
            'Lasso': {
                'model': Lasso(random_state=42),
                'params': {'alpha': [0.1, 1.0, 10.0]}
            },
            'SVR': {
                'model': SVR(),
                'params': {'C': [0.1, 1.0, 10.0], 'gamma': ['scale', 'auto']}
            },
            'MLPRegressor': {
                'model': MLPRegressor(random_state=42, max_iter=1000),
                'params': {'hidden_layer_sizes': [(50,), (100,), (50, 50)]}
            }
        }
    
    def prepare_features(self, df: pd.DataFrame, fundamental_data: Dict = None, market_data: Dict = None) -> pd.DataFrame:
        """特徴量を準備"""
        try:
            # テクニカル特徴量
            df_features = self.feature_engineer.create_technical_features(df)
            
            # ファンダメンタル特徴量
            if fundamental_data:
                df_features = self.feature_engineer.create_fundamental_features(df_features, fundamental_data)
            
            # 市場特徴量
            if market_data:
                df_features = self.feature_engineer.create_market_features(df_features, market_data)
            
            # NaN値を処理
            df_features = df_features.fillna(method='ffill').fillna(method='bfill')
            
            return df_features
            
        except Exception as e:
            self.logger.error(f"特徴量準備エラー: {e}")
            return df
    
    def create_target_variable(self, df: pd.DataFrame, horizon: int = 1) -> pd.Series:
        """ターゲット変数を作成"""
        try:
            # 将来の価格をターゲットとして設定
            target = df['Close'].shift(-horizon)
            return target
            
        except Exception as e:
            self.logger.error(f"ターゲット変数作成エラー: {e}")
            return pd.Series()
    
    def train_model(self, symbol: str, df: pd.DataFrame, model_name: str = 'RandomForest', 
                   fundamental_data: Dict = None, market_data: Dict = None, horizon: int = 1) -> bool:
        """モデルを訓練"""
        try:
            # 特徴量を準備
            df_features = self.prepare_features(df, fundamental_data, market_data)
            
            # ターゲット変数を作成
            target = self.create_target_variable(df_features, horizon)
            
            # 有効なデータのみを抽出
            valid_data = df_features.dropna()
            valid_target = target.loc[valid_data.index]
            
            if len(valid_data) < 50:  # 最小データ数チェック
                self.logger.warning(f"データが不足しています: {symbol} ({len(valid_data)}件)")
                return False
            
            # 特徴量を選択
            feature_columns = [col for col in valid_data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
            X = valid_data[feature_columns]
            y = valid_target
            
            # データを分割
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # スケーリング
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # モデルを取得
            model_config = self.model_configs.get(model_name, self.model_configs['RandomForest'])
            model = model_config['model']
            
            # モデルを訓練
            model.fit(X_train_scaled, y_train)
            
            # 予測精度を評価
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # モデルとスケーラーを保存
            model_key = f"{symbol}_{model_name}_{horizon}"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            self.logger.info(f"モデル訓練完了: {symbol} {model_name} (MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"モデル訓練エラー: {e}")
            return False
    
    def predict(self, symbol: str, df: pd.DataFrame, model_name: str = 'RandomForest', 
                horizon: int = 1, fundamental_data: Dict = None, market_data: Dict = None) -> Optional[MLPrediction]:
        """予測を実行"""
        try:
            model_key = f"{symbol}_{model_name}_{horizon}"
            
            if model_key not in self.models:
                self.logger.warning(f"モデルが見つかりません: {model_key}")
                return None
            
            # 特徴量を準備
            df_features = self.prepare_features(df, fundamental_data, market_data)
            
            # 最新のデータを取得
            latest_data = df_features.iloc[-1:]
            
            # 特徴量を選択
            feature_columns = [col for col in latest_data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
            X = latest_data[feature_columns]
            
            # NaN値を処理
            X = X.fillna(method='ffill').fillna(0)
            
            # スケーリング
            scaler = self.scalers[model_key]
            X_scaled = scaler.transform(X)
            
            # 予測を実行
            model = self.models[model_key]
            predicted_price = model.predict(X_scaled)[0]
            
            # 信頼度を計算（簡易版）
            confidence = min(0.95, max(0.1, 1.0 - abs(predicted_price - df['Close'].iloc[-1]) / df['Close'].iloc[-1]))
            
            prediction = MLPrediction(
                symbol=symbol,
                predicted_price=predicted_price,
                confidence=confidence,
                prediction_horizon=horizon,
                model_name=model_name,
                features_used=feature_columns,
                timestamp=datetime.now()
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"予測エラー: {e}")
            return None
    
    def ensemble_predict(self, symbol: str, df: pd.DataFrame, horizon: int = 1, 
                        fundamental_data: Dict = None, market_data: Dict = None) -> Optional[MLPrediction]:
        """アンサンブル予測を実行"""
        try:
            predictions = []
            model_names = ['RandomForest', 'GradientBoosting', 'LinearRegression', 'Ridge']
            
            # 複数のモデルで予測
            for model_name in model_names:
                prediction = self.predict(symbol, df, model_name, horizon, fundamental_data, market_data)
                if prediction:
                    predictions.append(prediction)
            
            if not predictions:
                return None
            
            # 予測結果を統合（重み付き平均）
            weights = [p.confidence for p in predictions]
            total_weight = sum(weights)
            
            if total_weight == 0:
                return predictions[0]  # フォールバック
            
            # 重み付き平均を計算
            weighted_price = sum(p.predicted_price * p.confidence for p in predictions) / total_weight
            avg_confidence = sum(weights) / len(weights)
            
            # アンサンブル予測結果を作成
            ensemble_prediction = MLPrediction(
                symbol=symbol,
                predicted_price=weighted_price,
                confidence=avg_confidence,
                prediction_horizon=horizon,
                model_name="Ensemble",
                features_used=list(set([f for p in predictions for f in p.features_used])),
                timestamp=datetime.now()
            )
            
            return ensemble_prediction
            
        except Exception as e:
            self.logger.error(f"アンサンブル予測エラー: {e}")
            return None
    
    def save_models(self, filepath: str):
        """モデルを保存"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers
            }
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            self.logger.info(f"モデルを保存しました: {filepath}")
            
        except Exception as e:
            self.logger.error(f"モデル保存エラー: {e}")
    
    def load_models(self, filepath: str):
        """モデルを読み込み"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data.get('models', {})
            self.scalers = model_data.get('scalers', {})
            self.logger.info(f"モデルを読み込みました: {filepath}")
            
        except Exception as e:
            self.logger.error(f"モデル読み込みエラー: {e}")

class TechnicalAnalyzer:
    """テクニカル分析クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feature_engineer = FeatureEngineer()
    
    def analyze_symbol(self, df: pd.DataFrame) -> List[TechnicalIndicator]:
        """銘柄のテクニカル分析を実行"""
        try:
            indicators = []
            
            # 特徴量を計算
            df_features = self.feature_engineer.create_technical_features(df)
            latest = df_features.iloc[-1]
            
            # RSI分析
            rsi = latest.get('RSI', 50)
            if rsi < 30:
                indicators.append(TechnicalIndicator(
                    name="RSI",
                    value=rsi,
                    signal="buy",
                    strength=min(1.0, (30 - rsi) / 30),
                    description=f"RSIが過売り水準 ({rsi:.1f})"
                ))
            elif rsi > 70:
                indicators.append(TechnicalIndicator(
                    name="RSI",
                    value=rsi,
                    signal="sell",
                    strength=min(1.0, (rsi - 70) / 30),
                    description=f"RSIが過買い水準 ({rsi:.1f})"
                ))
            
            # MACD分析
            macd = latest.get('MACD', 0)
            macd_signal = latest.get('MACD_signal', 0)
            if macd > macd_signal:
                indicators.append(TechnicalIndicator(
                    name="MACD",
                    value=macd - macd_signal,
                    signal="buy",
                    strength=min(1.0, abs(macd - macd_signal) / abs(macd_signal) if macd_signal != 0 else 0),
                    description="MACDがシグナル線を上抜け"
                ))
            else:
                indicators.append(TechnicalIndicator(
                    name="MACD",
                    value=macd - macd_signal,
                    signal="sell",
                    strength=min(1.0, abs(macd - macd_signal) / abs(macd_signal) if macd_signal != 0 else 0),
                    description="MACDがシグナル線を下抜け"
                ))
            
            # 移動平均分析
            price = latest['Close']
            ma_5 = latest.get('MA_5', price)
            ma_20 = latest.get('MA_20', price)
            
            if price > ma_5 > ma_20:
                indicators.append(TechnicalIndicator(
                    name="Moving Average",
                    value=(price - ma_20) / ma_20 * 100,
                    signal="buy",
                    strength=min(1.0, (price - ma_20) / ma_20),
                    description="価格が短期・長期移動平均を上回る"
                ))
            elif price < ma_5 < ma_20:
                indicators.append(TechnicalIndicator(
                    name="Moving Average",
                    value=(price - ma_20) / ma_20 * 100,
                    signal="sell",
                    strength=min(1.0, (ma_20 - price) / ma_20),
                    description="価格が短期・長期移動平均を下回る"
                ))
            
            # ボリンジャーバンド分析
            bb_position = latest.get('BB_position', 0.5)
            if bb_position < 0.2:
                indicators.append(TechnicalIndicator(
                    name="Bollinger Bands",
                    value=bb_position,
                    signal="buy",
                    strength=min(1.0, (0.2 - bb_position) / 0.2),
                    description="価格がボリンジャーバンド下限付近"
                ))
            elif bb_position > 0.8:
                indicators.append(TechnicalIndicator(
                    name="Bollinger Bands",
                    value=bb_position,
                    signal="sell",
                    strength=min(1.0, (bb_position - 0.8) / 0.2),
                    description="価格がボリンジャーバンド上限付近"
                ))
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"テクニカル分析エラー: {e}")
            return []

class EnhancedMLAnalyzer:
    """強化された機械学習分析クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ml_manager = MLModelManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.models_trained = set()
    
    def analyze_symbol(self, symbol: str, period: str = "1y", 
                      fundamental_data: Dict = None, market_data: Dict = None) -> Dict[str, Any]:
        """銘柄の包括的分析を実行"""
        try:
            # 株価データを取得
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {"error": "データが取得できませんでした"}
            
            # テクニカル分析
            technical_indicators = self.technical_analyzer.analyze_symbol(df)
            
            # 機械学習予測
            predictions = {}
            
            # 複数の予測期間で予測
            for horizon in [1, 5, 10]:
                # モデルが訓練されていない場合は訓練
                model_key = f"{symbol}_RandomForest_{horizon}"
                if model_key not in self.ml_manager.models:
                    success = self.ml_manager.train_model(symbol, df, 'RandomForest', fundamental_data, market_data, horizon)
                    if success:
                        self.models_trained.add(model_key)
                
                # 予測を実行
                prediction = self.ml_manager.predict(symbol, df, 'RandomForest', horizon, fundamental_data, market_data)
                if prediction:
                    predictions[f"{horizon}day"] = prediction
            
            # アンサンブル予測
            ensemble_prediction = self.ml_manager.ensemble_predict(symbol, df, 1, fundamental_data, market_data)
            
            # 分析結果をまとめる
            analysis_result = {
                'symbol': symbol,
                'current_price': df['Close'].iloc[-1],
                'technical_indicators': [
                    {
                        'name': ind.name,
                        'value': ind.value,
                        'signal': ind.signal,
                        'strength': ind.strength,
                        'description': ind.description
                    }
                    for ind in technical_indicators
                ],
                'ml_predictions': {
                    horizon: {
                        'predicted_price': pred.predicted_price,
                        'confidence': pred.confidence,
                        'model_name': pred.model_name,
                        'features_count': len(pred.features_used)
                    }
                    for horizon, pred in predictions.items()
                },
                'ensemble_prediction': {
                    'predicted_price': ensemble_prediction.predicted_price,
                    'confidence': ensemble_prediction.confidence,
                    'model_name': ensemble_prediction.model_name
                } if ensemble_prediction else None,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"包括的分析エラー: {e}")
            return {"error": str(e)}
    
    def batch_analyze(self, symbols: List[str], period: str = "1y") -> Dict[str, Dict[str, Any]]:
        """複数銘柄の一括分析"""
        results = {}
        
        for symbol in symbols:
            try:
                result = self.analyze_symbol(symbol, period)
                results[symbol] = result
                
            except Exception as e:
                self.logger.error(f"一括分析エラー {symbol}: {e}")
                results[symbol] = {"error": str(e)}
        
        return results
    
    def get_model_performance(self, symbol: str) -> Dict[str, Any]:
        """モデルの性能を取得"""
        try:
            performance = {}
            
            for model_key in self.models_trained:
                if symbol in model_key:
                    # モデルの性能指標を計算（簡易版）
                    performance[model_key] = {
                        'trained': True,
                        'last_trained': datetime.now().isoformat(),
                        'status': 'active'
                    }
            
            return performance
            
        except Exception as e:
            self.logger.error(f"モデル性能取得エラー: {e}")
            return {}

# グローバルインスタンス
enhanced_ml_analyzer = EnhancedMLAnalyzer()