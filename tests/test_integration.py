"""
Integration Tests for Stock Analysis Tool
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from cache_manager import CacheManager
from performance_optimizer import PerformanceMonitor, MemoryOptimizer
from enhanced_ai_analyzer import EnhancedAIAnalyzer
from realtime_manager import RealTimeDataManager, AlertManager

class TestSystemIntegration(unittest.TestCase):
    """Test system integration"""
    
    def setUp(self):
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize components
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.cache_manager = CacheManager(tempfile.mkdtemp())
        self.performance_monitor = PerformanceMonitor()
        self.memory_optimizer = MemoryOptimizer()
        self.ai_analyzer = EnhancedAIAnalyzer()
        self.realtime_manager = RealTimeDataManager()
        self.alert_manager = AlertManager(self.realtime_manager)
    
    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_cache_integration(self):
        """Test database and cache integration"""
        # Save data to database
        stock_data = {
            'symbol': '7203.T',
            'date': date(2024, 1, 1),
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        db_result = self.db_manager.save_stock_data(stock_data)
        self.assertTrue(db_result)
        
        # Cache the data
        cache_key = f"stock_data_{stock_data['symbol']}_{stock_data['date']}"
        cache_result = self.cache_manager.set(cache_key, stock_data)
        self.assertTrue(cache_result)
        
        # Retrieve from cache
        cached_data = self.cache_manager.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['symbol'], stock_data['symbol'])
        
        # Retrieve from database
        db_data = self.db_manager.get_stock_data(stock_data['symbol'])
        self.assertIsNotNone(db_data)
        self.assertEqual(db_data['symbol'], stock_data['symbol'])
    
    def test_ai_database_integration(self):
        """Test AI analyzer and database integration"""
        # Create sample data
        data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000],
            'date': pd.date_range('2024-01-01', periods=11)
        })
        
        # Prepare features
        X, y = self.ai_analyzer.prepare_features(data)
        self.assertGreater(len(X), 0)
        self.assertGreater(len(y), 0)
        
        # Train model
        performance = self.ai_analyzer.train_ensemble_model(X, y, 'TEST.T')
        self.assertIsInstance(performance, dict)
        
        # Save analysis result to database
        result_data = {
            'model_performance': performance,
            'feature_count': X.shape[1],
            'sample_count': len(X)
        }
        
        db_result = self.db_manager.save_analysis_result(
            'ai_prediction', 'TEST.T', result_data, 0.85
        )
        self.assertTrue(db_result)
    
    def test_realtime_alert_integration(self):
        """Test realtime manager and alert integration"""
        # Add symbol to watch list
        symbol = '7203.T'
        self.realtime_manager.add_symbol(symbol)
        self.assertIn(symbol, self.realtime_manager.watched_symbols)
        
        # Add alert
        callback = lambda alert, data: None
        self.alert_manager.add_alert(symbol, 'price_above', 'manual', 2600.0, callback)
        self.assertEqual(len(self.alert_manager.alerts), 1)
        
        # Verify symbol was added to realtime manager
        self.assertIn(symbol, self.realtime_manager.watched_symbols)
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration"""
        # Get current metrics
        metrics = self.performance_monitor.get_current_metrics()
        self.assertIsNotNone(metrics)
        
        # Get memory usage
        memory_info = self.performance_monitor.get_memory_usage()
        self.assertIsInstance(memory_info, dict)
        
        # Optimize memory
        self.memory_optimizer.cleanup_memory()
        
        # Check memory usage
        memory_check = self.memory_optimizer.check_memory_usage()
        self.assertIsInstance(memory_check, bool)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        symbol = '7203.T'
        
        # 1. Save stock data to database
        stock_data = {
            'symbol': symbol,
            'date': date(2024, 1, 1),
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        db_result = self.db_manager.save_stock_data(stock_data)
        self.assertTrue(db_result)
        
        # 2. Cache the data
        cache_key = f"stock_data_{symbol}_{stock_data['date']}"
        cache_result = self.cache_manager.set(cache_key, stock_data)
        self.assertTrue(cache_result)
        
        # 3. Create sample data for AI analysis
        data = pd.DataFrame({
            'close': [2500, 2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2590, 2600],
            'high': [2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2590, 2600, 2610],
            'low': [2490, 2500, 2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2590],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000, 2000000],
            'date': pd.date_range('2024-01-01', periods=11)
        })
        
        # 4. Prepare features and train AI model
        X, y = self.ai_analyzer.prepare_features(data)
        self.assertGreater(len(X), 0)
        
        performance = self.ai_analyzer.train_ensemble_model(X, y, symbol)
        self.assertIsInstance(performance, dict)
        
        # 5. Save AI analysis result
        ai_result = {
            'model_performance': performance,
            'prediction_confidence': 0.85,
            'recommendation': 'buy'
        }
        
        db_result = self.db_manager.save_analysis_result(
            'ai_analysis', symbol, ai_result, 0.85
        )
        self.assertTrue(db_result)
        
        # 6. Add to realtime monitoring
        self.realtime_manager.add_symbol(symbol)
        self.assertIn(symbol, self.realtime_manager.watched_symbols)
        
        # 7. Add alert
        callback = lambda alert, data: None
        self.alert_manager.add_alert(symbol, 'price_above', 'manual', 2600.0, callback)
        self.assertEqual(len(self.alert_manager.alerts), 1)
        
        # 8. Verify all data is accessible
        cached_data = self.cache_manager.get(cache_key)
        self.assertIsNotNone(cached_data)
        
        db_data = self.db_manager.get_stock_data(symbol)
        self.assertIsNotNone(db_data)
        
        # 9. Check system performance
        metrics = self.performance_monitor.get_current_metrics()
        self.assertIsNotNone(metrics)
        
        # 10. Verify database statistics
        stats = self.db_manager.get_database_stats()
        self.assertIsInstance(stats, dict)
        self.assertGreater(stats['stock_data_count'], 0)
        self.assertGreater(stats['analysis_results_count'], 0)

class TestDataConsistency(unittest.TestCase):
    """Test data consistency across components"""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.cache_manager = CacheManager(tempfile.mkdtemp())
    
    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_data_consistency_between_db_and_cache(self):
        """Test data consistency between database and cache"""
        symbol = '7203.T'
        date_obj = date(2024, 1, 1)
        
        # Original data
        original_data = {
            'symbol': symbol,
            'date': date_obj,
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        # Save to database
        self.db_manager.save_stock_data(original_data)
        
        # Save to cache
        cache_key = f"stock_data_{symbol}_{date_obj}"
        self.cache_manager.set(cache_key, original_data)
        
        # Retrieve from both
        db_data = self.db_manager.get_stock_data(symbol)
        cache_data = self.cache_manager.get(cache_key)
        
        # Verify consistency
        self.assertIsNotNone(db_data)
        self.assertIsNotNone(cache_data)
        
        # Check key fields
        self.assertEqual(db_data['symbol'], cache_data['symbol'])
        self.assertEqual(db_data['close'], cache_data['close'])
        self.assertEqual(db_data['volume'], cache_data['volume'])
    
    def test_concurrent_access(self):
        """Test concurrent access to database and cache"""
        symbol = '7203.T'
        
        # Simulate concurrent writes
        data1 = {
            'symbol': symbol,
            'date': date(2024, 1, 1),
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        data2 = {
            'symbol': symbol,
            'date': date(2024, 1, 2),
            'open': 2520.0,
            'high': 2570.0,
            'low': 2500.0,
            'close': 2540.0,
            'volume': 1100000
        }
        
        # Save both records
        result1 = self.db_manager.save_stock_data(data1)
        result2 = self.db_manager.save_stock_data(data2)
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        
        # Cache both records
        cache_key1 = f"stock_data_{symbol}_{data1['date']}"
        cache_key2 = f"stock_data_{symbol}_{data2['date']}"
        
        cache_result1 = self.cache_manager.set(cache_key1, data1)
        cache_result2 = self.cache_manager.set(cache_key2, data2)
        
        self.assertTrue(cache_result1)
        self.assertTrue(cache_result2)
        
        # Verify both records exist
        cached_data1 = self.cache_manager.get(cache_key1)
        cached_data2 = self.cache_manager.get(cache_key2)
        
        self.assertIsNotNone(cached_data1)
        self.assertIsNotNone(cached_data2)
        
        self.assertEqual(cached_data1['close'], 2520.0)
        self.assertEqual(cached_data2['close'], 2540.0)

if __name__ == '__main__':
    unittest.main()