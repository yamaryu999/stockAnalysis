"""
Comprehensive Security Management System
包括的セキュリティ管理システム - 暗号化、アクセス制御、監査ログ、脅威検出
"""

import hashlib
import hmac
import secrets
import base64
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from collections import deque
from enum import Enum
import os
import ipaddress
import re
import sqlite3
from contextlib import contextmanager
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
import warnings
warnings.filterwarnings('ignore')

class SecurityLevel(Enum):
    """セキュリティレベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """脅威タイプ"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALICIOUS_REQUEST = "malicious_request"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

@dataclass
class SecurityEvent:
    """セキュリティイベント"""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class AccessControlRule:
    """アクセス制御ルール"""
    rule_id: str
    resource: str
    action: str
    conditions: Dict[str, Any]
    allowed: bool
    priority: int
    enabled: bool = True

@dataclass
class UserSession:
    """ユーザーセッション"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True

class EncryptionManager:
    """暗号化管理クラス"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.master_key = master_key or self._generate_master_key()
        self.fernet = Fernet(self._derive_key(self.master_key))
        
        # 非対称暗号化用のキーペア
        self.private_key, self.public_key = self._generate_key_pair()
    
    def _generate_master_key(self) -> str:
        """マスターキーを生成"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _derive_key(self, password: str) -> bytes:
        """パスワードからキーを導出"""
        password_bytes = password.encode()
        salt = b'stock_analysis_salt'  # 実際の実装ではランダムなソルトを使用
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def _generate_key_pair(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """RSAキーペアを生成"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def encrypt_data(self, data: Union[str, bytes, Dict]) -> str:
        """データを暗号化"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data, default=str)
            elif isinstance(data, str):
                data = data.encode()
            
            encrypted_data = self.fernet.encrypt(data)
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"データ暗号化エラー: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict]:
        """データを復号化"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            
            # JSONとして解析を試行
            try:
                return json.loads(decrypted_data.decode())
            except json.JSONDecodeError:
                return decrypted_data.decode()
                
        except Exception as e:
            self.logger.error(f"データ復号化エラー: {e}")
            raise
    
    def encrypt_with_public_key(self, data: str) -> str:
        """公開鍵でデータを暗号化"""
        try:
            encrypted_data = self.public_key.encrypt(
                data.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"公開鍵暗号化エラー: {e}")
            raise
    
    def decrypt_with_private_key(self, encrypted_data: str) -> str:
        """秘密鍵でデータを復号化"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"秘密鍵復号化エラー: {e}")
            raise
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """パスワードをハッシュ化"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        
        return base64.b64encode(password_hash).decode(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """パスワードを検証"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(computed_hash, password_hash)
        except Exception as e:
            self.logger.error(f"パスワード検証エラー: {e}")
            return False

class AccessControlManager:
    """アクセス制御管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.access_rules = {}
        self.user_permissions = {}
        self.session_manager = SessionManager()
        
    def add_access_rule(self, rule: AccessControlRule):
        """アクセス制御ルールを追加"""
        self.access_rules[rule.rule_id] = rule
        self.logger.info(f"アクセス制御ルール追加: {rule.rule_id}")
    
    def remove_access_rule(self, rule_id: str):
        """アクセス制御ルールを削除"""
        if rule_id in self.access_rules:
            del self.access_rules[rule_id]
            self.logger.info(f"アクセス制御ルール削除: {rule_id}")
    
    def check_access(self, user_id: str, resource: str, action: str, 
                    context: Dict[str, Any] = None) -> bool:
        """アクセス権限をチェック"""
        try:
            # セッションの有効性をチェック
            if not self.session_manager.is_session_valid(user_id):
                self.logger.warning(f"無効なセッション: {user_id}")
                return False
            
            # ユーザーの権限をチェック
            if not self._check_user_permissions(user_id, resource, action):
                return False
            
            # アクセス制御ルールをチェック
            if not self._evaluate_access_rules(user_id, resource, action, context):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"アクセスチェックエラー: {e}")
            return False
    
    def _check_user_permissions(self, user_id: str, resource: str, action: str) -> bool:
        """ユーザー権限をチェック"""
        if user_id not in self.user_permissions:
            return False
        
        user_perms = self.user_permissions[user_id]
        
        # 管理者権限のチェック
        if user_perms.get('role') == 'admin':
            return True
        
        # リソース別権限のチェック
        resource_perms = user_perms.get('resources', {})
        if resource in resource_perms:
            return action in resource_perms[resource]
        
        return False
    
    def _evaluate_access_rules(self, user_id: str, resource: str, action: str, 
                             context: Dict[str, Any] = None) -> bool:
        """アクセス制御ルールを評価"""
        applicable_rules = []
        
        for rule in self.access_rules.values():
            if not rule.enabled:
                continue
            
            if rule.resource == resource or rule.resource == '*':
                if rule.action == action or rule.action == '*':
                    applicable_rules.append(rule)
        
        # 優先度順にソート
        applicable_rules.sort(key=lambda x: x.priority, reverse=True)
        
        # ルールを評価
        for rule in applicable_rules:
            if self._evaluate_rule_conditions(rule, user_id, context):
                return rule.allowed
        
        # デフォルトは拒否
        return False
    
    def _evaluate_rule_conditions(self, rule: AccessControlRule, user_id: str, 
                                context: Dict[str, Any] = None) -> bool:
        """ルール条件を評価"""
        try:
            conditions = rule.conditions
            
            # IPアドレス制限
            if 'allowed_ips' in conditions:
                client_ip = context.get('ip_address', '') if context else ''
                if not self._check_ip_access(client_ip, conditions['allowed_ips']):
                    return False
            
            # 時間制限
            if 'time_restrictions' in conditions:
                if not self._check_time_restrictions(conditions['time_restrictions']):
                    return False
            
            # ユーザーグループ制限
            if 'user_groups' in conditions:
                user_groups = self.user_permissions.get(user_id, {}).get('groups', [])
                if not any(group in conditions['user_groups'] for group in user_groups):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"ルール条件評価エラー: {e}")
            return False
    
    def _check_ip_access(self, client_ip: str, allowed_ips: List[str]) -> bool:
        """IPアドレスアクセスをチェック"""
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            for allowed_ip in allowed_ips:
                if '/' in allowed_ip:
                    # CIDR表記
                    network = ipaddress.ip_network(allowed_ip, strict=False)
                    if client_ip_obj in network:
                        return True
                else:
                    # 単一IP
                    if client_ip == allowed_ip:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"IPアドレスチェックエラー: {e}")
            return False
    
    def _check_time_restrictions(self, time_restrictions: Dict[str, Any]) -> bool:
        """時間制限をチェック"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            current_weekday = current_time.weekday()
            
            # 時間制限
            if 'hours' in time_restrictions:
                allowed_hours = time_restrictions['hours']
                if current_hour not in allowed_hours:
                    return False
            
            # 曜日制限
            if 'weekdays' in time_restrictions:
                allowed_weekdays = time_restrictions['weekdays']
                if current_weekday not in allowed_weekdays:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"時間制限チェックエラー: {e}")
            return False

class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self, session_timeout: int = 3600):
        self.logger = logging.getLogger(__name__)
        self.session_timeout = session_timeout
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        
    def create_session(self, user_id: str, ip_address: str, 
                      user_agent: str) -> str:
        """セッションを作成"""
        try:
            session_id = secrets.token_urlsafe(32)
            current_time = datetime.now()
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=current_time,
                last_activity=current_time,
                expires_at=current_time + timedelta(seconds=self.session_timeout)
            )
            
            with self.session_lock:
                self.active_sessions[session_id] = session
            
            self.logger.info(f"セッション作成: {user_id} ({session_id[:8]}...)")
            return session_id
            
        except Exception as e:
            self.logger.error(f"セッション作成エラー: {e}")
            raise
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """セッションを検証"""
        try:
            with self.session_lock:
                session = self.active_sessions.get(session_id)
                
                if not session:
                    return None
                
                if not session.is_active:
                    return None
                
                if datetime.now() > session.expires_at:
                    session.is_active = False
                    return None
                
                # 最終アクティビティを更新
                session.last_activity = datetime.now()
                
                return session
                
        except Exception as e:
            self.logger.error(f"セッション検証エラー: {e}")
            return None
    
    def is_session_valid(self, user_id: str) -> bool:
        """セッションの有効性をチェック"""
        with self.session_lock:
            for session in self.active_sessions.values():
                if session.user_id == user_id and session.is_active:
                    if datetime.now() <= session.expires_at:
                        return True
            return False
    
    def invalidate_session(self, session_id: str):
        """セッションを無効化"""
        try:
            with self.session_lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id].is_active = False
                    self.logger.info(f"セッション無効化: {session_id[:8]}...")
                    
        except Exception as e:
            self.logger.error(f"セッション無効化エラー: {e}")
    
    def invalidate_user_sessions(self, user_id: str):
        """ユーザーの全セッションを無効化"""
        try:
            with self.session_lock:
                for session in self.active_sessions.values():
                    if session.user_id == user_id:
                        session.is_active = False
                
                self.logger.info(f"ユーザーセッション無効化: {user_id}")
                
        except Exception as e:
            self.logger.error(f"ユーザーセッション無効化エラー: {e}")
    
    def cleanup_expired_sessions(self):
        """期限切れセッションをクリーンアップ"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            with self.session_lock:
                for session_id, session in self.active_sessions.items():
                    if current_time > session.expires_at:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
            
            if expired_sessions:
                self.logger.info(f"期限切れセッションクリーンアップ: {len(expired_sessions)}件")
                
        except Exception as e:
            self.logger.error(f"セッションクリーンアップエラー: {e}")

class ThreatDetector:
    """脅威検出クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.threat_patterns = self._load_threat_patterns()
        self.attack_attempts = {}
        self.blocked_ips = set()
        
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """脅威パターンを読み込み"""
        return {
            'sql_injection': [
                r"('|(\\')|(;)|(\\;)|(\\*)|(\\|)|(\\-\\-)|(\\/\\*)|(\\*\\/))",
                r"(union|select|insert|update|delete|drop|create|alter)",
                r"(script|javascript|vbscript|onload|onerror)",
                r"(<script|</script|javascript:|vbscript:)"
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"vbscript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*="
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c"
            ],
            'command_injection': [
                r"[;&|`$]",
                r"(cat|ls|dir|type|more|less|head|tail|grep|find|awk|sed)",
                r"(wget|curl|nc|netcat|telnet|ftp|ssh)"
            ]
        }
    
    def detect_threat(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """脅威を検出"""
        try:
            # IPアドレスをチェック
            client_ip = request_data.get('ip_address', '')
            if client_ip in self.blocked_ips:
                return self._create_security_event(
                    ThreatType.UNAUTHORIZED_ACCESS,
                    SecurityLevel.HIGH,
                    client_ip,
                    "Blocked IP address attempted access"
                )
            
            # ブルートフォース攻撃をチェック
            brute_force_event = self._detect_brute_force(client_ip)
            if brute_force_event:
                return brute_force_event
            
            # パターンマッチングによる脅威検出
            for threat_type, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if self._check_pattern(request_data, pattern):
                        return self._create_security_event(
                            ThreatType(threat_type),
                            SecurityLevel.HIGH,
                            client_ip,
                            f"Detected {threat_type} pattern"
                        )
            
            # レート制限をチェック
            rate_limit_event = self._check_rate_limit(client_ip)
            if rate_limit_event:
                return rate_limit_event
            
            return None
            
        except Exception as e:
            self.logger.error(f"脅威検出エラー: {e}")
            return None
    
    def _detect_brute_force(self, client_ip: str) -> Optional[SecurityEvent]:
        """ブルートフォース攻撃を検出"""
        try:
            current_time = time.time()
            window_start = current_time - 300  # 5分間のウィンドウ
            
            if client_ip not in self.attack_attempts:
                self.attack_attempts[client_ip] = []
            
            # 古い試行を削除
            self.attack_attempts[client_ip] = [
                attempt for attempt in self.attack_attempts[client_ip]
                if attempt > window_start
            ]
            
            # 新しい試行を追加
            self.attack_attempts[client_ip].append(current_time)
            
            # 閾値をチェック（5分間に10回以上）
            if len(self.attack_attempts[client_ip]) >= 10:
                self.blocked_ips.add(client_ip)
                return self._create_security_event(
                    ThreatType.BRUTE_FORCE,
                    SecurityLevel.CRITICAL,
                    client_ip,
                    f"Brute force attack detected: {len(self.attack_attempts[client_ip])} attempts"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"ブルートフォース検出エラー: {e}")
            return None
    
    def _check_pattern(self, request_data: Dict[str, Any], pattern: str) -> bool:
        """パターンをチェック"""
        try:
            # リクエストデータの全フィールドをチェック
            for key, value in request_data.items():
                if isinstance(value, str):
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
                elif isinstance(value, dict):
                    if self._check_pattern(value, pattern):
                        return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and re.search(pattern, item, re.IGNORECASE):
                            return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"パターンチェックエラー: {e}")
            return False
    
    def _check_rate_limit(self, client_ip: str) -> Optional[SecurityEvent]:
        """レート制限をチェック"""
        try:
            current_time = time.time()
            window_start = current_time - 60  # 1分間のウィンドウ
            
            if client_ip not in self.attack_attempts:
                self.attack_attempts[client_ip] = []
            
            # 最近のリクエスト数をカウント
            recent_requests = [
                attempt for attempt in self.attack_attempts[client_ip]
                if attempt > window_start
            ]
            
            # 1分間に100回以上のリクエスト
            if len(recent_requests) >= 100:
                return self._create_security_event(
                    ThreatType.RATE_LIMIT_EXCEEDED,
                    SecurityLevel.MEDIUM,
                    client_ip,
                    f"Rate limit exceeded: {len(recent_requests)} requests per minute"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"レート制限チェックエラー: {e}")
            return None
    
    def _create_security_event(self, threat_type: ThreatType, severity: SecurityLevel,
                             source_ip: str, description: str) -> SecurityEvent:
        """セキュリティイベントを作成"""
        return SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            timestamp=datetime.now(),
            event_type=threat_type.value,
            severity=severity,
            source_ip=source_ip,
            user_id=None,
            description=description,
            details={'threat_type': threat_type.value}
        )

class AuditLogger:
    """監査ログクラス"""
    
    def __init__(self, db_path: str = "security_audit.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """データベースを初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_events (
                        event_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        source_ip TEXT NOT NULL,
                        user_id TEXT,
                        description TEXT NOT NULL,
                        details TEXT,
                        resolved BOOLEAN DEFAULT 0,
                        resolved_at TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS access_logs (
                        log_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        user_id TEXT,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT,
                        success BOOLEAN NOT NULL,
                        details TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS authentication_logs (
                        log_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        user_id TEXT,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT,
                        success BOOLEAN NOT NULL,
                        failure_reason TEXT,
                        details TEXT
                    )
                """)
                
                # インデックスの作成
                conn.execute("CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs(user_id)")
                
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}")
    
    def log_security_event(self, event: SecurityEvent):
        """セキュリティイベントをログ"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO security_events 
                    (event_id, timestamp, event_type, severity, source_ip, user_id, 
                     description, details, resolved, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.severity.value,
                    event.source_ip,
                    event.user_id,
                    event.description,
                    json.dumps(event.details),
                    event.resolved,
                    event.resolved_at.isoformat() if event.resolved_at else None
                ))
                
        except Exception as e:
            self.logger.error(f"セキュリティイベントログエラー: {e}")
    
    def log_access(self, user_id: str, resource: str, action: str,
                  ip_address: str, user_agent: str, success: bool,
                  details: Dict[str, Any] = None):
        """アクセスログを記録"""
        try:
            log_id = secrets.token_urlsafe(16)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO access_logs 
                    (log_id, timestamp, user_id, resource, action, ip_address, 
                     user_agent, success, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id,
                    datetime.now().isoformat(),
                    user_id,
                    resource,
                    action,
                    ip_address,
                    user_agent,
                    success,
                    json.dumps(details) if details else None
                ))
                
        except Exception as e:
            self.logger.error(f"アクセスログエラー: {e}")
    
    def log_authentication(self, user_id: str, ip_address: str, user_agent: str,
                          success: bool, failure_reason: str = None,
                          details: Dict[str, Any] = None):
        """認証ログを記録"""
        try:
            log_id = secrets.token_urlsafe(16)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO authentication_logs 
                    (log_id, timestamp, user_id, ip_address, user_agent, 
                     success, failure_reason, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id,
                    datetime.now().isoformat(),
                    user_id,
                    ip_address,
                    user_agent,
                    success,
                    failure_reason,
                    json.dumps(details) if details else None
                ))
                
        except Exception as e:
            self.logger.error(f"認証ログエラー: {e}")
    
    def get_security_events(self, start_date: datetime = None, 
                           end_date: datetime = None,
                           severity: SecurityLevel = None) -> List[SecurityEvent]:
        """セキュリティイベントを取得"""
        try:
            query = "SELECT * FROM security_events WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            query += " ORDER BY timestamp DESC LIMIT 1000"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = SecurityEvent(
                        event_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        event_type=row[2],
                        severity=SecurityLevel(row[3]),
                        source_ip=row[4],
                        user_id=row[5],
                        description=row[6],
                        details=json.loads(row[7]) if row[7] else {},
                        resolved=bool(row[8]),
                        resolved_at=datetime.fromisoformat(row[9]) if row[9] else None
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.logger.error(f"セキュリティイベント取得エラー: {e}")
            return []

class SecurityManager:
    """セキュリティ管理システム"""
    
    def __init__(self, master_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # コンポーネントの初期化
        self.encryption_manager = EncryptionManager(master_key)
        self.access_control = AccessControlManager()
        self.threat_detector = ThreatDetector()
        self.audit_logger = AuditLogger()
        
        # セキュリティ設定
        self.security_config = {
            'enable_encryption': True,
            'enable_access_control': True,
            'enable_threat_detection': True,
            'enable_audit_logging': True,
            'session_timeout': 3600,
            'max_login_attempts': 5,
            'lockout_duration': 900  # 15分
        }
        
        # ユーザー管理
        self.users = {}
        self.login_attempts = {}
        
        # デフォルトルールの設定
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """デフォルトセキュリティルールを設定"""
        # 管理者アクセスルール
        admin_rule = AccessControlRule(
            rule_id='admin_access',
            resource='*',
            action='*',
            conditions={},
            allowed=True,
            priority=100
        )
        self.access_control.add_access_rule(admin_rule)
        
        # 一般ユーザーアクセスルール
        user_rule = AccessControlRule(
            rule_id='user_access',
            resource='analysis',
            action='read',
            conditions={},
            allowed=True,
            priority=50
        )
        self.access_control.add_access_rule(user_rule)
    
    def create_user(self, user_id: str, password: str, role: str = 'user',
                   permissions: Dict[str, Any] = None) -> bool:
        """ユーザーを作成"""
        try:
            if user_id in self.users:
                self.logger.warning(f"ユーザー既存: {user_id}")
                return False
            
            # パスワードをハッシュ化
            password_hash, salt = self.encryption_manager.hash_password(password)
            
            # ユーザー情報を暗号化して保存
            user_data = {
                'user_id': user_id,
                'password_hash': password_hash,
                'salt': salt,
                'role': role,
                'permissions': permissions or {},
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            encrypted_user_data = self.encryption_manager.encrypt_data(user_data)
            self.users[user_id] = encrypted_user_data
            
            self.logger.info(f"ユーザー作成完了: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"ユーザー作成エラー: {e}")
            return False
    
    def authenticate_user(self, user_id: str, password: str, 
                         ip_address: str, user_agent: str) -> Tuple[bool, Optional[str]]:
        """ユーザー認証"""
        try:
            # ログイン試行回数をチェック
            if self._is_account_locked(user_id):
                self.audit_logger.log_authentication(
                    user_id, ip_address, user_agent, False, "Account locked"
                )
                return False, "Account locked due to too many failed attempts"
            
            # ユーザーの存在確認
            if user_id not in self.users:
                self._record_failed_attempt(user_id, ip_address)
                self.audit_logger.log_authentication(
                    user_id, ip_address, user_agent, False, "User not found"
                )
                return False, "Invalid credentials"
            
            # ユーザーデータを復号化
            encrypted_user_data = self.users[user_id]
            user_data = self.encryption_manager.decrypt_data(encrypted_user_data)
            
            # パスワード検証
            if not self.encryption_manager.verify_password(
                password, user_data['password_hash'], user_data['salt']
            ):
                self._record_failed_attempt(user_id, ip_address)
                self.audit_logger.log_authentication(
                    user_id, ip_address, user_agent, False, "Invalid password"
                )
                return False, "Invalid credentials"
            
            # アカウントの有効性確認
            if not user_data.get('is_active', True):
                self.audit_logger.log_authentication(
                    user_id, ip_address, user_agent, False, "Account disabled"
                )
                return False, "Account disabled"
            
            # 成功したログイン試行をクリア
            self._clear_failed_attempts(user_id)
            
            # セッション作成
            session_id = self.access_control.session_manager.create_session(
                user_id, ip_address, user_agent
            )
            
            # 認証ログ記録
            self.audit_logger.log_authentication(
                user_id, ip_address, user_agent, True
            )
            
            self.logger.info(f"認証成功: {user_id}")
            return True, session_id
            
        except Exception as e:
            self.logger.error(f"認証エラー: {e}")
            return False, "Authentication error"
    
    def _is_account_locked(self, user_id: str) -> bool:
        """アカウントがロックされているかチェック"""
        if user_id not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[user_id]
        if len(attempts) < self.security_config['max_login_attempts']:
            return False
        
        # 最新の試行時刻をチェック
        latest_attempt = max(attempts)
        lockout_duration = self.security_config['lockout_duration']
        
        return (time.time() - latest_attempt) < lockout_duration
    
    def _record_failed_attempt(self, user_id: str, ip_address: str):
        """失敗したログイン試行を記録"""
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = []
        
        self.login_attempts[user_id].append(time.time())
        
        # 古い試行を削除（24時間以上前）
        cutoff_time = time.time() - 86400
        self.login_attempts[user_id] = [
            attempt for attempt in self.login_attempts[user_id]
            if attempt > cutoff_time
        ]
    
    def _clear_failed_attempts(self, user_id: str):
        """失敗したログイン試行をクリア"""
        if user_id in self.login_attempts:
            del self.login_attempts[user_id]
    
    def check_access(self, session_id: str, resource: str, action: str,
                    context: Dict[str, Any] = None) -> bool:
        """アクセス権限をチェック"""
        try:
            # セッション検証
            session = self.access_control.session_manager.validate_session(session_id)
            if not session:
                return False
            
            # アクセス制御チェック
            has_access = self.access_control.check_access(
                session.user_id, resource, action, context
            )
            
            # アクセスログ記録
            self.audit_logger.log_access(
                session.user_id, resource, action,
                session.ip_address, session.user_agent, has_access, context
            )
            
            return has_access
            
        except Exception as e:
            self.logger.error(f"アクセスチェックエラー: {e}")
            return False
    
    def detect_threats(self, request_data: Dict[str, Any]) -> List[SecurityEvent]:
        """脅威を検出"""
        try:
            if not self.security_config['enable_threat_detection']:
                return []
            
            threat_event = self.threat_detector.detect_threat(request_data)
            if threat_event:
                # セキュリティイベントをログ
                if self.security_config['enable_audit_logging']:
                    self.audit_logger.log_security_event(threat_event)
                
                return [threat_event]
            
            return []
            
        except Exception as e:
            self.logger.error(f"脅威検出エラー: {e}")
            return []
    
    def encrypt_sensitive_data(self, data: Union[str, Dict]) -> str:
        """機密データを暗号化"""
        if not self.security_config['enable_encryption']:
            return json.dumps(data) if isinstance(data, dict) else str(data)
        
        return self.encryption_manager.encrypt_data(data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Union[str, Dict]:
        """機密データを復号化"""
        if not self.security_config['enable_encryption']:
            try:
                return json.loads(encrypted_data)
            except json.JSONDecodeError:
                return encrypted_data
        
        return self.encryption_manager.decrypt_data(encrypted_data)
    
    def get_security_report(self, days: int = 7) -> Dict[str, Any]:
        """セキュリティレポートを生成"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # セキュリティイベントを取得
            security_events = self.audit_logger.get_security_events(
                start_date, end_date
            )
            
            # 統計を計算
            event_stats = {}
            for event in security_events:
                event_type = event.event_type
                if event_type not in event_stats:
                    event_stats[event_type] = 0
                event_stats[event_type] += 1
            
            # 重大度別統計
            severity_stats = {}
            for event in security_events:
                severity = event.severity.value
                if severity not in severity_stats:
                    severity_stats[severity] = 0
                severity_stats[severity] += 1
            
            # アクティブセッション数
            active_sessions = len([
                session for session in self.access_control.session_manager.active_sessions.values()
                if session.is_active and datetime.now() <= session.expires_at
            ])
            
            return {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'security_events': {
                    'total': len(security_events),
                    'by_type': event_stats,
                    'by_severity': severity_stats
                },
                'active_sessions': active_sessions,
                'blocked_ips': len(self.threat_detector.blocked_ips),
                'locked_accounts': len(self.login_attempts),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"セキュリティレポート生成エラー: {e}")
            return {'error': str(e)}
    
    def update_security_config(self, config: Dict[str, Any]):
        """セキュリティ設定を更新"""
        try:
            self.security_config.update(config)
            self.logger.info("セキュリティ設定更新完了")
        except Exception as e:
            self.logger.error(f"セキュリティ設定更新エラー: {e}")

# グローバルインスタンス
security_manager = SecurityManager()
