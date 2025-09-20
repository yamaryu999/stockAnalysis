import unittest
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# テスト対象のモジュールをインポート
from database_manager import DatabaseManager
from cache_manager import CacheManager, stock_cache
from logger_config import get_logger, measure_performance
from config_manager import ConfigManager, get_config
from error_handler import (
    StockAnalysisError, DataFetchError, AnalysisError, 
    ConfigurationError, DatabaseError, CacheError,
    ValidationError, RateLimitError, ErrorHandler,
    is_positive, is_non_negative, is_string, is_not_empty, is_valid_symbol
)

class TestDatabaseManager(unittest.TestCase):
    """データベースマネージャーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """データベース初期化のテスト"""
        # データベースが正常に初期化されることを確認
        self.assertTrue(os.path.exists(self.temp_db.name))
        
        # テーブルが作成されていることを確認
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['stock_data', 'financial_metrics', 'analysis_results', 
                             'user_settings', 'alerts']
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_save_and_get_stock_data(self):
        """株価データの保存と取得のテスト"""
        symbol = "7203.T"
        
        # テストデータを作成
        dates = pd.date_range('2024-01-01', periods=10)
        test_data = pd.DataFrame({
            'Open': np.random.rand(10) * 1000 + 2000,
            'High': np.random.rand(10) * 1000 + 2500,
            'Low': np.random.rand(10) * 1000 + 1500,
            'Close': np.random.rand(10) * 1000 + 2000,
            'Volume': np.random.randint(1000000, 10000000, 10)
        }, index=dates)
        
        # データを保存
        result = self.db_manager.save_stock_data(symbol, test_data)
        self.assertTrue(result)
        
        # データを取得
        retrieved_data = self.db_manager.get_stock_data(symbol)
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(len(retrieved_data), 10)
        self.assertEqual(list(retrieved_data.columns), ['open', 'high', 'low', 'close', 'volume'])
    
    def test_save_and_get_financial_metrics(self):
        """財務指標の保存と取得のテスト"""
        symbol = "7203.T"
        metrics = {
            'per': 15.5,
            'pbr': 1.2,
            'roe': 12.5,
            'dividend_yield': 2.8,
            'market_cap': 25000000000000,
            'debt_ratio': 0.3,
            'current_ratio': 1.5,
            'quick_ratio': 1.2
        }
        
        # 財務指標を保存
        result = self.db_manager.save_financial_metrics(symbol, metrics)
        self.assertTrue(result)
        
        # 財務指標を取得
        retrieved_metrics = self.db_manager.get_financial_metrics(symbol)
        self.assertIsNotNone(retrieved_metrics)
        self.assertEqual(retrieved_metrics['per'], 15.5)
        self.assertEqual(retrieved_metrics['pbr'], 1.2)
    
    def test_save_and_get_analysis_results(self):
        """分析結果の保存と取得のテスト"""
        analysis_type = "technical_analysis"
        symbol = "7203.T"
        result_data = {
            'trend': 'bullish',
            'strength': 0.85,
            'signals': ['buy', 'strong_buy']
        }
        confidence_score = 0.92
        
        # 分析結果を保存
        result = self.db_manager.save_analysis_result(
            analysis_type, symbol, result_data, confidence_score
        )
        self.assertTrue(result)
        
        # 分析結果を取得
        retrieved_results = self.db_manager.get_analysis_results(analysis_type)
        self.assertEqual(len(retrieved_results), 1)
        self.assertEqual(retrieved_results[0]['symbol'], symbol)
        self.assertEqual(retrieved_results[0]['confidence_score'], confidence_score)
        self.assertEqual(retrieved_results[0]['result_data']['trend'], 'bullish')
    
    def test_user_settings(self):
        """ユーザー設定のテスト"""
        key = "theme"
        value = "dark"
        
        # 設定を保存
        result = self.db_manager.save_user_setting(key, value)
        self.assertTrue(result)
        
        # 設定を取得
        retrieved_value = self.db_manager.get_user_setting(key)
        self.assertEqual(retrieved_value, value)
        
        # デフォルト値のテスト
        default_value = self.db_manager.get_user_setting("nonexistent_key", "default")
        self.assertEqual(default_value, "default")
    
    def test_alerts(self):
        """アラートのテスト"""
        symbol = "7203.T"
        alert_type = "price_alert"
        condition_data = {
            'target_price': 2500,
            'condition': 'above'
        }
        
        # アラートを追加
        result = self.db_manager.add_alert(symbol, alert_type, condition_data)
        self.assertTrue(result)
        
        # アラートを取得
        alerts = self.db_manager.get_active_alerts(symbol)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['symbol'], symbol)
        self.assertEqual(alerts[0]['alert_type'], alert_type)
        self.assertEqual(alerts[0]['condition_data']['target_price'], 2500)
    
    def test_database_stats(self):
        """データベース統計のテスト"""
        stats = self.db_manager.get_database_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('stock_data_count', stats)
        self.assertIn('financial_metrics_count', stats)
        self.assertIn('analysis_results_count', stats)
        self.assertIn('alerts_count', stats)
        self.assertIn('db_size_mb', stats)

class TestCacheManager(unittest.TestCase):
    """キャッシュマネージャーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(self.temp_dir, default_ttl=1)  # 1秒のTTL
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_set_and_get(self):
        """キャッシュの保存と取得のテスト"""
        key = "test_key"
        data = {"test": "data", "number": 123}
        
        # データをキャッシュに保存
        result = self.cache_manager.set(key, data)
        self.assertTrue(result)
        
        # データをキャッシュから取得
        retrieved_data = self.cache_manager.get(key)
        self.assertEqual(retrieved_data, data)
    
    def test_cache_expiration(self):
        """キャッシュの期限切れテスト"""
        key = "expire_test"
        data = "test_data"
        
        # データをキャッシュに保存
        self.cache_manager.set(key, data, ttl=1)  # 1秒のTTL
        
        # すぐに取得（まだ有効）
        retrieved_data = self.cache_manager.get(key)
        self.assertEqual(retrieved_data, data)
        
        # 2秒待機
        time.sleep(2)
        
        # 期限切れ後は取得できない
        retrieved_data = self.cache_manager.get(key)
        self.assertIsNone(retrieved_data)
    
    def test_cache_delete(self):
        """キャッシュの削除テスト"""
        key = "delete_test"
        data = "test_data"
        
        # データをキャッシュに保存
        self.cache_manager.set(key, data)
        
        # データが存在することを確認
        retrieved_data = self.cache_manager.get(key)
        self.assertEqual(retrieved_data, data)
        
        # キャッシュを削除
        result = self.cache_manager.delete(key)
        self.assertTrue(result)
        
        # 削除後は取得できない
        retrieved_data = self.cache_manager.get(key)
        self.assertIsNone(retrieved_data)
    
    def test_cache_clear(self):
        """キャッシュのクリアテスト"""
        # 複数のデータをキャッシュに保存
        for i in range(5):
            self.cache_manager.set(f"key_{i}", f"data_{i}")
        
        # データが存在することを確認
        for i in range(5):
            data = self.cache_manager.get(f"key_{i}")
            self.assertEqual(data, f"data_{i}")
        
        # キャッシュをクリア
        result = self.cache_manager.clear()
        self.assertTrue(result)
        
        # クリア後は全てのデータが取得できない
        for i in range(5):
            data = self.cache_manager.get(f"key_{i}")
            self.assertIsNone(data)
    
    def test_cache_stats(self):
        """キャッシュ統計のテスト"""
        # データをキャッシュに保存
        for i in range(3):
            self.cache_manager.set(f"key_{i}", f"data_{i}")
        
        stats = self.cache_manager.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('memory_cache_size', stats)
        self.assertIn('file_cache_count', stats)
        self.assertIn('total_cache_size_mb', stats)
        self.assertEqual(stats['memory_cache_size'], 3)
        self.assertEqual(stats['file_cache_count'], 3)

class TestConfigManager(unittest.TestCase):
    """設定マネージャーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
        self.temp_config.close()
        self.config_manager = ConfigManager(self.temp_config.name)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_config_creation(self):
        """設定作成のテスト"""
        config = self.config_manager.get_config()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.database)
        self.assertIsNotNone(config.cache)
        self.assertIsNotNone(config.api)
        self.assertIsNotNone(config.logging)
        self.assertIsNotNone(config.analysis)
        self.assertIsNotNone(config.ui)
        self.assertIsNotNone(config.security)
    
    def test_config_update(self):
        """設定更新のテスト"""
        # アプリケーション名を更新
        self.config_manager.update_config(app_name="テストアプリ")
        
        config = self.config_manager.get_config()
        self.assertEqual(config.app_name, "テストアプリ")
    
    def test_section_update(self):
        """セクション更新のテスト"""
        # データベース設定を更新
        self.config_manager.update_section('database', db_path="test.db")
        
        config = self.config_manager.get_config()
        self.assertEqual(config.database.db_path, "test.db")
    
    def test_config_validation(self):
        """設定検証のテスト"""
        # 正常な設定の検証
        is_valid = self.config_manager.validate_config()
        self.assertTrue(is_valid)
        
        # 無効な設定の検証
        self.config_manager.update_section('analysis', max_stocks_per_analysis=-1)
        is_valid = self.config_manager.validate_config()
        self.assertFalse(is_valid)

class TestErrorHandler(unittest.TestCase):
    """エラーハンドラーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_error_log = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_error_log.close()
        self.error_handler = ErrorHandler(
            log_errors=False,  # テスト中はログを無効化
            save_errors=True,
            error_log_file=self.temp_error_log.name
        )
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_error_log.name):
            os.unlink(self.temp_error_log.name)
    
    def test_custom_errors(self):
        """カスタムエラーのテスト"""
        # DataFetchError
        error = DataFetchError("データ取得に失敗", symbol="7203.T", api_name="yahoo_finance")
        self.assertEqual(error.error_code, "DATA_FETCH_ERROR")
        self.assertEqual(error.symbol, "7203.T")
        self.assertEqual(error.api_name, "yahoo_finance")
        
        # AnalysisError
        error = AnalysisError("分析に失敗", analysis_type="technical", symbol="7203.T")
        self.assertEqual(error.error_code, "ANALYSIS_ERROR")
        self.assertEqual(error.analysis_type, "technical")
        self.assertEqual(error.symbol, "7203.T")
        
        # ConfigurationError
        error = ConfigurationError("設定エラー", config_key="database_path")
        self.assertEqual(error.error_code, "CONFIGURATION_ERROR")
        self.assertEqual(error.config_key, "database_path")
        
        # DatabaseError
        error = DatabaseError("データベースエラー", operation="insert", table="stock_data")
        self.assertEqual(error.error_code, "DATABASE_ERROR")
        self.assertEqual(error.operation, "insert")
        self.assertEqual(error.table, "stock_data")
        
        # CacheError
        error = CacheError("キャッシュエラー", cache_key="test_key", operation="get")
        self.assertEqual(error.error_code, "CACHE_ERROR")
        self.assertEqual(error.cache_key, "test_key")
        self.assertEqual(error.operation, "get")
        
        # ValidationError
        error = ValidationError("バリデーションエラー", field="symbol", value="invalid")
        self.assertEqual(error.error_code, "VALIDATION_ERROR")
        self.assertEqual(error.field, "symbol")
        self.assertEqual(error.value, "invalid")
        
        # RateLimitError
        error = RateLimitError("レート制限エラー", api_name="yahoo_finance", retry_after=60)
        self.assertEqual(error.error_code, "RATE_LIMIT_ERROR")
        self.assertEqual(error.api_name, "yahoo_finance")
        self.assertEqual(error.retry_after, 60)
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        error = DataFetchError("テストエラー", symbol="7203.T")
        context = {"function": "test_function", "args": ["test_arg"]}
        
        error_info = self.error_handler.handle_error(error, context)
        
        self.assertIn('error_id', error_info)
        self.assertIn('timestamp', error_info)
        self.assertIn('error_type', error_info)
        self.assertIn('error_message', error_info)
        self.assertIn('context', error_info)
        self.assertEqual(error_info['error_type'], 'DataFetchError')
        self.assertEqual(error_info['error_message'], 'テストエラー')
        self.assertEqual(error_info['context']['function'], 'test_function')
    
    def test_error_statistics(self):
        """エラー統計のテスト"""
        # エラーを発生させる
        error1 = DataFetchError("エラー1", symbol="7203.T")
        error2 = AnalysisError("エラー2", analysis_type="technical")
        error3 = DataFetchError("エラー3", symbol="6758.T")
        
        self.error_handler.handle_error(error1)
        self.error_handler.handle_error(error2)
        self.error_handler.handle_error(error3)
        
        stats = self.error_handler.get_error_statistics()
        
        self.assertEqual(stats['total_errors'], 3)
        self.assertEqual(stats['session_errors'], 3)
        self.assertEqual(stats['error_types']['DataFetchError'], 2)
        self.assertEqual(stats['error_types']['AnalysisError'], 1)
        self.assertEqual(len(stats['recent_errors']), 3)

class TestValidationFunctions(unittest.TestCase):
    """バリデーション関数のテスト"""
    
    def test_is_positive(self):
        """正の数チェックのテスト"""
        self.assertTrue(is_positive(1))
        self.assertTrue(is_positive(1.5))
        self.assertTrue(is_positive(0.1))
        self.assertFalse(is_positive(0))
        self.assertFalse(is_positive(-1))
        self.assertFalse(is_positive(-1.5))
        self.assertFalse(is_positive("string"))
        self.assertFalse(is_positive(None))
    
    def test_is_non_negative(self):
        """非負数チェックのテスト"""
        self.assertTrue(is_non_negative(0))
        self.assertTrue(is_non_negative(1))
        self.assertTrue(is_non_negative(1.5))
        self.assertTrue(is_non_negative(0.1))
        self.assertFalse(is_non_negative(-1))
        self.assertFalse(is_non_negative(-1.5))
        self.assertFalse(is_non_negative("string"))
        self.assertFalse(is_non_negative(None))
    
    def test_is_string(self):
        """文字列チェックのテスト"""
        self.assertTrue(is_string("test"))
        self.assertTrue(is_string(""))
        self.assertFalse(is_string(123))
        self.assertFalse(is_string(1.5))
        self.assertFalse(is_string(None))
        self.assertFalse(is_string([]))
        self.assertFalse(is_string({}))
    
    def test_is_not_empty(self):
        """空でないチェックのテスト"""
        self.assertTrue(is_not_empty("test"))
        self.assertTrue(is_not_empty(" "))
        self.assertTrue(is_not_empty(123))
        self.assertTrue(is_not_empty(0))
        self.assertFalse(is_not_empty(""))
        self.assertFalse(is_not_empty(None))
        self.assertFalse(is_not_empty("   "))
    
    def test_is_valid_symbol(self):
        """有効な銘柄コードチェックのテスト"""
        self.assertTrue(is_valid_symbol("7203.T"))
        self.assertTrue(is_valid_symbol("6758.T"))
        self.assertTrue(is_valid_symbol("9984.T"))
        self.assertFalse(is_valid_symbol("7203"))
        self.assertFalse(is_valid_symbol("7203.t"))
        self.assertFalse(is_valid_symbol("ABCD.T"))
        self.assertFalse(is_valid_symbol("7203.TT"))
        self.assertFalse(is_valid_symbol(""))
        self.assertFalse(is_valid_symbol(None))
        self.assertFalse(is_valid_symbol(123))

class TestPerformanceDecorator(unittest.TestCase):
    """パフォーマンスデコレータのテスト"""
    
    def test_measure_performance(self):
        """パフォーマンス測定デコレータのテスト"""
        @measure_performance("test_operation")
        def test_function():
            time.sleep(0.1)  # 100ms待機
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")

def run_tests():
    """テストを実行"""
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # テストケースを追加
    test_classes = [
        TestDatabaseManager,
        TestCacheManager,
        TestConfigManager,
        TestErrorHandler,
        TestValidationFunctions,
        TestPerformanceDecorator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("🚀 改善された株価分析ツールのテストを開始します...")
    print("=" * 60)
    
    success = run_tests()
    
    print("=" * 60)
    if success:
        print("✅ 全てのテストが成功しました！")
    else:
        print("❌ 一部のテストが失敗しました。")
    
    print("テスト完了")
