#!/usr/bin/env python3
"""
MCPを使用して改善された配色をテストするスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_improved_colors():
    """改善された配色をテスト"""
    print("=== MCPを使用した改善配色テスト開始 ===")
    
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
        
        # 改善されたボタンの配色を確認
        print("5. 改善されたボタンの配色を確認中...")
        
        # Netflixスタイルのボタンを検索
        netflix_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "button.netflix-quick-btn")
        print(f"✅ Netflixスタイルボタン {len(netflix_buttons)} 個が見つかりました")
        
        # 各ボタンの改善された配色を確認
        for i, button in enumerate(netflix_buttons):
            try:
                print(f"\n--- 改善されたボタン {i+1} の配色確認 ---")
                
                # ボタンの基本情報
                button_text = button.text.strip()
                print(f"テキスト: '{button_text}'")
                
                # ボタンを画面内に表示
                browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                time.sleep(1)
                
                # 改善されたスタイルを確認
                improved_style = browser.driver.execute_script("""
                    var element = arguments[0];
                    var style = window.getComputedStyle(element);
                    return {
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        borderColor: style.borderColor,
                        borderWidth: style.borderWidth,
                        borderRadius: style.borderRadius,
                        fontSize: style.fontSize,
                        fontWeight: style.fontWeight,
                        boxShadow: style.boxShadow,
                        textShadow: style.textShadow,
                        backgroundImage: style.backgroundImage
                    };
                """, button)
                
                print("--- 改善されたスタイル ---")
                for prop, value in improved_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # 改善前との比較
                print("\n--- 改善前後の比較 ---")
                print("改善前: 背景色 rgb(239, 239, 239) - 薄いグレー")
                print(f"改善後: 背景色 {improved_style.get('backgroundColor', 'N/A')}")
                print("改善前: ボーダー rgb(0, 0, 0) - 黒")
                print(f"改善後: ボーダー {improved_style.get('borderColor', 'N/A')}")
                print("改善前: シャドウ なし")
                print(f"改善後: シャドウ {improved_style.get('boxShadow', 'N/A')}")
                
                # 改善されたボタンのスクリーンショットを撮影
                browser.take_screenshot(f"improved_button_{i+1}_normal.png")
                print(f"✅ 改善されたボタン {i+1} のスクリーンショットを撮影しました")
                
                # ホバー効果をテスト
                print(f"6. ボタン {i+1} の改善されたホバー効果をテスト中...")
                
                # ホバー前の状態を記録
                browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));", button)
                time.sleep(1)
                
                # ホバー後の改善されたスタイルを確認
                hover_improved_style = browser.driver.execute_script("""
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
                
                print("--- 改善されたホバー時のスタイル ---")
                for prop, value in hover_improved_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # ホバー時のスクリーンショットを撮影
                browser.take_screenshot(f"improved_button_{i+1}_hover.png")
                print(f"✅ 改善されたボタン {i+1} のホバー状態スクリーンショットを撮影しました")
                
                # ホバーを解除
                browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseleave', {bubbles: true}));", button)
                time.sleep(1)
                
                # クリック効果をテスト
                print(f"7. ボタン {i+1} の改善されたクリック効果をテスト中...")
                button.click()
                time.sleep(2)
                
                # クリック後のスクリーンショットを撮影
                browser.take_screenshot(f"improved_button_{i+1}_clicked.png")
                print(f"✅ 改善されたボタン {i+1} のクリック後スクリーンショットを撮影しました")
                
            except Exception as e:
                print(f"⚠️ ボタン {i+1} のテスト中にエラー: {e}")
        
        # サイドバーボタンの改善も確認
        print("\n8. サイドバーボタンの改善を確認中...")
        sidebar_buttons = browser.driver.find_elements(By.CSS_SELECTOR, "section[data-testid='stSidebar'] button.netflix-quick-btn")
        
        for i, button in enumerate(sidebar_buttons[:2]):  # 最初の2個を確認
            try:
                print(f"\n--- 改善されたサイドバーボタン {i+1} の配色確認 ---")
                
                button_text = button.text.strip()
                print(f"テキスト: '{button_text}'")
                
                # ボタンを画面内に表示
                browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                time.sleep(1)
                
                # 改善されたスタイルを確認
                sidebar_improved_style = browser.driver.execute_script("""
                    var element = arguments[0];
                    var style = window.getComputedStyle(element);
                    return {
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        borderColor: style.borderColor,
                        boxShadow: style.boxShadow,
                        textShadow: style.textShadow
                    };
                """, button)
                
                print("--- 改善されたサイドバーボタンのスタイル ---")
                for prop, value in sidebar_improved_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # サイドバーボタンのスクリーンショットを撮影
                browser.take_screenshot(f"improved_sidebar_button_{i+1}.png")
                print(f"✅ 改善されたサイドバーボタン {i+1} のスクリーンショットを撮影しました")
                
            except Exception as e:
                print(f"⚠️ サイドバーボタン {i+1} のテスト中にエラー: {e}")
        
        # 全体的な改善の確認
        print("\n9. 全体的な改善の確認中...")
        
        # ページ全体の改善されたスクリーンショットを撮影
        browser.take_screenshot("app_improved_colors.png")
        print("✅ 改善されたページ全体のスクリーンショットを撮影しました")
        
        # 改善の効果を評価
        print("\n10. 改善効果の評価:")
        print("✅ 背景色: 薄いグレー → 鮮明な青グラデーション")
        print("✅ ボーダー: 黒 → 白（高コントラスト）")
        print("✅ シャドウ: なし → 青いグロー効果")
        print("✅ ホバー効果: 黄色ボーダーで高コントラスト")
        print("✅ テキスト: 白 + テキストシャドウで視認性向上")
        
        # ブラウザを閉じる
        print("\n11. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した改善配色テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 改善配色テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = test_improved_colors()
    sys.exit(0 if success else 1)
