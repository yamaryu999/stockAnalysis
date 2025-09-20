#!/bin/bash

# WebSocketサーバー起動スクリプト
# リアルタイム通知システムのサーバーを起動

echo "🚀 WebSocketサーバーを起動しています..."

# 仮想環境をアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 仮想環境をアクティベートしました"
else
    echo "⚠️  仮想環境が見つかりません。システムのPythonを使用します。"
fi

# 必要な依存関係をチェック
echo "📦 依存関係をチェックしています..."

# websocketsライブラリの確認
python -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ websocketsライブラリが見つかりません。インストールします..."
    pip install websockets
fi

# ログディレクトリを作成
mkdir -p logs

# WebSocketサーバーを起動
echo "🌐 WebSocketサーバーを起動中..."
echo "📍 サーバーアドレス: ws://localhost:8765"
echo "🔄 リアルタイム通知システムが有効です"
echo ""
echo "終了するには Ctrl+C を押してください"
echo "----------------------------------------"

# サーバーを起動
python websocket_server.py

echo ""
echo "👋 WebSocketサーバーを終了しました"