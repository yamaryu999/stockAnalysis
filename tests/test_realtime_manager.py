"""
Tests for Real-time Manager Module
"""

import unittest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os
try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency for tests
    pd = None

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from realtime_manager import (
    MarketStatusMonitor, RealTimeDataManager, AlertManager,
    MarketData, Alert
)

class TestMarketStatusMonitor(unittest.TestCase):
    """Test MarketStatusMonitor class"""
    
    def setUp(self):
        self.monitor = MarketStatusMonitor()
    
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertIn('open', self.monitor.market_hours)
        self.assertIn('close', self.monitor.market_hours)
        self.assertIn('lunch_start', self.monitor.market_hours)
        self.assertIn('lunch_end', self.monitor.market_hours)
    
    @patch('realtime_manager.datetime')
    def test_is_market_open_weekday_open(self, mock_datetime):
        """Test market open on weekday during trading hours"""
        # Mock weekday (Monday = 0) at 10:00 AM
        mock_now = Mock()
        mock_now.weekday.return_value = 0
        mock_now.strftime.return_value = '10:00'
        mock_datetime.now.return_value = mock_now
        
        result = self.monitor.is_market_open()
        self.assertTrue(result)
    
    @patch('realtime_manager.datetime')
    def test_is_market_open_weekday_closed(self, mock_datetime):
        """Test market closed on weekday outside trading hours"""
        # Mock weekday (Monday = 0) at 8:00 AM (before market open)
        mock_now = Mock()
        mock_now.weekday.return_value = 0
        mock_now.strftime.return_value = '08:00'
        mock_datetime.now.return_value = mock_now
        
        result = self.monitor.is_market_open()
        self.assertFalse(result)
    
    @patch('realtime_manager.datetime')
    def test_is_market_open_weekend(self, mock_datetime):
        """Test market closed on weekend"""
        # Mock weekend (Saturday = 5)
        mock_now = Mock()
        mock_now.weekday.return_value = 5
        mock_now.strftime.return_value = '10:00'
        mock_datetime.now.return_value = mock_now
        
        result = self.monitor.is_market_open()
        self.assertFalse(result)
    
    @patch('realtime_manager.datetime')
    def test_is_market_open_lunch_time(self, mock_datetime):
        """Test market closed during lunch time"""
        # Mock weekday during lunch time
        mock_now = Mock()
        mock_now.weekday.return_value = 0
        mock_now.strftime.return_value = '12:00'
        mock_datetime.now.return_value = mock_now
        
        result = self.monitor.is_market_open()
        self.assertFalse(result)
    
    def test_get_market_status(self):
        """Test getting market status"""
        status = self.monitor.get_market_status()
        self.assertIn(status, ['open', 'closed'])
    
    def test_get_next_market_open(self):
        """Test getting next market open time"""
        next_open = self.monitor.get_next_market_open()
        self.assertIsInstance(next_open, datetime)

class TestRealTimeDataManager(unittest.TestCase):
    """Test RealTimeDataManager class"""
    
    def setUp(self):
        self.manager = RealTimeDataManager(update_interval=1)
    
    def test_initialization(self):
        """Test manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.update_interval, 1)
        self.assertIsInstance(self.manager.subscribers, list)
        self.assertIsInstance(self.manager.watched_symbols, set)
        self.assertIsInstance(self.manager.data_cache, dict)
    
    def test_add_subscriber(self):
        """Test adding subscriber"""
        callback = Mock()
        self.manager.add_subscriber(callback)
        
        self.assertIn(callback, self.manager.subscribers)
        self.assertEqual(len(self.manager.subscribers), 1)
    
    def test_remove_subscriber(self):
        """Test removing subscriber"""
        callback = Mock()
        self.manager.add_subscriber(callback)
        self.manager.remove_subscriber(callback)
        
        self.assertNotIn(callback, self.manager.subscribers)
        self.assertEqual(len(self.manager.subscribers), 0)
    
    def test_add_symbol(self):
        """Test adding symbol to watch list"""
        symbol = '7203.T'
        self.manager.add_symbol(symbol)
        
        self.assertIn(symbol, self.manager.watched_symbols)
    
    def test_remove_symbol(self):
        """Test removing symbol from watch list"""
        symbol = '7203.T'
        self.manager.add_symbol(symbol)
        self.manager.remove_symbol(symbol)
        
        self.assertNotIn(symbol, self.manager.watched_symbols)
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        self.assertFalse(self.manager.is_running)
        
        self.manager.start_monitoring()
        self.assertTrue(self.manager.is_running)
        
        self.manager.stop_monitoring()
        self.assertFalse(self.manager.is_running)
    
    @unittest.skipUnless(pd is not None, "pandas is required for this test")
    @patch('yfinance.Ticker')
    def test_fetch_symbol_data(self, mock_ticker):
        """Test fetching symbol data"""
        # Mock ticker data with realistic dataframe
        index = pd.date_range(end=datetime.now(), periods=4, freq='min')
        mock_data = pd.DataFrame({
            'Close': [98.5, 99.8, 100.5, 101.2],
            'Open': [98.0, 99.0, 100.0, 100.8],
            'High': [99.0, 100.0, 101.0, 101.5],
            'Low': [97.5, 98.8, 99.5, 100.5],
            'Volume': [100000, 120000, 150000, 170000]
        }, index=index)

        mock_info = {'previousClose': 99.0, 'bid': 100.0, 'ask': 101.0}

        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_info
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        data = self.manager._fetch_symbol_data('7203.T')
        
        self.assertIsNotNone(data)
        self.assertIsInstance(data, MarketData)
        self.assertEqual(data.symbol, '7203.T')
        self.assertEqual(data.price, 100)
        self.assertIsNotNone(data.vwap)
        self.assertIsNotNone(data.volatility)
        self.assertIsNotNone(data.momentum)
        self.assertIsNotNone(data.volume_ratio)
    
    @patch('yfinance.Ticker')
    def test_fetch_symbol_data_empty(self, mock_ticker):
        """Test fetching symbol data when data is empty"""
        mock_data = Mock()
        mock_data.empty = True
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        data = self.manager._fetch_symbol_data('7203.T')
        
        self.assertIsNone(data)

class TestAlertManager(unittest.TestCase):
    """Test AlertManager class"""
    
    def setUp(self):
        self.realtime_manager = Mock()
        self.alert_manager = AlertManager(self.realtime_manager)
    
    def test_initialization(self):
        """Test alert manager initialization"""
        self.assertIsNotNone(self.alert_manager)
        self.assertEqual(self.alert_manager.realtime_manager, self.realtime_manager)
        self.assertIsInstance(self.alert_manager.alerts, list)
        self.assertIsInstance(self.alert_manager.alert_callbacks, list)
    
    def test_add_alert(self):
        """Test adding alert"""
        symbol = '7203.T'
        alert_type = 'price_above'
        condition = 'manual'
        threshold = 2600.0
        callback = Mock()
        
        self.alert_manager.add_alert(symbol, alert_type, condition, threshold, callback)
        
        self.assertEqual(len(self.alert_manager.alerts), 1)
        alert = self.alert_manager.alerts[0]
        self.assertEqual(alert.symbol, symbol)
        self.assertEqual(alert.alert_type, alert_type)
        self.assertEqual(alert.threshold_value, threshold)
        self.assertFalse(alert.is_triggered)
        
        # Verify realtime manager was called
        self.realtime_manager.add_symbol.assert_called_once_with(symbol)
    
    def test_check_alerts_price_above(self):
        """Test checking price above alert"""
        # Add alert
        self.alert_manager.add_alert('7203.T', 'price_above', 'manual', 2600.0)
        
        # Create market data that should trigger alert
        market_data = MarketData(
            symbol='7203.T',
            price=2700.0,  # Above threshold
            change=100.0,
            change_percent=3.8,
            volume=1000000,
            timestamp=datetime.now(),
            market_status='open'
        )
        
        self.alert_manager.check_alerts(market_data)
        
        # Alert should be triggered
        alert = self.alert_manager.alerts[0]
        self.assertTrue(alert.is_triggered)
        self.assertEqual(alert.current_value, 2700.0)
    
    def test_check_alerts_price_below(self):
        """Test checking price below alert"""
        # Add alert
        self.alert_manager.add_alert('7203.T', 'price_below', 'manual', 2600.0)
        
        # Create market data that should trigger alert
        market_data = MarketData(
            symbol='7203.T',
            price=2500.0,  # Below threshold
            change=-100.0,
            change_percent=-3.8,
            volume=1000000,
            timestamp=datetime.now(),
            market_status='open'
        )
        
        self.alert_manager.check_alerts(market_data)
        
        # Alert should be triggered
        alert = self.alert_manager.alerts[0]
        self.assertTrue(alert.is_triggered)
        self.assertEqual(alert.current_value, 2500.0)
    
    def test_check_alerts_no_trigger(self):
        """Test checking alert that should not trigger"""
        # Add alert
        self.alert_manager.add_alert('7203.T', 'price_above', 'manual', 2600.0)
        
        # Create market data that should not trigger alert
        market_data = MarketData(
            symbol='7203.T',
            price=2500.0,  # Below threshold
            change=-100.0,
            change_percent=-3.8,
            volume=1000000,
            timestamp=datetime.now(),
            market_status='open'
        )
        
        self.alert_manager.check_alerts(market_data)
        
        # Alert should not be triggered
        alert = self.alert_manager.alerts[0]
        self.assertFalse(alert.is_triggered)
    
    def test_check_alerts_wrong_symbol(self):
        """Test checking alert for different symbol"""
        # Add alert for different symbol
        self.alert_manager.add_alert('6758.T', 'price_above', 'manual', 12000.0)
        
        # Create market data for different symbol
        market_data = MarketData(
            symbol='7203.T',  # Different symbol
            price=13000.0,
            change=1000.0,
            change_percent=8.3,
            volume=500000,
            timestamp=datetime.now(),
            market_status='open'
        )
        
        self.alert_manager.check_alerts(market_data)
        
        # Alert should not be triggered
        alert = self.alert_manager.alerts[0]
        self.assertFalse(alert.is_triggered)
    
    def test_check_alerts_already_triggered(self):
        """Test checking already triggered alert"""
        # Add alert and mark as triggered
        self.alert_manager.add_alert('7203.T', 'price_above', 'manual', 2600.0)
        self.alert_manager.alerts[0].is_triggered = True
        
        # Create market data that would trigger alert
        market_data = MarketData(
            symbol='7203.T',
            price=2700.0,
            change=100.0,
            change_percent=3.8,
            volume=1000000,
            timestamp=datetime.now(),
            market_status='open'
        )
        
        self.alert_manager.check_alerts(market_data)
        
        # Alert should remain triggered (not change)
        alert = self.alert_manager.alerts[0]
        self.assertTrue(alert.is_triggered)
    
    def test_trigger_alert_callback(self):
        """Test alert callback execution"""
        callback = Mock()
        self.alert_manager.alert_callbacks.append(callback)
        
        # Add alert
        self.alert_manager.add_alert('7203.T', 'price_above', 'manual', 2600.0)
        alert = self.alert_manager.alerts[0]
        
        # Create market data
        market_data = MarketData(
            symbol='7203.T',
            price=2700.0,
            change=100.0,
            change_percent=3.8,
            volume=1000000,
            timestamp=datetime.now(),
            market_status='open'
        )
        
        # Manually trigger alert
        alert.is_triggered = True
        alert.current_value = 2700.0
        alert.timestamp = datetime.now()
        
        self.alert_manager._trigger_alert(alert, market_data)
        
        # Callback should be called
        callback.assert_called_once_with(alert, market_data)

class TestMarketData(unittest.TestCase):
    """Test MarketData dataclass"""
    
    def test_market_data_creation(self):
        """Test creating MarketData instance"""
        timestamp = datetime.now()
        market_data = MarketData(
            symbol='7203.T',
            price=2500.0,
            change=50.0,
            change_percent=2.04,
            volume=1000000,
            timestamp=timestamp,
            market_status='open'
        )
        
        self.assertEqual(market_data.symbol, '7203.T')
        self.assertEqual(market_data.price, 2500.0)
        self.assertEqual(market_data.change, 50.0)
        self.assertEqual(market_data.change_percent, 2.04)
        self.assertEqual(market_data.volume, 1000000)
        self.assertEqual(market_data.timestamp, timestamp)
        self.assertEqual(market_data.market_status, 'open')

class TestAlert(unittest.TestCase):
    """Test Alert dataclass"""
    
    def test_alert_creation(self):
        """Test creating Alert instance"""
        timestamp = datetime.now()
        alert = Alert(
            symbol='7203.T',
            alert_type='price_above',
            condition='manual',
            current_value=2500.0,
            threshold_value=2600.0,
            timestamp=timestamp,
            is_triggered=False
        )
        
        self.assertEqual(alert.symbol, '7203.T')
        self.assertEqual(alert.alert_type, 'price_above')
        self.assertEqual(alert.condition, 'manual')
        self.assertEqual(alert.current_value, 2500.0)
        self.assertEqual(alert.threshold_value, 2600.0)
        self.assertEqual(alert.timestamp, timestamp)
        self.assertFalse(alert.is_triggered)
    
    def test_alert_default_triggered(self):
        """Test Alert with default is_triggered value"""
        timestamp = datetime.now()
        alert = Alert(
            symbol='7203.T',
            alert_type='price_above',
            condition='manual',
            current_value=2500.0,
            threshold_value=2600.0,
            timestamp=timestamp
        )
        
        self.assertFalse(alert.is_triggered)  # Default value

if __name__ == '__main__':
    unittest.main()
