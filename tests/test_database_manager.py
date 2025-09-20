"""
Tests for Database Manager Module
"""

import unittest
import tempfile
import os
import pandas as pd
from datetime import datetime, date
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test DatabaseManager class"""
    
    def setUp(self):
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        # Clean up temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Database should be created and tables should exist
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'stock_data', 'financial_metrics', 'analysis_results',
                'user_settings', 'alerts'
            ]
            
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_save_stock_data(self):
        """Test saving stock data"""
        stock_data = {
            'symbol': '7203.T',
            'date': date(2024, 1, 1),
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        
        result = self.db_manager.save_stock_data(stock_data)
        self.assertTrue(result)
        
        # Verify data was saved
        saved_data = self.db_manager.get_stock_data('7203.T')
        self.assertIsNotNone(saved_data)
        self.assertEqual(saved_data['symbol'], '7203.T')
    
    def test_save_financial_metrics(self):
        """Test saving financial metrics"""
        metrics = {
            'symbol': '7203.T',
            'date': date(2024, 1, 1),
            'per': 15.5,
            'pbr': 1.2,
            'roe': 8.5,
            'dividend_yield': 2.1,
            'market_cap': 1000000000,
            'debt_ratio': 0.3,
            'current_ratio': 1.5,
            'quick_ratio': 1.2
        }
        
        result = self.db_manager.save_financial_metrics('7203.T', metrics)
        self.assertTrue(result)
        
        # Verify data was saved
        saved_metrics = self.db_manager.get_financial_metrics('7203.T')
        self.assertIsNotNone(saved_metrics)
        self.assertEqual(saved_metrics['symbol'], '7203.T')
    
    def test_save_analysis_result(self):
        """Test saving analysis results"""
        result_data = {
            'analysis_type': 'technical',
            'recommendation': 'buy',
            'confidence': 0.85
        }
        
        result = self.db_manager.save_analysis_result(
            'technical', '7203.T', result_data, 0.85
        )
        self.assertTrue(result)
    
    def test_batch_insert_stock_data(self):
        """Test batch insertion of stock data"""
        stock_data_list = [
            {
                'symbol': '7203.T',
                'date': date(2024, 1, 1),
                'open': 2500.0,
                'high': 2550.0,
                'low': 2480.0,
                'close': 2520.0,
                'volume': 1000000
            },
            {
                'symbol': '6758.T',
                'date': date(2024, 1, 1),
                'open': 12000.0,
                'high': 12200.0,
                'low': 11800.0,
                'close': 12100.0,
                'volume': 500000
            }
        ]
        
        result = self.db_manager.batch_insert_stock_data(stock_data_list)
        self.assertTrue(result)
        
        # Verify data was saved
        saved_data1 = self.db_manager.get_stock_data('7203.T')
        saved_data2 = self.db_manager.get_stock_data('6758.T')
        
        self.assertIsNotNone(saved_data1)
        self.assertIsNotNone(saved_data2)
    
    def test_batch_insert_financial_metrics(self):
        """Test batch insertion of financial metrics"""
        metrics_list = [
            {
                'symbol': '7203.T',
                'date': date(2024, 1, 1),
                'per': 15.5,
                'pbr': 1.2,
                'roe': 8.5,
                'dividend_yield': 2.1,
                'market_cap': 1000000000,
                'debt_ratio': 0.3,
                'current_ratio': 1.5,
                'quick_ratio': 1.2
            },
            {
                'symbol': '6758.T',
                'date': date(2024, 1, 1),
                'per': 25.0,
                'pbr': 2.5,
                'roe': 12.0,
                'dividend_yield': 1.5,
                'market_cap': 2000000000,
                'debt_ratio': 0.2,
                'current_ratio': 2.0,
                'quick_ratio': 1.8
            }
        ]
        
        result = self.db_manager.batch_insert_financial_metrics(metrics_list)
        self.assertTrue(result)
        
        # Verify data was saved
        saved_metrics1 = self.db_manager.get_financial_metrics('7203.T')
        saved_metrics2 = self.db_manager.get_financial_metrics('6758.T')
        
        self.assertIsNotNone(saved_metrics1)
        self.assertIsNotNone(saved_metrics2)
    
    def test_optimize_database(self):
        """Test database optimization"""
        result = self.db_manager.optimize_database()
        self.assertTrue(result)
    
    def test_get_database_stats(self):
        """Test getting database statistics"""
        stats = self.db_manager.get_database_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('stock_data_count', stats)
        self.assertIn('financial_metrics_count', stats)
        self.assertIn('analysis_results_count', stats)
        self.assertIn('alerts_count', stats)
        self.assertIn('db_size_mb', stats)
    
    def test_cleanup_old_data(self):
        """Test cleanup of old data"""
        # Add some old data
        old_date = date(2020, 1, 1)
        stock_data = {
            'symbol': '7203.T',
            'date': old_date,
            'open': 2500.0,
            'high': 2550.0,
            'low': 2480.0,
            'close': 2520.0,
            'volume': 1000000
        }
        self.db_manager.save_stock_data(stock_data)
        
        # Cleanup data older than 1 year
        self.db_manager.cleanup_old_data(days=365)
        
        # Verify old data was removed
        saved_data = self.db_manager.get_stock_data('7203.T')
        self.assertIsNone(saved_data)
    
    def test_user_settings(self):
        """Test user settings functionality"""
        # Save setting
        result = self.db_manager.save_user_setting('theme', 'dark')
        self.assertTrue(result)
        
        # Get setting
        setting = self.db_manager.get_user_setting('theme')
        self.assertEqual(setting, 'dark')
        
        # Update setting
        result = self.db_manager.save_user_setting('theme', 'light')
        self.assertTrue(result)
        
        # Verify update
        setting = self.db_manager.get_user_setting('theme')
        self.assertEqual(setting, 'light')
    
    def test_alerts(self):
        """Test alerts functionality"""
        # Add alert
        alert_data = {
            'symbol': '7203.T',
            'alert_type': 'price_above',
            'threshold': 2600.0
        }
        
        result = self.db_manager.add_alert('7203.T', 'price_above', alert_data)
        self.assertTrue(result)
        
        # Get alerts
        alerts = self.db_manager.get_alerts('7203.T')
        self.assertIsInstance(alerts, list)
        self.assertEqual(len(alerts), 1)
        
        # Update alert status
        alert_id = alerts[0]['id']
        result = self.db_manager.update_alert_status(alert_id, False)
        self.assertTrue(result)
        
        # Verify update
        alerts = self.db_manager.get_alerts('7203.T')
        self.assertEqual(len(alerts), 0)  # Should be empty due to is_active=False

if __name__ == '__main__':
    unittest.main()