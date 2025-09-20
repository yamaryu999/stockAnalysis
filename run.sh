#!/bin/bash

# 🚀 日本株価分析ツール v5.0 - 最適化版 起動スクリプト
# 軽量で高速な株価分析ツール

echo "=== 🚀 日本株価分析ツール v5.0 - 最適化版 起動中 ==="

# 仮想環境をアクティベート
if [ -d "venv" ]; then
    echo "仮想環境をアクティベート中..."
    source venv/bin/activate
else
    echo "警告: 仮想環境が見つかりません"
    echo "仮想環境を作成してください: python3 -m venv venv"
    exit 1
fi

# 必要なディレクトリを作成
echo "必要なディレクトリを作成中..."
mkdir -p logs
mkdir -p cache
mkdir -p styles

# 依存関係をチェック
echo "依存関係をチェック中..."
python -c "import streamlit, pandas, plotly, yfinance" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "依存関係をインストール中..."
    pip install -r requirements.txt
fi

# ポート設定
PORT=${1:-8501}

echo "ポート ${PORT} でアプリケーションを起動中..."
echo "ブラウザで http://localhost:${PORT} にアクセスしてください"

# アプリケーションを起動
streamlit run app.py --server.port ${PORT} --server.headless false

echo "=== アプリケーション終了 ==="