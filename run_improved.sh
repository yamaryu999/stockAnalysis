#!/bin/bash

# 日本株価分析ツール v4.1 - Improved 起動スクリプト
# データベース対応 × エラーハンドリング強化 × パフォーマンス向上

echo "🚀 日本株価分析ツール v4.1 - Improved を起動します..."
echo "=================================================="

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
python -c "import streamlit, pandas, numpy, plotly, yfinance, sklearn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 必要な依存関係が不足しています。"
    echo "以下のコマンドで依存関係をインストールしてください："
    echo "pip install -r requirements.txt"
    exit 1
fi

# データベースの初期化
echo "💾 データベースを初期化中..."
python -c "
from database_manager import DatabaseManager
try:
    db = DatabaseManager()
    print('✅ データベースの初期化が完了しました')
except Exception as e:
    print(f'❌ データベースの初期化に失敗しました: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ データベースの初期化に失敗しました。"
    exit 1
fi

# キャッシュディレクトリの作成
echo "🗄️ キャッシュディレクトリを作成中..."
mkdir -p cache
mkdir -p logs

# 設定ファイルの確認
if [ ! -f "config.yaml" ]; then
    echo "⚙️ デフォルト設定ファイルを作成中..."
    python -c "
from config_manager import ConfigManager
try:
    config = ConfigManager()
    print('✅ デフォルト設定ファイルを作成しました')
except Exception as e:
    print(f'❌ 設定ファイルの作成に失敗しました: {e}')
    exit(1)
"
fi

# テストの実行（オプション）
if [ "$1" = "--test" ]; then
    echo "🧪 テストを実行中..."
    python test_improvements.py
    if [ $? -ne 0 ]; then
        echo "❌ テストが失敗しました。"
        exit 1
    fi
    echo "✅ 全てのテストが成功しました！"
fi

# アプリケーションの起動
echo "🚀 アプリケーションを起動中..."
echo "=================================================="
echo "📱 ブラウザで以下のURLにアクセスしてください："
echo "   http://localhost:8505"
echo "=================================================="
echo "🛑 アプリケーションを停止するには Ctrl+C を押してください"
echo ""

# 改善されたアプリケーションを起動
streamlit run app_improved.py --server.port 8505 --server.headless true
