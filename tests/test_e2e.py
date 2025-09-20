"""
End-to-End Tests for Stock Analysis Tool
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import subprocess
import time
import requests
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, 'test.db')
        self.test_cache_dir = os.path.join(self.temp_dir, 'cache')
        
        # Set up environment variables for testing
        os.environ['TEST_MODE'] = 'true'
        os.environ['TEST_DB_PATH'] = self.test_db
        os.environ['TEST_CACHE_DIR'] = self.test_cache_dir
    
    def tearDown(self):
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow from data input to results"""
        from database_manager import DatabaseManager
        from cache_manager import CacheManager
        from enhanced_ai_analyzer import EnhancedAIAnalyzer
        from realtime_manager import RealTimeDataManager, AlertManager
        from performance_optimizer import PerformanceMonitor
        
        # Initialize all components
        db_manager = DatabaseManager(self.test_db)
        cache_manager = CacheManager(self.test_cache_dir)
        ai_analyzer = EnhancedAIAnalyzer()
        realtime_manager = RealTimeDataManager()
        alert_manager = AlertManager(realtime_manager)
        performance_monitor = PerformanceMonitor()
        
        # Test data
        symbol = '7203.T'
        
        # Step 1: Save stock data
        stock_data = {
            'symbol': symbol,
            'date': date(2024, 1, 1),
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        db_result = db_manager.save_stock_data(stock_data)
        self.assertTrue(db_result)
        
        # Step 2: Cache the data
        cache_key = f"stock_data_{symbol}_{stock_data['date']}"
        cache_result = cache_manager.set(cache_key, stock_data)
        self.assertTrue(cache_result)
        
        # Step 3: Create historical data for AI analysis
        historical_data = pd.DataFrame({
            'close': [2400, 2420, 2440, 2460, 2480, 2500, 2520, 2540, 2560, 2580, 2600],
            'high': [2420, 2440, 2460, 2480, 2500, 2520, 2540, 2560, 2580, 2600, 2620],
            'low': [2380, 2400, 2420, 2440, 2460, 2480, 2500, 2520, 2540, 2560, 2580],
            'volume': [900000, 950000, 1000000, 1050000, 1100000, 1150000, 1200000, 1250000, 1300000, 1350000, 1400000],
            'date': pd.date_range('2023-12-01', periods=11)
        })
        
        # Step 4: AI Analysis
        X, y = ai_analyzer.prepare_features(historical_data)
        self.assertGreater(len(X), 0)
        
        # Train model
        performance = ai_analyzer.train_ensemble_model(X, y, symbol)
        self.assertIsInstance(performance, dict)
        
        # Step 5: Pattern Analysis
        patterns = ai_analyzer.analyze_market_patterns(symbol)
        self.assertIsInstance(patterns, dict)
        
        # Step 6: Sentiment Analysis
        sentiment_text = "This company shows strong growth potential with excellent financial performance."
        sentiment_result = ai_analyzer.analyze_sentiment(sentiment_text)
        self.assertIsInstance(sentiment_result, dict)
        
        # Step 7: Save analysis results
        analysis_result = {
            'model_performance': performance,
            'patterns': patterns,
            'sentiment': sentiment_result,
            'recommendation': 'buy',
            'confidence': 0.85
        }
        
        db_result = db_manager.save_analysis_result(
            'comprehensive_analysis', symbol, analysis_result, 0.85
        )
        self.assertTrue(db_result)
        
        # Step 8: Set up realtime monitoring
        realtime_manager.add_symbol(symbol)
        self.assertIn(symbol, realtime_manager.watched_symbols)
        
        # Step 9: Add alerts
        callback = lambda alert, data: None
        alert_manager.add_alert(symbol, 'price_above', 'manual', 2600.0, callback)
        self.assertEqual(len(alert_manager.alerts), 1)
        
        # Step 10: Performance monitoring
        metrics = performance_monitor.get_current_metrics()
        self.assertIsNotNone(metrics)
        
        memory_info = performance_monitor.get_memory_usage()
        self.assertIsInstance(memory_info, dict)
        
        # Step 11: Verify data integrity
        cached_data = cache_manager.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        db_data = db_manager.get_stock_data(symbol)
        self.assertIsNotNone(db_data)
        
        # Step 12: Check database statistics
        stats = db_manager.get_database_stats()
        self.assertIsInstance(stats, dict)
        self.assertGreater(stats['stock_data_count'], 0)
        self.assertGreater(stats['analysis_results_count'], 0)
        
        # Step 13: Cache statistics
        cache_stats = cache_manager.get_cache_stats()
        self.assertIsInstance(cache_stats, dict)
        self.assertGreater(cache_stats['total_requests'], 0)
    
    def test_error_handling_workflow(self):
        """Test error handling in complete workflow"""
        from database_manager import DatabaseManager
        from enhanced_ai_analyzer import EnhancedAIAnalyzer
        
        # Initialize components
        db_manager = DatabaseManager(self.test_db)
        ai_analyzer = EnhancedAIAnalyzer()
        
        # Test with invalid data
        invalid_data = {
            'symbol': '',  # Invalid symbol
            'date': 'invalid_date',  # Invalid date
            'open': -1000,  # Invalid price
            'high': 500,  # High < Open
            'low': 600,  # Low > High
            'close': 550,
            'volume': -1000  # Invalid volume
        }
        
        # Should handle invalid data gracefully
        db_result = db_manager.save_stock_data(invalid_data)
        # The method should still return True but handle validation internally
        self.assertTrue(db_result)
        
        # Test AI analysis with insufficient data
        insufficient_data = pd.DataFrame({
            'close': [100, 101],  # Only 2 data points
            'high': [101, 102],
            'low': [99, 100],
            'volume': [1000, 1100]
        })
        
        X, y = ai_analyzer.prepare_features(insufficient_data)
        # Should handle insufficient data gracefully
        if len(X) > 0:
            performance = ai_analyzer.train_ensemble_model(X, y, 'TEST.T')
            self.assertIsInstance(performance, dict)
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        from database_manager import DatabaseManager
        from cache_manager import CacheManager
        
        # Initialize components
        db_manager = DatabaseManager(self.test_db)
        cache_manager = CacheManager(self.test_cache_dir)
        
        # Simulate load with multiple operations
        symbols = ['7203.T', '6758.T', '9984.T', '9434.T', '6861.T']
        
        # Batch insert stock data
        stock_data_list = []
        for i, symbol in enumerate(symbols):
            stock_data_list.append({
                'symbol': symbol,
                'date': date(2024, 1, 1),
                'open': 2500.0 + i * 100,
                'high': 2550.0 + i * 100,
                'low': 2480.0 + i * 100,
                'close': 2520.0 + i * 100,
                'volume': 1000000 + i * 100000
            })
        
        # Test batch insertion
        batch_result = db_manager.batch_insert_stock_data(stock_data_list)
        self.assertTrue(batch_result)
        
        # Test cache operations
        for i, symbol in enumerate(symbols):
            cache_key = f"stock_data_{symbol}_{date(2024, 1, 1)}"
            cache_result = cache_manager.set(cache_key, stock_data_list[i])
            self.assertTrue(cache_result)
        
        # Verify all data was saved
        for symbol in symbols:
            db_data = db_manager.get_stock_data(symbol)
            self.assertIsNotNone(db_data)
            
            cache_key = f"stock_data_{symbol}_{date(2024, 1, 1)}"
            cache_data = cache_manager.get(cache_key)
            self.assertIsNotNone(cache_data)
    
    def test_data_consistency_across_restarts(self):
        """Test data consistency across system restarts"""
        from database_manager import DatabaseManager
        from cache_manager import CacheManager
        
        # First session
        db_manager1 = DatabaseManager(self.test_db)
        cache_manager1 = CacheManager(self.test_cache_dir)
        
        # Save data
        test_data = {
            'symbol': '7203.T',
            'date': date(2024, 1, 1),
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        db_manager1.save_stock_data(test_data)
        cache_manager1.set('test_key', test_data)
        
        # Simulate restart by creating new instances
        db_manager2 = DatabaseManager(self.test_db)
        cache_manager2 = CacheManager(self.test_cache_dir)
        
        # Verify data persistence
        db_data = db_manager2.get_stock_data('7203.T')
        self.assertIsNotNone(db_data)
        self.assertEqual(db_data['symbol'], '7203.T')
        
        cache_data = cache_manager2.get('test_key')
        self.assertIsNotNone(cache_data)
        self.assertEqual(cache_data['symbol'], '7203.T')
    
    @patch('yfinance.Ticker')
    def test_external_api_integration(self, mock_ticker):
        """Test integration with external APIs"""
        from enhanced_ai_analyzer import EnhancedAIAnalyzer
        
        # Mock yfinance data
        mock_data = pd.DataFrame({
            'Close': [2500, 2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2590, 2600],
            'High': [2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2590, 2600, 2610],
            'Low': [2490, 2500, 2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2590],
            'Volume': [1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000, 2000000]
        })
        
        mock_info = {'previousClose': 2490}
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_info
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        # Test AI analyzer with external data
        ai_analyzer = EnhancedAIAnalyzer()
        
        # Prepare features
        X, y = ai_analyzer.prepare_features(mock_data)
        self.assertGreater(len(X), 0)
        
        # Train model
        performance = ai_analyzer.train_ensemble_model(X, y, '7203.T')
        self.assertIsInstance(performance, dict)
        
        # Test prediction
        prediction = ai_analyzer.predict_price('7203.T', 5)
        self.assertIsInstance(prediction, dict)
        
        # Test pattern analysis
        patterns = ai_analyzer.analyze_market_patterns('7203.T')
        self.assertIsInstance(patterns, dict)

if __name__ == '__main__':
    unittest.main()