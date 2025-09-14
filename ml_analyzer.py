import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

class MLAnalyzer:
    """機械学習による分析を行うクラス"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.feature_importance = {}
    
    def prepare_features(self, stock_data: Dict, metrics: Dict) -> pd.DataFrame:
        """機械学習用の特徴量を準備"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return pd.DataFrame()
            
            data = stock_data['data']
            if data.empty or len(data) < 50:
                return pd.DataFrame()
            
            # 価格データから特徴量を抽出
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            features = pd.DataFrame(index=data.index)
            
            # 価格特徴量
            features['price'] = close
            features['price_change'] = close.pct_change()
            features['price_change_2'] = close.pct_change(2)
            features['price_change_5'] = close.pct_change(5)
            features['price_change_10'] = close.pct_change(10)
            
            # 移動平均特徴量
            features['ma_5'] = close.rolling(5).mean()
            features['ma_10'] = close.rolling(10).mean()
            features['ma_20'] = close.rolling(20).mean()
            features['ma_50'] = close.rolling(50).mean()
            
            # 移動平均乖離率
            features['ma_deviation_5'] = (close - features['ma_5']) / features['ma_5']
            features['ma_deviation_10'] = (close - features['ma_10']) / features['ma_10']
            features['ma_deviation_20'] = (close - features['ma_20']) / features['ma_20']
            
            # ボラティリティ特徴量
            features['volatility_5'] = close.rolling(5).std()
            features['volatility_10'] = close.rolling(10).std()
            features['volatility_20'] = close.rolling(20).std()
            
            # 出来高特徴量
            features['volume'] = volume
            features['volume_ma_5'] = volume.rolling(5).mean()
            features['volume_ratio'] = volume / features['volume_ma_5']
            
            # 高値・安値特徴量
            features['high_low_ratio'] = high / low
            features['close_high_ratio'] = close / high
            features['close_low_ratio'] = close / low
            
            # ファンダメンタル特徴量
            if metrics:
                features['pe_ratio'] = metrics.get('pe_ratio', 0)
                features['pb_ratio'] = metrics.get('pb_ratio', 0)
                features['roe'] = metrics.get('roe', 0)
                features['debt_ratio'] = metrics.get('debt_to_equity', 0)
                features['dividend_yield'] = metrics.get('dividend_yield', 0)
            
            # 欠損値を前の値で埋める
            features = features.fillna(method='ffill').fillna(0)
            
            return features
            
        except Exception as e:
            print(f"特徴量準備エラー: {e}")
            return pd.DataFrame()
    
    def create_target_variables(self, stock_data: Dict, prediction_horizons: List[int] = [1, 5, 10]) -> Dict:
        """予測対象変数を作成"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return {}
            
            data = stock_data['data']
            if data.empty:
                return {}
            
            close = data['Close']
            targets = {}
            
            for horizon in prediction_horizons:
                # 将来の価格変化率
                future_return = close.shift(-horizon) / close - 1
                targets[f'return_{horizon}d'] = future_return
                
                # 将来の価格方向（上昇/下降）
                future_direction = (future_return > 0).astype(int)
                targets[f'direction_{horizon}d'] = future_direction
                
                # 将来の価格レベル（高/中/低）
                future_quantile = pd.qcut(future_return, q=3, labels=[0, 1, 2], duplicates='drop')
                targets[f'level_{horizon}d'] = future_quantile.astype(float)
            
            return targets
            
        except Exception as e:
            print(f"ターゲット変数作成エラー: {e}")
            return {}
    
    def train_price_prediction_model(self, features: pd.DataFrame, targets: Dict, 
                                   target_name: str = 'return_1d') -> Dict:
        """価格予測モデルを訓練"""
        try:
            if features.empty or target_name not in targets:
                return None
            
            # データを準備
            X = features.dropna()
            y = targets[target_name].dropna()
            
            # 共通のインデックスでデータを揃える
            common_index = X.index.intersection(y.index)
            if len(common_index) < 50:
                return None
            
            X = X.loc[common_index]
            y = y.loc[common_index]
            
            # 欠損値を除去
            valid_mask = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_mask]
            y = y[valid_mask]
            
            if len(X) < 30:
                return None
            
            # データを分割
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # 特徴量を標準化
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # モデルを訓練
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'linear_regression': LinearRegression()
            }
            
            results = {}
            
            for model_name, model in models.items():
                # モデルを訓練
                model.fit(X_train_scaled, y_train)
                
                # 予測
                y_pred = model.predict(X_test_scaled)
                
                # 評価指標
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                # 特徴量重要度（Random Forestの場合）
                feature_importance = None
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(X.columns, model.feature_importances_))
                
                results[model_name] = {
                    'model': model,
                    'mse': mse,
                    'rmse': rmse,
                    'feature_importance': feature_importance,
                    'predictions': y_pred,
                    'actual': y_test
                }
            
            # 最良のモデルを選択
            best_model_name = min(results.keys(), key=lambda x: results[x]['rmse'])
            best_model = results[best_model_name]
            
            return {
                'best_model_name': best_model_name,
                'best_model': best_model,
                'all_results': results,
                'feature_names': X.columns.tolist(),
                'training_size': len(X_train),
                'test_size': len(X_test)
            }
            
        except Exception as e:
            print(f"価格予測モデル訓練エラー: {e}")
            return None
    
    def train_direction_prediction_model(self, features: pd.DataFrame, targets: Dict, 
                                       target_name: str = 'direction_1d') -> Dict:
        """方向予測モデルを訓練"""
        try:
            if features.empty or target_name not in targets:
                return None
            
            # データを準備
            X = features.dropna()
            y = targets[target_name].dropna()
            
            # 共通のインデックスでデータを揃える
            common_index = X.index.intersection(y.index)
            if len(common_index) < 50:
                return None
            
            X = X.loc[common_index]
            y = y.loc[common_index]
            
            # 欠損値を除去
            valid_mask = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_mask]
            y = y[valid_mask]
            
            if len(X) < 30:
                return None
            
            # データを分割
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # 特徴量を標準化
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # モデルを訓練
            models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'logistic_regression': LogisticRegression(random_state=42, max_iter=1000)
            }
            
            results = {}
            
            for model_name, model in models.items():
                # モデルを訓練
                model.fit(X_train_scaled, y_train)
                
                # 予測
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
                
                # 評価指標
                accuracy = accuracy_score(y_test, y_pred)
                
                # 特徴量重要度
                feature_importance = None
                if hasattr(model, 'feature_importances_'):
                    feature_importance = dict(zip(X.columns, model.feature_importances_))
                
                results[model_name] = {
                    'model': model,
                    'accuracy': accuracy,
                    'feature_importance': feature_importance,
                    'predictions': y_pred,
                    'prediction_probabilities': y_pred_proba,
                    'actual': y_test
                }
            
            # 最良のモデルを選択
            best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
            best_model = results[best_model_name]
            
            return {
                'best_model_name': best_model_name,
                'best_model': best_model,
                'all_results': results,
                'feature_names': X.columns.tolist(),
                'training_size': len(X_train),
                'test_size': len(X_test)
            }
            
        except Exception as e:
            print(f"方向予測モデル訓練エラー: {e}")
            return None
    
    def predict_future_price(self, model_result: Dict, features: pd.DataFrame) -> Dict:
        """将来価格を予測"""
        try:
            if not model_result or features.empty:
                return None
            
            # 最新の特徴量を取得
            latest_features = features.iloc[-1:].fillna(0)
            
            # 特徴量を標準化
            latest_features_scaled = self.scaler.transform(latest_features)
            
            # 予測
            best_model = model_result['best_model']['model']
            prediction = best_model.predict(latest_features_scaled)[0]
            
            # 信頼区間（簡易版）
            if hasattr(best_model, 'predict_proba'):
                # 分類モデルの場合
                proba = best_model.predict_proba(latest_features_scaled)[0]
                confidence = max(proba)
            else:
                # 回帰モデルの場合
                confidence = 0.7  # 簡易的な信頼度
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'model_name': model_result['best_model_name'],
                'feature_importance': model_result['best_model']['feature_importance']
            }
            
        except Exception as e:
            print(f"将来価格予測エラー: {e}")
            return None
    
    def analyze_pattern_recognition(self, stock_data: Dict) -> Dict:
        """パターン認識分析を実行"""
        try:
            if not stock_data or stock_data.get('data') is None:
                return None
            
            data = stock_data['data']
            if data.empty or len(data) < 50:
                return None
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data['Volume']
            
            patterns = {}
            
            # ヘッドアンドショルダー
            patterns['head_and_shoulders'] = self._detect_head_and_shoulders(high, low)
            
            # ダブルトップ/ボトム
            patterns['double_top'] = self._detect_double_top(high)
            patterns['double_bottom'] = self._detect_double_bottom(low)
            
            # 三角形成
            patterns['triangle'] = self._detect_triangle(high, low)
            
            # サポート・レジスタンス
            patterns['support_resistance'] = self._detect_support_resistance(close)
            
            # トレンドライン
            patterns['trendline'] = self._detect_trendline(close)
            
            return {
                'patterns': patterns,
                'pattern_count': sum(1 for pattern in patterns.values() if pattern),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"パターン認識分析エラー: {e}")
            return None
    
    def _detect_head_and_shoulders(self, high: pd.Series, low: pd.Series) -> bool:
        """ヘッドアンドショルダーパターンを検出"""
        try:
            if len(high) < 20:
                return False
            
            # 簡易的な検出ロジック
            recent_highs = high.tail(20)
            peaks = []
            
            for i in range(1, len(recent_highs) - 1):
                if (recent_highs.iloc[i] > recent_highs.iloc[i-1] and 
                    recent_highs.iloc[i] > recent_highs.iloc[i+1]):
                    peaks.append(recent_highs.iloc[i])
            
            if len(peaks) >= 3:
                # 中央のピークが最も高いかチェック
                middle_peak = peaks[len(peaks)//2]
                return middle_peak > max(peaks[0], peaks[-1])
            
            return False
            
        except Exception as e:
            print(f"ヘッドアンドショルダー検出エラー: {e}")
            return False
    
    def _detect_double_top(self, high: pd.Series) -> bool:
        """ダブルトップパターンを検出"""
        try:
            if len(high) < 20:
                return False
            
            recent_highs = high.tail(20)
            max_high = recent_highs.max()
            max_indices = recent_highs[recent_highs == max_high].index
            
            if len(max_indices) >= 2:
                # 2つのピークが近い値で発生しているかチェック
                return True
            
            return False
            
        except Exception as e:
            print(f"ダブルトップ検出エラー: {e}")
            return False
    
    def _detect_double_bottom(self, low: pd.Series) -> bool:
        """ダブルボトムパターンを検出"""
        try:
            if len(low) < 20:
                return False
            
            recent_lows = low.tail(20)
            min_low = recent_lows.min()
            min_indices = recent_lows[recent_lows == min_low].index
            
            if len(min_indices) >= 2:
                # 2つの谷が近い値で発生しているかチェック
                return True
            
            return False
            
        except Exception as e:
            print(f"ダブルボトム検出エラー: {e}")
            return False
    
    def _detect_triangle(self, high: pd.Series, low: pd.Series) -> bool:
        """三角形成パターンを検出"""
        try:
            if len(high) < 20:
                return False
            
            recent_highs = high.tail(20)
            recent_lows = low.tail(20)
            
            # 高値と安値の範囲が狭まっているかチェック
            early_range = recent_highs.head(10).max() - recent_lows.head(10).min()
            late_range = recent_highs.tail(10).max() - recent_lows.tail(10).min()
            
            return late_range < early_range * 0.8
            
        except Exception as e:
            print(f"三角形成検出エラー: {e}")
            return False
    
    def _detect_support_resistance(self, close: pd.Series) -> Dict:
        """サポート・レジスタンスレベルを検出"""
        try:
            if len(close) < 20:
                return {'support': None, 'resistance': None}
            
            recent_prices = close.tail(20)
            
            # 簡易的なサポート・レジスタンス検出
            support = recent_prices.min()
            resistance = recent_prices.max()
            
            return {
                'support': support,
                'resistance': resistance,
                'current_price': close.iloc[-1],
                'support_distance': (close.iloc[-1] - support) / close.iloc[-1],
                'resistance_distance': (resistance - close.iloc[-1]) / close.iloc[-1]
            }
            
        except Exception as e:
            print(f"サポート・レジスタンス検出エラー: {e}")
            return {'support': None, 'resistance': None}
    
    def _detect_trendline(self, close: pd.Series) -> Dict:
        """トレンドラインを検出"""
        try:
            if len(close) < 20:
                return {'trend': 'unknown', 'slope': 0}
            
            recent_prices = close.tail(20)
            
            # 線形回帰でトレンドを計算
            x = np.arange(len(recent_prices))
            y = recent_prices.values
            
            # 線形回帰
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.01:
                trend = 'uptrend'
            elif slope < -0.01:
                trend = 'downtrend'
            else:
                trend = 'sideways'
            
            return {
                'trend': trend,
                'slope': slope,
                'strength': abs(slope)
            }
            
        except Exception as e:
            print(f"トレンドライン検出エラー: {e}")
            return {'trend': 'unknown', 'slope': 0}
    
    def comprehensive_ml_analysis(self, stock_data: Dict, metrics: Dict) -> Dict:
        """包括的な機械学習分析を実行"""
        try:
            # 特徴量を準備
            features = self.prepare_features(stock_data, metrics)
            if features.empty:
                return None
            
            # ターゲット変数を作成
            targets = self.create_target_variables(stock_data)
            if not targets:
                return None
            
            # 価格予測モデルを訓練
            price_model = self.train_price_prediction_model(features, targets, 'return_1d')
            
            # 方向予測モデルを訓練
            direction_model = self.train_direction_prediction_model(features, targets, 'direction_1d')
            
            # パターン認識分析
            pattern_analysis = self.analyze_pattern_recognition(stock_data)
            
            # 将来予測
            future_predictions = {}
            if price_model:
                future_predictions['price'] = self.predict_future_price(price_model, features)
            if direction_model:
                future_predictions['direction'] = self.predict_future_price(direction_model, features)
            
            # 総合評価
            ml_score = self._calculate_ml_score(price_model, direction_model, pattern_analysis)
            
            return {
                'ml_score': ml_score,
                'price_prediction_model': price_model,
                'direction_prediction_model': direction_model,
                'pattern_analysis': pattern_analysis,
                'future_predictions': future_predictions,
                'feature_importance': self._get_combined_feature_importance(price_model, direction_model),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"包括的機械学習分析エラー: {e}")
            return None
    
    def _calculate_ml_score(self, price_model: Dict, direction_model: Dict, pattern_analysis: Dict) -> float:
        """機械学習スコアを計算"""
        try:
            score = 50  # ベーススコア
            
            # 価格予測モデルのスコア
            if price_model and 'best_model' in price_model:
                rmse = price_model['best_model']['rmse']
                # RMSEが小さいほど高スコア
                price_score = max(0, 50 - rmse * 1000)
                score += price_score * 0.4
            
            # 方向予測モデルのスコア
            if direction_model and 'best_model' in direction_model:
                accuracy = direction_model['best_model']['accuracy']
                # 精度が高いほど高スコア
                direction_score = (accuracy - 0.5) * 100
                score += direction_score * 0.4
            
            # パターン認識のスコア
            if pattern_analysis and 'pattern_count' in pattern_analysis:
                pattern_score = min(20, pattern_analysis['pattern_count'] * 5)
                score += pattern_score * 0.2
            
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"MLスコア計算エラー: {e}")
            return 50
    
    def _get_combined_feature_importance(self, price_model: Dict, direction_model: Dict) -> Dict:
        """結合された特徴量重要度を取得"""
        try:
            combined_importance = {}
            
            if price_model and 'best_model' in price_model and price_model['best_model']['feature_importance']:
                for feature, importance in price_model['best_model']['feature_importance'].items():
                    combined_importance[feature] = combined_importance.get(feature, 0) + importance * 0.5
            
            if direction_model and 'best_model' in direction_model and direction_model['best_model']['feature_importance']:
                for feature, importance in direction_model['best_model']['feature_importance'].items():
                    combined_importance[feature] = combined_importance.get(feature, 0) + importance * 0.5
            
            # 重要度でソート
            sorted_importance = dict(sorted(combined_importance.items(), key=lambda x: x[1], reverse=True))
            
            return sorted_importance
            
        except Exception as e:
            print(f"特徴量重要度結合エラー: {e}")
            return {}
