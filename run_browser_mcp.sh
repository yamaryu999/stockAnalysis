#!/bin/bash

# MCP Browser Server 起動スクリプト
# Chromeブラウザを使用したMCPサーバーを起動

echo "=== MCP Browser Server 起動中 ==="

# 仮想環境をアクティベート
source venv/bin/activate

# ログディレクトリを作成
mkdir -p logs

# Chromeがインストールされているかチェック
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "警告: Chromeブラウザが見つかりません"
    echo "ChromeまたはChromiumをインストールしてください"
    echo "Ubuntu/Debian: sudo apt install google-chrome-stable"
    echo "または: sudo apt install chromium-browser"
fi

# Pythonスクリプトを実行
echo "MCP Browser Clientを起動しています..."
python browser_mcp_client.py

echo "=== MCP Browser Server 終了 ==="
