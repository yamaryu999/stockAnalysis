#!/bin/bash

# Cursor 最適化スクリプト
# 使用方法: ./optimize_cursor.sh

echo "=== Cursor 最適化スクリプト ==="
echo "開始時刻: $(date)"
echo ""

# 1. 既存のCursorプロセスを終了
echo "1. 既存のCursorプロセスを終了中..."
pkill -f cursor 2>/dev/null
sleep 2
echo "✓ Cursorプロセスを終了しました"
echo ""

# 2. 一時ファイルをクリーンアップ
echo "2. 一時ファイルをクリーンアップ中..."
rm -rf /tmp/cursor-* 2>/dev/null
rm -rf ~/.cache/cursor-* 2>/dev/null
echo "✓ 一時ファイルをクリーンアップしました"
echo ""

# 3. ログファイルをクリーンアップ
echo "3. ログファイルをクリーンアップ中..."
find . -name "*.log" -type f -size +10M -delete 2>/dev/null
echo "✓ 大きなログファイルを削除しました"
echo ""

# 4. Pythonキャッシュをクリーンアップ
echo "4. Pythonキャッシュをクリーンアップ中..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -type f -delete 2>/dev/null
echo "✓ Pythonキャッシュをクリーンアップしました"
echo ""

# 5. メモリ使用量を確認
echo "5. メモリ使用量を確認中..."
free -h
echo ""

# 6. Cursorを再起動
echo "6. Cursorを再起動中..."
echo "Cursorを起動します..."
cursor . &
echo "✓ Cursorを起動しました"
echo ""

echo "最適化完了: $(date)"
echo ""
echo "=== 推奨事項 ==="
echo "1. 不要なタブを閉じてください"
echo "2. 大きなファイルを閉じてください"
echo "3. 拡張機能を必要最小限にしてください"
echo "4. 定期的に ./monitor_cursor.sh を実行してパフォーマンスを監視してください"