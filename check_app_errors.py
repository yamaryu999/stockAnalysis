#!/usr/bin/env python3
"""
Streamlitアプリケーションのエラーチェック用スクリプト
MCPブラウザクライアントを使用してアプリケーションの状態を確認
"""

import sys
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver():
    """Chromeドライバーを設定"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモード
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chromeドライバーの設定に失敗: {e}")
        return None

def check_streamlit_app(url="http://localhost:8504", timeout=30):
    """Streamlitアプリケーションの状態をチェック"""
    driver = setup_chrome_driver()
    if not driver:
        return False
    
    try:
        print(f"アプリケーションにアクセス中: {url}")
        driver.get(url)
        
        # ページの読み込みを待機
        wait = WebDriverWait(driver, timeout)
        
        # Streamlitのメインコンテンツが読み込まれるまで待機
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main")))
            print("✅ Streamlitアプリケーションが正常に読み込まれました")
        except TimeoutException:
            print("❌ Streamlitアプリケーションの読み込みがタイムアウトしました")
            return False
        
        # エラーメッセージをチェック
        error_elements = driver.find_elements(By.CLASS_NAME, "stAlert")
        if error_elements:
            print("⚠️ アラートメッセージが見つかりました:")
            for alert in error_elements:
                print(f"  - {alert.text}")
        
        # エラーメッセージをチェック（Streamlitのエラー表示）
        error_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stAlert']")
        if error_elements:
            print("⚠️ Streamlitアラートが見つかりました:")
            for alert in error_elements:
                print(f"  - {alert.text}")
        
        # ページタイトルを取得
        title = driver.title
        print(f"📄 ページタイトル: {title}")
        
        # 現在のURLを取得
        current_url = driver.current_url
        print(f"🔗 現在のURL: {current_url}")
        
        # スクリーンショットを保存
        screenshot_path = "app_error_check.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 スクリーンショットを保存しました: {screenshot_path}")
        
        # ページソースをチェック（エラーメッセージの検索）
        page_source = driver.page_source
        error_keywords = ["error", "Error", "ERROR", "exception", "Exception", "traceback", "Traceback"]
        found_errors = []
        
        for keyword in error_keywords:
            if keyword in page_source:
                # エラーキーワードの前後のコンテキストを取得
                start = page_source.find(keyword)
                if start != -1:
                    context = page_source[max(0, start-100):start+200]
                    found_errors.append(f"{keyword}: {context}")
        
        if found_errors:
            print("❌ ページソースにエラーが検出されました:")
            for error in found_errors[:5]:  # 最初の5つのエラーのみ表示
                print(f"  - {error}")
        else:
            print("✅ ページソースにエラーは検出されませんでした")
        
        return True
        
    except WebDriverException as e:
        print(f"❌ WebDriverエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        driver.quit()

def main():
    """メイン関数"""
    print("=== Streamlitアプリケーション エラーチェック ===")
    
    # 複数のポートでアプリケーションをチェック
    ports = [8501, 8502, 8503, 8504, 8505]
    
    for port in ports:
        url = f"http://localhost:{port}"
        print(f"\n🔍 ポート {port} をチェック中...")
        
        if check_streamlit_app(url, timeout=10):
            print(f"✅ ポート {port} でアプリケーションが動作しています")
            break
        else:
            print(f"❌ ポート {port} でアプリケーションが見つかりません")
    
    print("\n=== エラーチェック完了 ===")

if __name__ == "__main__":
    main()