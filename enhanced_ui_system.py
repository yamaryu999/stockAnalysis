"""
Enhanced User Experience System
強化されたユーザーエクスペリエンスシステム - 適応的UI、パーソナライゼーション、アクセシビリティ
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import json
import os
import time
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

@dataclass
class UserProfile:
    """ユーザープロファイル"""
    user_id: str
    preferences: Dict[str, Any]
    usage_patterns: Dict[str, Any]
    accessibility_needs: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

@dataclass
class UITheme:
    """UIテーマ"""
    name: str
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    accent_color: str
    font_family: str
    font_size: str

@dataclass
class LayoutConfig:
    """レイアウト設定"""
    columns: int
    sidebar_width: int
    main_content_width: int
    chart_height: int
    responsive: bool

class UserProfileManager:
    """ユーザープロファイル管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.profiles = {}
        self.usage_tracking = defaultdict(list)
        
    def create_user_profile(self, user_id: str, initial_preferences: Dict[str, Any] = None) -> UserProfile:
        """ユーザープロファイルを作成"""
        try:
            profile = UserProfile(
                user_id=user_id,
                preferences=initial_preferences or self._get_default_preferences(),
                usage_patterns={},
                accessibility_needs={},
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.profiles[user_id] = profile
            self.logger.info(f"ユーザープロファイル作成: {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"ユーザープロファイル作成エラー: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """ユーザープロファイルを取得"""
        return self.profiles.get(user_id)
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """ユーザー設定を更新"""
        try:
            if user_id in self.profiles:
                self.profiles[user_id].preferences.update(preferences)
                self.profiles[user_id].last_updated = datetime.now()
                self.logger.info(f"ユーザー設定更新: {user_id}")
        except Exception as e:
            self.logger.error(f"ユーザー設定更新エラー: {e}")
    
    def track_usage(self, user_id: str, action: str, context: Dict[str, Any] = None):
        """使用状況を追跡"""
        try:
            usage_data = {
                'action': action,
                'timestamp': datetime.now(),
                'context': context or {}
            }
            
            self.usage_tracking[user_id].append(usage_data)
            
            # 最新1000件のみ保持
            if len(self.usage_tracking[user_id]) > 1000:
                self.usage_tracking[user_id] = self.usage_tracking[user_id][-1000:]
                
        except Exception as e:
            self.logger.error(f"使用状況追跡エラー: {e}")
    
    def get_usage_analytics(self, user_id: str) -> Dict[str, Any]:
        """使用状況分析を取得"""
        try:
            if user_id not in self.usage_tracking:
                return {}
            
            usage_data = self.usage_tracking[user_id]
            
            # アクション別統計
            action_counts = defaultdict(int)
            for data in usage_data:
                action_counts[data['action']] += 1
            
            # 時間別統計
            hourly_usage = defaultdict(int)
            for data in usage_data:
                hour = data['timestamp'].hour
                hourly_usage[hour] += 1
            
            # 最近の使用状況
            recent_usage = usage_data[-10:] if len(usage_data) >= 10 else usage_data
            
            return {
                'total_actions': len(usage_data),
                'action_counts': dict(action_counts),
                'hourly_usage': dict(hourly_usage),
                'recent_usage': [asdict(data) for data in recent_usage],
                'most_used_action': max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None
            }
            
        except Exception as e:
            self.logger.error(f"使用状況分析エラー: {e}")
            return {}
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            'theme': 'light',
            'language': 'ja',
            'chart_type': 'candlestick',
            'timeframe': '1y',
            'notifications': True,
            'auto_refresh': True,
            'default_symbols': ['7203.T', '6758.T', '9984.T'],
            'dashboard_layout': 'standard'
        }

class ThemeManager:
    """テーマ管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.themes = self._initialize_themes()
        self.current_theme = 'light'
    
    def _initialize_themes(self) -> Dict[str, UITheme]:
        """テーマを初期化"""
        return {
            'light': UITheme(
                name='Light',
                primary_color='#1f77b4',
                secondary_color='#ff7f0e',
                background_color='#ffffff',
                text_color='#000000',
                accent_color='#2ca02c',
                font_family='Arial, sans-serif',
                font_size='14px'
            ),
            'dark': UITheme(
                name='Dark',
                primary_color='#00d4ff',
                secondary_color='#ff6b6b',
                background_color='#1a1a1a',
                text_color='#ffffff',
                accent_color='#4ecdc4',
                font_family='Arial, sans-serif',
                font_size='14px'
            ),
            'netflix': UITheme(
                name='Netflix',
                primary_color='#e50914',
                secondary_color='#b20710',
                background_color='#141414',
                text_color='#ffffff',
                accent_color='#f5f5f1',
                font_family='Netflix Sans, Arial, sans-serif',
                font_size='14px'
            ),
            'high_contrast': UITheme(
                name='High Contrast',
                primary_color='#000000',
                secondary_color='#ffffff',
                background_color='#ffffff',
                text_color='#000000',
                accent_color='#ff0000',
                font_family='Arial, sans-serif',
                font_size='16px'
            )
        }
    
    def get_theme(self, theme_name: str) -> Optional[UITheme]:
        """テーマを取得"""
        return self.themes.get(theme_name)
    
    def set_current_theme(self, theme_name: str):
        """現在のテーマを設定"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.logger.info(f"テーマ変更: {theme_name}")
    
    def get_current_theme(self) -> UITheme:
        """現在のテーマを取得"""
        return self.themes[self.current_theme]
    
    def apply_theme_css(self, theme: UITheme) -> str:
        """テーマCSSを適用"""
        return f"""
        <style>
        :root {{
            --primary-color: {theme.primary_color};
            --secondary-color: {theme.secondary_color};
            --background-color: {theme.background_color};
            --text-color: {theme.text_color};
            --accent-color: {theme.accent_color};
            --font-family: {theme.font_family};
            --font-size: {theme.font_size};
        }}
        
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: var(--font-family);
            font-size: var(--font-size);
        }}
        
        .main-header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: var(--text-color);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .metric-card {{
            background: var(--background-color);
            border: 2px solid var(--primary-color);
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }}
        
        .chart-container {{
            background: var(--background-color);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .sidebar {{
            background: var(--background-color);
            border-right: 2px solid var(--primary-color);
        }}
        
        .button-primary {{
            background-color: var(--primary-color);
            color: var(--text-color);
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-size: var(--font-size);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .button-primary:hover {{
            background-color: var(--secondary-color);
            transform: translateY(-1px);
        }}
        
        .alert-success {{
            background-color: var(--accent-color);
            color: var(--text-color);
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        
        .alert-warning {{
            background-color: var(--secondary-color);
            color: var(--text-color);
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        
        .alert-error {{
            background-color: #dc3545;
            color: white;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }}
        
        .loading-spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: var(--primary-color);
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .slide-in {{
            animation: slideIn 0.3s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(-100%); }}
            to {{ transform: translateX(0); }}
        }}
        </style>
        """

class ResponsiveLayoutManager:
    """レスポンシブレイアウト管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.screen_sizes = {
            'mobile': {'max_width': 768, 'columns': 1},
            'tablet': {'max_width': 1024, 'columns': 2},
            'desktop': {'max_width': 1920, 'columns': 3},
            'large': {'max_width': 9999, 'columns': 4}
        }
    
    def get_responsive_columns(self, screen_size: str = 'desktop') -> int:
        """レスポンシブ列数を取得"""
        return self.screen_sizes.get(screen_size, {}).get('columns', 3)
    
    def create_adaptive_layout(self, screen_size: str, content_items: List[Any]) -> List[Any]:
        """適応的レイアウトを作成"""
        try:
            columns = self.get_responsive_columns(screen_size)
            
            if screen_size == 'mobile':
                # モバイル: 縦積みレイアウト
                return self._create_mobile_layout(content_items)
            elif screen_size == 'tablet':
                # タブレット: 2列レイアウト
                return self._create_tablet_layout(content_items)
            else:
                # デスクトップ: 3-4列レイアウト
                return self._create_desktop_layout(content_items, columns)
                
        except Exception as e:
            self.logger.error(f"適応的レイアウト作成エラー: {e}")
            return content_items
    
    def _create_mobile_layout(self, content_items: List[Any]) -> List[Any]:
        """モバイルレイアウトを作成"""
        layout = []
        for item in content_items:
            layout.append(st.container())
            with layout[-1]:
                st.write(item)
        return layout
    
    def _create_tablet_layout(self, content_items: List[Any]) -> List[Any]:
        """タブレットレイアウトを作成"""
        layout = []
        for i in range(0, len(content_items), 2):
            col1, col2 = st.columns(2)
            layout.extend([col1, col2])
            
            with col1:
                st.write(content_items[i])
            
            if i + 1 < len(content_items):
                with col2:
                    st.write(content_items[i + 1])
        return layout
    
    def _create_desktop_layout(self, content_items: List[Any], columns: int) -> List[Any]:
        """デスクトップレイアウトを作成"""
        layout = []
        for i in range(0, len(content_items), columns):
            cols = st.columns(columns)
            layout.extend(cols)
            
            for j, col in enumerate(cols):
                if i + j < len(content_items):
                    with col:
                        st.write(content_items[i + j])
        return layout

class AccessibilityManager:
    """アクセシビリティ管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.accessibility_features = {
            'high_contrast': False,
            'large_text': False,
            'screen_reader': False,
            'keyboard_navigation': False,
            'color_blind_friendly': False
        }
    
    def enable_accessibility_feature(self, feature: str):
        """アクセシビリティ機能を有効化"""
        if feature in self.accessibility_features:
            self.accessibility_features[feature] = True
            self.logger.info(f"アクセシビリティ機能有効化: {feature}")
    
    def disable_accessibility_feature(self, feature: str):
        """アクセシビリティ機能を無効化"""
        if feature in self.accessibility_features:
            self.accessibility_features[feature] = False
            self.logger.info(f"アクセシビリティ機能無効化: {feature}")
    
    def get_accessibility_css(self) -> str:
        """アクセシビリティCSSを取得"""
        css = ""
        
        if self.accessibility_features['high_contrast']:
            css += """
            .high-contrast {
                filter: contrast(200%);
            }
            """
        
        if self.accessibility_features['large_text']:
            css += """
            .large-text {
                font-size: 18px !important;
            }
            """
        
        if self.accessibility_features['color_blind_friendly']:
            css += """
            .color-blind-friendly {
                color: #000000 !important;
                background-color: #ffffff !important;
            }
            """
        
        return css
    
    def add_aria_labels(self, element_type: str, label: str) -> str:
        """ARIAラベルを追加"""
        return f'aria-label="{label}" role="{element_type}"'

class PersonalizationEngine:
    """パーソナライゼーションエンジン"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_profiles = UserProfileManager()
        self.theme_manager = ThemeManager()
        self.layout_manager = ResponsiveLayoutManager()
        self.accessibility_manager = AccessibilityManager()
    
    def personalize_ui(self, user_id: str, screen_size: str = 'desktop') -> Dict[str, Any]:
        """UIをパーソナライズ"""
        try:
            profile = self.user_profiles.get_user_profile(user_id)
            if not profile:
                profile = self.user_profiles.create_user_profile(user_id)
            
            # テーマを適用
            theme = self.theme_manager.get_theme(profile.preferences.get('theme', 'light'))
            self.theme_manager.set_current_theme(profile.preferences.get('theme', 'light'))
            
            # レイアウトを設定
            layout_config = LayoutConfig(
                columns=self.layout_manager.get_responsive_columns(screen_size),
                sidebar_width=250,
                main_content_width=800,
                chart_height=400,
                responsive=True
            )
            
            # アクセシビリティ設定を適用
            for feature, enabled in profile.accessibility_needs.items():
                if enabled:
                    self.accessibility_manager.enable_accessibility_feature(feature)
            
            return {
                'theme': asdict(theme),
                'layout': asdict(layout_config),
                'preferences': profile.preferences,
                'accessibility_features': self.accessibility_manager.accessibility_features
            }
            
        except Exception as e:
            self.logger.error(f"UIパーソナライゼーションエラー: {e}")
            return {}
    
    def get_recommendations(self, user_id: str) -> List[str]:
        """推奨事項を取得"""
        try:
            analytics = self.user_profiles.get_usage_analytics(user_id)
            recommendations = []
            
            # 使用パターンに基づく推奨
            if analytics.get('most_used_action') == 'view_chart':
                recommendations.append("お気に入りのチャートをダッシュボードに追加することをお勧めします")
            
            if analytics.get('total_actions', 0) > 100:
                recommendations.append("高度な分析機能を試してみてください")
            
            # 時間帯に基づく推奨
            hourly_usage = analytics.get('hourly_usage', {})
            if hourly_usage:
                peak_hour = max(hourly_usage.items(), key=lambda x: x[1])[0]
                if 9 <= peak_hour <= 17:
                    recommendations.append("市場時間中の分析に最適化された設定をお勧めします")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"推奨事項取得エラー: {e}")
            return []

class InteractiveComponents:
    """インタラクティブコンポーネントクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.personalization_engine = PersonalizationEngine()
    
    def create_adaptive_dashboard(self, user_id: str, data: Dict[str, Any], 
                                screen_size: str = 'desktop') -> None:
        """適応的ダッシュボードを作成"""
        try:
            # UIをパーソナライズ
            ui_config = self.personalization_engine.personalize_ui(user_id, screen_size)
            
            # テーマを適用
            theme = ui_config.get('theme', {})
            st.markdown(self.personalization_engine.theme_manager.apply_theme_css(
                self.personalization_engine.theme_manager.get_current_theme()
            ), unsafe_allow_html=True)
            
            # アクセシビリティCSSを適用
            accessibility_css = self.personalization_engine.accessibility_manager.get_accessibility_css()
            if accessibility_css:
                st.markdown(f"<style>{accessibility_css}</style>", unsafe_allow_html=True)
            
            # ヘッダー
            st.markdown(f"""
            <div class="main-header fade-in">
                <h1>📈 パーソナライズされた株価分析ダッシュボード</h1>
                <p>ユーザー: {user_id} | 画面サイズ: {screen_size}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 推奨事項を表示
            recommendations = self.personalization_engine.get_recommendations(user_id)
            if recommendations:
                with st.expander("💡 推奨事項", expanded=False):
                    for rec in recommendations:
                        st.info(rec)
            
            # メトリクスカード
            self._create_metrics_cards(data.get('metrics', {}), ui_config['layout']['columns'])
            
            # チャートセクション
            self._create_chart_section(data.get('charts', {}), ui_config['layout'])
            
            # サイドバー
            self._create_sidebar(user_id, ui_config)
            
        except Exception as e:
            self.logger.error(f"適応的ダッシュボード作成エラー: {e}")
            st.error("ダッシュボードの作成中にエラーが発生しました")
    
    def _create_metrics_cards(self, metrics: Dict[str, Any], columns: int):
        """メトリクスカードを作成"""
        if not metrics:
            return
        
        st.subheader("📊 主要メトリクス")
        
        # レスポンシブ列を作成
        if columns >= 4:
            cols = st.columns(4)
        elif columns >= 3:
            cols = st.columns(3)
        elif columns >= 2:
            cols = st.columns(2)
        else:
            cols = [st.container()]
        
        metric_items = list(metrics.items())
        for i, (key, value) in enumerate(metric_items):
            col_index = i % len(cols)
            with cols[col_index]:
                st.markdown(f"""
                <div class="metric-card slide-in">
                    <h4>{key}</h4>
                    <h2>{value}</h2>
                </div>
                """, unsafe_allow_html=True)
    
    def _create_chart_section(self, charts: Dict[str, Any], layout_config: Dict[str, Any]):
        """チャートセクションを作成"""
        if not charts:
            return
        
        st.subheader("📈 チャート分析")
        
        for chart_name, chart_data in charts.items():
            with st.expander(f"📊 {chart_name}", expanded=True):
                st.markdown(f"""
                <div class="chart-container fade-in">
                """, unsafe_allow_html=True)
                
                # チャートを表示
                if isinstance(chart_data, dict) and 'figure' in chart_data:
                    st.plotly_chart(
                        chart_data['figure'],
                        use_container_width=True,
                        height=layout_config.get('chart_height', 400)
                    )
                else:
                    st.write(chart_data)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    def _create_sidebar(self, user_id: str, ui_config: Dict[str, Any]):
        """サイドバーを作成"""
        with st.sidebar:
            st.markdown("## ⚙️ 設定")
            
            # テーマ選択
            current_theme = ui_config.get('preferences', {}).get('theme', 'light')
            new_theme = st.selectbox(
                "テーマ",
                options=['light', 'dark', 'netflix', 'high_contrast'],
                index=['light', 'dark', 'netflix', 'high_contrast'].index(current_theme)
            )
            
            if new_theme != current_theme:
                self.personalization_engine.user_profiles.update_user_preferences(
                    user_id, {'theme': new_theme}
                )
                st.rerun()
            
            # アクセシビリティ設定
            st.markdown("### ♿ アクセシビリティ")
            
            accessibility_features = ui_config.get('accessibility_features', {})
            for feature, enabled in accessibility_features.items():
                new_enabled = st.checkbox(
                    feature.replace('_', ' ').title(),
                    value=enabled
                )
                
                if new_enabled != enabled:
                    if new_enabled:
                        self.personalization_engine.accessibility_manager.enable_accessibility_feature(feature)
                    else:
                        self.personalization_engine.accessibility_manager.disable_accessibility_feature(feature)
            
            # 使用状況統計
            st.markdown("### 📊 使用状況")
            analytics = self.personalization_engine.user_profiles.get_usage_analytics(user_id)
            
            if analytics:
                st.metric("総アクション数", analytics.get('total_actions', 0))
                st.metric("最も使用される機能", analytics.get('most_used_action', 'N/A'))
            
            # リフレッシュボタン
            if st.button("🔄 ダッシュボードを更新", type="primary"):
                st.rerun()

class NotificationSystem:
    """通知システム"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notifications = []
    
    def add_notification(self, message: str, notification_type: str = 'info', 
                        duration: int = 5):
        """通知を追加"""
        notification = {
            'id': len(self.notifications),
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now(),
            'duration': duration
        }
        
        self.notifications.append(notification)
        self.logger.info(f"通知追加: {message}")
    
    def display_notifications(self):
        """通知を表示"""
        for notification in self.notifications[-5:]:  # 最新5件のみ表示
            if notification['type'] == 'success':
                st.success(notification['message'])
            elif notification['type'] == 'warning':
                st.warning(notification['message'])
            elif notification['type'] == 'error':
                st.error(notification['message'])
            else:
                st.info(notification['message'])
    
    def clear_notifications(self):
        """通知をクリア"""
        self.notifications.clear()

class EnhancedUISystem:
    """強化されたUIシステム"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.personalization_engine = PersonalizationEngine()
        self.interactive_components = InteractiveComponents()
        self.notification_system = NotificationSystem()
    
    def initialize_ui(self, user_id: str = 'default_user', screen_size: str = 'desktop'):
        """UIを初期化"""
        try:
            # 使用状況を追跡
            self.personalization_engine.user_profiles.track_usage(
                user_id, 'ui_initialization', {'screen_size': screen_size}
            )
            
            # 通知システムを初期化
            self.notification_system.add_notification(
                "UIシステムが正常に初期化されました", 'success'
            )
            
            self.logger.info(f"UI初期化完了: {user_id}")
            
        except Exception as e:
            self.logger.error(f"UI初期化エラー: {e}")
            self.notification_system.add_notification(
                "UI初期化中にエラーが発生しました", 'error'
            )
    
    def create_enhanced_dashboard(self, user_id: str, data: Dict[str, Any], 
                                screen_size: str = 'desktop'):
        """強化されたダッシュボードを作成"""
        try:
            # 使用状況を追跡
            self.personalization_engine.user_profiles.track_usage(
                user_id, 'dashboard_view', {'screen_size': screen_size}
            )
            
            # 適応的ダッシュボードを作成
            self.interactive_components.create_adaptive_dashboard(
                user_id, data, screen_size
            )
            
            # 通知を表示
            self.notification_system.display_notifications()
            
        except Exception as e:
            self.logger.error(f"強化ダッシュボード作成エラー: {e}")
            st.error("ダッシュボードの作成中にエラーが発生しました")
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """ユーザーインサイトを取得"""
        try:
            profile = self.personalization_engine.user_profiles.get_user_profile(user_id)
            analytics = self.personalization_engine.user_profiles.get_usage_analytics(user_id)
            recommendations = self.personalization_engine.get_recommendations(user_id)
            
            return {
                'profile': asdict(profile) if profile else None,
                'analytics': analytics,
                'recommendations': recommendations,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"ユーザーインサイト取得エラー: {e}")
            return {}

# グローバルインスタンス
enhanced_ui_system = EnhancedUISystem()
