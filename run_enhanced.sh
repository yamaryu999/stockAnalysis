#!/bin/bash

# 🚀 日本株価分析ツール v4.0 - Enhanced UI 起動スクリプト

echo "🚀 日本株価分析ツール v4.0 - Enhanced UI を起動しています..."
echo ""

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "❌ 仮想環境が見つかりません。"
    echo "以下のコマンドで仮想環境を作成してください："
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# 仮想環境をアクティベート
echo "📦 仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係の確認
echo "🔍 依存関係を確認中..."
python -c "import streamlit, pandas, plotly, yfinance" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 必要な依存関係が不足しています。"
    echo "以下のコマンドで依存関係をインストールしてください："
    echo "pip install -r requirements.txt"
    exit 1
fi

# ポートの確認
PORT=8504
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  ポート $PORT は既に使用されています。"
    echo "別のポートを使用します..."
    PORT=8505
fi

echo "✅ 依存関係の確認完了"
echo ""
echo "🎨 Enhanced UI を起動中..."
echo "📱 ブラウザで http://localhost:$PORT にアクセスしてください"
echo ""
echo "🛑 停止するには Ctrl+C を押してください"
echo ""

# Enhanced UI版を起動
streamlit run app_ui_enhanced.py --server.port $PORT --server.headless false
