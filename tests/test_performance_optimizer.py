"""
Tests for Performance Optimizer Module
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from performance_optimizer import (
    PerformanceMonitor, QueryOptimizer, AsyncDataProcessor,
    MemoryOptimizer, BatchProcessor, performance_timer, memory_efficient
)

class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor class"""
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
    
    def test_get_current_metrics(self):
        """Test getting current performance metrics"""
        metrics = self.monitor.get_current_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertIn('cpu_usage', metrics.__dict__)
        self.assertIn('memory_usage', metrics.__dict__)
        self.assertIn('memory_available', metrics.__dict__)
        self.assertIn('disk_usage', metrics.__dict__)
        self.assertIn('network_io', metrics.__dict__)
        self.assertIn('timestamp', metrics.__dict__)
    
    def test_get_memory_usage(self):
        """Test getting memory usage details"""
        memory_info = self.monitor.get_memory_usage()
        
        self.assertIsInstance(memory_info, dict)
        self.assertIn('total', memory_info)
        self.assertIn('available', memory_info)
        self.assertIn('used', memory_info)
        self.assertIn('percent', memory_info)
    
    def test_optimize_memory(self):
        """Test memory optimization"""
        # Should not raise any exceptions
        self.monitor.optimize_memory()

class TestQueryOptimizer(unittest.TestCase):
    """Test QueryOptimizer class"""
    
    def setUp(self):
        self.db_manager = Mock()
        self.optimizer = QueryOptimizer(self.db_manager)
    
    def test_optimize_query(self):
        """Test query optimization"""
        query = "SELECT * FROM stock_data WHERE symbol = ?"
        optimized = self.optimizer.optimize_query(query)
        
        self.assertIsInstance(optimized, str)
        self.assertEqual(optimized, query)  # Should return same query for now
    
    def test_record_query_stats(self):
        """Test query statistics recording"""
        original_query = "SELECT * FROM stock_data"
        optimized_query = "SELECT symbol, price FROM stock_data"
        
        self.optimizer._record_query_stats(original_query, optimized_query)
        
        query_hash = hash(original_query)
        self.assertIn(query_hash, self.optimizer.query_stats)

class TestMemoryOptimizer(unittest.TestCase):
    """Test MemoryOptimizer class"""
    
    def setUp(self):
        self.optimizer = MemoryOptimizer()
    
    def test_optimize_dataframe(self):
        """Test DataFrame memory optimization"""
        # Create test DataFrame
        df = pd.DataFrame({
            'int_col': [1, 2, 3, 4, 5],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'str_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        optimized_df = self.optimizer.optimize_dataframe(df)
        
        self.assertIsInstance(optimized_df, pd.DataFrame)
        self.assertEqual(len(optimized_df), len(df))
    
    def test_check_memory_usage(self):
        """Test memory usage check"""
        result = self.optimizer.check_memory_usage()
        self.assertIsInstance(result, bool)
    
    def test_cleanup_memory(self):
        """Test memory cleanup"""
        # Should not raise any exceptions
        self.optimizer.cleanup_memory()

class TestBatchProcessor(unittest.TestCase):
    """Test BatchProcessor class"""
    
    def setUp(self):
        self.processor = BatchProcessor(batch_size=2, max_workers=2)
    
    def test_process_in_batches(self):
        """Test batch processing"""
        data = [1, 2, 3, 4, 5]
        
        def process_func(x):
            return x * 2
        
        results = self.processor.process_in_batches(data, process_func)
        
        self.assertEqual(len(results), len(data))
        self.assertEqual(results, [2, 4, 6, 8, 10])
    
    def test_process_with_progress(self):
        """Test processing with progress callback"""
        data = [1, 2, 3]
        progress_calls = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        def process_func(x):
            return x * 2
        
        results = self.processor.process_with_progress(data, process_func, progress_callback)
        
        self.assertEqual(len(results), len(data))
        self.assertEqual(len(progress_calls), len(data))

class TestDecorators(unittest.TestCase):
    """Test performance decorators"""
    
    def test_performance_timer(self):
        """Test performance timer decorator"""
        @performance_timer
        def test_function():
            return "test"
        
        result = test_function()
        self.assertEqual(result, "test")
    
    def test_memory_efficient(self):
        """Test memory efficient decorator"""
        @memory_efficient
        def test_function():
            return "test"
        
        result = test_function()
        self.assertEqual(result, "test")

class TestAsyncDataProcessor(unittest.TestCase):
    """Test AsyncDataProcessor class"""
    
    def setUp(self):
        self.processor = AsyncDataProcessor(max_workers=2)
    
    @unittest.skip("Requires async context")
    async def test_fetch_data_async(self):
        """Test async data fetching"""
        urls = ["https://httpbin.org/json", "https://httpbin.org/json"]
        
        async with self.processor:
            results = await self.processor.fetch_data_async(urls)
            
            self.assertIsInstance(results, list)
            self.assertEqual(len(results), len(urls))

if __name__ == '__main__':
    unittest.main()