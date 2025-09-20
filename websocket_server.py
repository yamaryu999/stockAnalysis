"""
WebSocketサーバー
リアルタイム通知システムのサーバー側実装
"""

import asyncio
import websockets
import json
import logging
import signal
import sys
from datetime import datetime
from realtime_manager import WebSocketServer, RealTimeDataManager, AlertManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedWebSocketServer(WebSocketServer):
    """拡張WebSocketサーバー"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        super().__init__(host, port)
        self.logger = logging.getLogger(__name__)
        self.server = None
        self.is_running = False
    
    async def start_server(self):
        """WebSocketサーバーを開始"""
        self.logger.info(f"WebSocketサーバーを開始: {self.host}:{self.port}")
        
        # リアルタイム監視を開始
        self.realtime_manager.start_monitoring()
        
        # WebSocketサーバーを開始
        self.server = await websockets.serve(
            self.register_client, 
            self.host, 
            self.port
        )
        
        self.is_running = True
        self.logger.info("WebSocketサーバーが正常に開始されました")
        
        # サーバーを永続実行
        await self.server.wait_closed()
    
    async def stop_server(self):
        """WebSocketサーバーを停止"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            self.logger.info("WebSocketサーバーを停止しました")
    
    async def _handle_message(self, websocket, message):
        """メッセージを処理（拡張版）"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'subscribe':
                symbol = data.get('symbol')
                if symbol:
                    self.realtime_manager.add_symbol(symbol)
                    await websocket.send(json.dumps({
                        'type': 'subscription_confirmed',
                        'symbol': symbol,
                        'timestamp': datetime.now().isoformat()
                    }))
                    self.logger.info(f"銘柄購読: {symbol}")
            
            elif command == 'unsubscribe':
                symbol = data.get('symbol')
                if symbol:
                    self.realtime_manager.remove_symbol(symbol)
                    await websocket.send(json.dumps({
                        'type': 'unsubscription_confirmed',
                        'symbol': symbol,
                        'timestamp': datetime.now().isoformat()
                    }))
                    self.logger.info(f"銘柄購読解除: {symbol}")
            
            elif command == 'add_alert':
                symbol = data.get('symbol')
                alert_type = data.get('alert_type')
                threshold = data.get('threshold')
                
                if symbol and alert_type and threshold:
                    self.alert_manager.add_alert(symbol, alert_type, 'manual', threshold)
                    await websocket.send(json.dumps({
                        'type': 'alert_added',
                        'symbol': symbol,
                        'alert_type': alert_type,
                        'threshold': threshold,
                        'timestamp': datetime.now().isoformat()
                    }))
                    self.logger.info(f"アラート追加: {symbol} {alert_type} {threshold}")
            
            elif command == 'get_status':
                # サーバー状態を返す
                status = {
                    'type': 'status',
                    'connected_clients': len(self.clients),
                    'monitored_symbols': list(self.realtime_manager.watched_symbols),
                    'active_alerts': len(self.alert_manager.alerts),
                    'server_time': datetime.now().isoformat(),
                    'market_status': self.realtime_manager.market_monitor.get_market_status()
                }
                await websocket.send(json.dumps(status))
            
            elif command == 'ping':
                # 接続確認
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            
        except Exception as e:
            self.logger.error(f"メッセージ処理エラー: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }))
    
    async def _broadcast_market_data(self, market_data):
        """市場データをブロードキャスト（拡張版）"""
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
            },
            'server_timestamp': datetime.now().isoformat()
        })
        
        # 全クライアントに送信
        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"クライアント送信エラー: {e}")
                disconnected_clients.add(client)
        
        # 切断されたクライアントを削除
        self.clients -= disconnected_clients
        
        if disconnected_clients:
            self.logger.info(f"切断されたクライアント: {len(disconnected_clients)}人")

# グローバルサーバーインスタンス
websocket_server = None

async def start_websocket_server(host: str = "localhost", port: int = 8765):
    """WebSocketサーバーを開始"""
    global websocket_server
    
    try:
        websocket_server = EnhancedWebSocketServer(host, port)
        await websocket_server.start_server()
        
    except Exception as e:
        logger.error(f"WebSocketサーバー開始エラー: {e}")
        raise

async def stop_websocket_server():
    """WebSocketサーバーを停止"""
    global websocket_server
    
    if websocket_server:
        await websocket_server.stop_server()
        websocket_server = None

def signal_handler(signum, frame):
    """シグナルハンドラー"""
    logger.info("シグナルを受信しました。サーバーを停止します...")
    
    # イベントループを取得して停止処理を実行
    loop = asyncio.get_event_loop()
    loop.create_task(stop_websocket_server())
    
    # イベントループを停止
    loop.stop()

def main():
    """メイン関数"""
    # シグナルハンドラーを登録
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # サーバー設定
    host = "localhost"
    port = 8765
    
    logger.info(f"WebSocketサーバーを開始します: {host}:{port}")
    
    try:
        # イベントループを開始
        asyncio.run(start_websocket_server(host, port))
        
    except KeyboardInterrupt:
        logger.info("キーボード割り込みを受信しました")
    except Exception as e:
        logger.error(f"サーバー実行エラー: {e}")
    finally:
        logger.info("WebSocketサーバーを終了します")

if __name__ == "__main__":
    main()