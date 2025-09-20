#!/usr/bin/env python3
"""
MCPを使用してアプリケーションの詳細な配色分析を行うスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def detailed_color_analysis():
    """詳細な配色分析を実行"""
    print("=== MCPを使用した詳細配色分析開始 ===")
    
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
        
        # 全てのボタン要素を探す
        print("5. ボタン要素を検索中...")
        try:
            # メインコンテナのボタン
            main_buttons = browser.driver.find_elements(By.CSS_SELECTOR, ".main .stButton > button")
            print(f"✅ メインコンテナに {len(main_buttons)} 個のボタンが見つかりました")
            
            # サイドバーのボタン
            sidebar_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "section[data-testid='stSidebar'] .stButton > button")
            print(f"✅ サイドバーに {len(sidebar_buttons)} 個のボタンが見つかりました")
            
            # 全てのボタン
            all_buttons = browser.driver.find_elements(By.CSS_SELECTOR, ".stButton > button")
            print(f"✅ 合計 {len(all_buttons)} 個のボタンが見つかりました")
            
            # ボタンの詳細情報を取得
            for i, button in enumerate(all_buttons[:5]):  # 最初の5個のボタンを分析
                try:
                    button_text = button.text.strip()
                    button_class = button.get_attribute("class")
                    button_style = button.get_attribute("style")
                    
                    print(f"\n--- ボタン {i+1} の詳細 ---")
                    print(f"テキスト: '{button_text}'")
                    print(f"クラス: {button_class}")
                    print(f"スタイル: {button_style}")
                    
                    # ボタンの位置とサイズを取得
                    location = button.location
                    size = button.size
                    print(f"位置: x={location['x']}, y={location['y']}")
                    print(f"サイズ: width={size['width']}, height={size['height']}")
                    
                except Exception as e:
                    print(f"⚠️ ボタン {i+1} の詳細取得中にエラー: {e}")
            
            # メインボタンをクリックしてホバー効果を確認
            if main_buttons:
                print("\n6. メインボタンのホバー効果を確認中...")
                main_button = main_buttons[0]
                
                # ボタンにホバー
                browser.driver.execute_script("arguments[0].scrollIntoView(true);", main_button)
                time.sleep(1)
                
                # ホバー前のスクリーンショット
                browser.take_screenshot("button_before_hover.png")
                print("✅ ホバー前のスクリーンショットを撮影しました")
                
                # ホバー効果をシミュレート
                browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", main_button)
                time.sleep(1)
                
                # ホバー後のスクリーンショット
                browser.take_screenshot("button_after_hover.png")
                print("✅ ホバー後のスクリーンショットを撮影しました")
                
                # ボタンをクリック
                print("7. メインボタンをクリック中...")
                main_button.click()
                time.sleep(2)
                
                # クリック後のスクリーンショット
                browser.take_screenshot("button_after_click.png")
                print("✅ クリック後のスクリーンショットを撮影しました")
            
            # サイドバーボタンをクリック
            if sidebar_buttons:
                print("\n8. サイドバーボタンのホバー効果を確認中...")
                sidebar_button = sidebar_buttons[0]
                
                # ボタンにホバー
                browser.driver.execute_script("arguments[0].scrollIntoView(true);", sidebar_button)
                time.sleep(1)
                
                # ホバー前のスクリーンショット
                browser.take_screenshot("sidebar_button_before_hover.png")
                print("✅ サイドバーボタンのホバー前スクリーンショットを撮影しました")
                
                # ホバー効果をシミュレート
                browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", sidebar_button)
                time.sleep(1)
                
                # ホバー後のスクリーンショット
                browser.take_screenshot("sidebar_button_after_hover.png")
                print("✅ サイドバーボタンのホバー後スクリーンショットを撮影しました")
                
                # ボタンをクリック
                print("9. サイドバーボタンをクリック中...")
                sidebar_button.click()
                time.sleep(2)
                
                # クリック後のスクリーンショット
                browser.take_screenshot("sidebar_button_after_click.png")
                print("✅ サイドバーボタンのクリック後スクリーンショットを撮影しました")
            
        except Exception as e:
            print(f"⚠️ ボタン分析中にエラーが発生しました: {e}")
        
        # CSSスタイルの確認
        print("\n10. CSSスタイルを確認中...")
        try:
            # ボタンの計算されたスタイルを取得
            if all_buttons:
                button = all_buttons[0]
                computed_style = browser.driver.execute_script("""
                    var element = arguments[0];
                    var style = window.getComputedStyle(element);
                    return {
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        borderColor: style.borderColor,
                        borderWidth: style.borderWidth,
                        fontSize: style.fontSize,
                        fontWeight: style.fontWeight,
                        boxShadow: style.boxShadow
                    };
                """, button)
                
                print("--- ボタンの計算されたスタイル ---")
                for prop, value in computed_style.items():
                    print(f"{prop}: {value}")
        except Exception as e:
            print(f"⚠️ CSSスタイル確認中にエラー: {e}")
        
        # ブラウザを閉じる
        print("\n11. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した詳細配色分析完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 詳細配色分析中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = detailed_color_analysis()
    sys.exit(0 if success else 1)
