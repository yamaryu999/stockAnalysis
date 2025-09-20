#!/usr/bin/env python3
"""
MCPを使用してボタンの配色を詳しく確認するスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_button_colors():
    """ボタンの配色を詳しく確認"""
    print("=== MCPを使用したボタン配色確認開始 ===")
    
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
        
        # ボタン要素を検索
        print("5. ボタン要素を検索中...")
        
        # メインのボタン（分析実行、結果表示）
        main_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "button.netflix-quick-btn")
        print(f"✅ メインボタン {len(main_buttons)} 個が見つかりました")
        
        # サイドバーのボタン
        sidebar_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "section[data-testid='stSidebar'] button")
        print(f"✅ サイドバーボタン {len(sidebar_buttons)} 個が見つかりました")
        
        # 各ボタンの詳細分析
        for i, button in enumerate(main_buttons):
            try:
                print(f"\n--- メインボタン {i+1} の詳細分析 ---")
                
                # ボタンの基本情報
                button_text = button.text.strip()
                button_class = button.get_attribute("class")
                print(f"テキスト: '{button_text}'")
                print(f"クラス: {button_class}")
                
                # ボタンの位置とサイズ
                location = button.location
                size = button.size
                print(f"位置: x={location['x']}, y={location['y']}")
                print(f"サイズ: width={size['width']}, height={size['height']}")
                
                # ボタンを画面内に表示
                browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                time.sleep(1)
                
                # ボタンの計算されたスタイルを取得
                computed_style = browser.driver.execute_script("""
                    var element = arguments[0];
                    var style = window.getComputedStyle(element);
                    return {
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        borderColor: style.borderColor,
                        borderWidth: style.borderWidth,
                        borderStyle: style.borderStyle,
                        fontSize: style.fontSize,
                        fontWeight: style.fontWeight,
                        fontFamily: style.fontFamily,
                        boxShadow: style.boxShadow,
                        borderRadius: style.borderRadius,
                        padding: style.padding,
                        margin: style.margin,
                        textShadow: style.textShadow,
                        backgroundImage: style.backgroundImage,
                        backgroundSize: style.backgroundSize,
                        backgroundPosition: style.backgroundPosition
                    };
                """, button)
                
                print("--- 計算されたスタイル ---")
                for prop, value in computed_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # ボタンのスクリーンショットを撮影
                print(f"6. ボタン {i+1} のスクリーンショットを撮影中...")
                browser.take_screenshot(f"button_{i+1}_normal.png")
                print(f"✅ ボタン {i+1} の通常状態スクリーンショットを撮影しました")
                
                # ホバー効果をテスト
                print(f"7. ボタン {i+1} のホバー効果をテスト中...")
                
                # ホバー前の状態を記録
                browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));", button)
                time.sleep(1)
                
                # ホバー後のスタイルを取得
                hover_style = browser.driver.execute_script("""
                    var element = arguments[0];
                    var style = window.getComputedStyle(element);
                    return {
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        borderColor: style.borderColor,
                        boxShadow: style.boxShadow,
                        transform: style.transform
                    };
                """, button)
                
                print("--- ホバー時のスタイル ---")
                for prop, value in hover_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # ホバー時のスクリーンショットを撮影
                browser.take_screenshot(f"button_{i+1}_hover.png")
                print(f"✅ ボタン {i+1} のホバー状態スクリーンショットを撮影しました")
                
                # ホバーを解除
                browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseleave', {bubbles: true}));", button)
                time.sleep(1)
                
                # クリック効果をテスト
                print(f"8. ボタン {i+1} のクリック効果をテスト中...")
                button.click()
                time.sleep(2)
                
                # クリック後のスクリーンショットを撮影
                browser.take_screenshot(f"button_{i+1}_clicked.png")
                print(f"✅ ボタン {i+1} のクリック後スクリーンショットを撮影しました")
                
            except Exception as e:
                print(f"⚠️ ボタン {i+1} の分析中にエラー: {e}")
        
        # サイドバーボタンの分析
        for i, button in enumerate(sidebar_buttons[:3]):  # 最初の3個のサイドバーボタンを分析
            try:
                print(f"\n--- サイドバーボタン {i+1} の詳細分析 ---")
                
                # ボタンの基本情報
                button_text = button.text.strip()
                button_class = button.get_attribute("class")
                print(f"テキスト: '{button_text}'")
                print(f"クラス: {button_class}")
                
                # ボタンを画面内に表示
                browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                time.sleep(1)
                
                # ボタンの計算されたスタイルを取得
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
                        boxShadow: style.boxShadow,
                        borderRadius: style.borderRadius
                    };
                """, button)
                
                print("--- サイドバーボタンの計算されたスタイル ---")
                for prop, value in computed_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # サイドバーボタンのスクリーンショットを撮影
                browser.take_screenshot(f"sidebar_button_{i+1}.png")
                print(f"✅ サイドバーボタン {i+1} のスクリーンショットを撮影しました")
                
            except Exception as e:
                print(f"⚠️ サイドバーボタン {i+1} の分析中にエラー: {e}")
        
        # 全体的な配色の確認
        print("\n9. 全体的な配色の確認中...")
        
        # ページ全体のスクリーンショットを撮影
        browser.take_screenshot("app_full_colors.png")
        print("✅ ページ全体のスクリーンショットを撮影しました")
        
        # ブラウザを閉じる
        print("\n10. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用したボタン配色確認完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ ボタン配色確認中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = check_button_colors()
    sys.exit(0 if success else 1)
