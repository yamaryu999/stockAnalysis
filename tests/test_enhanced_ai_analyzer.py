"""
Tests for Enhanced AI Analyzer Module
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_ai_analyzer import EnhancedAIAnalyzer

class TestEnhancedAIAnalyzer(unittest.TestCase):
    """Test EnhancedAIAnalyzer class"""
    
    def setUp(self):
        self.analyzer = EnhancedAIAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsInstance(self.analyzer.models, dict)
        self.assertIsInstance(self.analyzer.scalers, dict)
        self.assertIsInstance(self.analyzer.feature_importance, dict)
        self.assertIsInstance(self.analyzer.model_performance, dict)
    
    def test_prepare_features(self):
        """Test feature preparation"""
        # Create sample data
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000],
            'date': pd.date_range('2024-01-01', periods=11)
        })
        
        X, y = self.analyzer.prepare_features(data)
        
        self.assertIsInstance(X, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertGreater(len(X), 0)
        self.assertGreater(len(y), 0)
    
    def test_calculate_technical_indicators(self):
        """Test technical indicator calculations"""
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
        })
        
        features = self.analyzer._calculate_technical_indicators(data)
        
        self.assertIsInstance(features, pd.DataFrame)
        self.assertIn('sma_5', features.columns)
        self.assertIn('sma_20', features.columns)
        self.assertIn('rsi', features.columns)
        self.assertIn('macd', features.columns)
        self.assertIn('bb_upper', features.columns)
    
    def test_calculate_rsi(self):
        """Test RSI calculation"""
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112])
        rsi = self.analyzer._calculate_rsi(prices)
        
        self.assertIsInstance(rsi, pd.Series)
        self.assertEqual(len(rsi), len(prices))
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        self.assertTrue(all(0 <= val <= 100 for val in valid_rsi))
    
    def test_calculate_macd(self):
        """Test MACD calculation"""
        prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110])
        macd_line, signal_line, histogram = self.analyzer._calculate_macd(prices)
        
        self.assertIsInstance(macd_line, pd.Series)
        self.assertIsInstance(signal_line, pd.Series)
        self.assertIsInstance(histogram, pd.Series)
        self.assertEqual(len(macd_line), len(prices))
    
    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110])
        upper, middle, lower = self.analyzer._calculate_bollinger_bands(prices)
        
        self.assertIsInstance(upper, pd.Series)
        self.assertIsInstance(middle, pd.Series)
        self.assertIsInstance(lower, pd.Series)
        self.assertEqual(len(upper), len(prices))
        
        # Upper band should be higher than middle, middle higher than lower
        valid_data = upper.dropna()
        if len(valid_data) > 0:
            self.assertTrue(all(upper >= middle))
            self.assertTrue(all(middle >= lower))
    
    def test_calculate_stochastic(self):
        """Test Stochastic Oscillator calculation"""
        data = pd.DataFrame({
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        })
        
        stoch_k, stoch_d = self.analyzer._calculate_stochastic(data)
        
        self.assertIsInstance(stoch_k, pd.Series)
        self.assertIsInstance(stoch_d, pd.Series)
        self.assertEqual(len(stoch_k), len(data))
        
        # Stochastic should be between 0 and 100
        valid_k = stoch_k.dropna()
        if len(valid_k) > 0:
            self.assertTrue(all(0 <= val <= 100 for val in valid_k))
    
    def test_train_ensemble_model(self):
        """Test ensemble model training"""
        # Create sample data
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randn(100)
        
        performance = self.analyzer.train_ensemble_model(X, y, 'TEST.T')
        
        self.assertIsInstance(performance, dict)
        self.assertIn('TEST.T', self.analyzer.models)
        self.assertIn('TEST.T', self.analyzer.scalers)
        self.assertIn('TEST.T', self.analyzer.model_performance)
    
    def test_predict_price(self):
        """Test price prediction"""
        # First train a model
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randn(100)
        
        self.analyzer.train_ensemble_model(X, y, 'TEST.T')
        
        # Mock yfinance data
        with patch('yfinance.Ticker') as mock_ticker:
            mock_data = pd.DataFrame({
                'Close': [100, 101, 102, 103, 104],
                'High': [101, 102, 103, 104, 105],
                'Low': [99, 100, 101, 102, 103],
                'Volume': [1000, 1100, 1200, 1300, 1400]
            })
            mock_ticker.return_value.history.return_value = mock_data
            
            prediction = self.analyzer.predict_price('TEST.T', 5)
            
            self.assertIsInstance(prediction, dict)
            if 'error' not in prediction:
                self.assertIn('symbol', prediction)
                self.assertIn('predictions', prediction)
                self.assertIn('ensemble_prediction', prediction)
                self.assertIn('ensemble_confidence', prediction)
    
    def test_analyze_sentiment(self):
        """Test sentiment analysis"""
        text = "This is a great company with excellent prospects for growth."
        result = self.analyzer.analyze_sentiment(text)
        
        self.assertIsInstance(result, dict)
        self.assertIn('compound', result)
        self.assertIn('positive', result)
        self.assertIn('negative', result)
        self.assertIn('neutral', result)
        self.assertIn('overall_sentiment', result)
        
        # Scores should be between 0 and 1
        self.assertTrue(0 <= result['positive'] <= 1)
        self.assertTrue(0 <= result['negative'] <= 1)
        self.assertTrue(0 <= result['neutral'] <= 1)
    
    def test_clean_text(self):
        """Test text cleaning"""
        text = "This is a GREAT company!!! 123"
        cleaned = self.analyzer._clean_text(text)
        
        self.assertIsInstance(cleaned, str)
        self.assertNotIn('!!!', cleaned)
        self.assertNotIn('123', cleaned)
        self.assertIn('great', cleaned.lower())
    
    def test_calculate_custom_sentiment(self):
        """Test custom sentiment calculation"""
        positive_text = "good great excellent positive growth profit gain up rise"
        negative_text = "bad terrible negative loss down fall decline crash"
        neutral_text = "company business market"
        
        pos_score = self.analyzer._calculate_custom_sentiment(positive_text)
        neg_score = self.analyzer._calculate_custom_sentiment(negative_text)
        neutral_score = self.analyzer._calculate_custom_sentiment(neutral_text)
        
        self.assertGreater(pos_score, 0)
        self.assertLess(neg_score, 0)
        self.assertEqual(neutral_score, 0.0)
    
    def test_classify_sentiment(self):
        """Test sentiment classification"""
        positive_classification = self.analyzer._classify_sentiment(0.1)
        negative_classification = self.analyzer._classify_sentiment(-0.1)
        neutral_classification = self.analyzer._classify_sentiment(0.0)
        
        self.assertEqual(positive_classification, 'positive')
        self.assertEqual(negative_classification, 'negative')
        self.assertEqual(neutral_classification, 'neutral')
    
    def test_analyze_market_patterns(self):
        """Test market pattern analysis"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_data = pd.DataFrame({
                'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
                'High': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
                'Low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
                'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
            })
            mock_ticker.return_value.history.return_value = mock_data
            
            patterns = self.analyzer.analyze_market_patterns('TEST.T')
            
            self.assertIsInstance(patterns, dict)
            if 'error' not in patterns:
                self.assertIn('trend', patterns)
                self.assertIn('volatility', patterns)
                self.assertIn('support_resistance', patterns)
                self.assertIn('chart_patterns', patterns)
                self.assertIn('volume_patterns', patterns)
    
    def test_analyze_trend(self):
        """Test trend analysis"""
        data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        })
        
        trend = self.analyzer._analyze_trend(data)
        
        self.assertIsInstance(trend, dict)
        self.assertIn('short_term', trend)
        self.assertIn('long_term', trend)
        self.assertIn('strength', trend)
        self.assertIn('consistency', trend)
    
    def test_analyze_volatility(self):
        """Test volatility analysis"""
        data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        })
        
        volatility = self.analyzer._analyze_volatility(data)
        
        self.assertIsInstance(volatility, dict)
        self.assertIn('current', volatility)
        self.assertIn('historical', volatility)
        self.assertIn('trend', volatility)
        self.assertIn('level', volatility)
    
    def test_find_support_resistance(self):
        """Test support and resistance level finding"""
        data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'High': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'Low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        })
        
        sr = self.analyzer._find_support_resistance(data)
        
        self.assertIsInstance(sr, dict)
        self.assertIn('resistance_levels', sr)
        self.assertIn('support_levels', sr)
        self.assertIn('nearest_resistance', sr)
        self.assertIn('nearest_support', sr)
    
    def test_detect_chart_patterns(self):
        """Test chart pattern detection"""
        data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
        })
        
        patterns = self.analyzer._detect_chart_patterns(data)
        
        self.assertIsInstance(patterns, list)
    
    def test_analyze_volume_patterns(self):
        """Test volume pattern analysis"""
        data = pd.DataFrame({
            'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000]
        })
        
        volume_patterns = self.analyzer._analyze_volume_patterns(data)
        
        self.assertIsInstance(volume_patterns, dict)
        self.assertIn('current_volume', volume_patterns)
        self.assertIn('average_volume', volume_patterns)
        self.assertIn('volume_ratio', volume_patterns)
        self.assertIn('price_volume_correlation', volume_patterns)
        self.assertIn('volume_trend', volume_patterns)
    
    def test_get_model_performance_summary(self):
        """Test model performance summary"""
        # Add some mock performance data
        self.analyzer.model_performance['TEST.T'] = {
            'random_forest': {'r2': 0.8, 'rmse': 0.1, 'mae': 0.08},
            'gradient_boosting': {'r2': 0.75, 'rmse': 0.12, 'mae': 0.09}
        }
        
        summary = self.analyzer.get_model_performance_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('TEST.T', summary)
        self.assertIn('random_forest', summary['TEST.T'])
        self.assertIn('gradient_boosting', summary['TEST.T'])
    
    def test_optimize_hyperparameters(self):
        """Test hyperparameter optimization"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randn(100)
        
        optimized_params = self.analyzer.optimize_hyperparameters('TEST.T', X, y)
        
        self.assertIsInstance(optimized_params, dict)
        # Should contain optimized parameters for at least one model
        if optimized_params:
            self.assertTrue(any('random_forest' in params or 'gradient_boosting' in params 
                              for params in optimized_params.values()))

if __name__ == '__main__':
    unittest.main()