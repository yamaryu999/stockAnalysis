"""
MCP Browser Client for Chrome
Chromeブラウザを使用したMCPクライアント
"""

import yaml
import logging
import time
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import json
import requests
from datetime import datetime

class BrowserMCPClient:
    """Chromeブラウザを使用したMCPクライアント"""
    
    def __init__(self, config_path: str = "mcp_config.yaml"):
        """MCPクライアントを初期化"""
        self.config = self._load_config(config_path)
        self.driver = None
        self.wait = None
        self.logger = self._setup_logger()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                # 設定ファイルの構造を確認し、必要なセクションが存在することを保証
                if 'logging' not in config:
                    config['logging'] = {'level': 'INFO', 'log_file': 'logs/browser_mcp.log'}
                return config
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"設定ファイルの解析エラー: {e}")
            raise
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーを設定"""
        logger = logging.getLogger('BrowserMCP')
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
    
    def start_browser(self) -> bool:
        """Chromeブラウザを起動"""
        try:
            # Chromeオプションを設定
            chrome_options = Options()
            
            # 設定ファイルからオプションを読み込み
            chrome_options_list = self.config.get('chrome', {}).get('options', [])
            for option in chrome_options_list:
                chrome_options.add_argument(option)
            
            # ユーザーエージェントを設定
            chrome_options.add_argument(
                f"--user-agent={self.config['browser']['user_agent']}"
            )
            
            # ウィンドウサイズを設定
            chrome_options.add_argument(
                f"--window-size={self.config['browser']['window_size']}"
            )
            
            # ヘッドレスモードの設定
            if self.config['browser']['headless']:
                chrome_options.add_argument("--headless")
            
            # セキュリティ設定
            if self.config['security']['allow_insecure_certs']:
                chrome_options.add_argument("--allow-running-insecure-content")
                chrome_options.add_argument("--ignore-certificate-errors")
            
            # ChromeDriverを自動取得
            service = Service(ChromeDriverManager().install())
            
            # ブラウザを起動
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # タイムアウト設定
            self.driver.implicitly_wait(self.config['automation']['implicit_wait'])
            self.driver.set_page_load_timeout(self.config['automation']['page_load_timeout'])
            self.driver.set_script_timeout(self.config['automation']['script_timeout'])
            
            # WebDriverWaitを初期化
            self.wait = WebDriverWait(
                self.driver, 
                self.config['automation']['implicit_wait']
            )
            
            self.logger.info("Chromeブラウザが正常に起動しました")
            return True
            
        except Exception as e:
            self.logger.error(f"ブラウザの起動に失敗しました: {e}")
            return False
    
    def navigate_to(self, url: str) -> bool:
        """指定されたURLに移動"""
        try:
            self.logger.info(f"URLに移動中: {url}")
            self.driver.get(url)
            self.logger.info("ページの読み込みが完了しました")
            return True
        except TimeoutException:
            self.logger.error("ページの読み込みがタイムアウトしました")
            return False
        except Exception as e:
            self.logger.error(f"ページの移動に失敗しました: {e}")
            return False
    
    def find_element(self, by: By, value: str, timeout: int = None) -> Optional[Any]:
        """要素を検索"""
        try:
            wait_time = timeout or self.config['automation']['implicit_wait']
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"要素が見つかりません: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"要素の検索に失敗しました: {e}")
            return None
    
    def click_element(self, by: By, value: str) -> bool:
        """要素をクリック"""
        try:
            element = self.find_element(by, value)
            if element:
                element.click()
                self.logger.info(f"要素をクリックしました: {by}={value}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"要素のクリックに失敗しました: {e}")
            return False
    
    def input_text(self, by: By, value: str, text: str) -> bool:
        """テキストを入力"""
        try:
            element = self.find_element(by, value)
            if element:
                element.clear()
                element.send_keys(text)
                self.logger.info(f"テキストを入力しました: {text}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"テキストの入力に失敗しました: {e}")
            return False
    
    def get_page_source(self) -> str:
        """ページのソースを取得"""
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"ページソースの取得に失敗しました: {e}")
            return ""
    
    def get_page_title(self) -> str:
        """ページタイトルを取得"""
        try:
            return self.driver.title
        except Exception as e:
            self.logger.error(f"ページタイトルの取得に失敗しました: {e}")
            return ""
    
    def get_current_url(self) -> str:
        """現在のURLを取得"""
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"現在のURLの取得に失敗しました: {e}")
            return ""
    
    def execute_javascript(self, script: str) -> Any:
        """JavaScriptを実行"""
        try:
            result = self.driver.execute_script(script)
            self.logger.info("JavaScriptが実行されました")
            return result
        except Exception as e:
            self.logger.error(f"JavaScriptの実行に失敗しました: {e}")
            return None
    
    def take_screenshot(self, filename: str = None) -> str:
        """スクリーンショットを撮影"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            self.logger.info(f"スクリーンショットを保存しました: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"スクリーンショットの撮影に失敗しました: {e}")
            return ""
    
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> bool:
        """要素の出現を待機"""
        try:
            wait_time = timeout or self.config['automation']['implicit_wait']
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            self.logger.warning(f"要素の出現を待機中にタイムアウトしました: {by}={value}")
            return False
        except Exception as e:
            self.logger.error(f"要素の待機に失敗しました: {e}")
            return False
    
    def close_browser(self):
        """ブラウザを閉じる"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("ブラウザを閉じました")
        except Exception as e:
            self.logger.error(f"ブラウザの終了に失敗しました: {e}")
    
    def __enter__(self):
        """コンテキストマネージャーの開始"""
        if self.start_browser():
            return self
        else:
            raise Exception("ブラウザの起動に失敗しました")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了"""
        self.close_browser()


# 使用例
if __name__ == "__main__":
    # MCPクライアントの使用例
    with BrowserMCPClient() as browser:
        # Googleに移動
        browser.navigate_to("https://www.google.com")
        
        # 検索ボックスにテキストを入力
        browser.input_text(By.NAME, "q", "Python Selenium")
        
        # 検索ボタンをクリック
        browser.click_element(By.NAME, "btnK")
        
        # 結果を待機
        browser.wait_for_element(By.ID, "search")
        
        # スクリーンショットを撮影
        browser.take_screenshot("google_search_result.png")
        
        print(f"ページタイトル: {browser.get_page_title()}")
        print(f"現在のURL: {browser.get_current_url()}")
