#!/usr/bin/env python3
"""
MCP Browser Server 起動スクリプト
browser MCPサーバーを起動して待機状態にします
"""

import asyncio
import signal
import sys
import logging
from mcp_browser_server import MCPBrowserServer

class MCPServerManager:
    """MCPサーバーマネージャー"""
    
    def __init__(self):
        self.server = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """ロガーを設定"""
        logger = logging.getLogger('MCPServerManager')
        logger.setLevel(logging.INFO)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        return logger
    
    async def start_server(self):
        """MCPサーバーを開始"""
        try:
            self.logger.info("MCP Browser Serverを開始しています...")
            
            # MCPサーバーを初期化
            self.server = MCPBrowserServer()
            
            # シグナルハンドラーを設定
            self._setup_signal_handlers()
            
            # サーバーを開始
            await self.server.start_server()
            
        except KeyboardInterrupt:
            self.logger.info("サーバーの停止が要求されました")
        except Exception as e:
            self.logger.error(f"サーバーの開始に失敗しました: {e}")
        finally:
            await self.stop_server()
    
    def _setup_signal_handlers(self):
        """シグナルハンドラーを設定"""
        def signal_handler(signum, frame):
            self.logger.info(f"シグナル {signum} を受信しました")
            asyncio.create_task(self.stop_server())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def stop_server(self):
        """MCPサーバーを停止"""
        if self.server:
            await self.server.stop_server()
        self.logger.info("MCP Browser Serverが停止されました")

async def main():
    """メイン関数"""
    print("=== MCP Browser Server 起動 ===")
    print("Ctrl+C で停止できます")
    
    manager = MCPServerManager()
    await manager.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nサーバーを停止しています...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
