#!/usr/bin/env python3
"""
MCPを使用して「リアルタイム」や「スクリーニング」のテキストを検索するスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_realtime_screening():
    """「リアルタイム」や「スクリーニング」のテキストを検索"""
    print("=== MCPを使用した「リアルタイム」「スクリーニング」検索開始 ===")
    
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
        
        # 検索対象のキーワード
        search_keywords = ["リアルタイム", "スクリーニング", "realtime", "screening", "リアル", "スクリーン"]
        
        print("5. キーワード検索中...")
        
        for keyword in search_keywords:
            print(f"\n--- キーワード: '{keyword}' の検索 ---")
            
            try:
                # ページソースからキーワードを検索
                page_source = browser.get_page_source()
                keyword_count = page_source.lower().count(keyword.lower())
                print(f"ページソース内の出現回数: {keyword_count}")
                
                if keyword_count > 0:
                    # キーワードを含む要素を検索
                    elements_with_keyword = browser.driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                    print(f"キーワードを含む要素数: {len(elements_with_keyword)}")
                    
                    for i, element in enumerate(elements_with_keyword[:5]):  # 最初の5個を詳細表示
                        try:
                            tag_name = element.tag_name
                            element_text = element.text.strip()
                            element_class = element.get_attribute("class")
                            element_id = element.get_attribute("id")
                            
                            print(f"  要素 {i+1}:")
                            print(f"    タグ: <{tag_name}>")
                            print(f"    テキスト: '{element_text}'")
                            print(f"    クラス: {element_class}")
                            print(f"    ID: {element_id}")
                            
                            # 要素を画面内に表示
                            browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            time.sleep(1)
                            
                            # 要素のスクリーンショットを撮影
                            screenshot_name = f"keyword_{keyword}_{i+1}.png"
                            browser.take_screenshot(screenshot_name)
                            print(f"    ✅ スクリーンショットを撮影: {screenshot_name}")
                            
                        except Exception as e:
                            print(f"    要素 {i+1} の詳細取得エラー: {e}")
                
            except Exception as e:
                print(f"キーワード '{keyword}' の検索中にエラー: {e}")
        
        # タブやメニューを確認
        print("\n6. タブやメニュー要素を確認中...")
        
        # タブ要素を検索
        tab_selectors = [
            "[data-testid='stTabs']",
            ".stTabs",
            "[role='tab']",
            "[role='tablist']",
            ".tab",
            ".menu",
            ".nav"
        ]
        
        for selector in tab_selectors:
            try:
                elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"タブ要素 '{selector}': {len(elements)} 個が見つかりました")
                    
                    for i, element in enumerate(elements[:3]):  # 最初の3個を確認
                        try:
                            element_text = element.text.strip()
                            print(f"  タブ {i+1}: '{element_text}'")
                            
                            # キーワードが含まれているかチェック
                            for keyword in search_keywords:
                                if keyword.lower() in element_text.lower():
                                    print(f"    ⭐ キーワード '{keyword}' を含むタブです！")
                                    
                                    # タブをクリックして内容を確認
                                    try:
                                        element.click()
                                        time.sleep(2)
                                        
                                        # クリック後のスクリーンショットを撮影
                                        browser.take_screenshot(f"tab_clicked_{keyword}_{i+1}.png")
                                        print(f"    ✅ タブクリック後のスクリーンショットを撮影")
                                        
                                    except Exception as e:
                                        print(f"    タブクリックエラー: {e}")
                            
                        except Exception as e:
                            print(f"  タブ {i+1} の詳細取得エラー: {e}")
                            
            except Exception as e:
                print(f"セレクター '{selector}' の検索中にエラー: {e}")
        
        # セレクトボックスやドロップダウンメニューを確認
        print("\n7. セレクトボックスやドロップダウンメニューを確認中...")
        
        select_selectors = [
            ".stSelectbox",
            "select",
            "[role='combobox']",
            ".dropdown",
            ".menu-item"
        ]
        
        for selector in select_selectors:
            try:
                elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"セレクト要素 '{selector}': {len(elements)} 個が見つかりました")
                    
                    for i, element in enumerate(elements[:3]):  # 最初の3個を確認
                        try:
                            element_text = element.text.strip()
                            print(f"  セレクト {i+1}: '{element_text}'")
                            
                            # キーワードが含まれているかチェック
                            for keyword in search_keywords:
                                if keyword.lower() in element_text.lower():
                                    print(f"    ⭐ キーワード '{keyword}' を含むセレクトです！")
                            
                        except Exception as e:
                            print(f"  セレクト {i+1} の詳細取得エラー: {e}")
                            
            except Exception as e:
                print(f"セレクター '{selector}' の検索中にエラー: {e}")
        
        # ページ全体のスクリーンショットを撮影
        print("\n8. ページ全体のスクリーンショットを撮影中...")
        browser.take_screenshot("realtime_screening_search_result.png")
        print("✅ 検索結果のスクリーンショットを撮影しました")
        
        # 検索結果の要約
        print("\n9. 検索結果の要約:")
        print("✅ ページソース内でキーワードの存在を確認")
        print("✅ キーワードを含む要素の特定")
        print("✅ タブやメニュー要素の確認")
        print("✅ セレクトボックスやドロップダウンメニューの確認")
        
        # ブラウザを閉じる
        print("\n10. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した「リアルタイム」「スクリーニング」検索完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 検索中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = search_realtime_screening()
    sys.exit(0 if success else 1)
