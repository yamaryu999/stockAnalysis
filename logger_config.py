import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import json

class ColoredFormatter(logging.Formatter):
    """カラフルなログフォーマッター"""
    
    # ANSIカラーコード
    COLORS = {
        'DEBUG': '\033[36m',    # シアン
        'INFO': '\033[32m',     # 緑
        'WARNING': '\033[33m',  # 黄
        'ERROR': '\033[31m',    # 赤
        'CRITICAL': '\033[35m', # マゼンタ
        'RESET': '\033[0m'      # リセット
    }
    
    def format(self, record):
        # カラーコードを追加
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 例外情報がある場合は追加
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 追加のフィールドがある場合は追加
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class LoggerConfig:
    """ログ設定管理クラス"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_json: bool = False):
        
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
        
        # ログディレクトリの作成
        os.makedirs(log_dir, exist_ok=True)
        
        # ログ設定の初期化
        self._setup_logging()
    
    def _setup_logging(self):
        """ログ設定をセットアップ"""
        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # 既存のハンドラーをクリア
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # コンソールハンドラー
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            
            if self.enable_json:
                console_formatter = JSONFormatter()
            else:
                console_formatter = ColoredFormatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # ファイルハンドラー
        if self.enable_file:
            # 一般ログファイル
            general_log_file = os.path.join(self.log_dir, 'stock_analysis.log')
            general_handler = logging.handlers.RotatingFileHandler(
                general_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            general_handler.setLevel(self.log_level)
            
            if self.enable_json:
                general_formatter = JSONFormatter()
            else:
                general_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(module)-15s | %(funcName)-15s | %(lineno)-4d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            general_handler.setFormatter(general_formatter)
            root_logger.addHandler(general_handler)
            
            # エラーログファイル
            error_log_file = os.path.join(self.log_dir, 'error.log')
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            
            if self.enable_json:
                error_formatter = JSONFormatter()
            else:
                error_formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(module)-15s | %(funcName)-15s | %(lineno)-4d | %(message)s\n%(pathname)s\n%(exc_info)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            error_handler.setFormatter(error_formatter)
            root_logger.addHandler(error_handler)
            
            # パフォーマンスログファイル
            performance_log_file = os.path.join(self.log_dir, 'performance.log')
            performance_handler = logging.handlers.RotatingFileHandler(
                performance_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            performance_handler.setLevel(logging.INFO)
            
            if self.enable_json:
                performance_formatter = JSONFormatter()
            else:
                performance_formatter = logging.Formatter(
                    '%(asctime)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            performance_handler.setFormatter(performance_formatter)
            
            # パフォーマンス専用ロガー
            performance_logger = logging.getLogger('performance')
            performance_logger.addHandler(performance_handler)
            performance_logger.setLevel(logging.INFO)
            performance_logger.propagate = False
    
    def get_logger(self, name: str) -> logging.Logger:
        """指定された名前のロガーを取得"""
        return logging.getLogger(name)
    
    def get_performance_logger(self) -> logging.Logger:
        """パフォーマンス専用ロガーを取得"""
        return logging.getLogger('performance')
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """パフォーマンスログを記録"""
        perf_logger = self.get_performance_logger()
        
        log_data = {
            'operation': operation,
            'duration_seconds': duration,
            **kwargs
        }
        
        if self.enable_json:
            perf_logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            perf_logger.info(f"PERF | {operation} | {duration:.3f}s | {kwargs}")
    
    def log_api_call(self, api_name: str, symbol: str, success: bool, 
                    duration: float, error: Optional[str] = None):
        """API呼び出しログを記録"""
        logger = self.get_logger('api')
        
        log_data = {
            'api_name': api_name,
            'symbol': symbol,
            'success': success,
            'duration_seconds': duration,
            'error': error
        }
        
        if success:
            logger.info(f"API呼び出し成功: {api_name} - {symbol} ({duration:.3f}s)")
        else:
            logger.error(f"API呼び出し失敗: {api_name} - {symbol} ({duration:.3f}s) - {error}")
    
    def log_analysis_result(self, analysis_type: str, symbol: str, 
                          result_count: int, duration: float):
        """分析結果ログを記録"""
        logger = self.get_logger('analysis')
        
        logger.info(f"分析完了: {analysis_type} - {symbol} | 結果数: {result_count} | 処理時間: {duration:.3f}s")
    
    def log_user_action(self, user_id: str, action: str, details: dict = None):
        """ユーザーアクションログを記録"""
        logger = self.get_logger('user_action')
        
        log_data = {
            'user_id': user_id,
            'action': action,
            'details': details or {}
        }
        
        if self.enable_json:
            logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            logger.info(f"ユーザーアクション: {user_id} | {action} | {details}")

# グローバルログ設定インスタンス
logger_config = LoggerConfig()

# 便利な関数
def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得"""
    return logger_config.get_logger(name)

def log_performance(operation: str, duration: float, **kwargs):
    """パフォーマンスログを記録"""
    logger_config.log_performance(operation, duration, **kwargs)

def log_api_call(api_name: str, symbol: str, success: bool, 
                duration: float, error: Optional[str] = None):
    """API呼び出しログを記録"""
    logger_config.log_api_call(api_name, symbol, success, duration, error)

def log_analysis_result(analysis_type: str, symbol: str, 
                       result_count: int, duration: float):
    """分析結果ログを記録"""
    logger_config.log_analysis_result(analysis_type, symbol, result_count, duration)

def log_user_action(user_id: str, action: str, details: dict = None):
    """ユーザーアクションログを記録"""
    logger_config.log_user_action(user_id, action, details)

# パフォーマンス測定デコレータ
import time
from functools import wraps

def measure_performance(operation_name: str = None):
    """関数の実行時間を測定するデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_performance(operation, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_performance(operation, duration, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator

# エラーハンドリングデコレータ
def log_errors(logger_name: str = None):
    """エラーをログに記録するデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"エラーが発生しました: {func.__name__} - {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator
