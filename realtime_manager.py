"""
リアルタイムデータ更新システム
WebSocket対応、プッシュ通知、市場時間監視機能
"""

import asyncio
import websockets
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import logging
import yfinance as yf
import pandas as pd
from dataclasses import dataclass
import queue
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

@dataclass
class MarketData:
    """市場データクラス"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    market_status: str

@dataclass
class Alert:
    """アラートクラス"""
    symbol: str
    alert_type: str
    condition: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    is_triggered: bool = False

class MarketStatusMonitor:
    """市場状況監視クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_status = "closed"
        self.market_hours = {
            'open': '09:00',
            'close': '15:00',
            'lunch_start': '11:30',
            'lunch_end': '12:30'
        }
    
    def is_market_open(self) -> bool:
        """市場が開いているかチェック"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        weekday = now.weekday()
        
        # 土日は市場閉鎖
        if weekday >= 5:
            return False
        
        # 市場時間チェック
        if self.market_hours['open'] <= current_time <= self.market_hours['close']:
            # 昼休み時間チェック
            if self.market_hours['lunch_start'] <= current_time <= self.market_hours['lunch_end']:
                return False
            return True
        
        return False
    
    def get_market_status(self) -> str:
        """市場状況を取得"""
        if self.is_market_open():
            return "open"
        else:
            return "closed"
    
    def get_next_market_open(self) -> datetime:
        """次回市場開放時刻を取得"""
        now = datetime.now()
        
        # 今日の市場開放時刻
        today_open = now.replace(
            hour=9, minute=0, second=0, microsecond=0
        )
        
        # 今日が土日の場合
        if now.weekday() >= 5:
            # 次の月曜日
            days_ahead = 7 - now.weekday()
            next_open = today_open + timedelta(days=days_ahead)
        elif now < today_open:
            # 今日まだ市場が開いていない
            next_open = today_open
        else:
            # 明日の市場開放時刻
            next_open = today_open + timedelta(days=1)
            # 土日をスキップ
            while next_open.weekday() >= 5:
                next_open += timedelta(days=1)
        
        return next_open

class RealTimeDataManager:
    """リアルタイムデータ管理クラス"""
    
    def __init__(self, update_interval: int = 5):
        self.update_interval = update_interval  # 秒
        self.logger = logging.getLogger(__name__)
        self.market_monitor = MarketStatusMonitor()
        self.subscribers = []
        self.data_queue = queue.Queue()
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 監視対象銘柄
        self.watched_symbols = set()
        
        # データキャッシュ
        self.data_cache = {}
        self.cache_ttl = 30  # 秒
    
    def add_subscriber(self, callback: Callable[[MarketData], None]):
        """データ更新の購読者を追加"""
        self.subscribers.append(callback)
        self.logger.info(f"購読者を追加: {len(self.subscribers)}人")
    
    def remove_subscriber(self, callback: Callable[[MarketData], None]):
        """購読者を削除"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            self.logger.info(f"購読者を削除: {len(self.subscribers)}人")
    
    def add_symbol(self, symbol: str):
        """監視対象銘柄を追加"""
        self.watched_symbols.add(symbol)
        self.logger.info(f"監視銘柄を追加: {symbol}")
    
    def remove_symbol(self, symbol: str):
        """監視対象銘柄を削除"""
        self.watched_symbols.discard(symbol)
        self.logger.info(f"監視銘柄を削除: {symbol}")
    
    def start_monitoring(self):
        """リアルタイム監視を開始"""
        if self.is_running:
            self.logger.warning("リアルタイム監視は既に実行中です")
            return
        
        self.is_running = True
        self.logger.info("リアルタイム監視を開始")
        
        # 監視スレッドを開始
        monitor_thread = threading.Thread(target=self._monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # データ配信スレッドを開始
        distribution_thread = threading.Thread(target=self._distribution_loop)
        distribution_thread.daemon = True
        distribution_thread.start()
    
    def stop_monitoring(self):
        """リアルタイム監視を停止"""
        self.is_running = False
        self.logger.info("リアルタイム監視を停止")
    
    def _monitoring_loop(self):
        """監視ループ"""
        while self.is_running:
            try:
                if self.market_monitor.is_market_open():
                    self._update_market_data()
                else:
                    self.logger.debug("市場は閉鎖中です")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                time.sleep(self.update_interval)
    
    def _update_market_data(self):
        """市場データを更新"""
        try:
            for symbol in self.watched_symbols:
                # キャッシュチェック
                cache_key = f"{symbol}_{int(time.time() // self.cache_ttl)}"
                if cache_key in self.data_cache:
                    continue
                
                # データ取得
                data = self._fetch_symbol_data(symbol)
                if data:
                    self.data_cache[cache_key] = data
                    self.data_queue.put(data)
                
                # レート制限対応
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"市場データ更新エラー: {e}")
    
    def _fetch_symbol_data(self, symbol: str) -> Optional[MarketData]:
        """銘柄データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 現在価格を取得
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = info.get('previousClose', current_price)
            
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
            
            market_data = MarketData(
                symbol=symbol,
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                timestamp=datetime.now(),
                market_status=self.market_monitor.get_market_status()
            )
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"銘柄データ取得エラー {symbol}: {e}")
            return None
    
    def _distribution_loop(self):
        """データ配信ループ"""
        while self.is_running:
            try:
                if not self.data_queue.empty():
                    data = self.data_queue.get()
                    self._notify_subscribers(data)
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"データ配信エラー: {e}")
    
    def _notify_subscribers(self, data: MarketData):
        """購読者にデータを通知"""
        for callback in self.subscribers:
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"購読者通知エラー: {e}")

class AlertManager:
    """アラート管理クラス"""
    
    def __init__(self, realtime_manager: RealTimeDataManager):
        self.realtime_manager = realtime_manager
        self.logger = logging.getLogger(__name__)
        self.alerts = []
        self.alert_callbacks = []
    
    def add_alert(self, symbol: str, alert_type: str, condition: str, 
                  threshold_value: float, callback: Optional[Callable] = None):
        """アラートを追加"""
        alert = Alert(
            symbol=symbol,
            alert_type=alert_type,
            condition=condition,
            current_value=0.0,
            threshold_value=threshold_value,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        if callback:
            self.alert_callbacks.append(callback)
        
        # 監視対象銘柄に追加
        self.realtime_manager.add_symbol(symbol)
        
        self.logger.info(f"アラートを追加: {symbol} {alert_type} {condition} {threshold_value}")
    
    def check_alerts(self, market_data: MarketData):
        """アラートをチェック"""
        for alert in self.alerts:
            if alert.symbol != market_data.symbol:
                continue
            
            if alert.is_triggered:
                continue
            
            # アラート条件をチェック
            if self._check_alert_condition(alert, market_data):
                alert.is_triggered = True
                alert.current_value = market_data.price
                alert.timestamp = datetime.now()
                
                self._trigger_alert(alert, market_data)
    
    def _check_alert_condition(self, alert: Alert, market_data: MarketData) -> bool:
        """アラート条件をチェック"""
        try:
            if alert.alert_type == "price_above":
                return market_data.price > alert.threshold_value
            elif alert.alert_type == "price_below":
                return market_data.price < alert.threshold_value
            elif alert.alert_type == "change_percent_above":
                return market_data.change_percent > alert.threshold_value
            elif alert.alert_type == "change_percent_below":
                return market_data.change_percent < alert.threshold_value
            elif alert.alert_type == "volume_above":
                return market_data.volume > alert.threshold_value
            
            return False
            
        except Exception as e:
            self.logger.error(f"アラート条件チェックエラー: {e}")
            return False
    
    def _trigger_alert(self, alert: Alert, market_data: MarketData):
        """アラートを発火"""
        self.logger.info(f"アラート発火: {alert.symbol} {alert.alert_type}")
        
        # コールバックを実行
        for callback in self.alert_callbacks:
            try:
                callback(alert, market_data)
            except Exception as e:
                self.logger.error(f"アラートコールバックエラー: {e}")

class WebSocketServer:
    """WebSocketサーバークラス"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.clients = set()
        self.realtime_manager = RealTimeDataManager()
        self.alert_manager = AlertManager(self.realtime_manager)
        
        # リアルタイムデータの購読
        self.realtime_manager.add_subscriber(self._on_market_data_update)
    
    async def register_client(self, websocket, path):
        """クライアントを登録"""
        self.clients.add(websocket)
        self.logger.info(f"クライアント接続: {len(self.clients)}人")
        
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.logger.info(f"クライアント切断: {len(self.clients)}人")
    
    async def _handle_message(self, websocket, message):
        """メッセージを処理"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'subscribe':
                symbol = data.get('symbol')
                if symbol:
                    self.realtime_manager.add_symbol(symbol)
                    await websocket.send(json.dumps({
                        'type': 'subscription_confirmed',
                        'symbol': symbol
                    }))
            
            elif command == 'unsubscribe':
                symbol = data.get('symbol')
                if symbol:
                    self.realtime_manager.remove_symbol(symbol)
                    await websocket.send(json.dumps({
                        'type': 'unsubscription_confirmed',
                        'symbol': symbol
                    }))
            
            elif command == 'add_alert':
                symbol = data.get('symbol')
                alert_type = data.get('alert_type')
                threshold = data.get('threshold')
                
                if symbol and alert_type and threshold:
                    self.alert_manager.add_alert(symbol, alert_type, 'manual', threshold)
                    await websocket.send(json.dumps({
                        'type': 'alert_added',
                        'symbol': symbol
                    }))
            
        except Exception as e:
            self.logger.error(f"メッセージ処理エラー: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    def _on_market_data_update(self, market_data: MarketData):
        """市場データ更新時の処理"""
        # アラートチェック
        self.alert_manager.check_alerts(market_data)
        
        # WebSocketクライアントにデータを送信
        asyncio.create_task(self._broadcast_market_data(market_data))
    
    async def _broadcast_market_data(self, market_data: MarketData):
        """市場データをブロードキャスト"""
        if not self.clients:
            return
        
        message = json.dumps({
            'type': 'market_data',
            'data': {
                'symbol': market_data.symbol,
                'price': market_data.price,
                'change': market_data.change,
                'change_percent': market_data.change_percent,
                'volume': market_data.volume,
                'timestamp': market_data.timestamp.isoformat(),
                'market_status': market_data.market_status
            }
        })
        
        # 全クライアントに送信
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # 切断されたクライアントを削除
        self.clients -= disconnected_clients
    
    async def start_server(self):
        """WebSocketサーバーを開始"""
        self.logger.info(f"WebSocketサーバーを開始: {self.host}:{self.port}")
        
        # リアルタイム監視を開始
        self.realtime_manager.start_monitoring()
        
        # WebSocketサーバーを開始
        async with websockets.serve(self.register_client, self.host, self.port):
            await asyncio.Future()  # 永続実行

class NotificationManager:
    """通知管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_queue = queue.Queue()
        self.is_running = False
    
    def add_notification(self, title: str, message: str, notification_type: str = "info"):
        """通知を追加"""
        notification = {
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now()
        }
        
        self.notification_queue.put(notification)
        self.logger.info(f"通知を追加: {title}")
    
    def start_notification_service(self):
        """通知サービスを開始"""
        self.is_running = True
        notification_thread = threading.Thread(target=self._notification_loop)
        notification_thread.daemon = True
        notification_thread.start()
    
    def stop_notification_service(self):
        """通知サービスを停止"""
        self.is_running = False
    
    def _notification_loop(self):
        """通知ループ"""
        while self.is_running:
            try:
                if not self.notification_queue.empty():
                    notification = self.notification_queue.get()
                    self._send_notification(notification)
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"通知ループエラー: {e}")
    
    def _send_notification(self, notification: Dict):
        """通知を送信"""
        try:
            # ここで実際の通知送信処理を実装
            # 例: デスクトップ通知、メール、Slack等
            
            self.logger.info(f"通知送信: {notification['title']} - {notification['message']}")
            
        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")

# グローバルインスタンス
realtime_manager = RealTimeDataManager()
alert_manager = AlertManager(realtime_manager)
notification_manager = NotificationManager()

def start_realtime_services():
    """リアルタイムサービスを開始"""
    try:
        # リアルタイム監視を開始
        realtime_manager.start_monitoring()
        
        # 通知サービスを開始
        notification_manager.start_notification_service()
        
        logging.info("リアルタイムサービスを開始しました")
        
    except Exception as e:
        logging.error(f"リアルタイムサービス開始エラー: {e}")

def stop_realtime_services():
    """リアルタイムサービスを停止"""
    try:
        realtime_manager.stop_monitoring()
        notification_manager.stop_notification_service()
        
        logging.info("リアルタイムサービスを停止しました")
        
    except Exception as e:
        logging.error(f"リアルタイムサービス停止エラー: {e}")

# シグナルハンドラー
def signal_handler(signum, frame):
    """シグナルハンドラー"""
    logging.info("シグナルを受信しました。サービスを停止します...")
    stop_realtime_services()
    sys.exit(0)

# シグナル登録（メインスレッドでのみ実行）
def register_signal_handlers():
    """シグナルハンドラーを登録（メインスレッドでのみ実行）"""
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        logging.info("シグナルハンドラーを登録しました")
    except ValueError as e:
        logging.warning(f"シグナルハンドラーの登録に失敗しました（メインスレッド以外）: {e}")

# メインスレッドでのみシグナル登録を実行
if __name__ == "__main__":
    register_signal_handlers()