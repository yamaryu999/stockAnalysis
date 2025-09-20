#!/usr/bin/env python3
"""
MCPを使用してアプリケーション内の全てのボタンを特定するスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_all_buttons():
    """アプリケーション内の全てのボタンを特定"""
    print("=== MCPを使用した全ボタン特定開始 ===")
    
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
        
        # 全てのボタン要素を検索
        print("5. 全てのボタン要素を検索中...")
        
        # 様々なセレクターでボタンを検索
        button_selectors = [
            "button",
            ".stButton",
            ".stButton > button",
            "[data-testid='stButton']",
            "button[class*='st-']",
            "button[class*='netflix']",
            "button[class*='btn']",
            ".main button",
            "section[data-testid='stSidebar'] button",
            "div[data-testid='stApp'] button"
        ]
        
        all_buttons = []
        button_info = {}
        
        for selector in button_selectors:
            try:
                elements = browser.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"セレクター '{selector}': {len(elements)} 個の要素が見つかりました")
                
                for i, element in enumerate(elements):
                    try:
                        button_text = element.text.strip()
                        button_class = element.get_attribute("class")
                        element_id = element.get_attribute("id")
                        tag_name = element.tag_name
                        
                        # ボタンの情報を記録
                        button_key = f"{selector}_{i}"
                        button_info[button_key] = {
                            'text': button_text,
                            'class': button_class,
                            'id': element_id,
                            'tag': tag_name,
                            'selector': selector,
                            'element': element
                        }
                        
                        # テキストが含まれるボタンのみを詳細表示
                        if button_text and len(button_text) > 0:
                            print(f"  - ボタン: '{button_text}'")
                            print(f"    クラス: {button_class}")
                            print(f"    ID: {element_id}")
                            print(f"    タグ: {tag_name}")
                            
                            # 特定のキーワードを含むボタンを特定
                            keywords = ["リアルタイム", "スクリーニング", "分析", "結果", "実行", "表示", "開始", "停止", "更新", "検索"]
                            for keyword in keywords:
                                if keyword in button_text:
                                    print(f"    ⭐ キーワード '{keyword}' を含むボタンです！")
                                    all_buttons.append({
                                        'text': button_text,
                                        'class': button_class,
                                        'id': element_id,
                                        'keyword': keyword,
                                        'element': element
                                    })
                            print()
                        
                    except Exception as e:
                        print(f"  - 要素 {i} の詳細取得エラー: {e}")
                        
            except Exception as e:
                print(f"セレクター '{selector}' の検索中にエラー: {e}")
        
        # 特定されたボタンの詳細分析
        print(f"\n6. 特定されたボタン {len(all_buttons)} 個の詳細分析:")
        
        for i, button_data in enumerate(all_buttons):
            try:
                print(f"\n--- ボタン {i+1}: '{button_data['text']}' ---")
                print(f"キーワード: {button_data['keyword']}")
                print(f"クラス: {button_data['class']}")
                print(f"ID: {button_data['id']}")
                
                element = button_data['element']
                
                # ボタンを画面内に表示
                browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                
                # ボタンの現在のスタイルを取得
                current_style = browser.driver.execute_script("""
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
                        backgroundImage: style.backgroundImage,
                        padding: style.padding,
                        margin: style.margin
                    };
                """, element)
                
                print("--- 現在のスタイル ---")
                for prop, value in current_style.items():
                    if value and value != 'none' and value != 'normal':
                        print(f"{prop}: {value}")
                
                # ボタンのスクリーンショットを撮影
                screenshot_name = f"button_{button_data['keyword']}_{i+1}.png"
                browser.take_screenshot(screenshot_name)
                print(f"✅ スクリーンショットを撮影しました: {screenshot_name}")
                
            except Exception as e:
                print(f"⚠️ ボタン {i+1} の分析中にエラー: {e}")
        
        # ページ全体のスクリーンショットを撮影
        print("\n7. ページ全体のスクリーンショットを撮影中...")
        browser.take_screenshot("all_buttons_overview.png")
        print("✅ ページ全体のスクリーンショットを撮影しました")
        
        # 改善が必要なボタンのリストを作成
        print("\n8. 改善が必要なボタンのリスト:")
        improvement_needed = []
        
        for button_data in all_buttons:
            element = button_data['element']
            current_style = browser.driver.execute_script("""
                var element = arguments[0];
                var style = window.getComputedStyle(element);
                return {
                    backgroundColor: style.backgroundColor,
                    color: style.color,
                    borderColor: style.borderColor,
                    boxShadow: style.boxShadow
                };
            """, element)
            
            # 改善が必要かどうかを判定
            bg_color = current_style.get('backgroundColor', '')
            needs_improvement = False
            
            # 薄いグレーや透明背景の場合は改善が必要
            if '239, 239, 239' in bg_color or 'rgba(0, 0, 0, 0)' in bg_color or 'transparent' in bg_color:
                needs_improvement = True
            
            if needs_improvement:
                improvement_needed.append(button_data)
                print(f"  - '{button_data['text']}' (クラス: {button_data['class']})")
        
        print(f"\n改善が必要なボタン: {len(improvement_needed)} 個")
        
        # ブラウザを閉じる
        print("\n9. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した全ボタン特定完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ 全ボタン特定中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = find_all_buttons()
    sys.exit(0 if success else 1)
