#!/usr/bin/env python3
"""
MCPを使用して「分析実行」ボタンの問題をデバッグするスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def debug_analysis_button():
    """「分析実行」ボタンの問題をデバッグ"""
    print("=== MCPを使用した「分析実行」ボタンデバッグ開始 ===")
    
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
        
        # 初期状態のスクリーンショットを撮影
        print("5. 初期状態のスクリーンショットを撮影中...")
        browser.take_screenshot("debug_initial_state.png")
        print("✅ 初期状態のスクリーンショットを撮影しました")
        
        # 「分析実行」ボタンを検索
        print("\n6. 「分析実行」ボタンを検索中...")
        
        # 複数のセレクターでボタンを検索
        button_selectors = [
            "button:contains('分析実行')",
            "button:contains('🚀 分析実行')",
            ".netflix-quick-btn:contains('分析実行')",
            ".netflix-quick-btn:contains('🚀 分析実行')",
            "button[class*='netflix-quick-btn']",
            "button[class*='stButton']",
            "button"
        ]
        
        analysis_button = None
        for selector in button_selectors:
            try:
                if ":contains" in selector:
                    # XPathを使用してテキストを含む要素を検索
                    xpath = f"//button[contains(text(), '分析実行')]"
                    elements = browser.driver.find_elements(By.XPATH, xpath)
                else:
                    elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                
                print(f"セレクター '{selector}': {len(elements)} 個の要素が見つかりました")
                
                for element in elements:
                    try:
                        element_text = element.text.strip()
                        element_class = element.get_attribute("class")
                        is_enabled = element.is_enabled()
                        is_displayed = element.is_displayed()
                        
                        print(f"  要素: '{element_text}'")
                        print(f"    クラス: {element_class}")
                        print(f"    有効: {is_enabled}")
                        print(f"    表示: {is_displayed}")
                        
                        if "分析実行" in element_text and is_enabled and is_displayed:
                            analysis_button = element
                            print(f"    ✅ 「分析実行」ボタンを見つけました！")
                            break
                    except Exception as e:
                        print(f"    要素の詳細取得エラー: {e}")
                
                if analysis_button:
                    break
                    
            except Exception as e:
                print(f"セレクター '{selector}' の検索中にエラー: {e}")
        
        if not analysis_button:
            print("❌ 「分析実行」ボタンが見つかりませんでした")
            
            # 全てのボタンをリストアップ
            print("\n7. 全てのボタンをリストアップ中...")
            all_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "button")
            print(f"発見されたボタン数: {len(all_buttons)}")
            
            for i, button in enumerate(all_buttons):
                try:
                    button_text = button.text.strip()
                    button_class = button.get_attribute("class")
                    is_enabled = button.is_enabled()
                    is_displayed = button.is_displayed()
                    
                    print(f"  ボタン {i+1}: '{button_text}'")
                    print(f"    クラス: {button_class}")
                    print(f"    有効: {is_enabled}")
                    print(f"    表示: {is_displayed}")
                except Exception as e:
                    print(f"  ボタン {i+1} の詳細取得エラー: {e}")
            
            return False
        
        # ボタンの詳細情報を取得
        print("\n8. 「分析実行」ボタンの詳細情報を取得中...")
        
        button_text = analysis_button.text.strip()
        button_class = analysis_button.get_attribute("class")
        button_id = analysis_button.get_attribute("id")
        button_type = analysis_button.get_attribute("type")
        is_enabled = analysis_button.is_enabled()
        is_displayed = analysis_button.is_displayed()
        button_location = analysis_button.location
        button_size = analysis_button.size
        
        print(f"ボタンテキスト: '{button_text}'")
        print(f"ボタンクラス: {button_class}")
        print(f"ボタンID: {button_id}")
        print(f"ボタンタイプ: {button_type}")
        print(f"有効状態: {is_enabled}")
        print(f"表示状態: {is_displayed}")
        print(f"位置: x={button_location['x']}, y={button_location['y']}")
        print(f"サイズ: width={button_size['width']}, height={button_size['height']}")
        
        # ボタンを画面内に表示
        print("\n9. ボタンを画面内に表示中...")
        browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", analysis_button)
        time.sleep(2)
        
        # ボタンのスクリーンショットを撮影
        browser.take_screenshot("debug_button_before_click.png")
        print("✅ ボタンのスクリーンショットを撮影しました")
        
        # ボタンのスタイルを確認
        print("\n10. ボタンのスタイルを確認中...")
        try:
            styles = browser.execute_javascript(
                "var elem = arguments[0];"
                "var style = window.getComputedStyle(elem);"
                "return {"
                "backgroundColor: style.backgroundColor,"
                "color: style.color,"
                "border: style.border,"
                "cursor: style.cursor,"
                "pointerEvents: style.pointerEvents,"
                "opacity: style.opacity,"
                "visibility: style.visibility,"
                "display: style.display,"
                "position: style.position,"
                "zIndex: style.zIndex"
                "};", analysis_button
            )
            
            print("--- ボタンのスタイル ---")
            for key, value in styles.items():
                print(f"{key}: {value}")
                
        except Exception as e:
            print(f"スタイル取得エラー: {e}")
        
        # ボタンのクリックを試行
        print("\n11. ボタンのクリックを試行中...")
        
        try:
            # 通常のクリック
            print("通常のクリックを試行中...")
            analysis_button.click()
            time.sleep(3)
            
            # クリック後のスクリーンショット
            browser.take_screenshot("debug_button_after_normal_click.png")
            print("✅ 通常クリック後のスクリーンショットを撮影しました")
            
        except ElementClickInterceptedException as e:
            print(f"❌ クリックが遮断されました: {e}")
            
            # JavaScriptクリックを試行
            print("JavaScriptクリックを試行中...")
            try:
                browser.driver.execute_script("arguments[0].click();", analysis_button)
                time.sleep(3)
                
                # JavaScriptクリック後のスクリーンショット
                browser.take_screenshot("debug_button_after_js_click.png")
                print("✅ JavaScriptクリック後のスクリーンショットを撮影しました")
                
            except Exception as e:
                print(f"❌ JavaScriptクリックも失敗: {e}")
                
                # ActionChainsクリックを試行
                print("ActionChainsクリックを試行中...")
                try:
                    ActionChains(browser.driver).move_to_element(analysis_button).click().perform()
                    time.sleep(3)
                    
                    # ActionChainsクリック後のスクリーンショット
                    browser.take_screenshot("debug_button_after_actionchains_click.png")
                    print("✅ ActionChainsクリック後のスクリーンショットを撮影しました")
                    
                except Exception as e:
                    print(f"❌ ActionChainsクリックも失敗: {e}")
        
        except Exception as e:
            print(f"❌ クリック中にエラーが発生: {e}")
        
        # ページの状態を確認
        print("\n12. ページの状態を確認中...")
        
        # 現在のURLを確認
        current_url = browser.get_current_url()
        print(f"現在のURL: {current_url}")
        
        # ページタイトルを確認
        page_title = browser.get_page_title()
        print(f"ページタイトル: {page_title}")
        
        # エラーメッセージを検索
        print("\n13. エラーメッセージを検索中...")
        error_selectors = [
            ".error",
            ".alert",
            ".warning",
            ".stAlert",
            "[data-testid='stAlert']",
            ".stException",
            "[data-testid='stException']"
        ]
        
        for selector in error_selectors:
            try:
                error_elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                if error_elements:
                    print(f"エラー要素 '{selector}': {len(error_elements)} 個が見つかりました")
                    for i, error_element in enumerate(error_elements):
                        try:
                            error_text = error_element.text.strip()
                            if error_text:
                                print(f"  エラー {i+1}: {error_text}")
                        except Exception as e:
                            print(f"  エラー {i+1} のテキスト取得エラー: {e}")
            except Exception as e:
                print(f"エラーセレクター '{selector}' の検索中にエラー: {e}")
        
        # 最終状態のスクリーンショットを撮影
        print("\n14. 最終状態のスクリーンショットを撮影中...")
        browser.take_screenshot("debug_final_state.png")
        print("✅ 最終状態のスクリーンショットを撮影しました")
        
        # デバッグ結果の要約
        print("\n15. デバッグ結果の要約:")
        print("✅ ボタンの検索: 成功")
        print("✅ ボタンの状態確認: 完了")
        print("✅ クリック試行: 完了")
        print("✅ エラーメッセージ検索: 完了")
        print("✅ スクリーンショット撮影: 完了")
        
        # ブラウザを閉じる
        print("\n16. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した「分析実行」ボタンデバッグ完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ デバッグ中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = debug_analysis_button()
    sys.exit(0 if success else 1)
