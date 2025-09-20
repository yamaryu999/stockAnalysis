import os
import json
import yaml
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class DatabaseConfig:
    """データベース設定"""
    db_path: str = "stock_analysis.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    cleanup_days: int = 30

@dataclass
class CacheConfig:
    """キャッシュ設定"""
    cache_dir: str = "cache"
    default_ttl: int = 3600  # 1時間
    stock_data_ttl: int = 1800  # 30分
    financial_metrics_ttl: int = 3600  # 1時間
    analysis_results_ttl: int = 7200  # 2時間
    max_memory_cache_size: int = 1000
    cleanup_interval_hours: int = 6

@dataclass
class APIConfig:
    """API設定"""
    yahoo_finance_rate_limit: float = 0.2  # 秒
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "StockAnalysisTool/1.0"
    max_workers: int = 3

@dataclass
class LoggingConfig:
    """ログ設定"""
    log_dir: str = "logs"
    log_level: str = "INFO"
    max_file_size_mb: int = 10
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_json: bool = False

@dataclass
class AnalysisConfig:
    """分析設定"""
    max_stocks_per_analysis: int = 1000
    default_period: str = "1y"
    min_data_points: int = 30
    confidence_threshold: float = 0.7
    enable_ml_analysis: bool = True
    enable_news_analysis: bool = True
    enable_technical_analysis: bool = True

@dataclass
class UIConfig:
    """UI設定"""
    theme: str = "dark"
    language: str = "ja"
    currency: str = "JPY"
    auto_refresh: bool = True
    refresh_interval_minutes: int = 5
    max_display_results: int = 100
    enable_animations: bool = True

@dataclass
class SecurityConfig:
    """セキュリティ設定"""
    enable_api_key_validation: bool = False
    max_requests_per_minute: int = 100
    enable_cors: bool = True
    allowed_origins: list = None
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:8501", "http://localhost:8504"]

@dataclass
class AppConfig:
    """アプリケーション全体の設定"""
    database: DatabaseConfig
    cache: CacheConfig
    api: APIConfig
    logging: LoggingConfig
    analysis: AnalysisConfig
    ui: UIConfig
    security: SecurityConfig
    
    # アプリケーション情報
    app_name: str = "日本株価分析ツール"
    app_version: str = "4.0.0"
    app_description: str = "AI分析機能付き株価分析ツール"
    
    # 開発者情報
    developer: str = "yamaryu"
    github_url: str = "https://github.com/yamaryu999/stockAnalysis"
    
    def __post_init__(self):
        # デフォルト値で初期化
        if not hasattr(self, 'database') or self.database is None:
            self.database = DatabaseConfig()
        if not hasattr(self, 'cache') or self.cache is None:
            self.cache = CacheConfig()
        if not hasattr(self, 'api') or self.api is None:
            self.api = APIConfig()
        if not hasattr(self, 'logging') or self.logging is None:
            self.logging = LoggingConfig()
        if not hasattr(self, 'analysis') or self.analysis is None:
            self.analysis = AnalysisConfig()
        if not hasattr(self, 'ui') or self.ui is None:
            self.ui = UIConfig()
        if not hasattr(self, 'security') or self.security is None:
            self.security = SecurityConfig()

class ConfigManager:
    """設定管理クラス"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self._config: Optional[AppConfig] = None
        self._load_config()
    
    def _load_config(self):
        """設定を読み込み"""
        try:
            if os.path.exists(self.config_file):
                self._config = self._load_from_file(self.config_file)
                self.logger.info(f"設定ファイルを読み込みました: {self.config_file}")
            else:
                # デフォルト設定を作成
                self._config = self._create_default_config()
                self._save_config()
                self.logger.info("デフォルト設定を作成しました")
                
        except Exception as e:
            self.logger.error(f"設定読み込みエラー: {e}")
            self._config = self._create_default_config()
    
    def _create_default_config(self) -> AppConfig:
        """デフォルト設定を作成"""
        return AppConfig(
            database=DatabaseConfig(),
            cache=CacheConfig(),
            api=APIConfig(),
            logging=LoggingConfig(),
            analysis=AnalysisConfig(),
            ui=UIConfig(),
            security=SecurityConfig()
        )
    
    def _load_from_file(self, file_path: str) -> AppConfig:
        """ファイルから設定を読み込み"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"サポートされていないファイル形式: {file_path.suffix}")
        
        return self._dict_to_config(data)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """辞書から設定オブジェクトを作成"""
        config_data = {}
        
        # 各セクションの設定を処理
        for section_name, section_class in [
            ('database', DatabaseConfig),
            ('cache', CacheConfig),
            ('api', APIConfig),
            ('logging', LoggingConfig),
            ('analysis', AnalysisConfig),
            ('ui', UIConfig),
            ('security', SecurityConfig)
        ]:
            if section_name in data:
                section_data = data[section_name]
                config_data[section_name] = section_class(**section_data)
            else:
                config_data[section_name] = section_class()
        
        # アプリケーション情報
        for key in ['app_name', 'app_version', 'app_description', 'developer', 'github_url']:
            if key in data:
                config_data[key] = data[key]
        
        return AppConfig(**config_data)
    
    def _save_config(self):
        """設定をファイルに保存"""
        try:
            config_dict = self._config_to_dict()
            
            file_path = Path(self.config_file)
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, ensure_ascii=False, indent=2)
            elif file_path.suffix.lower() in ['.yml', '.yaml']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"設定を保存しました: {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """設定オブジェクトを辞書に変換"""
        config_dict = asdict(self._config)
        return config_dict
    
    def get_config(self) -> AppConfig:
        """現在の設定を取得"""
        return self._config
    
    def update_config(self, **kwargs):
        """設定を更新"""
        try:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                else:
                    self.logger.warning(f"不明な設定キー: {key}")
            
            self._save_config()
            self.logger.info("設定を更新しました")
            
        except Exception as e:
            self.logger.error(f"設定更新エラー: {e}")
    
    def update_section(self, section_name: str, **kwargs):
        """特定のセクションの設定を更新"""
        try:
            if hasattr(self._config, section_name):
                section = getattr(self._config, section_name)
                for key, value in kwargs.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
                    else:
                        self.logger.warning(f"不明な設定キー: {section_name}.{key}")
                
                self._save_config()
                self.logger.info(f"{section_name}セクションの設定を更新しました")
            else:
                self.logger.error(f"不明なセクション: {section_name}")
                
        except Exception as e:
            self.logger.error(f"セクション設定更新エラー: {e}")
    
    def get_database_config(self) -> DatabaseConfig:
        """データベース設定を取得"""
        return self._config.database
    
    def get_cache_config(self) -> CacheConfig:
        """キャッシュ設定を取得"""
        return self._config.cache
    
    def get_api_config(self) -> APIConfig:
        """API設定を取得"""
        return self._config.api
    
    def get_logging_config(self) -> LoggingConfig:
        """ログ設定を取得"""
        return self._config.logging
    
    def get_analysis_config(self) -> AnalysisConfig:
        """分析設定を取得"""
        return self._config.analysis
    
    def get_ui_config(self) -> UIConfig:
        """UI設定を取得"""
        return self._config.ui
    
    def get_security_config(self) -> SecurityConfig:
        """セキュリティ設定を取得"""
        return self._config.security
    
    def reset_to_default(self):
        """設定をデフォルトにリセット"""
        try:
            self._config = self._create_default_config()
            self._save_config()
            self.logger.info("設定をデフォルトにリセットしました")
            
        except Exception as e:
            self.logger.error(f"設定リセットエラー: {e}")
    
    def export_config(self, export_path: str):
        """設定をエクスポート"""
        try:
            config_dict = self._config_to_dict()
            
            export_file = Path(export_path)
            if export_file.suffix.lower() == '.json':
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, ensure_ascii=False, indent=2)
            elif export_file.suffix.lower() in ['.yml', '.yaml']:
                with open(export_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"サポートされていないファイル形式: {export_file.suffix}")
            
            self.logger.info(f"設定をエクスポートしました: {export_path}")
            
        except Exception as e:
            self.logger.error(f"設定エクスポートエラー: {e}")
    
    def import_config(self, import_path: str):
        """設定をインポート"""
        try:
            imported_config = self._load_from_file(import_path)
            self._config = imported_config
            self._save_config()
            self.logger.info(f"設定をインポートしました: {import_path}")
            
        except Exception as e:
            self.logger.error(f"設定インポートエラー: {e}")
    
    def validate_config(self) -> bool:
        """設定の妥当性を検証"""
        try:
            # 基本的な検証
            if not self._config:
                return False
            
            # データベース設定の検証
            db_config = self._config.database
            if not db_config.db_path or not isinstance(db_config.db_path, str):
                self.logger.error("データベースパスが無効です")
                return False
            
            # キャッシュ設定の検証
            cache_config = self._config.cache
            if cache_config.default_ttl <= 0:
                self.logger.error("キャッシュTTLが無効です")
                return False
            
            # API設定の検証
            api_config = self._config.api
            if api_config.max_retries < 0 or api_config.timeout <= 0:
                self.logger.error("API設定が無効です")
                return False
            
            # 分析設定の検証
            analysis_config = self._config.analysis
            if analysis_config.max_stocks_per_analysis <= 0:
                self.logger.error("分析設定が無効です")
                return False
            
            self.logger.info("設定の検証が完了しました")
            return True
            
        except Exception as e:
            self.logger.error(f"設定検証エラー: {e}")
            return False

# グローバル設定マネージャーインスタンス
config_manager = ConfigManager()

# 便利な関数
def get_config() -> AppConfig:
    """現在の設定を取得"""
    return config_manager.get_config()

def get_database_config() -> DatabaseConfig:
    """データベース設定を取得"""
    return config_manager.get_database_config()

def get_cache_config() -> CacheConfig:
    """キャッシュ設定を取得"""
    return config_manager.get_cache_config()

def get_api_config() -> APIConfig:
    """API設定を取得"""
    return config_manager.get_api_config()

def get_logging_config() -> LoggingConfig:
    """ログ設定を取得"""
    return config_manager.get_logging_config()

def get_analysis_config() -> AnalysisConfig:
    """分析設定を取得"""
    return config_manager.get_analysis_config()

def get_ui_config() -> UIConfig:
    """UI設定を取得"""
    return config_manager.get_ui_config()

def get_security_config() -> SecurityConfig:
    """セキュリティ設定を取得"""
    return config_manager.get_security_config()

def update_config(**kwargs):
    """設定を更新"""
    config_manager.update_config(**kwargs)

def update_section(section_name: str, **kwargs):
    """特定のセクションの設定を更新"""
    config_manager.update_section(section_name, **kwargs)
