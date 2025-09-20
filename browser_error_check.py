#!/usr/bin/env python3
"""
ブラウザでのエラー確認用スクリプト
MCPブラウザクライアントを使用してアプリケーションのエラーを詳細に確認
"""

import sys
import os
import time
import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver():
    """Chromeドライバーを設定（ヘッドレスモード無効）"""
    chrome_options = Options()
    # ヘッドレスモードを無効にしてブラウザを表示
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chromeドライバーの設定に失敗: {e}")
        return None

def check_browser_console_errors(driver):
    """ブラウザのコンソールエラーをチェック"""
    try:
        # JavaScriptを実行してコンソールログを取得
        logs = driver.get_log('browser')
        if logs:
            print("🔍 ブラウザコンソールエラー:")
            for log in logs:
                if log['level'] in ['SEVERE', 'ERROR']:
                    print(f"  ❌ {log['level']}: {log['message']}")
                elif log['level'] == 'WARNING':
                    print(f"  ⚠️ {log['level']}: {log['message']}")
                else:
                    print(f"  ℹ️ {log['level']}: {log['message']}")
        else:
            print("✅ ブラウザコンソールにエラーはありません")
    except Exception as e:
        print(f"❌ コンソールログの取得に失敗: {e}")

def check_network_errors(driver):
    """ネットワークエラーをチェック"""
    try:
        # JavaScriptを実行してネットワークエラーを取得
        network_logs = driver.get_log('performance')
        if network_logs:
            print("🔍 ネットワークエラー:")
            for log in network_logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    if response['status'] >= 400:
                        print(f"  ❌ HTTP {response['status']}: {response['url']}")
        else:
            print("✅ ネットワークエラーはありません")
    except Exception as e:
        print(f"❌ ネットワークログの取得に失敗: {e}")

def check_streamlit_errors(driver):
    """Streamlit固有のエラーをチェック"""
    try:
        # Streamlitのエラーメッセージを探す
        error_selectors = [
            "[data-testid='stAlert']",
            ".stAlert",
            ".stException",
            ".stError",
            ".stWarning",
            ".stInfo",
            ".stSuccess"
        ]
        
        found_errors = []
        for selector in error_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                if element.is_displayed():
                    text = element.text.strip()
                    if text:
                        found_errors.append(f"{selector}: {text}")
        
        if found_errors:
            print("🔍 Streamlitエラー/アラート:")
            for error in found_errors:
                print(f"  ⚠️ {error}")
        else:
            print("✅ Streamlitエラー/アラートはありません")
            
    except Exception as e:
        print(f"❌ Streamlitエラーチェックに失敗: {e}")

def check_css_loading_errors(driver):
    """CSS読み込みエラーをチェック"""
    try:
        # CSSファイルの読み込み状況をチェック
        css_elements = driver.find_elements(By.TAG_NAME, "link")
        css_errors = []
        
        for css in css_elements:
            if css.get_attribute("rel") == "stylesheet":
                href = css.get_attribute("href")
                if href and "color_theory_design.css" in href:
                    print(f"✅ 色彩学CSSファイルが読み込まれています: {href}")
                elif href:
                    print(f"ℹ️ CSSファイル: {href}")
        
        # インラインスタイルの確認
        style_elements = driver.find_elements(By.TAG_NAME, "style")
        if style_elements:
            print(f"✅ {len(style_elements)}個のインラインスタイルが読み込まれています")
        
    except Exception as e:
        print(f"❌ CSSチェックに失敗: {e}")

def check_javascript_errors(driver):
    """JavaScriptエラーをチェック"""
    try:
        # JavaScriptの実行エラーをチェック
        js_errors = driver.execute_script("""
            return window.console && window.console.error ? 
                   window.console.error.toString() : 'No console.error available';
        """)
        
        # ページ内のJavaScriptエラーをチェック
        js_result = driver.execute_script("""
            var errors = [];
            if (window.onerror) {
                errors.push('onerror handler exists');
            }
            return errors;
        """)
        
        print(f"ℹ️ JavaScript状態: {js_result}")
        
    except Exception as e:
        print(f"❌ JavaScriptチェックに失敗: {e}")

def detailed_error_check(url="http://localhost:8505", timeout=30):
    """詳細なエラーチェックを実行"""
    driver = setup_chrome_driver()
    if not driver:
        return False
    
    try:
        print(f"🌐 アプリケーションにアクセス中: {url}")
        driver.get(url)
        
        # ページの読み込みを待機
        wait = WebDriverWait(driver, timeout)
        
        print("⏳ ページの読み込みを待機中...")
        time.sleep(5)  # 追加の待機時間
        
        # Streamlitのメインコンテンツが読み込まれるまで待機
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main")))
            print("✅ Streamlitアプリケーションが正常に読み込まれました")
        except TimeoutException:
            print("❌ Streamlitアプリケーションの読み込みがタイムアウトしました")
            # タイムアウトでも他のチェックを続行
        
        # ページ情報を表示
        title = driver.title
        print(f"📄 ページタイトル: {title}")
        current_url = driver.current_url
        print(f"🔗 現在のURL: {current_url}")
        
        # 各種エラーチェックを実行
        print("\n" + "="*50)
        print("🔍 詳細エラーチェック開始")
        print("="*50)
        
        check_browser_console_errors(driver)
        print()
        
        check_network_errors(driver)
        print()
        
        check_streamlit_errors(driver)
        print()
        
        check_css_loading_errors(driver)
        print()
        
        check_javascript_errors(driver)
        print()
        
        # スクリーンショットを保存
        screenshot_path = "browser_error_check.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 スクリーンショットを保存しました: {screenshot_path}")
        
        # ページソースの一部を保存（デバッグ用）
        page_source_path = "page_source_debug.html"
        with open(page_source_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"📄 ページソースを保存しました: {page_source_path}")
        
        return True
        
    except WebDriverException as e:
        print(f"❌ WebDriverエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        print("\n⏳ ブラウザを5秒後に閉じます...")
        time.sleep(5)
        driver.quit()

def main():
    """メイン関数"""
    print("=== ブラウザエラー詳細チェック ===")
    
    # 複数のポートでアプリケーションをチェック
    ports = [8501, 8502, 8503, 8504, 8505, 8506]
    
    for port in ports:
        url = f"http://localhost:{port}"
        print(f"\n🔍 ポート {port} を詳細チェック中...")
        
        if detailed_error_check(url, timeout=15):
            print(f"✅ ポート {port} でアプリケーションが動作しています")
            break
        else:
            print(f"❌ ポート {port} でアプリケーションが見つかりません")
    
    print("\n=== ブラウザエラーチェック完了 ===")

if __name__ == "__main__":
    main()