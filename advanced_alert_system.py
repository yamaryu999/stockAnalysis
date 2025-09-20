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
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from enum import Enum
import sqlite3
import os

class AlertType(Enum):
    """アラートタイプ"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE_PERCENT = "price_change_percent"
    VOLUME_SPIKE = "volume_spike"
    TECHNICAL_SIGNAL = "technical_signal"
    NEWS_SENTIMENT = "news_sentiment"
    CUSTOM_CONDITION = "custom_condition"

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
                if self._evaluate_condition(condition, data):
                    return {
                        'condition': condition,
                        'data': data,
                        'rule': rule
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"条件チェックエラー: {e}")
            return None
    
    def _get_symbol_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """銘柄データを取得"""
        try:
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
    
    def _evaluate_condition(self, condition: AlertCondition, data: Dict[str, Any]) -> bool:
        """条件を評価"""
        try:
            # 現在値を取得
            if condition.alert_type == AlertType.PRICE_ABOVE:
                current_value = data.get('price', 0)
            elif condition.alert_type == AlertType.PRICE_BELOW:
                current_value = data.get('price', 0)
            elif condition.alert_type == AlertType.PRICE_CHANGE_PERCENT:
                current_value = data.get('change_percent', 0)
            elif condition.alert_type == AlertType.VOLUME_SPIKE:
                current_value = data.get('volume', 0)
            else:
                current_value = 0
            
            # 比較演算子で評価
            if condition.comparison_operator == '>':
                return current_value > condition.threshold_value
            elif condition.comparison_operator == '<':
                return current_value < condition.threshold_value
            elif condition.comparison_operator == '>=':
                return current_value >= condition.threshold_value
            elif condition.comparison_operator == '<=':
                return current_value <= condition.threshold_value
            elif condition.comparison_operator == '==':
                return abs(current_value - condition.threshold_value) < 0.01
            elif condition.comparison_operator == '!=':
                return abs(current_value - condition.threshold_value) >= 0.01
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"条件評価エラー: {e}")
            return False
    
    def _trigger_alert(self, rule: AlertRule, trigger_data: Dict[str, Any]):
        """アラートを発火"""
        try:
            condition = trigger_data['condition']
            data = trigger_data['data']
            
            # アラート発火を作成
            trigger_id = f"{rule.id}_{condition.symbol}_{int(time.time())}"
            
            trigger = AlertTrigger(
                id=trigger_id,
                rule_id=rule.id,
                symbol=condition.symbol,
                alert_type=condition.alert_type,
                condition=condition.condition,
                current_value=data.get('price', 0),
                threshold_value=condition.threshold_value,
                severity=rule.severity,
                message=f"{condition.symbol} で {condition.condition} 条件が満たされました",
                timestamp=datetime.now(),
                metadata={
                    'rule_name': rule.name,
                    'data': data
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