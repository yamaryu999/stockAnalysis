# MCP Browser Setup for Chrome

Chromeブラウザを使用したMCP（Model Context Protocol）の設定と使用方法について説明します。

## 概要

このプロジェクトでは、Chromeブラウザを自動化してMCPプロトコルで制御するシステムを構築しています。Selenium WebDriverを使用してブラウザを制御し、MCPサーバーとして機能します。

## ファイル構成

- `mcp_config.yaml` - MCP設定ファイル
- `browser_mcp_client.py` - ブラウザクライアント（Selenium WebDriver）
- `mcp_browser_server.py` - MCPサーバー
- `test_browser_mcp.py` - テストスクリプト
- `run_browser_mcp.sh` - 起動スクリプト

## 必要な依存関係

```bash
pip install selenium webdriver-manager pyyaml
```

## 設定

### mcp_config.yaml

```yaml
mcp:
  browser:
    type: chrome
    headless: false
    window_size: "1920,1080"
    user_agent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    
  chrome:
    executable_path: null  # 自動検出
    options:
      - "--no-sandbox"
      - "--disable-dev-shm-usage"
      - "--disable-gpu"
      
  server:
    host: "localhost"
    port: 3000
    timeout: 30
```

## 使用方法

### 1. 基本的な使用方法

```python
from browser_mcp_client import BrowserMCPClient

# コンテキストマネージャーを使用
with BrowserMCPClient() as browser:
    # Googleに移動
    browser.navigate_to("https://www.google.com")
    
    # 検索ボックスにテキストを入力
    browser.input_text("name", "q", "Python Selenium")
    
    # 検索ボタンをクリック
    browser.click_element("name", "btnK")
    
    # スクリーンショットを撮影
    browser.take_screenshot("result.png")
```

### 2. MCPサーバーとして使用

```python
from mcp_browser_server import MCPBrowserServer
import asyncio

async def main():
    server = MCPBrowserServer()
    await server.start_server()

asyncio.run(main())
```

### 3. 起動スクリプトを使用

```bash
./run_browser_mcp.sh
```

## 利用可能なメソッド

### ブラウザクライアント

- `navigate_to(url)` - URLに移動
- `find_element(by, value)` - 要素を検索
- `click_element(by, value)` - 要素をクリック
- `input_text(by, value, text)` - テキストを入力
- `get_page_source()` - ページソースを取得
- `get_page_title()` - ページタイトルを取得
- `get_current_url()` - 現在のURLを取得
- `execute_javascript(script)` - JavaScriptを実行
- `take_screenshot(filename)` - スクリーンショットを撮影
- `wait_for_element(by, value)` - 要素の出現を待機

### MCPサーバー

- `browser/navigate` - ナビゲーション
- `browser/click` - クリック操作
- `browser/input` - テキスト入力
- `browser/get_text` - テキスト取得
- `browser/screenshot` - スクリーンショット
- `browser/execute_script` - JavaScript実行

## テスト

テストスクリプトを実行して動作を確認できます：

```bash
python test_browser_mcp.py
```

## トラブルシューティング

### Chromeがインストールされていない場合

```bash
# Ubuntu/Debian
sudo apt install google-chrome-stable

# または
sudo apt install chromium-browser
```

### ChromeDriverの問題

webdriver-managerが自動的にChromeDriverをダウンロードしますが、手動でインストールすることも可能です。

### 権限の問題

```bash
chmod +x run_browser_mcp.sh
```

## ログ

ログは `logs/browser_mcp.log` に保存されます。

## セキュリティ

- 本番環境では適切なセキュリティ設定を行ってください
- 信頼できないWebサイトへのアクセスは避けてください
- 必要に応じてプロキシ設定を追加してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
