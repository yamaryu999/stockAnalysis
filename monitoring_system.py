"""
Comprehensive Monitoring System for Stock Analysis Tool
Performance monitoring, error tracking, and system health monitoring
"""

import time
import psutil
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import deque
import sqlite3
import os
from pathlib import Path
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

@dataclass
class SystemMetrics:
    """System metrics data class"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    network_sent: int
    network_recv: int
    active_connections: int
    process_count: int

@dataclass
class ApplicationMetrics:
    """Application metrics data class"""
    timestamp: datetime
    active_users: int
    requests_per_minute: int
    response_time_avg: float
    error_rate: float
    cache_hit_rate: float
    database_query_time: float
    ai_prediction_time: float

@dataclass
class Alert:
    """Alert data class"""
    id: str
    timestamp: datetime
    level: str  # 'info', 'warning', 'error', 'critical'
    category: str  # 'system', 'application', 'security', 'performance'
    message: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MetricsCollector:
    """Metrics collection class"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.system_metrics_history = deque(maxlen=history_size)
        self.application_metrics_history = deque(maxlen=history_size)
        self.logger = logging.getLogger(__name__)
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Active connections
            try:
                connections = psutil.net_connections()
                active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                active_connections = 0
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                memory_available=memory.available / (1024**3),  # GB
                disk_usage=disk.percent,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                active_connections=active_connections,
                process_count=process_count
            )
            
            self.system_metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_application_metrics(self, 
                                  active_users: int = 0,
                                  requests_per_minute: int = 0,
                                  response_time_avg: float = 0.0,
                                  error_rate: float = 0.0,
                                  cache_hit_rate: float = 0.0,
                                  database_query_time: float = 0.0,
                                  ai_prediction_time: float = 0.0) -> ApplicationMetrics:
        """Collect application metrics"""
        try:
            metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                active_users=active_users,
                requests_per_minute=requests_per_minute,
                response_time_avg=response_time_avg,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate,
                database_query_time=database_query_time,
                ai_prediction_time=ai_prediction_time
            )
            
            self.application_metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting application metrics: {e}")
            return None
    
    def get_system_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get system metrics summary for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.system_metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {}
            
            return {
                'avg_cpu_usage': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
                'max_cpu_usage': max(m.cpu_usage for m in recent_metrics),
                'avg_memory_usage': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                'max_memory_usage': max(m.memory_usage for m in recent_metrics),
                'avg_disk_usage': sum(m.disk_usage for m in recent_metrics) / len(recent_metrics),
                'max_disk_usage': max(m.disk_usage for m in recent_metrics),
                'total_network_sent': recent_metrics[-1].network_sent - recent_metrics[0].network_sent,
                'total_network_recv': recent_metrics[-1].network_recv - recent_metrics[0].network_recv,
                'avg_active_connections': sum(m.active_connections for m in recent_metrics) / len(recent_metrics),
                'avg_process_count': sum(m.process_count for m in recent_metrics) / len(recent_metrics),
                'sample_count': len(recent_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics summary: {e}")
            return {}
    
    def get_application_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get application metrics summary for specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.application_metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {}
            
            return {
                'avg_active_users': sum(m.active_users for m in recent_metrics) / len(recent_metrics),
                'max_active_users': max(m.active_users for m in recent_metrics),
                'avg_requests_per_minute': sum(m.requests_per_minute for m in recent_metrics) / len(recent_metrics),
                'max_requests_per_minute': max(m.requests_per_minute for m in recent_metrics),
                'avg_response_time': sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics),
                'max_response_time': max(m.response_time_avg for m in recent_metrics),
                'avg_error_rate': sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
                'max_error_rate': max(m.error_rate for m in recent_metrics),
                'avg_cache_hit_rate': sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics),
                'avg_database_query_time': sum(m.database_query_time for m in recent_metrics) / len(recent_metrics),
                'avg_ai_prediction_time': sum(m.ai_prediction_time for m in recent_metrics) / len(recent_metrics),
                'sample_count': len(recent_metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting application metrics summary: {e}")
            return {}

class AlertManager:
    """Alert management class"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = []
        self.notification_handlers = []
        self.logger = logging.getLogger(__name__)
        
        # Default alert rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        self.alert_rules = [
            {
                'name': 'high_cpu_usage',
                'condition': lambda metrics: metrics.cpu_usage > 80,
                'level': 'warning',
                'category': 'performance',
                'message': 'High CPU usage detected'
            },
            {
                'name': 'critical_cpu_usage',
                'condition': lambda metrics: metrics.cpu_usage > 95,
                'level': 'critical',
                'category': 'performance',
                'message': 'Critical CPU usage detected'
            },
            {
                'name': 'high_memory_usage',
                'condition': lambda metrics: metrics.memory_usage > 85,
                'level': 'warning',
                'category': 'performance',
                'message': 'High memory usage detected'
            },
            {
                'name': 'critical_memory_usage',
                'condition': lambda metrics: metrics.memory_usage > 95,
                'level': 'critical',
                'category': 'performance',
                'message': 'Critical memory usage detected'
            },
            {
                'name': 'high_disk_usage',
                'condition': lambda metrics: metrics.disk_usage > 90,
                'level': 'warning',
                'category': 'system',
                'message': 'High disk usage detected'
            },
            {
                'name': 'high_error_rate',
                'condition': lambda metrics: metrics.error_rate > 5,
                'level': 'warning',
                'category': 'application',
                'message': 'High error rate detected'
            },
            {
                'name': 'critical_error_rate',
                'condition': lambda metrics: metrics.error_rate > 20,
                'level': 'critical',
                'category': 'application',
                'message': 'Critical error rate detected'
            },
            {
                'name': 'low_cache_hit_rate',
                'condition': lambda metrics: metrics.cache_hit_rate < 50,
                'level': 'warning',
                'category': 'performance',
                'message': 'Low cache hit rate detected'
            }
        ]
    
    def add_alert_rule(self, name: str, condition: Callable, level: str, category: str, message: str):
        """Add custom alert rule"""
        self.alert_rules.append({
            'name': name,
            'condition': condition,
            'level': level,
            'category': category,
            'message': message
        })
    
    def check_alerts(self, system_metrics: SystemMetrics, application_metrics: ApplicationMetrics):
        """Check for alert conditions"""
        try:
            for rule in self.alert_rules:
                try:
                    if rule['condition'](system_metrics) or rule['condition'](application_metrics):
                        self._create_alert(rule, system_metrics, application_metrics)
                except Exception as e:
                    self.logger.error(f"Error checking alert rule {rule['name']}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
    
    def _create_alert(self, rule: Dict, system_metrics: SystemMetrics, application_metrics: ApplicationMetrics):
        """Create new alert"""
        alert_id = f"{rule['name']}_{int(time.time())}"
        
        # Check if similar alert already exists (within last 5 minutes)
        recent_alerts = [a for a in self.alerts 
                        if a.category == rule['category'] and 
                        not a.resolved and 
                        (datetime.now() - a.timestamp).seconds < 300]
        
        if recent_alerts:
            return  # Don't create duplicate alerts
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            level=rule['level'],
            category=rule['category'],
            message=rule['message'],
            details={
                'rule_name': rule['name'],
                'system_metrics': asdict(system_metrics),
                'application_metrics': asdict(application_metrics)
            }
        )
        
        self.alerts.append(alert)
        self.logger.warning(f"Alert created: {alert.message} (Level: {alert.level})")
        
        # Send notifications
        self._send_notifications(alert)
    
    def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error sending notification: {e}")
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    def resolve_alert(self, alert_id: str):
        """Resolve alert"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                self.logger.info(f"Alert resolved: {alert.message}")
                break
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alerts_by_level(self, level: str) -> List[Alert]:
        """Get alerts by level"""
        return [alert for alert in self.alerts if alert.level == level]
    
    def get_alerts_by_category(self, category: str) -> List[Alert]:
        """Get alerts by category"""
        return [alert for alert in self.alerts if alert.category == category]

class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_checks = []
        self._setup_default_checks()
    
    def _setup_default_checks(self):
        """Setup default health checks"""
        self.health_checks = [
            {
                'name': 'database_connectivity',
                'check': self._check_database_connectivity,
                'critical': True
            },
            {
                'name': 'disk_space',
                'check': self._check_disk_space,
                'critical': True
            },
            {
                'name': 'memory_availability',
                'check': self._check_memory_availability,
                'critical': True
            },
            {
                'name': 'network_connectivity',
                'check': self._check_network_connectivity,
                'critical': False
            },
            {
                'name': 'external_api_access',
                'check': self._check_external_api_access,
                'critical': False
            }
        ]
    
    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Try to connect to database
            db_path = "stock_analysis.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT 1")
                cursor.fetchone()
                conn.close()
                return {'status': 'healthy', 'message': 'Database connection successful'}
            else:
                return {'status': 'warning', 'message': 'Database file not found'}
        except Exception as e:
            return {'status': 'critical', 'message': f'Database connection failed: {e}'}
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            
            if free_percent < 5:
                return {'status': 'critical', 'message': f'Critical disk space: {free_percent:.1f}% free'}
            elif free_percent < 10:
                return {'status': 'warning', 'message': f'Low disk space: {free_percent:.1f}% free'}
            else:
                return {'status': 'healthy', 'message': f'Disk space OK: {free_percent:.1f}% free'}
        except Exception as e:
            return {'status': 'critical', 'message': f'Disk space check failed: {e}'}
    
    def _check_memory_availability(self) -> Dict[str, Any]:
        """Check memory availability"""
        try:
            memory = psutil.virtual_memory()
            available_percent = (memory.available / memory.total) * 100
            
            if available_percent < 5:
                return {'status': 'critical', 'message': f'Critical memory: {available_percent:.1f}% available'}
            elif available_percent < 10:
                return {'status': 'warning', 'message': f'Low memory: {available_percent:.1f}% available'}
            else:
                return {'status': 'healthy', 'message': f'Memory OK: {available_percent:.1f}% available'}
        except Exception as e:
            return {'status': 'critical', 'message': f'Memory check failed: {e}'}
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            if response.status_code == 200:
                return {'status': 'healthy', 'message': 'Network connectivity OK'}
            else:
                return {'status': 'warning', 'message': f'Network connectivity issues: {response.status_code}'}
        except Exception as e:
            return {'status': 'warning', 'message': f'Network connectivity check failed: {e}'}
    
    def _check_external_api_access(self) -> Dict[str, Any]:
        """Check external API access"""
        try:
            # Check Yahoo Finance API
            response = requests.get('https://query1.finance.yahoo.com/v1/finance/search?q=AAPL', timeout=10)
            if response.status_code == 200:
                return {'status': 'healthy', 'message': 'External API access OK'}
            else:
                return {'status': 'warning', 'message': f'External API issues: {response.status_code}'}
        except Exception as e:
            return {'status': 'warning', 'message': f'External API check failed: {e}'}
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = 'healthy'
        
        for check in self.health_checks:
            try:
                result = check['check']()
                results[check['name']] = result
                
                if result['status'] == 'critical':
                    overall_status = 'critical'
                elif result['status'] == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
                    
            except Exception as e:
                results[check['name']] = {
                    'status': 'critical',
                    'message': f'Health check failed: {e}'
                }
                overall_status = 'critical'
        
        return {
            'overall_status': overall_status,
            'timestamp': datetime.now(),
            'checks': results
        }
    
    def add_health_check(self, name: str, check_func: Callable, critical: bool = False):
        """Add custom health check"""
        self.health_checks.append({
            'name': name,
            'check': check_func,
            'critical': critical
        })

class MonitoringDashboard:
    """Monitoring dashboard"""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager, health_checker: HealthChecker):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.health_checker = health_checker
        self.logger = logging.getLogger(__name__)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # System metrics summary
            system_summary = self.metrics_collector.get_system_metrics_summary(hours=1)
            
            # Application metrics summary
            app_summary = self.metrics_collector.get_application_metrics_summary(hours=1)
            
            # Health check results
            health_results = self.health_checker.run_health_checks()
            
            # Active alerts
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Alert summary
            alert_summary = {
                'total_active': len(active_alerts),
                'critical': len([a for a in active_alerts if a.level == 'critical']),
                'warning': len([a for a in active_alerts if a.level == 'warning']),
                'error': len([a for a in active_alerts if a.level == 'error']),
                'info': len([a for a in active_alerts if a.level == 'info'])
            }
            
            return {
                'timestamp': datetime.now(),
                'system_metrics': system_summary,
                'application_metrics': app_summary,
                'health_status': health_results,
                'alerts': alert_summary,
                'active_alerts': [asdict(alert) for alert in active_alerts[:10]]  # Last 10 alerts
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {}

class MonitoringSystem:
    """Main monitoring system"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.is_running = False
        self.monitoring_thread = None
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.health_checker = HealthChecker()
        self.dashboard = MonitoringDashboard(
            self.metrics_collector, 
            self.alert_manager, 
            self.health_checker
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Setup email notifications
        self._setup_email_notifications()
    
    def _setup_email_notifications(self):
        """Setup email notifications"""
        def email_notification_handler(alert: Alert):
            if alert.level in ['critical', 'error']:
                self._send_email_alert(alert)
        
        self.alert_manager.add_notification_handler(email_notification_handler)
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            # Email configuration (should be in config file)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "alerts@stockanalysis.com"
            sender_password = "your_password"
            receiver_email = "admin@stockanalysis.com"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"Stock Analysis Alert - {alert.level.upper()}"
            
            body = f"""
Alert Details:
- Level: {alert.level}
- Category: {alert.category}
- Message: {alert.message}
- Time: {alert.timestamp}
- Details: {json.dumps(alert.details, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
            
            self.logger.info(f"Email alert sent for: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def start_monitoring(self):
        """Start monitoring system"""
        if self.is_running:
            self.logger.warning("Monitoring system is already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info("Monitoring system started")
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Monitoring system stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect metrics
                system_metrics = self.metrics_collector.collect_system_metrics()
                application_metrics = self.metrics_collector.collect_application_metrics()
                
                # Check alerts
                if system_metrics and application_metrics:
                    self.alert_manager.check_alerts(system_metrics, application_metrics)
                
                # Sleep for collection interval
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.collection_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            'is_running': self.is_running,
            'collection_interval': self.collection_interval,
            'metrics_history_size': len(self.metrics_collector.system_metrics_history),
            'total_alerts': len(self.alert_manager.alerts),
            'active_alerts': len(self.alert_manager.get_active_alerts())
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return self.dashboard.get_dashboard_data()
    
    def resolve_alert(self, alert_id: str):
        """Resolve alert"""
        self.alert_manager.resolve_alert(alert_id)
    
    def add_custom_alert_rule(self, name: str, condition: Callable, level: str, category: str, message: str):
        """Add custom alert rule"""
        self.alert_manager.add_alert_rule(name, condition, level, category, message)
    
    def add_custom_health_check(self, name: str, check_func: Callable, critical: bool = False):
        """Add custom health check"""
        self.health_checker.add_health_check(name, check_func, critical)

# Global monitoring system instance
monitoring_system = MonitoringSystem()

def start_monitoring():
    """Start global monitoring system"""
    monitoring_system.start_monitoring()

def stop_monitoring():
    """Stop global monitoring system"""
    monitoring_system.stop_monitoring()

def get_monitoring_status():
    """Get monitoring system status"""
    return monitoring_system.get_status()

def get_dashboard_data():
    """Get dashboard data"""
    return monitoring_system.get_dashboard_data()