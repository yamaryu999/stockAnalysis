"""Realtime alert bridge module
Connects realtime market data stream with the advanced alert system.
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from advanced_alert_system import advanced_alert_system
from realtime_manager import realtime_manager, MarketData


class RealtimeAlertBridge:
    """Bridge realtime market snapshots into the advanced alert system."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._registered = False
        self._register_bridge()

    def _register_bridge(self) -> None:
        if self._registered:
            return
        realtime_manager.add_subscriber(self._on_market_data)
        self._registered = True
        self.logger.info("リアルタイムアラートブリッジを登録しました")

    def _on_market_data(self, market_data: MarketData) -> None:
        """Handle realtime market updates and forward them to the alert system."""
        try:
            snapshot: Dict[str, Any] = {
                'price': market_data.price,
                'change': market_data.change,
                'change_percent': market_data.change_percent,
                'volume': market_data.volume,
                'bid': market_data.bid,
                'ask': market_data.ask,
                'high': market_data.high,
                'low': market_data.low,
                'vwap': market_data.vwap,
                'volatility': market_data.volatility,
                'momentum': market_data.momentum,
                'volume_ratio': market_data.volume_ratio,
                'market_status': market_data.market_status
            }

            filtered_snapshot = {k: v for k, v in snapshot.items() if v is not None}
            advanced_alert_system.update_market_snapshot(
                market_data.symbol,
                filtered_snapshot,
                market_data.timestamp
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error(f"リアルタイムデータ橋渡しエラー: {exc}")


def ensure_bridge() -> RealtimeAlertBridge:
    """Ensure a singleton bridge instance exists."""
    global realtime_alert_bridge
    return realtime_alert_bridge


realtime_alert_bridge = RealtimeAlertBridge()
