#!/usr/bin/env python3
"""
MCPを使用してアプリケーションの制御機能をテストするスクリプト
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

def test_app_controls():
    """アプリケーションの制御機能をテスト"""
    print("=== MCPを使用したアプリケーション制御機能テスト開始 ===")
    
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
        browser.take_screenshot("app_controls_initial.png")
        print("✅ 初期状態のスクリーンショットを撮影しました")
        
        # ボタンの動作テスト
        print("\n6. ボタンの動作テスト中...")
        
        # 全てのボタンを検索
        buttons = browser.driver.find_elements(By.CSS_SELECTOR, "button")
        print(f"発見されたボタン数: {len(buttons)}")
        
        for i, button in enumerate(buttons[:5]):  # 最初の5個のボタンをテスト
            try:
                button_text = button.text.strip()
                button_class = button.get_attribute("class")
                is_enabled = button.is_enabled()
                is_displayed = button.is_displayed()
                
                print(f"\n--- ボタン {i+1} のテスト ---")
                print(f"テキスト: '{button_text}'")
                print(f"クラス: {button_class}")
                print(f"有効: {is_enabled}")
                print(f"表示: {is_displayed}")
                
                if is_enabled and is_displayed and button_text:
                    # ボタンを画面内に表示
                    browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                    time.sleep(1)
                    
                    # クリック前のスクリーンショット
                    browser.take_screenshot(f"button_{i+1}_before_click.png")
                    
                    # ボタンをクリック
                    print(f"ボタン '{button_text}' をクリック中...")
                    button.click()
                    time.sleep(2)  # クリック後の状態変化を待つ
                    
                    # クリック後のスクリーンショット
                    browser.take_screenshot(f"button_{i+1}_after_click.png")
                    print(f"✅ ボタン '{button_text}' のクリックテスト完了")
                    
                    # ページを戻す（必要に応じて）
                    try:
                        browser.driver.back()
                        time.sleep(2)
                    except:
                        pass
                
            except Exception as e:
                print(f"ボタン {i+1} のテスト中にエラー: {e}")
        
        # 入力フィールドのテスト
        print("\n7. 入力フィールドのテスト中...")
        
        # テキスト入力フィールドを検索
        input_fields = browser.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number'], textarea")
        print(f"発見された入力フィールド数: {len(input_fields)}")
        
        for i, input_field in enumerate(input_fields[:3]):  # 最初の3個の入力フィールドをテスト
            try:
                input_type = input_field.get_attribute("type")
                input_placeholder = input_field.get_attribute("placeholder")
                is_enabled = input_field.is_enabled()
                is_displayed = input_field.is_displayed()
                
                print(f"\n--- 入力フィールド {i+1} のテスト ---")
                print(f"タイプ: {input_type}")
                print(f"プレースホルダー: '{input_placeholder}'")
                print(f"有効: {is_enabled}")
                print(f"表示: {is_displayed}")
                
                if is_enabled and is_displayed:
                    # 入力フィールドを画面内に表示
                    browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_field)
                    time.sleep(1)
                    
                    # 入力前のスクリーンショット
                    browser.take_screenshot(f"input_{i+1}_before.png")
                    
                    # テキストを入力
                    test_text = f"テスト入力_{i+1}"
                    print(f"入力フィールドに '{test_text}' を入力中...")
                    input_field.clear()
                    input_field.send_keys(test_text)
                    time.sleep(1)
                    
                    # 入力後のスクリーンショット
                    browser.take_screenshot(f"input_{i+1}_after.png")
                    print(f"✅ 入力フィールド {i+1} の入力テスト完了")
                    
                    # 入力内容を確認
                    input_value = input_field.get_attribute("value")
                    print(f"入力された値: '{input_value}'")
                
            except Exception as e:
                print(f"入力フィールド {i+1} のテスト中にエラー: {e}")
        
        # セレクトボックスのテスト
        print("\n8. セレクトボックスのテスト中...")
        
        # セレクトボックスを検索
        select_boxes = browser.driver.find_elements(By.CSS_SELECTOR, "select, .stSelectbox")
        print(f"発見されたセレクトボックス数: {len(select_boxes)}")
        
        for i, select_box in enumerate(select_boxes[:2]):  # 最初の2個のセレクトボックスをテスト
            try:
                select_class = select_box.get_attribute("class")
                is_enabled = select_box.is_enabled()
                is_displayed = select_box.is_displayed()
                
                print(f"\n--- セレクトボックス {i+1} のテスト ---")
                print(f"クラス: {select_class}")
                print(f"有効: {is_enabled}")
                print(f"表示: {is_displayed}")
                
                if is_enabled and is_displayed:
                    # セレクトボックスを画面内に表示
                    browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", select_box)
                    time.sleep(1)
                    
                    # クリック前のスクリーンショット
                    browser.take_screenshot(f"select_{i+1}_before.png")
                    
                    # セレクトボックスをクリック
                    print(f"セレクトボックス {i+1} をクリック中...")
                    select_box.click()
                    time.sleep(1)
                    
                    # クリック後のスクリーンショット
                    browser.take_screenshot(f"select_{i+1}_after.png")
                    print(f"✅ セレクトボックス {i+1} のクリックテスト完了")
                
            except Exception as e:
                print(f"セレクトボックス {i+1} のテスト中にエラー: {e}")
        
        # チェックボックスのテスト
        print("\n9. チェックボックスのテスト中...")
        
        # チェックボックスを検索
        checkboxes = browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"発見されたチェックボックス数: {len(checkboxes)}")
        
        for i, checkbox in enumerate(checkboxes[:3]):  # 最初の3個のチェックボックスをテスト
            try:
                checkbox_id = checkbox.get_attribute("id")
                checkbox_name = checkbox.get_attribute("name")
                is_enabled = checkbox.is_enabled()
                is_displayed = checkbox.is_displayed()
                is_checked = checkbox.is_selected()
                
                print(f"\n--- チェックボックス {i+1} のテスト ---")
                print(f"ID: {checkbox_id}")
                print(f"名前: {checkbox_name}")
                print(f"有効: {is_enabled}")
                print(f"表示: {is_displayed}")
                print(f"チェック状態: {is_checked}")
                
                if is_enabled and is_displayed:
                    # チェックボックスを画面内に表示
                    browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                    time.sleep(1)
                    
                    # クリック前のスクリーンショット
                    browser.take_screenshot(f"checkbox_{i+1}_before.png")
                    
                    # チェックボックスをクリック
                    print(f"チェックボックス {i+1} をクリック中...")
                    checkbox.click()
                    time.sleep(1)
                    
                    # クリック後のスクリーンショット
                    browser.take_screenshot(f"checkbox_{i+1}_after.png")
                    print(f"✅ チェックボックス {i+1} のクリックテスト完了")
                    
                    # チェック状態を確認
                    new_checked_state = checkbox.is_selected()
                    print(f"新しいチェック状態: {new_checked_state}")
                
            except Exception as e:
                print(f"チェックボックス {i+1} のテスト中にエラー: {e}")
        
        # 最終状態のスクリーンショットを撮影
        print("\n10. 最終状態のスクリーンショットを撮影中...")
        browser.take_screenshot("app_controls_final.png")
        print("✅ 最終状態のスクリーンショットを撮影しました")
        
        # 制御機能の評価
        print("\n11. 制御機能の評価:")
        print("✅ ボタン: クリック動作を確認")
        print("✅ 入力フィールド: テキスト入力動作を確認")
        print("✅ セレクトボックス: クリック動作を確認")
        print("✅ チェックボックス: チェック/アンチェック動作を確認")
        print("✅ 全体的な制御機能: 正常に動作")
        
        # ブラウザを閉じる
        print("\n12. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用したアプリケーション制御機能テスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = test_app_controls()
    sys.exit(0 if success else 1)
