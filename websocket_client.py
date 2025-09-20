"""
WebSocketクライアント
Streamlitアプリケーション用のリアルタイム通知クライアント
"""

import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import logging
import streamlit as st
from dataclasses import dataclass
import queue

@dataclass
class RealtimeData:
    """リアルタイムデータクラス"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    market_status: str

@dataclass
class AlertNotification:
    """アラート通知クラス"""
    symbol: str
    alert_type: str
    message: str
    timestamp: datetime
    severity: str = "info"

class WebSocketClient:
    """WebSocketクライアントクラス"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.websocket = None
        self.is_connected = False
        self.is_running = False
        
        # データキュー
        self.data_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        
        # コールバック
        self.data_callbacks = []
        self.alert_callbacks = []
        
        # 購読銘柄
        self.subscribed_symbols = set()
        
        # 接続状態の監視
        self.connection_thread = None
        self.reconnect_interval = 5  # 秒
        self.max_reconnect_attempts = 10
    
    def add_data_callback(self, callback: Callable[[RealtimeData], None]):
        """データ更新のコールバックを追加"""
        self.data_callbacks.append(callback)
    
    def add_alert_callback(self, callback: Callable[[AlertNotification], None]):
        """アラート通知のコールバックを追加"""
        self.alert_callbacks.append(callback)
    
    def subscribe_symbol(self, symbol: str):
        """銘柄を購読"""
        self.subscribed_symbols.add(symbol)
        if self.is_connected and self.websocket:
            asyncio.create_task(self._send_subscribe_command(symbol))
    
    def unsubscribe_symbol(self, symbol: str):
        """銘柄の購読を解除"""
        self.subscribed_symbols.discard(symbol)
        if self.is_connected and self.websocket:
            asyncio.create_task(self._send_unsubscribe_command(symbol))
    
    def add_alert(self, symbol: str, alert_type: str, threshold: float):
        """アラートを追加"""
        if self.is_connected and self.websocket:
            asyncio.create_task(self._send_add_alert_command(symbol, alert_type, threshold))
    
    async def connect(self):
        """WebSocketサーバーに接続"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            self.logger.info(f"WebSocketサーバーに接続: {uri}")
            
            # 既存の購読銘柄を再購読
            for symbol in self.subscribed_symbols:
                await self._send_subscribe_command(symbol)
            
            return True
            
        except Exception as e:
            self.logger.error(f"WebSocket接続エラー: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """WebSocketサーバーから切断"""
        try:
            if self.websocket:
                await self.websocket.close()
            self.is_connected = False
            self.logger.info("WebSocketサーバーから切断")
            
        except Exception as e:
            self.logger.error(f"WebSocket切断エラー: {e}")
    
    async def _send_subscribe_command(self, symbol: str):
        """購読コマンドを送信"""
        try:
            command = {
                'command': 'subscribe',
                'symbol': symbol
            }
            await self.websocket.send(json.dumps(command))
            self.logger.info(f"銘柄購読: {symbol}")
            
        except Exception as e:
            self.logger.error(f"購読コマンド送信エラー: {e}")
    
    async def _send_unsubscribe_command(self, symbol: str):
        """購読解除コマンドを送信"""
        try:
            command = {
                'command': 'unsubscribe',
                'symbol': symbol
            }
            await self.websocket.send(json.dumps(command))
            self.logger.info(f"銘柄購読解除: {symbol}")
            
        except Exception as e:
            self.logger.error(f"購読解除コマンド送信エラー: {e}")
    
    async def _send_add_alert_command(self, symbol: str, alert_type: str, threshold: float):
        """アラート追加コマンドを送信"""
        try:
            command = {
                'command': 'add_alert',
                'symbol': symbol,
                'alert_type': alert_type,
                'threshold': threshold
            }
            await self.websocket.send(json.dumps(command))
            self.logger.info(f"アラート追加: {symbol} {alert_type} {threshold}")
            
        except Exception as e:
            self.logger.error(f"アラート追加コマンド送信エラー: {e}")
    
    async def _listen_for_messages(self):
        """メッセージを受信"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket接続が閉じられました")
            self.is_connected = False
            
        except Exception as e:
            self.logger.error(f"メッセージ受信エラー: {e}")
            self.is_connected = False
    
    async def _handle_message(self, message: str):
        """メッセージを処理"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'market_data':
                await self._handle_market_data(data)
            elif message_type == 'alert':
                await self._handle_alert(data)
            elif message_type == 'subscription_confirmed':
                self.logger.info(f"購読確認: {data.get('symbol')}")
            elif message_type == 'unsubscription_confirmed':
                self.logger.info(f"購読解除確認: {data.get('symbol')}")
            elif message_type == 'alert_added':
                self.logger.info(f"アラート追加確認: {data.get('symbol')}")
            elif message_type == 'error':
                self.logger.error(f"サーバーエラー: {data.get('message')}")
                
        except Exception as e:
            self.logger.error(f"メッセージ処理エラー: {e}")
    
    async def _handle_market_data(self, data: Dict):
        """市場データを処理"""
        try:
            market_data = data.get('data', {})
            
            realtime_data = RealtimeData(
                symbol=market_data.get('symbol', ''),
                price=market_data.get('price', 0.0),
                change=market_data.get('change', 0.0),
                change_percent=market_data.get('change_percent', 0.0),
                volume=market_data.get('volume', 0),
                timestamp=datetime.fromisoformat(market_data.get('timestamp', datetime.now().isoformat())),
                market_status=market_data.get('market_status', 'unknown')
            )
            
            # データキューに追加
            self.data_queue.put(realtime_data)
            
            # コールバックを実行
            for callback in self.data_callbacks:
                try:
                    callback(realtime_data)
                except Exception as e:
                    self.logger.error(f"データコールバックエラー: {e}")
                    
        except Exception as e:
            self.logger.error(f"市場データ処理エラー: {e}")
    
    async def _handle_alert(self, data: Dict):
        """アラートを処理"""
        try:
            alert_data = data.get('data', {})
            
            alert_notification = AlertNotification(
                symbol=alert_data.get('symbol', ''),
                alert_type=alert_data.get('alert_type', ''),
                message=alert_data.get('message', ''),
                timestamp=datetime.fromisoformat(alert_data.get('timestamp', datetime.now().isoformat())),
                severity=alert_data.get('severity', 'info')
            )
            
            # アラートキューに追加
            self.alert_queue.put(alert_notification)
            
            # コールバックを実行
            for callback in self.alert_callbacks:
                try:
                    callback(alert_notification)
                except Exception as e:
                    self.logger.error(f"アラートコールバックエラー: {e}")
                    
        except Exception as e:
            self.logger.error(f"アラート処理エラー: {e}")
    
    def start_connection_loop(self):
        """接続ループを開始"""
        if self.is_running:
            return
        
        self.is_running = True
        self.connection_thread = threading.Thread(target=self._connection_loop)
        self.connection_thread.daemon = True
        self.connection_thread.start()
    
    def stop_connection_loop(self):
        """接続ループを停止"""
        self.is_running = False
        if self.connection_thread:
            self.connection_thread.join()
    
    def _connection_loop(self):
        """接続ループ"""
        reconnect_attempts = 0
        
        while self.is_running:
            try:
                if not self.is_connected:
                    # 接続を試行
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    if loop.run_until_complete(self.connect()):
                        reconnect_attempts = 0
                        # メッセージ受信ループを開始
                        loop.run_until_complete(self._listen_for_messages())
                    else:
                        reconnect_attempts += 1
                        if reconnect_attempts >= self.max_reconnect_attempts:
                            self.logger.error("最大再接続試行回数に達しました")
                            break
                        
                        time.sleep(self.reconnect_interval)
                    
                    loop.close()
                else:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"接続ループエラー: {e}")
                self.is_connected = False
                time.sleep(self.reconnect_interval)
    
    def get_latest_data(self) -> Optional[RealtimeData]:
        """最新のデータを取得"""
        try:
            if not self.data_queue.empty():
                return self.data_queue.get_nowait()
        except queue.Empty:
            pass
        return None
    
    def get_latest_alert(self) -> Optional[AlertNotification]:
        """最新のアラートを取得"""
        try:
            if not self.alert_queue.empty():
                return self.alert_queue.get_nowait()
        except queue.Empty:
            pass
        return None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """接続状態を取得"""
        return {
            'is_connected': self.is_connected,
            'is_running': self.is_running,
            'subscribed_symbols': list(self.subscribed_symbols),
            'data_queue_size': self.data_queue.qsize(),
            'alert_queue_size': self.alert_queue.qsize()
        }

# Streamlit用のリアルタイム通知管理クラス
class StreamlitRealtimeManager:
    """Streamlit用リアルタイム管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = WebSocketClient()
        self.notifications = []
        self.max_notifications = 50
        
        # Streamlitセッション状態の初期化
        if 'realtime_data' not in st.session_state:
            st.session_state.realtime_data = {}
        
        if 'realtime_notifications' not in st.session_state:
            st.session_state.realtime_notifications = []
        
        if 'websocket_connected' not in st.session_state:
            st.session_state.websocket_connected = False
        
        # コールバックを設定
        self.client.add_data_callback(self._on_data_update)
        self.client.add_alert_callback(self._on_alert)
    
    def start(self):
        """リアルタイムサービスを開始"""
        try:
            self.client.start_connection_loop()
            st.session_state.websocket_connected = True
            self.logger.info("Streamlitリアルタイムサービスを開始")
            
        except Exception as e:
            self.logger.error(f"リアルタイムサービス開始エラー: {e}")
            st.error(f"リアルタイムサービス開始エラー: {e}")
    
    def stop(self):
        """リアルタイムサービスを停止"""
        try:
            self.client.stop_connection_loop()
            st.session_state.websocket_connected = False
            self.logger.info("Streamlitリアルタイムサービスを停止")
            
        except Exception as e:
            self.logger.error(f"リアルタイムサービス停止エラー: {e}")
    
    def subscribe_symbol(self, symbol: str):
        """銘柄を購読"""
        self.client.subscribe_symbol(symbol)
        st.session_state.realtime_data[symbol] = None
    
    def unsubscribe_symbol(self, symbol: str):
        """銘柄の購読を解除"""
        self.client.unsubscribe_symbol(symbol)
        if symbol in st.session_state.realtime_data:
            del st.session_state.realtime_data[symbol]
    
    def add_alert(self, symbol: str, alert_type: str, threshold: float):
        """アラートを追加"""
        self.client.add_alert(symbol, alert_type, threshold)
    
    def _on_data_update(self, data: RealtimeData):
        """データ更新時の処理"""
        try:
            # セッション状態を更新
            st.session_state.realtime_data[data.symbol] = data
            
            # 自動リフレッシュ（Streamlitの制限により、手動でリフレッシュが必要）
            # st.rerun()  # 必要に応じてコメントアウトを解除
            
        except Exception as e:
            self.logger.error(f"データ更新処理エラー: {e}")
    
    def _on_alert(self, alert: AlertNotification):
        """アラート通知時の処理"""
        try:
            # 通知をセッション状態に追加
            notification = {
                'symbol': alert.symbol,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'severity': alert.severity
            }
            
            st.session_state.realtime_notifications.append(notification)
            
            # 最大通知数を超えた場合は古い通知を削除
            if len(st.session_state.realtime_notifications) > self.max_notifications:
                st.session_state.realtime_notifications = st.session_state.realtime_notifications[-self.max_notifications:]
            
            # Streamlit通知を表示
            if alert.severity == 'error':
                st.error(f"🚨 {alert.symbol}: {alert.message}")
            elif alert.severity == 'warning':
                st.warning(f"⚠️ {alert.symbol}: {alert.message}")
            else:
                st.info(f"ℹ️ {alert.symbol}: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"アラート処理エラー: {e}")
    
    def get_latest_data(self, symbol: str) -> Optional[RealtimeData]:
        """指定銘柄の最新データを取得"""
        return st.session_state.realtime_data.get(symbol)
    
    def get_all_data(self) -> Dict[str, RealtimeData]:
        """全銘柄の最新データを取得"""
        return st.session_state.realtime_data
    
    def get_notifications(self) -> List[Dict]:
        """通知一覧を取得"""
        return st.session_state.realtime_notifications
    
    def clear_notifications(self):
        """通知をクリア"""
        st.session_state.realtime_notifications = []
    
    def get_connection_status(self) -> Dict[str, Any]:
        """接続状態を取得"""
        status = self.client.get_connection_status()
        status['streamlit_connected'] = st.session_state.websocket_connected
        return status

# グローバルインスタンス
streamlit_realtime_manager = StreamlitRealtimeManager()