import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os
from contextlib import contextmanager
from performance_optimizer import QueryOptimizer, performance_timer, memory_efficient

class DatabaseManager:
    """SQLiteデータベース管理クラス"""
    
    def __init__(self, db_path: str = "stock_analysis.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.query_optimizer = QueryOptimizer(self)
        self._init_database()
    
    def _init_database(self):
        """データベースの初期化"""
        try:
            with self.get_connection() as conn:
                # 株価データテーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS stock_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        date DATE NOT NULL,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, date)
                    )
                """)
                
                # 財務指標テーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS financial_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        date DATE NOT NULL,
                        per REAL,
                        pbr REAL,
                        roe REAL,
                        dividend_yield REAL,
                        market_cap REAL,
                        debt_ratio REAL,
                        current_ratio REAL,
                        quick_ratio REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, date)
                    )
                """)
                
                # 分析結果テーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_type TEXT NOT NULL,
                        symbol TEXT,
                        result_data TEXT,  -- JSON形式
                        confidence_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # ユーザー設定テーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # アラートテーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        condition_data TEXT,  -- JSON形式
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        triggered_at TIMESTAMP
                    )
                """)
                
                # インデックスの作成（最適化）
                conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_financial_metrics_symbol_date ON financial_metrics(symbol, date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_symbol_active ON alerts(symbol, is_active)")
                
                # 追加のパフォーマンスインデックス
                conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_financial_metrics_per ON financial_metrics(per)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_financial_metrics_pbr ON financial_metrics(pbr)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_financial_metrics_roe ON financial_metrics(roe)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_analysis_results_confidence ON analysis_results(confidence_score)")
                
                # データベース最適化設定
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                conn.execute("PRAGMA cache_size = 10000")
                conn.execute("PRAGMA temp_store = MEMORY")
                
                conn.commit()
                self.logger.info("データベースの初期化が完了しました")
                
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """データベース接続のコンテキストマネージャー"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"データベース接続エラー: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_stock_data(self, stock_or_symbol, data: Optional[pd.DataFrame] = None) -> bool:
        """株価データを保存
        - dictを渡した場合: 単一レコードを挿入
        - (symbol, DataFrame) を渡した場合: 複数レコードを挿入
        """
        try:
            with self.get_connection() as conn:
                if isinstance(stock_or_symbol, dict):
                    rec = stock_or_symbol
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO stock_data
                        (symbol, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            rec.get('symbol'),
                            rec.get('date'),
                            rec.get('open'),
                            rec.get('high'),
                            rec.get('low'),
                            rec.get('close'),
                            rec.get('volume', 0),
                        ),
                    )
                    conn.commit()
                    self.logger.info(f"株価データ(1件)を保存しました: {rec.get('symbol')}")
                    return True
                else:
                    symbol = stock_or_symbol
                    if data is None or data.empty:
                        return False
                    # 既存データを削除（この銘柄）
                    conn.execute("DELETE FROM stock_data WHERE symbol = ?", (symbol,))
                    for date, row in data.iterrows():
                        conn.execute(
                            """
                            INSERT INTO stock_data
                            (symbol, date, open, high, low, close, volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                symbol,
                                getattr(date, 'date', lambda: date)() if hasattr(date, 'date') else date,
                                row.get('Open') if 'Open' in row else row.get('open'),
                                row.get('High') if 'High' in row else row.get('high'),
                                row.get('Low') if 'Low' in row else row.get('low'),
                                row.get('Close') if 'Close' in row else row.get('close'),
                                row.get('Volume') if 'Volume' in row else row.get('volume', 0),
                            ),
                        )
                    conn.commit()
                    self.logger.info(f"株価データを保存しました: {symbol}")
                    return True
        except Exception as e:
            self.logger.error(f"株価データ保存エラー: {e}")
            return False
    
    def get_stock_data(self, symbol: str, days: int = 10000) -> Optional[Dict]:
        """最新の株価データ1件を取得（dict）。指定期間外ならNone。"""
        try:
            with self.get_connection() as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).date()
                row = conn.execute(
                    """
                    SELECT symbol, date, open, high, low, close, volume
                    FROM stock_data
                    WHERE symbol = ? AND date >= ?
                    ORDER BY date DESC
                    LIMIT 1
                    """,
                    (symbol, cutoff_date),
                ).fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            self.logger.error(f"株価データ取得エラー {symbol}: {e}")
            return None
    
    def save_financial_metrics(self, symbol: str, metrics: Dict, date: datetime = None) -> bool:
        """財務指標を保存"""
        try:
            if date is None:
                date = datetime.now()
            
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO financial_metrics
                    (symbol, date, per, pbr, roe, dividend_yield, market_cap, 
                     debt_ratio, current_ratio, quick_ratio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol, date.date(),
                    metrics.get('per'), metrics.get('pbr'), metrics.get('roe'),
                    metrics.get('dividend_yield'), metrics.get('market_cap'),
                    metrics.get('debt_ratio'), metrics.get('current_ratio'),
                    metrics.get('quick_ratio')
                ))
                
                conn.commit()
                self.logger.info(f"財務指標を保存しました: {symbol}")
                return True
                
        except Exception as e:
            self.logger.error(f"財務指標保存エラー {symbol}: {e}")
            return False
    
    @performance_timer
    @memory_efficient
    def get_financial_metrics(self, symbol: str) -> Optional[Dict]:
        """最新の財務指標を取得（最適化版）"""
        try:
            with self.get_connection() as conn:
                # 最適化されたクエリ
                query = """
                    SELECT symbol, date, per, pbr, roe, dividend_yield, 
                           market_cap, debt_ratio, current_ratio, quick_ratio
                    FROM financial_metrics 
                    WHERE symbol = ? 
                    ORDER BY date DESC 
                    LIMIT 1
                """
                
                optimized_query = self.query_optimizer.optimize_query(query)
                cursor = conn.execute(optimized_query, (symbol,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            self.logger.error(f"財務指標取得エラー {symbol}: {e}")
            return None
    
    def save_analysis_result(self, analysis_type: str, symbol: str, 
                           result_data: Dict, confidence_score: float = None) -> bool:
        """分析結果を保存"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO analysis_results
                    (analysis_type, symbol, result_data, confidence_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    analysis_type, symbol, 
                    json.dumps(result_data, ensure_ascii=False, default=str),
                    confidence_score
                ))
                
                conn.commit()
                self.logger.info(f"分析結果を保存しました: {analysis_type} - {symbol}")
                return True
                
        except Exception as e:
            self.logger.error(f"分析結果保存エラー {analysis_type} - {symbol}: {e}")
            return False
    
    def get_analysis_results(self, analysis_type: str, limit: int = 100) -> List[Dict]:
        """分析結果を取得"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT * FROM analysis_results 
                    WHERE analysis_type = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """
                
                cursor = conn.execute(query, (analysis_type, limit))
                results = []
                
                for row in cursor.fetchall():
                    result = dict(row)
                    result['result_data'] = json.loads(result['result_data'])
                    results.append(result)
                
                return results
                
        except Exception as e:
            self.logger.error(f"分析結果取得エラー {analysis_type}: {e}")
            return []
    
    def save_user_setting(self, key: str, value: Any) -> bool:
        """ユーザー設定を保存"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_settings
                    (setting_key, setting_value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, json.dumps(value, ensure_ascii=False, default=str)))
                
                conn.commit()
                self.logger.info(f"ユーザー設定を保存しました: {key}")
                return True
                
        except Exception as e:
            self.logger.error(f"ユーザー設定保存エラー {key}: {e}")
            return False
    
    def get_user_setting(self, key: str, default_value: Any = None) -> Any:
        """ユーザー設定を取得"""
        try:
            with self.get_connection() as conn:
                query = "SELECT setting_value FROM user_settings WHERE setting_key = ?"
                cursor = conn.execute(query, (key,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row['setting_value'])
                return default_value
                
        except Exception as e:
            self.logger.error(f"ユーザー設定取得エラー {key}: {e}")
            return default_value
    
    def add_alert(self, symbol: str, alert_type: str, condition_data: Dict) -> bool:
        """アラートを追加"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO alerts
                    (symbol, alert_type, condition_data)
                    VALUES (?, ?, ?)
                """, (symbol, alert_type, json.dumps(condition_data, ensure_ascii=False)))
                
                conn.commit()
                self.logger.info(f"アラートを追加しました: {symbol} - {alert_type}")
                return True
                
        except Exception as e:
            self.logger.error(f"アラート追加エラー {symbol}: {e}")
            return False
    
    def get_active_alerts(self, symbol: str = None) -> List[Dict]:
        """アクティブなアラートを取得"""
        try:
            with self.get_connection() as conn:
                if symbol:
                    query = """
                        SELECT * FROM alerts 
                        WHERE symbol = ? AND is_active = 1 
                        ORDER BY created_at DESC
                    """
                    cursor = conn.execute(query, (symbol,))
                else:
                    query = """
                        SELECT * FROM alerts 
                        WHERE is_active = 1 
                        ORDER BY created_at DESC
                    """
                    cursor = conn.execute(query)
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    result['condition_data'] = json.loads(result['condition_data'])
                    results.append(result)
                
                return results
                
        except Exception as e:
            self.logger.error(f"アラート取得エラー: {e}")
            return []

    # 互換API（テスト用）
    def get_alerts(self, symbol: Optional[str] = None) -> List[Dict]:
        """アクティブなアラート一覧を取得（互換メソッド）"""
        return self.get_active_alerts(symbol)

    def update_alert_status(self, alert_id: int, is_active: bool) -> bool:
        """アラートの有効/無効を更新"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE alerts SET is_active = ? WHERE id = ?",
                    (1 if is_active else 0, alert_id),
                )
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"アラート更新エラー: {e}")
            return False
    
    def cleanup_old_data(self, days: int = 30):
        """古いデータをクリーンアップ（stock_data/financial_metrics/analysis_results）"""
        try:
            with self.get_connection() as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).date()
                # 古い株価データ
                conn.execute("DELETE FROM stock_data WHERE date < ?", (cutoff_date,))
                # 古い財務指標
                conn.execute("DELETE FROM financial_metrics WHERE date < ?", (cutoff_date,))
                # 古い分析結果（作成日時ベース）
                conn.execute("DELETE FROM analysis_results WHERE date(created_at) < ?", (cutoff_date,))
                conn.commit()
                self.logger.info(f"{days}日より古いデータをクリーンアップしました")
        except Exception as e:
            self.logger.error(f"データクリーンアップエラー: {e}")
    
    def get_database_stats(self) -> Dict:
        """データベース統計情報を取得"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # 各テーブルのレコード数
                tables = ['stock_data', 'financial_metrics', 'analysis_results', 'alerts']
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                    stats[f'{table}_count'] = cursor.fetchone()['count']
                
                # データベースサイズ
                stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"データベース統計取得エラー: {e}")
            return {}
    
    def batch_insert_stock_data(self, stock_data_list: List[Dict]) -> bool:
        """株価データのバッチ挿入（最適化版）"""
        try:
            with self.get_connection() as conn:
                # バッチ挿入用のSQL
                query = """
                    INSERT OR REPLACE INTO stock_data
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                # データを準備
                data_tuples = []
                for data in stock_data_list:
                    data_tuples.append((
                        data.get('symbol'),
                        data.get('date'),
                        data.get('open'),
                        data.get('high'),
                        data.get('low'),
                        data.get('close'),
                        data.get('volume')
                    ))
                
                # バッチ実行
                conn.executemany(query, data_tuples)
                conn.commit()
                
                self.logger.info(f"バッチ挿入完了: {len(stock_data_list)}件")
                return True
                
        except Exception as e:
            self.logger.error(f"バッチ挿入エラー: {e}")
            return False
    
    def batch_insert_financial_metrics(self, metrics_list: List[Dict]) -> bool:
        """財務指標のバッチ挿入（最適化版）"""
        try:
            with self.get_connection() as conn:
                query = """
                    INSERT OR REPLACE INTO financial_metrics
                    (symbol, date, per, pbr, roe, dividend_yield, market_cap,
                     debt_ratio, current_ratio, quick_ratio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                data_tuples = []
                for metrics in metrics_list:
                    data_tuples.append((
                        metrics.get('symbol'),
                        metrics.get('date'),
                        metrics.get('per'),
                        metrics.get('pbr'),
                        metrics.get('roe'),
                        metrics.get('dividend_yield'),
                        metrics.get('market_cap'),
                        metrics.get('debt_ratio'),
                        metrics.get('current_ratio'),
                        metrics.get('quick_ratio')
                    ))
                
                conn.executemany(query, data_tuples)
                conn.commit()
                
                self.logger.info(f"財務指標バッチ挿入完了: {len(metrics_list)}件")
                return True
                
        except Exception as e:
            self.logger.error(f"財務指標バッチ挿入エラー: {e}")
            return False
    
    def optimize_database(self) -> bool:
        """データベース最適化を実行"""
        try:
            with self.get_connection() as conn:
                # ANALYZE実行
                conn.execute("ANALYZE")
                
                # 統計情報更新
                conn.execute("PRAGMA optimize")
                
                conn.commit()
                self.logger.info("データベース最適化が完了しました")
                return True
                
        except Exception as e:
            self.logger.error(f"データベース最適化エラー: {e}")
            return False
