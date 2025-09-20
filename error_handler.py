import logging
import traceback
import functools
from typing import Any, Callable, Optional, Union, Dict
from datetime import datetime
import json
import os

class StockAnalysisError(Exception):
    """株価分析ツールの基底例外クラス"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """例外情報を辞書形式で取得"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class DataFetchError(StockAnalysisError):
    """データ取得エラー"""
    
    def __init__(self, message: str, symbol: str = None, api_name: str = None, details: Dict = None):
        super().__init__(message, "DATA_FETCH_ERROR", details)
        self.symbol = symbol
        self.api_name = api_name

class AnalysisError(StockAnalysisError):
    """分析エラー"""
    
    def __init__(self, message: str, analysis_type: str = None, symbol: str = None, details: Dict = None):
        super().__init__(message, "ANALYSIS_ERROR", details)
        self.analysis_type = analysis_type
        self.symbol = symbol

class ConfigurationError(StockAnalysisError):
    """設定エラー"""
    
    def __init__(self, message: str, config_key: str = None, details: Dict = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key

class DatabaseError(StockAnalysisError):
    """データベースエラー"""
    
    def __init__(self, message: str, operation: str = None, table: str = None, details: Dict = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation
        self.table = table

class CacheError(StockAnalysisError):
    """キャッシュエラー"""
    
    def __init__(self, message: str, cache_key: str = None, operation: str = None, details: Dict = None):
        super().__init__(message, "CACHE_ERROR", details)
        self.cache_key = cache_key
        self.operation = operation

class ValidationError(StockAnalysisError):
    """バリデーションエラー"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value

class RateLimitError(StockAnalysisError):
    """レート制限エラー"""
    
    def __init__(self, message: str, api_name: str = None, retry_after: int = None, details: Dict = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.api_name = api_name
        self.retry_after = retry_after

class ErrorHandler:
    """エラーハンドリングクラス"""
    
    def __init__(self, log_errors: bool = True, save_errors: bool = True, error_log_file: str = "error_log.json"):
        self.log_errors = log_errors
        self.save_errors = save_errors
        self.error_log_file = error_log_file
        self.logger = logging.getLogger(__name__)
        self._error_count = 0
        self._max_errors_per_session = 1000
    
    def handle_error(self, error: Exception, context: Dict = None) -> Dict:
        """エラーを処理"""
        self._error_count += 1
        
        # エラー情報を構築
        error_info = {
            'error_id': f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._error_count:04d}",
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # カスタムエラーの場合は詳細情報を追加
        if isinstance(error, StockAnalysisError):
            error_info.update(error.to_dict())
        
        # ログに記録
        if self.log_errors:
            self._log_error(error_info)
        
        # ファイルに保存
        if self.save_errors:
            self._save_error(error_info)
        
        # エラー数制限チェック
        if self._error_count >= self._max_errors_per_session:
            self.logger.critical(f"エラー数が上限に達しました: {self._max_errors_per_session}")
        
        return error_info
    
    def _log_error(self, error_info: Dict):
        """エラーをログに記録"""
        try:
            error_type = error_info['error_type']
            error_message = error_info['error_message']
            error_id = error_info['error_id']
            
            if error_type in ['DataFetchError', 'RateLimitError']:
                self.logger.warning(f"[{error_id}] {error_type}: {error_message}")
            elif error_type in ['ValidationError', 'ConfigurationError']:
                self.logger.error(f"[{error_id}] {error_type}: {error_message}")
            else:
                self.logger.error(f"[{error_id}] {error_type}: {error_message}", exc_info=True)
                
        except Exception as e:
            self.logger.critical(f"エラーログ記録に失敗: {e}")
    
    def _save_error(self, error_info: Dict):
        """エラーをファイルに保存"""
        try:
            # エラーログファイルが存在しない場合は作成
            if not os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            
            # 既存のエラーログを読み込み
            with open(self.error_log_file, 'r', encoding='utf-8') as f:
                error_log = json.load(f)
            
            # 新しいエラーを追加
            error_log.append(error_info)
            
            # 最新1000件のみ保持
            if len(error_log) > 1000:
                error_log = error_log[-1000:]
            
            # ファイルに保存
            with open(self.error_log_file, 'w', encoding='utf-8') as f:
                json.dump(error_log, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.critical(f"エラーファイル保存に失敗: {e}")
    
    def get_error_statistics(self) -> Dict:
        """エラー統計情報を取得"""
        try:
            if not os.path.exists(self.error_log_file):
                return {'total_errors': 0, 'error_types': {}, 'recent_errors': []}
            
            with open(self.error_log_file, 'r', encoding='utf-8') as f:
                error_log = json.load(f)
            
            # エラー種別の集計
            error_types = {}
            for error in error_log:
                error_type = error.get('error_type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # 最近のエラー（最新10件）
            recent_errors = error_log[-10:] if error_log else []
            
            return {
                'total_errors': len(error_log),
                'session_errors': self._error_count,
                'error_types': error_types,
                'recent_errors': recent_errors
            }
            
        except Exception as e:
            self.logger.error(f"エラー統計取得に失敗: {e}")
            return {'total_errors': 0, 'error_types': {}, 'recent_errors': []}
    
    def clear_error_log(self):
        """エラーログをクリア"""
        try:
            if os.path.exists(self.error_log_file):
                os.remove(self.error_log_file)
            self._error_count = 0
            self.logger.info("エラーログをクリアしました")
        except Exception as e:
            self.logger.error(f"エラーログクリアに失敗: {e}")

# グローバルエラーハンドラーインスタンス
error_handler = ErrorHandler()

# デコレータ関数
def handle_errors(context: Dict = None, reraise: bool = True, return_default: Any = None):
    """エラーハンドリングデコレータ"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # エラー情報を構築
                error_context = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200],  # 長すぎる場合は切り詰め
                    'kwargs': str(kwargs)[:200],
                    **(context or {})
                }
                
                # エラーを処理
                error_info = error_handler.handle_error(e, error_context)
                
                # エラーを再発生させるか、デフォルト値を返すか
                if reraise:
                    raise
                else:
                    return return_default
        
        return wrapper
    return decorator

def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0, 
                  exceptions: tuple = (Exception,)):
    """リトライ機能付きエラーハンドリングデコレータ"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # エラーをログに記録
                        error_context = {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_retries': max_retries,
                            'delay': current_delay
                        }
                        error_handler.handle_error(e, error_context)
                        
                        # 待機
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # 最終試行でも失敗した場合
                        error_context = {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_retries': max_retries,
                            'final_attempt': True
                        }
                        error_handler.handle_error(e, error_context)
                        raise
            
            # ここには到達しないはずだが、念のため
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def validate_input(**validators):
    """入力値検証デコレータ"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 引数の検証
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        if not validator(value):
                            raise ValidationError(
                                f"パラメータ '{param_name}' の値が無効です: {value}",
                                field=param_name,
                                value=value
                            )
                    except Exception as e:
                        if isinstance(e, ValidationError):
                            raise
                        else:
                            raise ValidationError(
                                f"パラメータ '{param_name}' の検証中にエラーが発生しました: {e}",
                                field=param_name,
                                value=value
                            )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# 便利な検証関数
def is_positive(value):
    """正の数かチェック"""
    return isinstance(value, (int, float)) and value > 0

def is_non_negative(value):
    """非負数かチェック"""
    return isinstance(value, (int, float)) and value >= 0

def is_string(value):
    """文字列かチェック"""
    return isinstance(value, str)

def is_not_empty(value):
    """空でないかチェック"""
    return value is not None and str(value).strip() != ""

def is_valid_symbol(value):
    """有効な銘柄コードかチェック"""
    if not isinstance(value, str):
        return False
    # 基本的な銘柄コード形式をチェック（4桁の数字 + .T）
    return len(value) == 6 and value.endswith('.T') and value[:4].isdigit()

# 便利な関数
def handle_error(error: Exception, context: Dict = None) -> Dict:
    """エラーを処理"""
    return error_handler.handle_error(error, context)

def get_error_statistics() -> Dict:
    """エラー統計情報を取得"""
    return error_handler.get_error_statistics()

def clear_error_log():
    """エラーログをクリア"""
    error_handler.clear_error_log()
