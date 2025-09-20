#!/usr/bin/env python3
"""
MCPを使用してアプリケーションの構造を分析するスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def analyze_app_structure():
    """アプリケーションの構造を分析"""
    print("=== MCPを使用したアプリケーション構造分析開始 ===")
    
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
        time.sleep(5)
        
        # ページの構造を分析
        print("5. ページの構造を分析中...")
        
        # 全ての要素を検索
        try:
            # ボタン要素を様々なセレクターで検索
            selectors = [
                "button",
                ".stButton",
                ".stButton > button",
                "[data-testid='stButton']",
                "section[data-testid='stSidebar'] button",
                ".main button",
                "div[data-testid='stApp'] button"
            ]
            
            for selector in selectors:
                elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"セレクター '{selector}': {len(elements)} 個の要素が見つかりました")
                
                if elements:
                    for i, element in enumerate(elements[:3]):  # 最初の3個を詳細表示
                        try:
                            tag_name = element.tag_name
                            text = element.text.strip()
                            class_name = element.get_attribute("class")
                            element_id = element.get_attribute("id")
                            
                            print(f"  - 要素 {i+1}: <{tag_name}>")
                            print(f"    テキスト: '{text}'")
                            print(f"    クラス: {class_name}")
                            print(f"    ID: {element_id}")
                            
                        except Exception as e:
                            print(f"  - 要素 {i+1}: 詳細取得エラー - {e}")
            
            # Streamlitの特定要素を検索
            print("\n6. Streamlitの特定要素を検索中...")
            streamlit_elements = [
                "section[data-testid='stSidebar']",
                "div[data-testid='stApp']",
                ".main",
                ".stApp",
                ".stTabs",
                ".stSelectbox",
                ".stTextInput",
                ".stNumberInput"
            ]
            
            for selector in streamlit_elements:
                elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Streamlit要素 '{selector}': {len(elements)} 個が見つかりました")
                
                if elements:
                    element = elements[0]
                    try:
                        is_displayed = element.is_displayed()
                        is_enabled = element.is_enabled()
                        size = element.size
                        location = element.location
                        
                        print(f"  - 表示状態: {is_displayed}")
                        print(f"  - 有効状態: {is_enabled}")
                        print(f"  - サイズ: {size}")
                        print(f"  - 位置: {location}")
                        
                    except Exception as e:
                        print(f"  - 詳細取得エラー: {e}")
            
            # ページのHTMLソースの一部を取得
            print("\n7. ページソースの一部を確認中...")
            page_source = browser.get_page_source()
            
            # ボタン関連のHTMLを検索
            button_keywords = ["button", "stButton", "click", "onclick"]
            for keyword in button_keywords:
                count = page_source.lower().count(keyword.lower())
                print(f"'{keyword}' の出現回数: {count}")
            
            # ページのタイトルとURLを再確認
            print(f"\n8. ページ情報:")
            print(f"タイトル: {browser.get_page_title()}")
            print(f"URL: {browser.get_current_url()}")
            
            # ページの高さと幅を取得
            page_height = browser.driver.execute_script("return document.body.scrollHeight")
            page_width = browser.driver.execute_script("return document.body.scrollWidth")
            print(f"ページサイズ: {page_width} x {page_height}")
            
            # スクロール可能な要素を確認
            scrollable_elements = browser.driver.find_elements(By.CSS_SELECTOR, "*")
            scrollable_count = 0
            for element in scrollable_elements:
                try:
                    if element.size['height'] > 0 and element.size['width'] > 0:
                        scrollable_count += 1
                except:
                    pass
            print(f"スクロール可能な要素数: {scrollable_count}")
            
        except Exception as e:
            print(f"⚠️ 構造分析中にエラーが発生しました: {e}")
        
        # 最終的なスクリーンショットを撮影
        print("\n9. 最終スクリーンショットを撮影中...")
        final_screenshot = browser.take_screenshot("app_final_structure.png")
        if final_screenshot:
            print(f"✅ 最終スクリーンショットを保存しました: {final_screenshot}")
        
        # ブラウザを閉じる
        print("\n10. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用したアプリケーション構造分析完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 構造分析中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = analyze_app_structure()
    sys.exit(0 if success else 1)
