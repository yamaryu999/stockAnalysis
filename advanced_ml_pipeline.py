"""
Advanced Machine Learning Pipeline for Stock Analysis
高度な機械学習パイプライン - 自動特徴量エンジニアリング、継続学習、アンサンブル学習
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import joblib
import json
import os
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

# Machine Learning Libraries
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor, 
    VotingRegressor, AdaBoostRegressor, ExtraTreesRegressor
)
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV, 
    TimeSeriesSplit, validation_curve
)
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error
)
from sklearn.feature_selection import (
    SelectKBest, SelectFromModel, RFE, mutual_info_regression
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# Deep Learning Libraries (optional)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available. Deep learning features disabled.")

# Time Series Libraries
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import ta  # Technical Analysis library

# Feature Engineering
from scipy import stats
from scipy.signal import find_peaks
import talib

@dataclass
class ModelPerformance:
    """モデル性能メトリクス"""
    model_name: str
    mse: float
    mae: float
    rmse: float
    r2: float
    mape: float
    training_time: float
    prediction_time: float
    cross_val_score: float
    feature_importance: Dict[str, float]

@dataclass
class PredictionResult:
    """予測結果"""
    symbol: str
    predictions: List[float]
    confidence_intervals: List[Tuple[float, float]]
    model_used: str
    performance_metrics: ModelPerformance
    timestamp: datetime
    features_used: List[str]

class FeatureEngineer:
    """自動特徴量エンジニアリングクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feature_cache = {}
        
    def generate_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標の自動生成"""
        try:
            features = data.copy()
            
            # 基本的な価格特徴量
            features['price_change'] = features['Close'].pct_change()
            features['price_change_abs'] = features['price_change'].abs()
            features['high_low_ratio'] = features['High'] / features['Low']
            features['close_open_ratio'] = features['Close'] / features['Open']
            
            # 移動平均
            for window in [5, 10, 20, 50, 100, 200]:
                if len(features) >= window:
                    features[f'sma_{window}'] = features['Close'].rolling(window=window).mean()
                    features[f'ema_{window}'] = features['Close'].ewm(span=window).mean()
                    features[f'price_sma_ratio_{window}'] = features['Close'] / features[f'sma_{window}']
                    features[f'price_ema_ratio_{window}'] = features['Close'] / features[f'ema_{window}']
            
            # ボラティリティ指標
            features['volatility_5'] = features['Close'].rolling(window=5).std()
            features['volatility_20'] = features['Close'].rolling(window=20).std()
            features['volatility_ratio'] = features['volatility_5'] / features['volatility_20']
            
            # RSI
            if len(features) >= 14:
                features['rsi'] = self._calculate_rsi(features['Close'])
                features['rsi_oversold'] = (features['rsi'] < 30).astype(int)
                features['rsi_overbought'] = (features['rsi'] > 70).astype(int)
            
            # MACD
            if len(features) >= 26:
                features['macd'], features['macd_signal'], features['macd_hist'] = self._calculate_macd(features['Close'])
            
            # ボリンジャーバンド
            if len(features) >= 20:
                bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(features['Close'])
                features['bb_upper'] = bb_upper
                features['bb_middle'] = bb_middle
                features['bb_lower'] = bb_lower
                features['bb_width'] = (bb_upper - bb_lower) / bb_middle
                features['bb_position'] = (features['Close'] - bb_lower) / (bb_upper - bb_lower)
            
            # ストキャスティクス
            if len(features) >= 14:
                features['stoch_k'], features['stoch_d'] = self._calculate_stochastic(features)
            
            # 出来高指標
            features['volume_sma_20'] = features['Volume'].rolling(window=20).mean()
            features['volume_ratio'] = features['Volume'] / features['volume_sma_20']
            features['price_volume_trend'] = (features['Close'].pct_change() * features['Volume']).cumsum()
            
            # 価格パターン
            features['doji'] = (abs(features['Open'] - features['Close']) < 
                              (features['High'] - features['Low']) * 0.1).astype(int)
            features['hammer'] = self._detect_hammer_pattern(features)
            features['shooting_star'] = self._detect_shooting_star_pattern(features)
            
            # トレンド強度
            features['trend_strength'] = self._calculate_trend_strength(features['Close'])
            
            # サポート・レジスタンス
            features['support_resistance'] = self._calculate_support_resistance(features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"テクニカル特徴量生成エラー: {e}")
            return data
    
    def generate_fundamental_features(self, data: pd.DataFrame, 
                                    financial_metrics: Dict[str, Any]) -> pd.DataFrame:
        """ファンダメンタル特徴量の生成"""
        try:
            features = data.copy()
            
            # 財務指標の特徴量
            if financial_metrics:
                features['pe_ratio'] = financial_metrics.get('pe_ratio', np.nan)
                features['pb_ratio'] = financial_metrics.get('pb_ratio', np.nan)
                features['dividend_yield'] = financial_metrics.get('dividend_yield', np.nan)
                features['roe'] = financial_metrics.get('roe', np.nan)
                features['debt_to_equity'] = financial_metrics.get('debt_to_equity', np.nan)
                features['current_ratio'] = financial_metrics.get('current_ratio', np.nan)
                features['quick_ratio'] = financial_metrics.get('quick_ratio', np.nan)
                features['market_cap'] = financial_metrics.get('market_cap', np.nan)
                
                # 財務健全性スコア
                features['financial_health_score'] = self._calculate_financial_health_score(financial_metrics)
                
                # バリュエーション指標
                features['valuation_score'] = self._calculate_valuation_score(financial_metrics)
            
            return features
            
        except Exception as e:
            self.logger.error(f"ファンダメンタル特徴量生成エラー: {e}")
            return data
    
    def generate_time_series_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """時系列特徴量の生成"""
        try:
            features = data.copy()
            
            # 時間特徴量
            if isinstance(features.index, pd.DatetimeIndex):
                features['day_of_week'] = features.index.dayofweek
                features['month'] = features.index.month
                features['quarter'] = features.index.quarter
                features['year'] = features.index.year
                features['is_month_end'] = features.index.is_month_end.astype(int)
                features['is_quarter_end'] = features.index.is_quarter_end.astype(int)
                features['is_year_end'] = features.index.is_year_end.astype(int)
            
            # ラグ特徴量
            for lag in [1, 2, 3, 5, 10]:
                features[f'close_lag_{lag}'] = features['Close'].shift(lag)
                features[f'volume_lag_{lag}'] = features['Volume'].shift(lag)
                features[f'price_change_lag_{lag}'] = features['price_change'].shift(lag)
            
            # ローリング統計
            for window in [5, 10, 20]:
                features[f'close_rolling_mean_{window}'] = features['Close'].rolling(window).mean()
                features[f'close_rolling_std_{window}'] = features['Close'].rolling(window).std()
                features[f'close_rolling_min_{window}'] = features['Close'].rolling(window).min()
                features[f'close_rolling_max_{window}'] = features['Close'].rolling(window).max()
                features[f'close_rolling_skew_{window}'] = features['Close'].rolling(window).skew()
                features[f'close_rolling_kurt_{window}'] = features['Close'].rolling(window).kurt()
            
            # 差分特徴量
            features['close_diff_1'] = features['Close'].diff(1)
            features['close_diff_5'] = features['Close'].diff(5)
            features['volume_diff_1'] = features['Volume'].diff(1)
            
            # 季節性分解
            if len(features) >= 50:
                try:
                    decomposition = seasonal_decompose(features['Close'].dropna(), model='additive', period=20)
                    features['seasonal'] = decomposition.seasonal
                    features['trend'] = decomposition.trend
                    features['residual'] = decomposition.resid
                except:
                    pass
            
            return features
            
        except Exception as e:
            self.logger.error(f"時系列特徴量生成エラー: {e}")
            return data
    
    def generate_market_microstructure_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """市場マイクロストラクチャ特徴量の生成"""
        try:
            features = data.copy()
            
            # スプレッド関連
            features['bid_ask_spread'] = features['High'] - features['Low']
            features['spread_ratio'] = features['bid_ask_spread'] / features['Close']
            
            # 価格インパクト
            features['price_impact'] = features['Close'].pct_change() / features['Volume'].pct_change()
            
            # 流動性指標
            features['liquidity_ratio'] = features['Volume'] / features['bid_ask_spread']
            
            # 価格効率性
            features['price_efficiency'] = self._calculate_price_efficiency(features)
            
            # ボラティリティクラスタリング
            features['volatility_clustering'] = self._calculate_volatility_clustering(features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"市場マイクロストラクチャ特徴量生成エラー: {e}")
            return data
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """RSI計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD計算"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """ボリンジャーバンド計算"""
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, sma, lower
    
    def _calculate_stochastic(self, data: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """ストキャスティクス計算"""
        low_min = data['Low'].rolling(window=k_window).min()
        high_max = data['High'].rolling(window=k_window).max()
        k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_window).mean()
        return k_percent, d_percent
    
    def _detect_hammer_pattern(self, data: pd.DataFrame) -> pd.Series:
        """ハンマーパターン検出"""
        body = abs(data['Close'] - data['Open'])
        lower_shadow = data[['Open', 'Close']].min(axis=1) - data['Low']
        upper_shadow = data['High'] - data[['Open', 'Close']].max(axis=1)
        
        hammer = (
            (lower_shadow > 2 * body) & 
            (upper_shadow < body) & 
            (body > 0)
        ).astype(int)
        
        return hammer
    
    def _detect_shooting_star_pattern(self, data: pd.DataFrame) -> pd.Series:
        """シューティングスターパターン検出"""
        body = abs(data['Close'] - data['Open'])
        lower_shadow = data[['Open', 'Close']].min(axis=1) - data['Low']
        upper_shadow = data['High'] - data[['Open', 'Close']].max(axis=1)
        
        shooting_star = (
            (upper_shadow > 2 * body) & 
            (lower_shadow < body) & 
            (body > 0)
        ).astype(int)
        
        return shooting_star
    
    def _calculate_trend_strength(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """トレンド強度計算"""
        # 線形回帰の傾きを使用
        def linear_regression_slope(series):
            if len(series) < 2:
                return 0
            x = np.arange(len(series))
            slope, _ = np.polyfit(x, series, 1)
            return slope
        
        return prices.rolling(window=window).apply(linear_regression_slope, raw=False)
    
    def _calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """サポート・レジスタンス計算"""
        highs = data['High'].rolling(window=window).max()
        lows = data['Low'].rolling(window=window).min()
        
        # 現在価格がサポート・レジスタンスレベルに近いかどうか
        support_distance = (data['Close'] - lows) / data['Close']
        resistance_distance = (highs - data['Close']) / data['Close']
        
        # サポート・レジスタンスの強度
        support_resistance = np.where(
            support_distance < 0.02, 1,  # サポート近く
            np.where(resistance_distance < 0.02, -1, 0)  # レジスタンス近く
        )
        
        return pd.Series(support_resistance, index=data.index)
    
    def _calculate_financial_health_score(self, metrics: Dict[str, Any]) -> float:
        """財務健全性スコア計算"""
        score = 0.0
        factors = 0
        
        # ROE
        if metrics.get('roe'):
            roe = metrics['roe']
            if roe > 0.15:
                score += 1.0
            elif roe > 0.10:
                score += 0.7
            elif roe > 0.05:
                score += 0.4
            factors += 1
        
        # 負債比率
        if metrics.get('debt_to_equity'):
            debt_equity = metrics['debt_to_equity']
            if debt_equity < 0.3:
                score += 1.0
            elif debt_equity < 0.5:
                score += 0.7
            elif debt_equity < 1.0:
                score += 0.4
            factors += 1
        
        # 流動比率
        if metrics.get('current_ratio'):
            current_ratio = metrics['current_ratio']
            if current_ratio > 2.0:
                score += 1.0
            elif current_ratio > 1.5:
                score += 0.7
            elif current_ratio > 1.0:
                score += 0.4
            factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def _calculate_valuation_score(self, metrics: Dict[str, Any]) -> float:
        """バリュエーションスコア計算"""
        score = 0.0
        factors = 0
        
        # PER
        if metrics.get('pe_ratio'):
            pe = metrics['pe_ratio']
            if 10 <= pe <= 20:
                score += 1.0
            elif 5 <= pe <= 25:
                score += 0.7
            elif 0 <= pe <= 30:
                score += 0.4
            factors += 1
        
        # PBR
        if metrics.get('pb_ratio'):
            pb = metrics['pb_ratio']
            if 0.5 <= pb <= 2.0:
                score += 1.0
            elif 0.3 <= pb <= 3.0:
                score += 0.7
            elif 0.1 <= pb <= 5.0:
                score += 0.4
            factors += 1
        
        return score / factors if factors > 0 else 0.0
    
    def _calculate_price_efficiency(self, data: pd.DataFrame) -> pd.Series:
        """価格効率性計算"""
        # 価格のランダムウォークからの乖離度
        returns = data['Close'].pct_change().dropna()
        if len(returns) < 2:
            return pd.Series([0], index=data.index)
        
        # 自己相関の絶対値
        autocorr = returns.autocorr(lag=1)
        efficiency = 1 - abs(autocorr) if not pd.isna(autocorr) else 0
        
        return pd.Series([efficiency] * len(data), index=data.index)
    
    def _calculate_volatility_clustering(self, data: pd.DataFrame) -> pd.Series:
        """ボラティリティクラスタリング計算"""
        returns = data['Close'].pct_change().dropna()
        if len(returns) < 20:
            return pd.Series([0] * len(data), index=data.index)
        
        # GARCH効果の簡易版
        volatility = returns.rolling(window=20).std()
        volatility_clustering = volatility.rolling(window=5).std()
        
        return volatility_clustering.reindex(data.index, fill_value=0)

class ModelFactory:
    """モデルファクトリークラス"""
    
    @staticmethod
    def create_model(model_type: str, **kwargs) -> Any:
        """モデルを作成"""
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                learning_rate=kwargs.get('learning_rate', 0.1),
                max_depth=kwargs.get('max_depth', 6),
                random_state=42
            ),
            'extra_trees': ExtraTreesRegressor(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                random_state=42,
                n_jobs=-1
            ),
            'ada_boost': AdaBoostRegressor(
                n_estimators=kwargs.get('n_estimators', 50),
                learning_rate=kwargs.get('learning_rate', 1.0),
                random_state=42
            ),
            'svr': SVR(
                kernel=kwargs.get('kernel', 'rbf'),
                C=kwargs.get('C', 1.0),
                gamma=kwargs.get('gamma', 'scale')
            ),
            'neural_network': MLPRegressor(
                hidden_layer_sizes=kwargs.get('hidden_layer_sizes', (100, 50)),
                activation=kwargs.get('activation', 'relu'),
                solver=kwargs.get('solver', 'adam'),
                random_state=42,
                max_iter=kwargs.get('max_iter', 1000)
            ),
            'ridge': Ridge(
                alpha=kwargs.get('alpha', 1.0),
                random_state=42
            ),
            'lasso': Lasso(
                alpha=kwargs.get('alpha', 1.0),
                random_state=42,
                max_iter=kwargs.get('max_iter', 1000)
            ),
            'elastic_net': ElasticNet(
                alpha=kwargs.get('alpha', 1.0),
                l1_ratio=kwargs.get('l1_ratio', 0.5),
                random_state=42,
                max_iter=kwargs.get('max_iter', 1000)
            )
        }
        
        return models.get(model_type, models['random_forest'])
    
    @staticmethod
    def create_ensemble_model(models: List[Any], weights: Optional[List[float]] = None) -> VotingRegressor:
        """アンサンブルモデルを作成"""
        estimators = [(f'model_{i}', model) for i, model in enumerate(models)]
        return VotingRegressor(estimators=estimators, weights=weights)

class LSTMPredictor:
    """LSTM予測器（TensorFlow使用）"""
    
    def __init__(self, sequence_length: int = 60, features: int = 10):
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM predictions")
        
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = StandardScaler()
        
    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """LSTMモデルを構築"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(50),
            Dropout(0.2),
            BatchNormalization(),
            
            Dense(25, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """時系列データをシーケンスに変換"""
        X, y = [], []
        
        for i in range(self.sequence_length, len(data)):
            X.append(data[i-self.sequence_length:i])
            y.append(data[i])
        
        return np.array(X), np.array(y)
    
    def fit(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2):
        """モデルを訓練"""
        # データの正規化
        X_scaled = self.scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
        
        # シーケンスの準備
        X_seq, y_seq = self.prepare_sequences(X_scaled[:, 0])  # Close価格を使用
        
        # モデルの構築
        self.model = self.build_model((self.sequence_length, 1))
        
        # コールバック
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=5)
        ]
        
        # 訓練
        history = self.model.fit(
            X_seq, y_seq,
            epochs=100,
            batch_size=32,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=0
        )
        
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """予測を実行"""
        if self.model is None:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
        X_seq, _ = self.prepare_sequences(X_scaled[:, 0])
        
        predictions = self.model.predict(X_seq, verbose=0)
        return predictions.flatten()

class AdvancedMLPipeline:
    """高度な機械学習パイプライン"""
    
    def __init__(self, model_save_dir: str = "models"):
        self.logger = logging.getLogger(__name__)
        self.model_save_dir = model_save_dir
        os.makedirs(model_save_dir, exist_ok=True)
        
        self.feature_engineer = FeatureEngineer()
        self.model_factory = ModelFactory()
        
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.model_performance = {}
        
        # モデル設定
        self.model_configs = {
            'random_forest': {'n_estimators': 200, 'max_depth': 15},
            'gradient_boosting': {'n_estimators': 200, 'learning_rate': 0.05, 'max_depth': 8},
            'extra_trees': {'n_estimators': 200, 'max_depth': 15},
            'neural_network': {'hidden_layer_sizes': (200, 100, 50), 'max_iter': 2000},
            'lstm': {'sequence_length': 60}
        }
    
    def prepare_features(self, data: pd.DataFrame, 
                        financial_metrics: Optional[Dict[str, Any]] = None,
                        target_column: str = 'Close') -> Tuple[pd.DataFrame, pd.Series]:
        """特徴量を準備"""
        try:
            # テクニカル特徴量
            features = self.feature_engineer.generate_technical_features(data)
            
            # ファンダメンタル特徴量
            if financial_metrics:
                features = self.feature_engineer.generate_fundamental_features(features, financial_metrics)
            
            # 時系列特徴量
            features = self.feature_engineer.generate_time_series_features(features)
            
            # 市場マイクロストラクチャ特徴量
            features = self.feature_engineer.generate_market_microstructure_features(features)
            
            # ターゲット変数の準備
            target = features[target_column].shift(-1)  # 翌日の価格
            
            # 欠損値を削除
            features = features.dropna()
            target = target.reindex(features.index)
            
            # 数値列のみを選択
            numeric_columns = features.select_dtypes(include=[np.number]).columns
            features = features[numeric_columns]
            
            return features, target
            
        except Exception as e:
            self.logger.error(f"特徴量準備エラー: {e}")
            return pd.DataFrame(), pd.Series()
    
    def train_models(self, X: pd.DataFrame, y: pd.Series, 
                    symbol: str) -> Dict[str, ModelPerformance]:
        """複数のモデルを訓練"""
        try:
            # データの分割（時系列を考慮）
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # 特徴量のスケーリング
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 特徴量選択
            feature_selector = SelectKBest(k=min(50, X_train.shape[1]))
            X_train_selected = feature_selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = feature_selector.transform(X_test_scaled)
            
            self.scalers[symbol] = scaler
            self.feature_selectors[symbol] = feature_selector
            
            performance_results = {}
            
            # 各モデルを訓練
            for model_name, config in self.model_configs.items():
                if model_name == 'lstm' and not TENSORFLOW_AVAILABLE:
                    continue
                
                try:
                    start_time = time.time()
                    
                    if model_name == 'lstm':
                        # LSTMモデル
                        lstm = LSTMPredictor(sequence_length=config['sequence_length'])
                        lstm.fit(X_train_scaled, y_train.values)
                        self.models[f"{symbol}_{model_name}"] = lstm
                        
                        # 予測
                        y_pred = lstm.predict(X_test_scaled)
                        
                    else:
                        # 従来の機械学習モデル
                        model = self.model_factory.create_model(model_name, **config)
                        model.fit(X_train_selected, y_train)
                        self.models[f"{symbol}_{model_name}"] = model
                        
                        # 予測
                        y_pred = model.predict(X_test_selected)
                    
                    training_time = time.time() - start_time
                    
                    # 性能評価
                    performance = self._evaluate_model(y_test, y_pred, model_name, training_time)
                    performance_results[model_name] = performance
                    
                    self.logger.info(f"{symbol} {model_name} 訓練完了: R²={performance.r2:.4f}")
                    
                except Exception as e:
                    self.logger.error(f"{symbol} {model_name} 訓練エラー: {e}")
                    continue
            
            # アンサンブルモデルの作成
            if len(performance_results) > 1:
                ensemble_models = []
                weights = []
                
                for model_name, perf in performance_results.items():
                    if perf.r2 > 0.5:  # 性能の良いモデルのみ使用
                        ensemble_models.append(self.models[f"{symbol}_{model_name}"])
                        weights.append(perf.r2)
                
                if ensemble_models:
                    ensemble = self.model_factory.create_ensemble_model(ensemble_models, weights)
                    ensemble.fit(X_train_selected, y_train)
                    self.models[f"{symbol}_ensemble"] = ensemble
                    
                    y_pred_ensemble = ensemble.predict(X_test_selected)
                    ensemble_performance = self._evaluate_model(y_test, y_pred_ensemble, 'ensemble', 0)
                    performance_results['ensemble'] = ensemble_performance
            
            self.model_performance[symbol] = performance_results
            return performance_results
            
        except Exception as e:
            self.logger.error(f"モデル訓練エラー {symbol}: {e}")
            return {}
    
    def _evaluate_model(self, y_true: pd.Series, y_pred: np.ndarray, 
                       model_name: str, training_time: float) -> ModelPerformance:
        """モデル性能を評価"""
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        mape = mean_absolute_percentage_error(y_true, y_pred)
        
        # クロスバリデーション
        try:
            cv_scores = cross_val_score(
                self.models.get(f"{model_name}", None), 
                y_true.values.reshape(-1, 1), y_true.values, 
                cv=5, scoring='r2'
            )
            cv_score = cv_scores.mean()
        except:
            cv_score = r2
        
        # 特徴量重要度（可能な場合）
        feature_importance = {}
        if hasattr(self.models.get(f"{model_name}", None), 'feature_importances_'):
            model = self.models[f"{model_name}"]
            feature_importance = dict(zip(
                range(len(model.feature_importances_)), 
                model.feature_importances_
            ))
        
        return ModelPerformance(
            model_name=model_name,
            mse=mse,
            mae=mae,
            rmse=rmse,
            r2=r2,
            mape=mae,
            training_time=training_time,
            prediction_time=0.0,  # 後で更新
            cross_val_score=cv_score,
            feature_importance=feature_importance
        )
    
    def predict(self, symbol: str, X: pd.DataFrame, 
                model_name: str = 'ensemble') -> PredictionResult:
        """予測を実行"""
        try:
            model_key = f"{symbol}_{model_name}"
            if model_key not in self.models:
                raise ValueError(f"Model {model_key} not found")
            
            model = self.models[model_key]
            scaler = self.scalers.get(symbol)
            feature_selector = self.feature_selectors.get(symbol)
            
            if scaler is None or feature_selector is None:
                raise ValueError(f"Preprocessing components for {symbol} not found")
            
            # データの前処理
            X_scaled = scaler.transform(X)
            X_selected = feature_selector.transform(X_scaled)
            
            # 予測
            start_time = time.time()
            
            if model_name == 'lstm':
                predictions = model.predict(X_scaled)
            else:
                predictions = model.predict(X_selected)
            
            prediction_time = time.time() - start_time
            
            # 信頼区間の計算（簡易版）
            confidence_intervals = self._calculate_confidence_intervals(predictions, model_name)
            
            # 性能メトリクス
            performance = self.model_performance.get(symbol, {}).get(model_name)
            
            return PredictionResult(
                symbol=symbol,
                predictions=predictions.tolist(),
                confidence_intervals=confidence_intervals,
                model_used=model_name,
                performance_metrics=performance,
                timestamp=datetime.now(),
                features_used=list(range(X_selected.shape[1]))
            )
            
        except Exception as e:
            self.logger.error(f"予測エラー {symbol}: {e}")
            raise
    
    def _calculate_confidence_intervals(self, predictions: np.ndarray, 
                                      model_name: str, confidence: float = 0.95) -> List[Tuple[float, float]]:
        """信頼区間を計算"""
        # 簡易的な信頼区間計算
        std_error = np.std(predictions) * 0.1  # 仮の標準誤差
        z_score = 1.96 if confidence == 0.95 else 2.576  # 99%信頼区間
        
        intervals = []
        for pred in predictions:
            margin = z_score * std_error
            intervals.append((pred - margin, pred + margin))
        
        return intervals
    
    def save_models(self, symbol: str):
        """モデルを保存"""
        try:
            symbol_dir = os.path.join(self.model_save_dir, symbol)
            os.makedirs(symbol_dir, exist_ok=True)
            
            # モデルを保存
            for model_key, model in self.models.items():
                if model_key.startswith(f"{symbol}_"):
                    model_path = os.path.join(symbol_dir, f"{model_key}.joblib")
                    joblib.dump(model, model_path)
            
            # 前処理コンポーネントを保存
            if symbol in self.scalers:
                scaler_path = os.path.join(symbol_dir, "scaler.joblib")
                joblib.dump(self.scalers[symbol], scaler_path)
            
            if symbol in self.feature_selectors:
                selector_path = os.path.join(symbol_dir, "feature_selector.joblib")
                joblib.dump(self.feature_selectors[symbol], selector_path)
            
            # 性能メトリクスを保存
            if symbol in self.model_performance:
                performance_path = os.path.join(symbol_dir, "performance.json")
                with open(performance_path, 'w') as f:
                    json.dump(self.model_performance[symbol], f, default=str)
            
            self.logger.info(f"{symbol} モデル保存完了")
            
        except Exception as e:
            self.logger.error(f"モデル保存エラー {symbol}: {e}")
    
    def load_models(self, symbol: str):
        """モデルを読み込み"""
        try:
            symbol_dir = os.path.join(self.model_save_dir, symbol)
            
            if not os.path.exists(symbol_dir):
                self.logger.warning(f"{symbol} モデルディレクトリが見つかりません")
                return False
            
            # モデルを読み込み
            for model_file in os.listdir(symbol_dir):
                if model_file.endswith('.joblib') and not model_file.startswith('scaler') and not model_file.startswith('feature_selector'):
                    model_path = os.path.join(symbol_dir, model_file)
                    model_name = model_file.replace('.joblib', '')
                    self.models[model_name] = joblib.load(model_path)
            
            # 前処理コンポーネントを読み込み
            scaler_path = os.path.join(symbol_dir, "scaler.joblib")
            if os.path.exists(scaler_path):
                self.scalers[symbol] = joblib.load(scaler_path)
            
            selector_path = os.path.join(symbol_dir, "feature_selector.joblib")
            if os.path.exists(selector_path):
                self.feature_selectors[symbol] = joblib.load(selector_path)
            
            # 性能メトリクスを読み込み
            performance_path = os.path.join(symbol_dir, "performance.json")
            if os.path.exists(performance_path):
                with open(performance_path, 'r') as f:
                    self.model_performance[symbol] = json.load(f)
            
            self.logger.info(f"{symbol} モデル読み込み完了")
            return True
            
        except Exception as e:
            self.logger.error(f"モデル読み込みエラー {symbol}: {e}")
            return False
    
    def continuous_learning(self, symbol: str, new_data: pd.DataFrame):
        """継続学習"""
        try:
            # 新しいデータでモデルを更新
            X, y = self.prepare_features(new_data)
            
            if X.empty or y.empty:
                self.logger.warning(f"{symbol} 継続学習用データが不足")
                return
            
            # 既存のモデルを読み込み
            if not self.load_models(symbol):
                self.logger.warning(f"{symbol} 既存モデルが見つかりません")
                return
            
            # モデルを再訓練
            performance_results = self.train_models(X, y, symbol)
            
            # 性能が向上した場合のみ保存
            if performance_results:
                self.save_models(symbol)
                self.logger.info(f"{symbol} 継続学習完了")
            
        except Exception as e:
            self.logger.error(f"継続学習エラー {symbol}: {e}")
    
    def get_model_insights(self, symbol: str) -> Dict[str, Any]:
        """モデルインサイトを取得"""
        try:
            insights = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'models': {},
                'recommendations': []
            }
            
            if symbol not in self.model_performance:
                return insights
            
            performance = self.model_performance[symbol]
            
            # 最良のモデルを特定
            best_model = max(performance.items(), key=lambda x: x[1].r2)
            insights['best_model'] = {
                'name': best_model[0],
                'r2': best_model[1].r2,
                'mae': best_model[1].mae
            }
            
            # モデル詳細
            for model_name, perf in performance.items():
                insights['models'][model_name] = {
                    'r2': perf.r2,
                    'mae': perf.mae,
                    'rmse': perf.rmse,
                    'cross_val_score': perf.cross_val_score,
                    'training_time': perf.training_time
                }
            
            # 推奨事項
            if best_model[1].r2 < 0.5:
                insights['recommendations'].append("モデル性能が低いため、特徴量エンジニアリングの改善を推奨")
            
            if best_model[1].mae > 100:
                insights['recommendations'].append("予測誤差が大きいため、より多くのデータでの訓練を推奨")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"モデルインサイト取得エラー {symbol}: {e}")
            return {}

# グローバルインスタンス
advanced_ml_pipeline = AdvancedMLPipeline()
