#!/usr/bin/env python3
"""
Browser MCP テストスクリプト
browser MCPの動作をテストします
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By

def test_browser_mcp():
    """browser MCPのテストを実行"""
    print("=== Browser MCP テスト開始 ===")
    
    try:
        # MCPクライアントを初期化
        print("1. MCPクライアントを初期化中...")
        browser = BrowserMCPClient()
        
        # ブラウザを起動
        print("2. ブラウザを起動中...")
        if not browser.start_browser():
            print("❌ ブラウザの起動に失敗しました")
            return False
        
        print("✅ ブラウザが正常に起動しました")
        
        # Googleに移動
        print("3. Googleに移動中...")
        if browser.navigate_to("https://www.google.com"):
            print("✅ Googleに正常に移動しました")
        else:
            print("❌ Googleへの移動に失敗しました")
            return False
        
        # ページタイトルを取得
        title = browser.get_page_title()
        print(f"4. ページタイトル: {title}")
        
        # 現在のURLを取得
        current_url = browser.get_current_url()
        print(f"5. 現在のURL: {current_url}")
        
        # 検索ボックスにテキストを入力
        print("6. 検索ボックスにテキストを入力中...")
        if browser.input_text(By.NAME, "q", "Python MCP"):
            print("✅ テキストの入力に成功しました")
        else:
            print("❌ テキストの入力に失敗しました")
        
        # スクリーンショットを撮影
        print("7. スクリーンショットを撮影中...")
        screenshot_path = browser.take_screenshot("test_mcp_screenshot.png")
        if screenshot_path:
            print(f"✅ スクリーンショットを保存しました: {screenshot_path}")
        else:
            print("❌ スクリーンショットの撮影に失敗しました")
        
        # JavaScriptを実行
        print("8. JavaScriptを実行中...")
        result = browser.execute_javascript("return document.title;")
        print(f"JavaScript実行結果: {result}")
        
        # ページソースの一部を取得
        print("9. ページソースの一部を取得中...")
        page_source = browser.get_page_source()
        print(f"ページソースの長さ: {len(page_source)} 文字")
        
        # ブラウザを閉じる
        print("10. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== Browser MCP テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = test_browser_mcp()
    sys.exit(0 if success else 1)