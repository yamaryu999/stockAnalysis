"""
高度なアラートシステム
複雑な条件設定、通知配信、アラート管理機能
"""

import asyncio
import json
import logging
import smtplib
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Deque
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from enum import Enum
import sqlite3
import os
from collections import deque, defaultdict
import statistics

class AlertType(Enum):
    """アラートタイプ"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE_PERCENT = "price_change_percent"
    VOLUME_SPIKE = "volume_spike"
    TECHNICAL_SIGNAL = "technical_signal"
    NEWS_SENTIMENT = "news_sentiment"
    CUSTOM_CONDITION = "custom_condition"
    VWAP_DEVIATION = "vwap_deviation"
    VOLATILITY_SPIKE = "volatility_spike"
    BID_ASK_SPREAD = "bid_ask_spread"
    MOMENTUM_SHIFT = "momentum_shift"

class AlertSeverity(Enum):
    """アラート重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """通知チャネル"""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    DESKTOP = "desktop"
    SMS = "sms"
    LINE = "line"

@dataclass
class AlertCondition:
    """アラート条件クラス"""
    symbol: str
    alert_type: AlertType
    condition: str
    threshold_value: float
    comparison_operator: str  # '>', '<', '>=', '<=', '==', '!='
    time_window: int  # 分
    enabled: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AlertRule:
    """アラートルールクラス"""
    id: str
    name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity
    notification_channels: List[NotificationChannel]
    cooldown_period: int  # 分
    enabled: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AlertTrigger:
    """アラート発火クラス"""
    id: str
    rule_id: str
    symbol: str
    alert_type: AlertType
    condition: str
    current_value: float
    threshold_value: float
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]

class NotificationService:
    """通知サービスクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_notification_config()
    
    def _load_notification_config(self) -> Dict[str, Any]:
        """通知設定を読み込み"""
        try:
            config_file = 'notification_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # デフォルト設定
                return {
                    'email': {
                        'smtp_server': '',
                        'smtp_port': 587,
                        'username': '',
                        'password': '',
                        'from_email': '',
                        'enabled': False
                    },
                    'slack': {
                        'webhook_url': '',
                        'channel': '#alerts',
                        'enabled': False
                    },
                    'discord': {
                        'webhook_url': '',
                        'enabled': False
                    },
                    'line': {
                        'token': '',
                        'enabled': False
                    },
                    'desktop': {
                        'enabled': True
                    }
                }
        except Exception as e:
            self.logger.error(f"通知設定読み込みエラー: {e}")
            return {}
    
    async def send_notification(self, channel: NotificationChannel, message: str, 
                              alert_trigger: AlertTrigger) -> bool:
        """通知を送信"""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(message, alert_trigger)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(message, alert_trigger)
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord(message, alert_trigger)
            elif channel == NotificationChannel.DESKTOP:
                return await self._send_desktop(message, alert_trigger)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(message, alert_trigger)
            elif channel == NotificationChannel.LINE:
                return await self._send_line(message, alert_trigger)
            else:
                self.logger.warning(f"未対応の通知チャネル: {channel}")
                return False
                
        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")
            return False
    
    async def _send_email(self, message: str, alert_trigger: AlertTrigger) -> bool:
        """メール通知を送信"""
        try:
            email_config = self.config.get('email', {})
            if not email_config.get('enabled', False):
                return False
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = email_config.get('to_email', email_config['from_email'])
            msg['Subject'] = f"🚨 株価アラート: {alert_trigger.symbol}"
            
            body = f"""
            <html>
            <body>
                <h2>🚨 株価アラート</h2>
                <p><strong>銘柄:</strong> {alert_trigger.symbol}</p>
                <p><strong>アラートタイプ:</strong> {alert_trigger.alert_type.value}</p>
                <p><strong>現在値:</strong> {alert_trigger.current_value}</p>
                <p><strong>閾値:</strong> {alert_trigger.threshold_value}</p>
                <p><strong>重要度:</strong> {alert_trigger.severity.value}</p>
                <p><strong>メッセージ:</strong> {message}</p>
                <p><strong>発火時刻:</strong> {alert_trigger.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"メール通知送信完了: {alert_trigger.symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"メール送信エラー: {e}")
            return False
    
    async def _send_slack(self, message: str, alert_trigger: AlertTrigger) -> bool:
        """Slack通知を送信"""
        try:
            slack_config = self.config.get('slack', {})
            if not slack_config.get('enabled', False):
                return False
            
            webhook_url = slack_config['webhook_url']
            channel = slack_config.get('channel', '#alerts')
            
            severity_emoji = {
                AlertSeverity.LOW: "🟡",
                AlertSeverity.MEDIUM: "🟠",
                AlertSeverity.HIGH: "🔴",
                AlertSeverity.CRITICAL: "🚨"
            }
            
            payload = {
                "channel": channel,
                "username": "株価アラートボット",
                "icon_emoji": ":chart_with_upwards_trend:",
                "attachments": [
                    {
                        "color": "danger" if alert_trigger.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL] else "warning",
                        "title": f"{severity_emoji.get(alert_trigger.severity, '🔔')} 株価アラート",
                        "fields": [
                            {"title": "銘柄", "value": alert_trigger.symbol, "short": True},
                            {"title": "アラートタイプ", "value": alert_trigger.alert_type.value, "short": True},
                            {"title": "現在値", "value": str(alert_trigger.current_value), "short": True},
                            {"title": "閾値", "value": str(alert_trigger.threshold_value), "short": True},
                            {"title": "重要度", "value": alert_trigger.severity.value, "short": True},
                            {"title": "発火時刻", "value": alert_trigger.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                        ],
                        "text": message,
                        "footer": "株価分析ツール",
                        "ts": int(alert_trigger.timestamp.timestamp())
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Slack通知送信完了: {alert_trigger.symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Slack送信エラー: {e}")
            return False
    
    async def _send_discord(self, message: str, alert_trigger: AlertTrigger) -> bool:
        """Discord通知を送信"""
        try:
            discord_config = self.config.get('discord', {})
            if not discord_config.get('enabled', False):
                return False
            
            webhook_url = discord_config['webhook_url']
            
            severity_color = {
                AlertSeverity.LOW: 0xFFFF00,      # 黄色
                AlertSeverity.MEDIUM: 0xFF8C00,   # オレンジ
                AlertSeverity.HIGH: 0xFF0000,     # 赤
                AlertSeverity.CRITICAL: 0x8B0000  # ダークレッド
            }
            
            embed = {
                "title": f"🚨 株価アラート: {alert_trigger.symbol}",
                "description": message,
                "color": severity_color.get(alert_trigger.severity, 0x00FF00),
                "fields": [
                    {"name": "銘柄", "value": alert_trigger.symbol, "inline": True},
                    {"name": "アラートタイプ", "value": alert_trigger.alert_type.value, "inline": True},
                    {"name": "現在値", "value": str(alert_trigger.current_value), "inline": True},
                    {"name": "閾値", "value": str(alert_trigger.threshold_value), "inline": True},
                    {"name": "重要度", "value": alert_trigger.severity.value, "inline": True},
                    {"name": "発火時刻", "value": alert_trigger.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "inline": True}
                ],
                "footer": {"text": "株価分析ツール"},
                "timestamp": alert_trigger.timestamp.isoformat()
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Discord通知送信完了: {alert_trigger.symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Discord送信エラー: {e}")
            return False

    async def _send_line(self, message: str, alert_trigger: AlertTrigger) -> bool:
        """LINE Notify に通知を送信"""
        try:
            line_config = self.config.get('line', {})
            if not line_config.get('enabled', False):
                return False

            token = line_config.get('token')
            if not token:
                self.logger.warning("LINE通知トークンが設定されていません")
                return False

            severity_emoji = {
                AlertSeverity.LOW: "🟡",
                AlertSeverity.MEDIUM: "🟠",
                AlertSeverity.HIGH: "🔴",
                AlertSeverity.CRITICAL: "🚨"
            }

            emoji = severity_emoji.get(alert_trigger.severity, "🔔")
            payload = {
                'message': f"{emoji} {alert_trigger.symbol} ({alert_trigger.alert_type.value})\n{message}\n閾値: {alert_trigger.threshold_value}\n現在値: {alert_trigger.current_value}"
            }

            response = requests.post(
                'https://notify-api.line.me/api/notify',
                headers={'Authorization': f'Bearer {token}'},
                data=payload,
                timeout=10
            )
            response.raise_for_status()

            self.logger.info(f"LINE通知送信完了: {alert_trigger.symbol}")
            return True

        except Exception as e:
            self.logger.error(f"LINE送信エラー: {e}")
            return False
    
    async def _send_desktop(self, message: str, alert_trigger: AlertTrigger) -> bool:
        """デスクトップ通知を送信"""
        try:
            desktop_config = self.config.get('desktop', {})
            if not desktop_config.get('enabled', False):
                return False
            
            # Streamlitの通知機能を使用
            import streamlit as st
            
            severity_emoji = {
                AlertSeverity.LOW: "🟡",
                AlertSeverity.MEDIUM: "🟠", 
                AlertSeverity.HIGH: "🔴",
                AlertSeverity.CRITICAL: "🚨"
            }
            
            emoji = severity_emoji.get(alert_trigger.severity, "🔔")
            
            if alert_trigger.severity == AlertSeverity.CRITICAL:
                st.error(f"{emoji} {alert_trigger.symbol}: {message}")
            elif alert_trigger.severity == AlertSeverity.HIGH:
                st.error(f"{emoji} {alert_trigger.symbol}: {message}")
            elif alert_trigger.severity == AlertSeverity.MEDIUM:
                st.warning(f"{emoji} {alert_trigger.symbol}: {message}")
            else:
                st.info(f"{emoji} {alert_trigger.symbol}: {message}")
            
            self.logger.info(f"デスクトップ通知送信完了: {alert_trigger.symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"デスクトップ通知エラー: {e}")
            return False
    
    async def _send_webhook(self, message: str, alert_trigger: AlertTrigger) -> bool:
        """Webhook通知を送信"""
        try:
            webhook_config = self.config.get('webhook', {})
            if not webhook_config.get('enabled', False):
                return False
            
            webhook_url = webhook_config['url']
            
            payload = {
                "alert_id": alert_trigger.id,
                "symbol": alert_trigger.symbol,
                "alert_type": alert_trigger.alert_type.value,
                "current_value": alert_trigger.current_value,
                "threshold_value": alert_trigger.threshold_value,
                "severity": alert_trigger.severity.value,
                "message": message,
                "timestamp": alert_trigger.timestamp.isoformat(),
                "metadata": alert_trigger.metadata
            }
            
            headers = webhook_config.get('headers', {'Content-Type': 'application/json'})
            
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Webhook通知送信完了: {alert_trigger.symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Webhook送信エラー: {e}")
            return False

class AlertDatabase:
    """アラートデータベースクラス"""
    
    def __init__(self, db_path: str = "alerts.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """データベースを初期化"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # アラートルールテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    conditions TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    notification_channels TEXT NOT NULL,
                    cooldown_period INTEGER DEFAULT 60,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_triggered TIMESTAMP
                )
            """)
            
            # アラート発火履歴テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_triggers (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    threshold_value REAL NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (rule_id) REFERENCES alert_rules (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}")
    
    def save_alert_rule(self, rule: AlertRule) -> bool:
        """アラートルールを保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO alert_rules 
                (id, name, description, conditions, severity, notification_channels, 
                 cooldown_period, enabled, created_at, last_triggered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.id,
                rule.name,
                rule.description,
                json.dumps([asdict(condition) for condition in rule.conditions]),
                rule.severity.value,
                json.dumps([channel.value for channel in rule.notification_channels]),
                rule.cooldown_period,
                rule.enabled,
                rule.created_at.isoformat(),
                rule.last_triggered.isoformat() if rule.last_triggered else None
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"アラートルールを保存: {rule.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"アラートルール保存エラー: {e}")
            return False
    
    def load_alert_rules(self) -> List[AlertRule]:
        """アラートルールを読み込み"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM alert_rules WHERE enabled = 1")
            rows = cursor.fetchall()
            
            rules = []
            for row in rows:
                conditions_data = json.loads(row[3])
                conditions = [AlertCondition(**condition) for condition in conditions_data]
                
                notification_channels = [NotificationChannel(channel) for channel in json.loads(row[5])]
                
                rule = AlertRule(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    conditions=conditions,
                    severity=AlertSeverity(row[4]),
                    notification_channels=notification_channels,
                    cooldown_period=row[6],
                    enabled=bool(row[7]),
                    created_at=datetime.fromisoformat(row[8]),
                    last_triggered=datetime.fromisoformat(row[9]) if row[9] else None
                )
                rules.append(rule)
            
            conn.close()
            return rules
            
        except Exception as e:
            self.logger.error(f"アラートルール読み込みエラー: {e}")
            return []
    
    def save_alert_trigger(self, trigger: AlertTrigger) -> bool:
        """アラート発火を保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alert_triggers 
                (id, rule_id, symbol, alert_type, condition, current_value, 
                 threshold_value, severity, message, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trigger.id,
                trigger.rule_id,
                trigger.symbol,
                trigger.alert_type.value,
                trigger.condition,
                trigger.current_value,
                trigger.threshold_value,
                trigger.severity.value,
                trigger.message,
                trigger.timestamp.isoformat(),
                json.dumps(trigger.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"アラート発火を保存: {trigger.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"アラート発火保存エラー: {e}")
            return False
    
    def get_alert_history(self, symbol: Optional[str] = None, 
                         limit: int = 100) -> List[AlertTrigger]:
        """アラート履歴を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT * FROM alert_triggers 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (symbol, limit))
            else:
                cursor.execute("""
                    SELECT * FROM alert_triggers 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            
            triggers = []
            for row in rows:
                trigger = AlertTrigger(
                    id=row[0],
                    rule_id=row[1],
                    symbol=row[2],
                    alert_type=AlertType(row[3]),
                    condition=row[4],
                    current_value=row[5],
                    threshold_value=row[6],
                    severity=AlertSeverity(row[7]),
                    message=row[8],
                    timestamp=datetime.fromisoformat(row[9]),
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                triggers.append(trigger)
            
            conn.close()
            return triggers
            
        except Exception as e:
            self.logger.error(f"アラート履歴取得エラー: {e}")
            return []

class AdvancedAlertSystem:
    """高度なアラートシステム"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_service = NotificationService()
        self.database = AlertDatabase()
        
        # アラートルール
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # 実行状態
        self.is_running = False
        self.monitoring_thread = None
        
        # データソース
        self.data_sources = {}
        
        # コールバック
        self.alert_callbacks = []

        # リアルタイムスナップショット
        self.realtime_snapshots: Dict[str, Dict[str, Any]] = {}
        self.realtime_history: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=600))
        self.snapshot_ttl = timedelta(seconds=30)
        self.snapshot_lock = threading.Lock()

        # ルールを読み込み
        self._load_rules()
    
    def _load_rules(self):
        """ルールを読み込み"""
        try:
            rules = self.database.load_alert_rules()
            for rule in rules:
                self.alert_rules[rule.id] = rule
            
            self.logger.info(f"アラートルールを読み込み: {len(rules)}件")
            
        except Exception as e:
            self.logger.error(f"ルール読み込みエラー: {e}")
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """アラートルールを追加"""
        try:
            self.alert_rules[rule.id] = rule
            
            # データベースに保存
            success = self.database.save_alert_rule(rule)
            
            if success:
                self.logger.info(f"アラートルールを追加: {rule.id}")
                return True
            else:
                # データベース保存に失敗した場合はメモリからも削除
                del self.alert_rules[rule.id]
                return False
                
        except Exception as e:
            self.logger.error(f"アラートルール追加エラー: {e}")
            return False
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """アラートルールを削除"""
        try:
            if rule_id in self.alert_rules:
                del self.alert_rules[rule_id]
                self.logger.info(f"アラートルールを削除: {rule_id}")
                return True
            else:
                self.logger.warning(f"アラートルールが見つかりません: {rule_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"アラートルール削除エラー: {e}")
            return False
    
    def update_data_source(self, symbol: str, data_source: Callable[[], Dict[str, Any]]):
        """データソースを更新"""
        self.data_sources[symbol] = data_source

    def update_market_snapshot(self, symbol: str, snapshot: Dict[str, Any], timestamp: Optional[datetime] = None):
        """外部からのリアルタイムデータを取り込み"""
        try:
            ts = timestamp or datetime.now()

            enriched_snapshot = dict(snapshot)
            enriched_snapshot.setdefault('symbol', symbol)
            enriched_snapshot['timestamp'] = ts

            with self.snapshot_lock:
                self.realtime_snapshots[symbol] = enriched_snapshot
                history = self.realtime_history[symbol]
                history.append(dict(enriched_snapshot))

        except Exception as e:
            self.logger.error(f"スナップショット更新エラー: {e}")
    
    def start_monitoring(self):
        """監視を開始"""
        if self.is_running:
            self.logger.warning("アラート監視は既に実行中です")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info("アラート監視を開始")
    
    def stop_monitoring(self):
        """監視を停止"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        self.logger.info("アラート監視を停止")
    
    def _monitoring_loop(self):
        """監視ループ"""
        while self.is_running:
            try:
                for rule_id, rule in self.alert_rules.items():
                    if not rule.enabled:
                        continue
                    
                    # クールダウンチェック
                    if self._is_in_cooldown(rule):
                        continue
                    
                    # ルールの条件をチェック
                    triggered = self._check_rule_conditions(rule)
                    
                    if triggered:
                        self._trigger_alert(rule, triggered)
                
                time.sleep(1)  # 1秒間隔でチェック
                
            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                time.sleep(5)
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """クールダウン期間中かチェック"""
        if not rule.last_triggered:
            return False
        
        cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_period)
        return datetime.now() < cooldown_end
    
    def _check_rule_conditions(self, rule: AlertRule) -> Optional[Dict[str, Any]]:
        """ルールの条件をチェック"""
        try:
            for condition in rule.conditions:
                if not condition.enabled:
                    continue
                
                # データを取得
                data = self._get_symbol_data(condition.symbol)
                if not data:
                    continue

                # 条件をチェック
                history = self._get_symbol_history(condition.symbol)
                evaluated_value = self._evaluate_condition(condition, data, history)
                if evaluated_value is not None:
                    return {
                        'condition': condition,
                        'data': data,
                        'rule': rule,
                        'current_value': evaluated_value,
                        'history': history
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"条件チェックエラー: {e}")
            return None
    
    def _get_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """銘柄データを取得"""
        try:
            with self.snapshot_lock:
                snapshot = self.realtime_snapshots.get(symbol)
                if snapshot:
                    snapshot_ts = snapshot.get('timestamp')
                    if not isinstance(snapshot_ts, datetime):
                        snapshot_ts = datetime.now()
                    if datetime.now() - snapshot_ts <= self.snapshot_ttl:
                        return dict(snapshot)

            if symbol in self.data_sources:
                return self.data_sources[symbol]()
            else:
                # デフォルトのデータ取得
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d", interval="1m")
                
                if hist.empty:
                    return None
                
                return {
                    'price': hist['Close'].iloc[-1],
                    'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                    'high': hist['High'].iloc[-1],
                    'low': hist['Low'].iloc[-1],
                    'open': hist['Open'].iloc[-1],
                    'change': hist['Close'].iloc[-1] - hist['Open'].iloc[-1],
                    'change_percent': ((hist['Close'].iloc[-1] - hist['Open'].iloc[-1]) / hist['Open'].iloc[-1]) * 100
                }
                
        except Exception as e:
            self.logger.error(f"データ取得エラー {symbol}: {e}")
            return None

    def _get_symbol_history(self, symbol: str) -> List[Dict[str, Any]]:
        """銘柄のリアルタイム履歴を取得"""
        with self.snapshot_lock:
            history = self.realtime_history.get(symbol)
            if not history:
                return []
            return list(history)
    
    def _evaluate_condition(
        self,
        condition: AlertCondition,
        data: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Optional[float]:
        """条件を評価し、閾値を満たした場合は現在値を返す"""
        try:
            alert_type = condition.alert_type
            current_value: Optional[float] = None

            if alert_type in {AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW}:
                current_value = float(data.get('price', 0))
            elif alert_type == AlertType.PRICE_CHANGE_PERCENT:
                current_value = float(data.get('change_percent', 0))
            elif alert_type == AlertType.VOLUME_SPIKE:
                current_value = self._calculate_volume_rate(data, history, condition.time_window)
            elif alert_type == AlertType.VWAP_DEVIATION:
                current_value = self._calculate_vwap_deviation(data, history, condition.time_window)
            elif alert_type == AlertType.VOLATILITY_SPIKE:
                current_value = self._calculate_volatility(history, condition.time_window)
            elif alert_type == AlertType.BID_ASK_SPREAD:
                bid = data.get('bid')
                ask = data.get('ask')
                if bid and ask and bid > 0:
                    current_value = ((ask - bid) / bid) * 100
            elif alert_type == AlertType.MOMENTUM_SHIFT:
                current_value = self._calculate_momentum(history, condition.time_window)
            else:
                current_value = float(data.get('price', 0))

            if current_value is None:
                return None

            operator = condition.comparison_operator
            threshold = condition.threshold_value

            if operator == '>':
                matched = current_value > threshold
            elif operator == '<':
                matched = current_value < threshold
            elif operator == '>=':
                matched = current_value >= threshold
            elif operator == '<=':
                matched = current_value <= threshold
            elif operator == '==':
                matched = abs(current_value - threshold) < 1e-6
            elif operator == '!=':
                matched = abs(current_value - threshold) >= 1e-6
            else:
                matched = False

            return current_value if matched else None

        except Exception as e:
            self.logger.error(f"条件評価エラー: {e}")
            return None

    def _filter_history(self, history: List[Dict[str, Any]], minutes: int) -> List[Dict[str, Any]]:
        """指定時間内の履歴を抽出"""
        if not history:
            return []

        if not minutes or minutes <= 0:
            return history

        cutoff = datetime.now() - timedelta(minutes=minutes)
        filtered = []
        for entry in history:
            ts = entry.get('timestamp')
            if isinstance(ts, datetime) and ts >= cutoff:
                filtered.append(entry)
        return filtered

    def _calculate_volume_rate(
        self,
        data: Dict[str, Any],
        history: List[Dict[str, Any]],
        time_window: int
    ) -> Optional[float]:
        """出来高の急増率または現在出来高を計算"""
        current_volume = data.get('volume')
        if current_volume is None:
            return None

        if not time_window or time_window <= 0:
            return float(current_volume)

        window = self._filter_history(history, time_window)
        volumes = [entry.get('volume') for entry in window if entry.get('volume') is not None]
        if len(volumes) < 2:
            return float(current_volume)

        baseline = sum(volumes[:-1]) / max(len(volumes) - 1, 1)
        if baseline <= 0:
            return float(current_volume)

        return float(current_volume) / baseline

    def _calculate_vwap_deviation(
        self,
        data: Dict[str, Any],
        history: List[Dict[str, Any]],
        time_window: int
    ) -> Optional[float]:
        """現在価格とVWAPの乖離率を計算"""
        price = data.get('price')
        if not price:
            return None

        vwap = data.get('vwap')

        if vwap is None:
            window = self._filter_history(history, time_window or 15)
            total_volume = 0.0
            weighted_price = 0.0

            for entry in window:
                vol = entry.get('volume')
                p = entry.get('price')
                if vol is not None and p is not None:
                    total_volume += vol
                    weighted_price += vol * p

            if total_volume > 0:
                vwap = weighted_price / total_volume

        if not vwap or vwap == 0:
            return None

        return ((price - vwap) / vwap) * 100

    def _calculate_volatility(
        self,
        history: List[Dict[str, Any]],
        time_window: int
    ) -> Optional[float]:
        """時間窓内の実現ボラティリティ (パーセント) を計算"""
        window = self._filter_history(history, time_window or 10)
        prices = [entry.get('price') for entry in window if entry.get('price') is not None]

        if len(prices) < 2:
            return None

        returns = []
        for prev, curr in zip(prices[:-1], prices[1:]):
            if prev and prev != 0:
                returns.append((curr - prev) / prev * 100)

        if len(returns) < 2:
            return None

        try:
            return statistics.pstdev(returns)
        except statistics.StatisticsError:
            return None

    def _calculate_momentum(
        self,
        history: List[Dict[str, Any]],
        time_window: int
    ) -> Optional[float]:
        """時間窓内の価格モメンタム (パーセント) を計算"""
        window = self._filter_history(history, time_window or 5)
        prices = [entry.get('price') for entry in window if entry.get('price') is not None]

        if len(prices) < 2:
            return None

        start_price = prices[0]
        end_price = prices[-1]

        if not start_price or start_price == 0:
            return None

        return ((end_price - start_price) / start_price) * 100
    
    def _trigger_alert(self, rule: AlertRule, trigger_data: Dict[str, Any]):
        """アラートを発火"""
        try:
            condition = trigger_data['condition']
            data = trigger_data['data']
            current_value = trigger_data.get('current_value', data.get('price', 0))
            
            # アラート発火を作成
            trigger_id = f"{rule.id}_{condition.symbol}_{int(time.time())}"
            
            trigger = AlertTrigger(
                id=trigger_id,
                rule_id=rule.id,
                symbol=condition.symbol,
                alert_type=condition.alert_type,
                condition=condition.condition,
                current_value=current_value,
                threshold_value=condition.threshold_value,
                severity=rule.severity,
                message=f"{condition.symbol} で {condition.condition} 条件が満たされました (現在値: {round(current_value, 4)})",
                timestamp=datetime.now(),
                metadata={
                    'rule_name': rule.name,
                    'data': data,
                    'current_value': current_value,
                    'history_size': len(trigger_data.get('history', []))
                }
            )
            
            # データベースに保存
            self.database.save_alert_trigger(trigger)
            
            # ルールの最終発火時刻を更新
            rule.last_triggered = datetime.now()
            condition.last_triggered = datetime.now()
            condition.trigger_count += 1
            
            # データベースを更新
            self.database.save_alert_rule(rule)
            
            # 通知を送信
            asyncio.create_task(self._send_notifications(trigger))
            
            # コールバックを実行
            for callback in self.alert_callbacks:
                try:
                    callback(trigger)
                except Exception as e:
                    self.logger.error(f"コールバック実行エラー: {e}")
            
            self.logger.info(f"アラートを発火: {trigger_id}")
            
        except Exception as e:
            self.logger.error(f"アラート発火エラー: {e}")
    
    async def _send_notifications(self, trigger: AlertTrigger):
        """通知を送信"""
        try:
            rule = self.alert_rules.get(trigger.rule_id)
            if not rule:
                return
            
            message = trigger.message
            
            # 各通知チャネルに送信
            for channel in rule.notification_channels:
                try:
                    await self.notification_service.send_notification(channel, message, trigger)
                except Exception as e:
                    self.logger.error(f"通知送信エラー {channel}: {e}")
            
        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")
    
    def add_alert_callback(self, callback: Callable[[AlertTrigger], None]):
        """アラートコールバックを追加"""
        self.alert_callbacks.append(callback)
    
    def get_alert_rules(self) -> List[AlertRule]:
        """アラートルール一覧を取得"""
        return list(self.alert_rules.values())
    
    def get_alert_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[AlertTrigger]:
        """アラート履歴を取得"""
        return self.database.get_alert_history(symbol, limit)
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム状態を取得"""
        return {
            'is_running': self.is_running,
            'total_rules': len(self.alert_rules),
            'enabled_rules': len([r for r in self.alert_rules.values() if r.enabled]),
            'data_sources': len(self.data_sources),
            'callbacks': len(self.alert_callbacks)
        }

# グローバルインスタンス
advanced_alert_system = AdvancedAlertSystem()
