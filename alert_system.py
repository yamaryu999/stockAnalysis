import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import json
import os

class AlertSystem:
    """
    アラート機能システム
    
    価格アラート、シグナルアラート、リスクアラートを管理します。
    """
    
    def __init__(self, alerts_file: str = "alerts.json"):
        self.alerts_file = alerts_file
        self.alerts = self._load_alerts()
        self.alert_callbacks = []
    
    def _load_alerts(self) -> List[Dict]:
        """アラート設定を読み込み"""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"アラート読み込みエラー: {e}")
                return []
        return []
    
    def _save_alerts(self):
        """アラート設定を保存"""
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"アラート保存エラー: {e}")
    
    def add_price_alert(self, symbol: str, target_price: float, condition: str, 
                       alert_type: str = "price", description: str = "") -> str:
        """
        価格アラートを追加
        
        Args:
            symbol: 銘柄コード
            target_price: 目標価格
            condition: 条件 ("above", "below", "cross_up", "cross_down")
            alert_type: アラートタイプ
            description: 説明
            
        Returns:
            アラートID
        """
        alert_id = f"price_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = {
            'id': alert_id,
            'type': 'price',
            'symbol': symbol,
            'target_price': target_price,
            'condition': condition,
            'description': description,
            'created_at': datetime.now(),
            'status': 'active',
            'triggered_at': None,
            'triggered_price': None
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        
        return alert_id
    
    def add_signal_alert(self, symbol: str, signal_type: str, 
                        description: str = "") -> str:
        """
        シグナルアラートを追加
        
        Args:
            symbol: 銘柄コード
            signal_type: シグナルタイプ ("buy", "sell", "hold")
            description: 説明
            
        Returns:
            アラートID
        """
        alert_id = f"signal_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = {
            'id': alert_id,
            'type': 'signal',
            'symbol': symbol,
            'signal_type': signal_type,
            'description': description,
            'created_at': datetime.now(),
            'status': 'active',
            'triggered_at': None,
            'triggered_signal': None
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        
        return alert_id
    
    def add_risk_alert(self, symbol: str, risk_type: str, threshold: float,
                      description: str = "") -> str:
        """
        リスクアラートを追加
        
        Args:
            symbol: 銘柄コード
            risk_type: リスクタイプ ("volatility", "drawdown", "beta")
            threshold: 閾値
            description: 説明
            
        Returns:
            アラートID
        """
        alert_id = f"risk_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = {
            'id': alert_id,
            'type': 'risk',
            'symbol': symbol,
            'risk_type': risk_type,
            'threshold': threshold,
            'description': description,
            'created_at': datetime.now(),
            'status': 'active',
            'triggered_at': None,
            'triggered_value': None
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        
        return alert_id
    
    def check_price_alerts(self, symbol: str, current_price: float, 
                          previous_price: float = None) -> List[Dict]:
        """
        価格アラートをチェック
        
        Args:
            symbol: 銘柄コード
            current_price: 現在価格
            previous_price: 前回価格
            
        Returns:
            トリガーされたアラートのリスト
        """
        triggered_alerts = []
        
        for alert in self.alerts:
            if (alert['type'] == 'price' and 
                alert['symbol'] == symbol and 
                alert['status'] == 'active'):
                
                target_price = alert['target_price']
                condition = alert['condition']
                triggered = False
                
                if condition == "above" and current_price >= target_price:
                    triggered = True
                elif condition == "below" and current_price <= target_price:
                    triggered = True
                elif condition == "cross_up" and previous_price and previous_price < target_price <= current_price:
                    triggered = True
                elif condition == "cross_down" and previous_price and previous_price > target_price >= current_price:
                    triggered = True
                
                if triggered:
                    alert['status'] = 'triggered'
                    alert['triggered_at'] = datetime.now()
                    alert['triggered_price'] = current_price
                    triggered_alerts.append(alert.copy())
        
        if triggered_alerts:
            self._save_alerts()
        
        return triggered_alerts
    
    def check_signal_alerts(self, symbol: str, current_signal: str) -> List[Dict]:
        """
        シグナルアラートをチェック
        
        Args:
            symbol: 銘柄コード
            current_signal: 現在のシグナル
            
        Returns:
            トリガーされたアラートのリスト
        """
        triggered_alerts = []
        
        for alert in self.alerts:
            if (alert['type'] == 'signal' and 
                alert['symbol'] == symbol and 
                alert['status'] == 'active'):
                
                if alert['signal_type'] == current_signal:
                    alert['status'] = 'triggered'
                    alert['triggered_at'] = datetime.now()
                    alert['triggered_signal'] = current_signal
                    triggered_alerts.append(alert.copy())
        
        if triggered_alerts:
            self._save_alerts()
        
        return triggered_alerts
    
    def check_risk_alerts(self, symbol: str, risk_metrics: Dict) -> List[Dict]:
        """
        リスクアラートをチェック
        
        Args:
            symbol: 銘柄コード
            risk_metrics: リスク指標
            
        Returns:
            トリガーされたアラートのリスト
        """
        triggered_alerts = []
        
        for alert in self.alerts:
            if (alert['type'] == 'risk' and 
                alert['symbol'] == symbol and 
                alert['status'] == 'active'):
                
                risk_type = alert['risk_type']
                threshold = alert['threshold']
                triggered = False
                
                if risk_type in risk_metrics:
                    current_value = risk_metrics[risk_type]
                    
                    if risk_type == "volatility" and current_value >= threshold:
                        triggered = True
                    elif risk_type == "drawdown" and current_value >= threshold:
                        triggered = True
                    elif risk_type == "beta" and current_value >= threshold:
                        triggered = True
                
                if triggered:
                    alert['status'] = 'triggered'
                    alert['triggered_at'] = datetime.now()
                    alert['triggered_value'] = current_value
                    triggered_alerts.append(alert.copy())
        
        if triggered_alerts:
            self._save_alerts()
        
        return triggered_alerts
    
    def get_active_alerts(self, symbol: str = None) -> List[Dict]:
        """アクティブなアラートを取得"""
        if symbol:
            return [alert for alert in self.alerts 
                   if alert['status'] == 'active' and alert['symbol'] == symbol]
        return [alert for alert in self.alerts if alert['status'] == 'active']
    
    def get_triggered_alerts(self, symbol: str = None) -> List[Dict]:
        """トリガーされたアラートを取得"""
        if symbol:
            return [alert for alert in self.alerts 
                   if alert['status'] == 'triggered' and alert['symbol'] == symbol]
        return [alert for alert in self.alerts if alert['status'] == 'triggered']
    
    def delete_alert(self, alert_id: str) -> bool:
        """アラートを削除"""
        for i, alert in enumerate(self.alerts):
            if alert['id'] == alert_id:
                del self.alerts[i]
                self._save_alerts()
                return True
        return False
    
    def update_alert(self, alert_id: str, updates: Dict) -> bool:
        """アラートを更新"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert.update(updates)
                self._save_alerts()
                return True
        return False
    
    def add_alert_callback(self, callback: Callable):
        """アラートコールバックを追加"""
        self.alert_callbacks.append(callback)
    
    def _notify_alerts(self, triggered_alerts: List[Dict]):
        """アラート通知を実行"""
        for callback in self.alert_callbacks:
            try:
                callback(triggered_alerts)
            except Exception as e:
                print(f"アラート通知エラー: {e}")
    
    def process_alerts(self, symbol: str, stock_data: Dict, 
                      signal_data: Dict = None, risk_data: Dict = None) -> List[Dict]:
        """
        全アラートを処理
        
        Args:
            symbol: 銘柄コード
            stock_data: 株価データ
            signal_data: シグナルデータ
            risk_data: リスクデータ
            
        Returns:
            トリガーされたアラートのリスト
        """
        all_triggered = []
        
        # 価格アラートをチェック
        if stock_data and 'data' in stock_data and not stock_data['data'].empty:
            current_price = stock_data['data']['Close'].iloc[-1]
            previous_price = stock_data['data']['Close'].iloc[-2] if len(stock_data['data']) > 1 else None
            
            price_alerts = self.check_price_alerts(symbol, current_price, previous_price)
            all_triggered.extend(price_alerts)
        
        # シグナルアラートをチェック
        if signal_data and 'signal' in signal_data:
            signal_alerts = self.check_signal_alerts(symbol, signal_data['signal'])
            all_triggered.extend(signal_alerts)
        
        # リスクアラートをチェック
        if risk_data:
            risk_alerts = self.check_risk_alerts(symbol, risk_data)
            all_triggered.extend(risk_alerts)
        
        # 通知を実行
        if all_triggered:
            self._notify_alerts(all_triggered)
        
        return all_triggered
    
    def get_alert_summary(self) -> Dict:
        """アラートサマリーを取得"""
        active_count = len(self.get_active_alerts())
        triggered_count = len(self.get_triggered_alerts())
        
        # タイプ別集計
        type_counts = {}
        for alert in self.alerts:
            alert_type = alert['type']
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': active_count,
            'triggered_alerts': triggered_count,
            'type_counts': type_counts
        }
    
    def cleanup_old_alerts(self, days: int = 30):
        """古いアラートをクリーンアップ"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.alerts = [
            alert for alert in self.alerts 
            if alert.get('created_at', datetime.now()) > cutoff_date
        ]
        
        self._save_alerts()
