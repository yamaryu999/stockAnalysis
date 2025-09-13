#!/bin/bash

# 日本株価分析ツール起動スクリプト

echo "📈 日本株価分析ツールを起動しています..."

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "仮想環境を作成しています..."
    python3 -m venv venv
fi

# 仮想環境のアクティベート
echo "仮想環境をアクティベートしています..."
source venv/bin/activate

# 依存関係のインストール
echo "依存関係をインストールしています..."
pip install -r requirements.txt

# Streamlitアプリの起動（メールアドレス入力をスキップ）
echo "アプリケーションを起動しています..."
echo "ブラウザで http://localhost:8501 にアクセスしてください"
echo "" | streamlit run app.py
