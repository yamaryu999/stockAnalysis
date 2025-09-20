"""
MCP Browser Server
Chromeブラウザを使用したMCPサーバー
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from browser_mcp_client import BrowserMCPClient
import yaml
from datetime import datetime

class MCPBrowserServer:
    """MCP Browser Server"""
    
    def __init__(self, config_path: str = "mcp_config.yaml"):
        """MCPサーバーを初期化"""
        self.config = self._load_config(config_path)
        self.browser_client = None
        self.logger = self._setup_logger()
        self.is_running = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"設定ファイルの解析エラー: {e}")
            raise
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーを設定"""
        logger = logging.getLogger('MCPBrowserServer')
        logger.setLevel(getattr(logging, self.config['logging']['level']))
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(
            self.config['logging']['log_file'], 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def start_server(self):
        """MCPサーバーを開始"""
        try:
            self.logger.info("MCP Browser Serverを開始しています...")
            
            # ブラウザクライアントを初期化
            self.browser_client = BrowserMCPClient()
            
            # ブラウザを起動
            if not self.browser_client.start_browser():
                raise Exception("ブラウザの起動に失敗しました")
            
            self.is_running = True
            self.logger.info("MCP Browser Serverが正常に開始されました")
            
            # サーバーループを開始
            await self._server_loop()
            
        except Exception as e:
            self.logger.error(f"サーバーの開始に失敗しました: {e}")
            raise
        finally:
            await self.stop_server()
    
    def initialize_browser_client(self):
        """ブラウザクライアントを初期化（テスト用）"""
        if not self.browser_client:
            self.browser_client = BrowserMCPClient()
    
    async def _server_loop(self):
        """メインサーバーループ"""
        self.logger.info("サーバーループを開始しました")
        
        try:
            while self.is_running:
                # ここでMCPプロトコルのメッセージを待機
                # 実際の実装では、WebSocketやHTTPサーバーを使用
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("サーバーの停止が要求されました")
        except Exception as e:
            self.logger.error(f"サーバーループでエラーが発生しました: {e}")
    
    async def stop_server(self):
        """MCPサーバーを停止"""
        try:
            self.logger.info("MCP Browser Serverを停止しています...")
            self.is_running = False
            
            if self.browser_client:
                self.browser_client.close_browser()
            
            self.logger.info("MCP Browser Serverが正常に停止されました")
            
        except Exception as e:
            self.logger.error(f"サーバーの停止に失敗しました: {e}")
    
    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCPリクエストを処理"""
        try:
            method = request.get('method', '')
            params = request.get('params', {})
            
            self.logger.info(f"MCPリクエストを受信: {method}")
            
            # メソッドに応じて処理を分岐
            if method == 'browser/navigate':
                return self._handle_navigate(params)
            elif method == 'browser/click':
                return self._handle_click(params)
            elif method == 'browser/input':
                return self._handle_input(params)
            elif method == 'browser/get_text':
                return self._handle_get_text(params)
            elif method == 'browser/screenshot':
                return self._handle_screenshot(params)
            elif method == 'browser/execute_script':
                return self._handle_execute_script(params)
            else:
                return {
                    'error': f'Unknown method: {method}',
                    'id': request.get('id')
                }
                
        except Exception as e:
            self.logger.error(f"MCPリクエストの処理に失敗しました: {e}")
            return {
                'error': str(e),
                'id': request.get('id')
            }
    
    def _handle_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """ナビゲーション処理"""
        url = params.get('url', '')
        if not url:
            return {'error': 'URL is required'}
        
        success = self.browser_client.navigate_to(url)
        return {
            'result': {
                'success': success,
                'url': self.browser_client.get_current_url(),
                'title': self.browser_client.get_page_title()
            }
        }
    
    def _handle_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """クリック処理"""
        selector = params.get('selector', '')
        selector_type = params.get('selector_type', 'css')
        
        if not selector:
            return {'error': 'Selector is required'}
        
        # セレクタータイプをByに変換
        by_map = {
            'css': 'css selector',
            'xpath': 'xpath',
            'id': 'id',
            'class': 'class name',
            'tag': 'tag name',
            'name': 'name'
        }
        
        by_type = by_map.get(selector_type, 'css selector')
        
        success = self.browser_client.click_element(by_type, selector)
        return {
            'result': {
                'success': success,
                'selector': selector,
                'selector_type': selector_type
            }
        }
    
    def _handle_input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """テキスト入力処理"""
        selector = params.get('selector', '')
        text = params.get('text', '')
        selector_type = params.get('selector_type', 'css')
        
        if not selector or text is None:
            return {'error': 'Selector and text are required'}
        
        # セレクタータイプをByに変換
        by_map = {
            'css': 'css selector',
            'xpath': 'xpath',
            'id': 'id',
            'class': 'class name',
            'tag': 'tag name',
            'name': 'name'
        }
        
        by_type = by_map.get(selector_type, 'css selector')
        
        success = self.browser_client.input_text(by_type, selector, text)
        return {
            'result': {
                'success': success,
                'selector': selector,
                'text': text,
                'selector_type': selector_type
            }
        }
    
    def _handle_get_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """テキスト取得処理"""
        selector = params.get('selector', '')
        selector_type = params.get('selector_type', 'css')
        
        if not selector:
            return {'error': 'Selector is required'}
        
        # セレクタータイプをByに変換
        by_map = {
            'css': 'css selector',
            'xpath': 'xpath',
            'id': 'id',
            'class': 'class name',
            'tag': 'tag name',
            'name': 'name'
        }
        
        by_type = by_map.get(selector_type, 'css selector')
        
        element = self.browser_client.find_element(by_type, selector)
        text = element.text if element else ""
        
        return {
            'result': {
                'text': text,
                'selector': selector,
                'selector_type': selector_type
            }
        }
    
    def _handle_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """スクリーンショット処理"""
        filename = params.get('filename', '')
        
        screenshot_path = self.browser_client.take_screenshot(filename)
        
        return {
            'result': {
                'screenshot_path': screenshot_path,
                'success': bool(screenshot_path)
            }
        }
    
    def _handle_execute_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """JavaScript実行処理"""
        script = params.get('script', '')
        
        if not script:
            return {'error': 'Script is required'}
        
        result = self.browser_client.execute_javascript(script)
        
        return {
            'result': {
                'script_result': result,
                'success': result is not None
            }
        }


async def main():
    """メイン関数"""
    server = MCPBrowserServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\nサーバーを停止しています...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        await server.stop_server()


if __name__ == "__main__":
    asyncio.run(main())
