"""Tests for realtime enhancements in AdvancedAlertSystem."""

import unittest
from datetime import datetime, timedelta

from advanced_alert_system import (
    AdvancedAlertSystem,
    AlertCondition,
    AlertType,
    AlertDatabase
)


class TestAdvancedAlertRealtime(unittest.TestCase):
    """Validate realtime snapshot ingestion and new alert types."""

    def setUp(self):
        self.system = AdvancedAlertSystem()
        # Use in-memory DB for isolation
        self.system.database = AlertDatabase(':memory:')
        self.system.alert_rules = {}
        self.symbol = 'TEST.T'
        self.base_time = datetime.now()
        self.system.realtime_history.clear()
        self.system.realtime_snapshots.clear()

    def tearDown(self):
        self.system.stop_monitoring()

    def _update_snapshots(self, prices, volumes=None, vwap=None, start_offset=0):
        volumes = volumes or [1000] * len(prices)
        for idx, price in enumerate(prices):
            snapshot = {
                'price': price,
                'volume': volumes[idx],
                'vwap': vwap[idx] if isinstance(vwap, list) else vwap
            }
            self.system.update_market_snapshot(
                self.symbol,
                snapshot,
                self.base_time + timedelta(seconds=start_offset + idx)
            )

    def test_update_market_snapshot_records_history(self):
        """Snapshots should be cached and available via history."""
        self._update_snapshots([100.0, 101.2])

        data = self.system._get_symbol_data(self.symbol)
        history = self.system._get_symbol_history(self.symbol)

        self.assertAlmostEqual(data['price'], 101.2)
        self.assertEqual(len(history), 2)

    def test_vwap_deviation_condition_triggers(self):
        """VWAP deviation alert should trigger on large gap."""
        prices = [100.0, 101.0, 105.0]
        vwap_values = [100.0, 100.5, 100.0]
        volumes = [1000, 1200, 1500]
        self._update_snapshots(prices, volumes=volumes, vwap=vwap_values)

        data = self.system._get_symbol_data(self.symbol)
        history = self.system._get_symbol_history(self.symbol)
        condition = AlertCondition(
            symbol=self.symbol,
            alert_type=AlertType.VWAP_DEVIATION,
            condition='VWAP deviation > 3',
            threshold_value=3.0,
            comparison_operator='>',
            time_window=15
        )

        value = self.system._evaluate_condition(condition, data, history)
        self.assertIsNotNone(value)
        self.assertGreater(value, 3.0)

    def test_volatility_and_momentum_conditions(self):
        """Volatility spike and momentum shift should be detected."""
        prices = [100.0, 104.0, 98.0, 106.0, 108.0]
        volumes = [1000, 1100, 1300, 1250, 1400]
        self._update_snapshots(prices, volumes=volumes)

        data = self.system._get_symbol_data(self.symbol)
        history = self.system._get_symbol_history(self.symbol)

        volatility_condition = AlertCondition(
            symbol=self.symbol,
            alert_type=AlertType.VOLATILITY_SPIKE,
            condition='Volatility > 1',
            threshold_value=1.0,
            comparison_operator='>',
            time_window=15
        )

        momentum_condition = AlertCondition(
            symbol=self.symbol,
            alert_type=AlertType.MOMENTUM_SHIFT,
            condition='Momentum > 4',
            threshold_value=4.0,
            comparison_operator='>',
            time_window=15
        )

        volatility_value = self.system._evaluate_condition(volatility_condition, data, history)
        momentum_value = self.system._evaluate_condition(momentum_condition, data, history)

        self.assertIsNotNone(volatility_value)
        self.assertGreater(volatility_value, 1.0)
        self.assertIsNotNone(momentum_value)
        self.assertGreater(momentum_value, 4.0)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
