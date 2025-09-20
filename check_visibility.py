#!/usr/bin/env python3
"""
高視認性デザインの確認用スクリプト
MCPブラウザクライアントを使用して視認性を詳細に確認
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

def check_visibility_improvements(driver):
    """視認性の改善をチェック"""
    try:
        print("🔍 視認性改善チェック:")
        
        # フォントサイズの確認
        main_header = driver.find_element(By.CLASS_NAME, "main-header")
        header_h1 = main_header.find_element(By.TAG_NAME, "h1")
        header_font_size = driver.execute_script("return window.getComputedStyle(arguments[0]).fontSize", header_h1)
        print(f"  📏 メインヘッダーフォントサイズ: {header_font_size}")
        
        # コントラスト比の確認
        header_color = driver.execute_script("return window.getComputedStyle(arguments[0]).color", header_h1)
        header_bg = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", main_header)
        print(f"  🎨 ヘッダーテキストカラー: {header_color}")
        print(f"  🎨 ヘッダー背景カラー: {header_bg}")
        
        # メトリックカードの確認
        metric_cards = driver.find_elements(By.CLASS_NAME, "metric-card")
        if metric_cards:
            print(f"  📊 メトリックカード数: {len(metric_cards)}")
            for i, card in enumerate(metric_cards[:4]):  # 最初の4つをチェック
                card_padding = driver.execute_script("return window.getComputedStyle(arguments[0]).padding", card)
                card_font_size = driver.execute_script("return window.getComputedStyle(arguments[0]).fontSize", card)
                print(f"    📦 カード{i+1} パディング: {card_padding}")
                print(f"    📦 カード{i+1} フォントサイズ: {card_font_size}")
        
        # ボタンの確認
        buttons = driver.find_elements(By.CSS_SELECTOR, ".stButton > button")
        if buttons:
            button = buttons[0]
            button_height = driver.execute_script("return window.getComputedStyle(arguments[0]).height", button)
            button_font_size = driver.execute_script("return window.getComputedStyle(arguments[0]).fontSize", button)
            print(f"  🔘 ボタンの高さ: {button_height}")
            print(f"  🔘 ボタンのフォントサイズ: {button_font_size}")
        
        # タブの確認
        tabs = driver.find_elements(By.CSS_SELECTOR, ".stTabs [data-baseweb='tab']")
        if tabs:
            tab = tabs[0]
            tab_height = driver.execute_script("return window.getComputedStyle(arguments[0]).height", tab)
            tab_font_size = driver.execute_script("return window.getComputedStyle(arguments[0]).fontSize", tab)
            print(f"  📑 タブの高さ: {tab_height}")
            print(f"  📑 タブのフォントサイズ: {tab_font_size}")
        
        print("✅ 視認性チェック完了")
        
    except Exception as e:
        print(f"❌ 視認性チェックに失敗: {e}")

def check_css_loading(driver):
    """CSS読み込み状況をチェック"""
    try:
        print("🔍 CSS読み込み状況:")
        
        # CSSファイルの確認
        css_elements = driver.find_elements(By.TAG_NAME, "link")
        css_files = []
        for css in css_elements:
            if css.get_attribute("rel") == "stylesheet":
                href = css.get_attribute("href")
                if href:
                    css_files.append(href)
        
        print(f"  📄 読み込まれたCSSファイル数: {len(css_files)}")
        for css_file in css_files:
            print(f"    - {css_file}")
        
        # インラインスタイルの確認
        style_elements = driver.find_elements(By.TAG_NAME, "style")
        print(f"  📄 インラインスタイル数: {len(style_elements)}")
        
        # 高視認性CSSの確認
        high_visibility_css = any("improved_visibility_design.css" in css for css in css_files)
        if high_visibility_css:
            print("  ✅ 高視認性デザインCSSが読み込まれています")
        else:
            print("  ⚠️ 高視認性デザインCSSが見つかりません")
        
    except Exception as e:
        print(f"❌ CSSチェックに失敗: {e}")

def check_accessibility_features(driver):
    """アクセシビリティ機能をチェック"""
    try:
        print("🔍 アクセシビリティ機能:")
        
        # フォーカス可能要素の確認
        focusable_elements = driver.find_elements(By.CSS_SELECTOR, "button, input, select, textarea, a[href], [tabindex]")
        print(f"  ⌨️ フォーカス可能要素数: {len(focusable_elements)}")
        
        # アリアラベルの確認
        aria_elements = driver.find_elements(By.CSS_SELECTOR, "[aria-label], [aria-labelledby], [aria-describedby]")
        print(f"  ♿ ARIAラベル要素数: {len(aria_elements)}")
        
        # コントラスト比の確認（簡易版）
        main_text = driver.find_element(By.CLASS_NAME, "stApp")
        text_color = driver.execute_script("return window.getComputedStyle(arguments[0]).color", main_text)
        bg_color = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", main_text)
        print(f"  🎨 メインテキストカラー: {text_color}")
        print(f"  🎨 メイン背景カラー: {bg_color}")
        
        print("✅ アクセシビリティチェック完了")
        
    except Exception as e:
        print(f"❌ アクセシビリティチェックに失敗: {e}")

def detailed_visibility_check(url="http://localhost:8510", timeout=30):
    """詳細な視認性チェックを実行"""
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
        
        # 各種チェックを実行
        print("\n" + "="*60)
        print("🔍 高視認性デザイン詳細チェック")
        print("="*60)
        
        check_css_loading(driver)
        print()
        
        check_visibility_improvements(driver)
        print()
        
        check_accessibility_features(driver)
        print()
        
        # スクリーンショットを保存
        screenshot_path = "visibility_check.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 スクリーンショットを保存しました: {screenshot_path}")
        
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
    print("=== 高視認性デザイン確認 ===")
    
    # ポート8510でアプリケーションをチェック
    url = "http://localhost:8510"
    print(f"\n🔍 ポート 8510 を詳細チェック中...")
    
    if detailed_visibility_check(url, timeout=15):
        print(f"✅ ポート 8510 でアプリケーションが動作しています")
    else:
        print(f"❌ ポート 8510 でアプリケーションが見つかりません")
    
    print("\n=== 高視認性デザイン確認完了 ===")

if __name__ == "__main__":
    main()