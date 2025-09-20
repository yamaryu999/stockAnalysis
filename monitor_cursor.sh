#!/bin/bash

# Cursor パフォーマンス監視スクリプト
# 使用方法: ./monitor_cursor.sh

echo "=== Cursor パフォーマンス監視 ==="
echo "開始時刻: $(date)"
echo ""

# メモリ使用量
echo "--- メモリ使用量 ---"
free -h
echo ""

# CPU使用率
echo "--- CPU使用率 ---"
top -bn1 | head -10
echo ""

# Cursorプロセス
echo "--- Cursorプロセス ---"
ps aux | grep -E "(cursor|node)" | grep -v grep
echo ""

# ディスク使用量
echo "--- ディスク使用量 ---"
df -h
echo ""

# ネットワーク接続
echo "--- ネットワーク接続 ---"
netstat -tuln | grep -E "(3000|8501|8080|9000)"
echo ""

# ログファイルサイズ
echo "--- ログファイルサイズ ---"
find . -name "*.log" -type f -exec ls -lh {} \; 2>/dev/null | head -10
echo ""

echo "監視完了: $(date)"