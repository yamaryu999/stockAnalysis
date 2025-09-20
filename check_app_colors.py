#!/usr/bin/env python3
"""
MCPを使用してアプリケーションの配色を確認するスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By

def check_app_colors():
    """アプリケーションの配色を確認"""
    print("=== MCPを使用した配色確認開始 ===")
    
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
        
        # アプリケーションに移動
        print("3. アプリケーションに移動中...")
        app_url = "http://localhost:8501"
        if browser.navigate_to(app_url):
            print("✅ アプリケーションに正常に移動しました")
        else:
            print("❌ アプリケーションへの移動に失敗しました")
            return False
        
        # ページの読み込みを待機
        print("4. ページの読み込みを待機中...")
        time.sleep(3)
        
        # ページタイトルを取得
        title = browser.get_page_title()
        print(f"5. ページタイトル: {title}")
        
        # 現在のURLを取得
        current_url = browser.get_current_url()
        print(f"6. 現在のURL: {current_url}")
        
        # メインページのスクリーンショットを撮影
        print("7. メインページのスクリーンショットを撮影中...")
        main_screenshot = browser.take_screenshot("app_main_colors.png")
        if main_screenshot:
            print(f"✅ メインページのスクリーンショットを保存しました: {main_screenshot}")
        else:
            print("❌ メインページのスクリーンショットの撮影に失敗しました")
        
        # ページを少しスクロールしてボタンエリアを確認
        print("8. ページをスクロールしてボタンエリアを確認中...")
        browser.execute_javascript("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # スクロール後のスクリーンショットを撮影
        print("9. スクロール後のスクリーンショットを撮影中...")
        scroll_screenshot = browser.take_screenshot("app_scroll_colors.png")
        if scroll_screenshot:
            print(f"✅ スクロール後のスクリーンショットを保存しました: {scroll_screenshot}")
        else:
            print("❌ スクロール後のスクリーンショットの撮影に失敗しました")
        
        # サイドバーのボタンを探してクリック
        print("10. サイドバーのボタンを確認中...")
        try:
            # サイドバーのボタン要素を探す
            sidebar_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "section[data-testid='stSidebar'] .stButton > button")
            if sidebar_buttons:
                print(f"✅ サイドバーに {len(sidebar_buttons)} 個のボタンが見つかりました")
                
                # 最初のボタンをクリック
                if len(sidebar_buttons) > 0:
                    print("11. 最初のサイドバーボタンをクリック中...")
                    sidebar_buttons[0].click()
                    time.sleep(2)
                    
                    # クリック後のスクリーンショットを撮影
                    print("12. クリック後のスクリーンショットを撮影中...")
                    click_screenshot = browser.take_screenshot("app_click_colors.png")
                    if click_screenshot:
                        print(f"✅ クリック後のスクリーンショットを保存しました: {click_screenshot}")
                    else:
                        print("❌ クリック後のスクリーンショットの撮影に失敗しました")
            else:
                print("⚠️ サイドバーのボタンが見つかりませんでした")
        except Exception as e:
            print(f"⚠️ サイドバーボタンの確認中にエラーが発生しました: {e}")
        
        # ページソースの一部を取得してボタンスタイルを確認
        print("13. ページソースからボタンスタイルを確認中...")
        page_source = browser.get_page_source()
        if "stButton" in page_source:
            print("✅ ボタン要素がページに存在します")
        else:
            print("⚠️ ボタン要素が見つかりませんでした")
        
        # ブラウザを閉じる
        print("14. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した配色確認完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 配色確認中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = check_app_colors()
    sys.exit(0 if success else 1)
