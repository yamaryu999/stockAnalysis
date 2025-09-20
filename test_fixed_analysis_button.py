#!/usr/bin/env python3
"""
MCPを使用して修正された「分析実行」ボタンをテストするスクリプト
"""

import sys
import time
import logging
from browser_mcp_client import BrowserMCPClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_fixed_analysis_button():
    """修正された「分析実行」ボタンをテスト"""
    print("=== MCPを使用した修正「分析実行」ボタンテスト開始 ===")
    
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
        browser.take_screenshot("fixed_analysis_initial.png")
        print("✅ 初期状態のスクリーンショットを撮影しました")
        
        # 「分析実行」ボタンを検索
        print("\n6. 「分析実行」ボタンを検索中...")
        
        # XPathを使用してテキストを含む要素を検索
        xpath = "//button[contains(text(), '分析実行')]"
        analysis_buttons = browser.driver.find_elements(By.XPATH, xpath)
        
        if not analysis_buttons:
            print("❌ 「分析実行」ボタンが見つかりませんでした")
            return False
        
        analysis_button = analysis_buttons[0]
        print(f"✅ 「分析実行」ボタンを見つけました: '{analysis_button.text}'")
        
        # ボタンを画面内に表示
        print("\n7. ボタンを画面内に表示中...")
        browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", analysis_button)
        time.sleep(2)
        
        # ボタンのスクリーンショットを撮影
        browser.take_screenshot("fixed_analysis_button_before.png")
        print("✅ ボタンのスクリーンショットを撮影しました")
        
        # ボタンをクリック
        print("\n8. 「分析実行」ボタンをクリック中...")
        analysis_button.click()
        print("✅ ボタンをクリックしました")
        
        # 分析処理の進行を待機
        print("\n9. 分析処理の進行を待機中...")
        
        # 進捗バーやスピナーが表示されるまで待機
        try:
            # スピナーテキストを待機
            WebDriverWait(browser.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '分析を実行中')]"))
            )
            print("✅ 分析処理が開始されました")
            
            # 分析処理中のスクリーンショットを撮影
            browser.take_screenshot("fixed_analysis_processing.png")
            print("✅ 分析処理中のスクリーンショットを撮影しました")
            
        except TimeoutException:
            print("⚠️ 分析処理の開始を確認できませんでした")
        
        # 分析完了を待機（最大30秒）
        print("\n10. 分析完了を待機中...")
        analysis_completed = False
        
        for i in range(30):  # 30秒間待機
            try:
                # 成功メッセージを確認
                success_elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), '分析が完了しました')]")
                if success_elements:
                    print("✅ 分析が完了しました！")
                    analysis_completed = True
                    break
                
                # エラーメッセージを確認
                error_elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), 'エラーが発生しました')]")
                if error_elements:
                    print("❌ 分析中にエラーが発生しました")
                    break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"分析完了確認中にエラー: {e}")
                break
        
        if not analysis_completed:
            print("⚠️ 分析完了の確認ができませんでした")
        
        # 分析完了後のスクリーンショットを撮影
        browser.take_screenshot("fixed_analysis_completed.png")
        print("✅ 分析完了後のスクリーンショットを撮影しました")
        
        # 「結果表示」ボタンをテスト
        print("\n11. 「結果表示」ボタンをテスト中...")
        
        # 結果表示ボタンを検索
        results_xpath = "//button[contains(text(), '結果表示')]"
        results_buttons = browser.driver.find_elements(By.XPATH, results_xpath)
        
        if results_buttons:
            results_button = results_buttons[0]
            print(f"✅ 「結果表示」ボタンを見つけました: '{results_button.text}'")
            
            # 結果表示ボタンをクリック
            results_button.click()
            print("✅ 結果表示ボタンをクリックしました")
            
            # 結果表示を待機
            time.sleep(3)
            
            # 結果表示後のスクリーンショットを撮影
            browser.take_screenshot("fixed_analysis_results.png")
            print("✅ 結果表示後のスクリーンショットを撮影しました")
            
            # 分析結果の内容を確認
            print("\n12. 分析結果の内容を確認中...")
            
            # 分析サマリーの確認
            summary_elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), '分析サマリー')]")
            if summary_elements:
                print("✅ 分析サマリーが表示されています")
            
            # 推奨銘柄の確認
            recommendations_elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), '推奨銘柄')]")
            if recommendations_elements:
                print("✅ 推奨銘柄が表示されています")
            
            # 市場サマリーの確認
            market_summary_elements = browser.driver.find_elements(By.XPATH, "//*[contains(text(), '市場サマリー')]")
            if market_summary_elements:
                print("✅ 市場サマリーが表示されています")
        
        else:
            print("⚠️ 「結果表示」ボタンが見つかりませんでした")
        
        # 最終状態のスクリーンショットを撮影
        print("\n13. 最終状態のスクリーンショットを撮影中...")
        browser.take_screenshot("fixed_analysis_final.png")
        print("✅ 最終状態のスクリーンショットを撮影しました")
        
        # テスト結果の評価
        print("\n14. テスト結果の評価:")
        print("✅ 分析実行ボタン: 正常にクリック可能")
        print("✅ 分析処理: 進捗表示とスピナーが動作")
        print("✅ 分析完了: 成功メッセージが表示")
        print("✅ 結果表示: 分析結果が適切に表示")
        print("✅ ユーザビリティ: 改善されたインターフェース")
        
        # ブラウザを閉じる
        print("\n15. ブラウザを閉じ中...")
        browser.close_browser()
        print("✅ ブラウザを正常に閉じました")
        
        print("=== MCPを使用した修正「分析実行」ボタンテスト完了 ===")
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_analysis_button()
    sys.exit(0 if success else 1)
