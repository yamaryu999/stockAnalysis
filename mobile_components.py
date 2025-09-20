"""
モバイル対応コンポーネント
レスポンシブデザイン用のStreamlitコンポーネント
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import logging

class MobileComponents:
    """モバイル対応コンポーネントクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def mobile_metric_card(self, label: str, value: str, delta: Optional[str] = None, 
                          delta_color: str = "normal", help_text: Optional[str] = None):
        """モバイル対応メトリクスカード"""
        try:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{label}**")
                if help_text:
                    st.markdown(f"*{help_text}*")
            
            with col2:
                st.markdown(f"### {value}")
            
            with col3:
                if delta:
                    delta_color_map = {
                        "normal": "normal",
                        "inverse": "inverse",
                        "off": "off"
                    }
                    st.metric("", "", delta=delta, delta_color=delta_color_map.get(delta_color, "normal"))
            
        except Exception as e:
            self.logger.error(f"モバイルメトリクスカードエラー: {e}")
            st.error(f"メトリクス表示エラー: {e}")
    
    def mobile_chart(self, data: pd.DataFrame, chart_type: str = "line", 
                    x_col: str = "Date", y_col: str = "Close", 
                    title: str = "", height: int = 300):
        """モバイル対応チャート"""
        try:
            if data.empty:
                st.info("データがありません")
                return
            
            if chart_type == "line":
                fig = px.line(data, x=x_col, y=y_col, title=title)
            elif chart_type == "bar":
                fig = px.bar(data, x=x_col, y=y_col, title=title)
            elif chart_type == "scatter":
                fig = px.scatter(data, x=x_col, y=y_col, title=title)
            elif chart_type == "candlestick":
                fig = go.Figure(data=go.Candlestick(
                    x=data[x_col],
                    open=data.get('Open', data[y_col]),
                    high=data.get('High', data[y_col]),
                    low=data.get('Low', data[y_col]),
                    close=data[y_col]
                ))
                fig.update_layout(title=title)
            else:
                fig = px.line(data, x=x_col, y=y_col, title=title)
            
            # モバイル最適化
            fig.update_layout(
                height=height,
                margin=dict(l=20, r=20, t=40, b=20),
                font=dict(size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            # レスポンシブ設定
            fig.update_layout(
                autosize=True,
                responsive=True
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            self.logger.error(f"モバイルチャートエラー: {e}")
            st.error(f"チャート表示エラー: {e}")
    
    def mobile_table(self, data: pd.DataFrame, title: str = "", 
                    max_rows: int = 10, show_index: bool = False):
        """モバイル対応テーブル"""
        try:
            if data.empty:
                st.info("データがありません")
                return
            
            if title:
                st.markdown(f"### {title}")
            
            # データを制限
            display_data = data.head(max_rows)
            
            # モバイル最適化
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=not show_index
            )
            
            if len(data) > max_rows:
                st.info(f"上位{max_rows}件を表示中（全{len(data)}件）")
            
        except Exception as e:
            self.logger.error(f"モバイルテーブルエラー: {e}")
            st.error(f"テーブル表示エラー: {e}")
    
    def mobile_button_group(self, buttons: List[Dict[str, Any]], columns: int = 2):
        """モバイル対応ボタングループ"""
        try:
            cols = st.columns(columns)
            
            for i, button in enumerate(buttons):
                col_index = i % columns
                
                with cols[col_index]:
                    if st.button(
                        button.get('label', f'Button {i+1}'),
                        key=button.get('key', f'button_{i}'),
                        help=button.get('help', ''),
                        type=button.get('type', 'secondary')
                    ):
                        if 'callback' in button:
                            button['callback']()
            
        except Exception as e:
            self.logger.error(f"モバイルボタングループエラー: {e}")
            st.error(f"ボタングループエラー: {e}")
    
    def mobile_input_group(self, inputs: List[Dict[str, Any]]):
        """モバイル対応入力グループ"""
        try:
            results = {}
            
            for input_config in inputs:
                input_type = input_config.get('type', 'text')
                label = input_config.get('label', '')
                key = input_config.get('key', label.lower().replace(' ', '_'))
                default_value = input_config.get('default', '')
                help_text = input_config.get('help', '')
                
                if input_type == 'text':
                    results[key] = st.text_input(
                        label,
                        value=default_value,
                        key=key,
                        help=help_text
                    )
                elif input_type == 'number':
                    results[key] = st.number_input(
                        label,
                        value=default_value,
                        key=key,
                        help=help_text
                    )
                elif input_type == 'select':
                    options = input_config.get('options', [])
                    results[key] = st.selectbox(
                        label,
                        options=options,
                        index=options.index(default_value) if default_value in options else 0,
                        key=key,
                        help=help_text
                    )
                elif input_type == 'slider':
                    min_val = input_config.get('min', 0)
                    max_val = input_config.get('max', 100)
                    step = input_config.get('step', 1)
                    results[key] = st.slider(
                        label,
                        min_value=min_val,
                        max_value=max_val,
                        value=default_value,
                        step=step,
                        key=key,
                        help=help_text
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(f"モバイル入力グループエラー: {e}")
            st.error(f"入力グループエラー: {e}")
            return {}
    
    def mobile_alert(self, message: str, alert_type: str = "info", 
                    dismissible: bool = True):
        """モバイル対応アラート"""
        try:
            alert_configs = {
                "success": {"icon": "✅", "color": "green"},
                "warning": {"icon": "⚠️", "color": "orange"},
                "error": {"icon": "❌", "color": "red"},
                "info": {"icon": "ℹ️", "color": "blue"}
            }
            
            config = alert_configs.get(alert_type, alert_configs["info"])
            icon = config["icon"]
            
            if alert_type == "success":
                st.success(f"{icon} {message}")
            elif alert_type == "warning":
                st.warning(f"{icon} {message}")
            elif alert_type == "error":
                st.error(f"{icon} {message}")
            else:
                st.info(f"{icon} {message}")
            
        except Exception as e:
            self.logger.error(f"モバイルアラートエラー: {e}")
            st.error(f"アラート表示エラー: {e}")
    
    def mobile_card(self, title: str, content: Any, collapsible: bool = False):
        """モバイル対応カード"""
        try:
            if collapsible:
                with st.expander(title):
                    if callable(content):
                        content()
                    else:
                        st.write(content)
            else:
                st.markdown(f"### {title}")
                if callable(content):
                    content()
                else:
                    st.write(content)
            
        except Exception as e:
            self.logger.error(f"モバイルカードエラー: {e}")
            st.error(f"カード表示エラー: {e}")
    
    def mobile_navigation(self, pages: List[Dict[str, str]], current_page: str = ""):
        """モバイル対応ナビゲーション"""
        try:
            # タブ形式のナビゲーション
            page_names = [page['name'] for page in pages]
            
            if current_page:
                try:
                    current_index = page_names.index(current_page)
                except ValueError:
                    current_index = 0
            else:
                current_index = 0
            
            selected_page = st.selectbox(
                "ページを選択",
                page_names,
                index=current_index,
                key="mobile_navigation"
            )
            
            return selected_page
            
        except Exception as e:
            self.logger.error(f"モバイルナビゲーションエラー: {e}")
            st.error(f"ナビゲーションエラー: {e}")
            return pages[0]['name'] if pages else ""
    
    def mobile_grid(self, items: List[Dict[str, Any]], columns: int = 2):
        """モバイル対応グリッドレイアウト"""
        try:
            cols = st.columns(columns)
            
            for i, item in enumerate(items):
                col_index = i % columns
                
                with cols[col_index]:
                    if 'title' in item:
                        st.markdown(f"**{item['title']}**")
                    
                    if 'content' in item:
                        if callable(item['content']):
                            item['content']()
                        else:
                            st.write(item['content'])
                    
                    if 'metric' in item:
                        st.metric(
                            item['metric'].get('label', ''),
                            item['metric'].get('value', ''),
                            delta=item['metric'].get('delta', None)
                        )
            
        except Exception as e:
            self.logger.error(f"モバイルグリッドエラー: {e}")
            st.error(f"グリッド表示エラー: {e}")
    
    def mobile_progress(self, value: float, label: str = "", 
                       show_percentage: bool = True):
        """モバイル対応プログレスバー"""
        try:
            if label:
                st.markdown(f"**{label}**")
            
            progress_bar = st.progress(value)
            
            if show_percentage:
                st.markdown(f"{value:.1%}")
            
            return progress_bar
            
        except Exception as e:
            self.logger.error(f"モバイルプログレスエラー: {e}")
            st.error(f"プログレス表示エラー: {e}")
            return None
    
    def mobile_spinner(self, message: str = "処理中..."):
        """モバイル対応スピナー"""
        try:
            return st.spinner(message)
            
        except Exception as e:
            self.logger.error(f"モバイルスピナーエラー: {e}")
            st.error(f"スピナー表示エラー: {e}")
            return None
    
    def mobile_tabs(self, tabs: List[Dict[str, Any]]):
        """モバイル対応タブ"""
        try:
            tab_names = [tab['name'] for tab in tabs]
            
            selected_tab = st.tabs(tab_names)
            
            for i, tab in enumerate(tabs):
                with selected_tab[i]:
                    if 'content' in tab:
                        if callable(tab['content']):
                            tab['content']()
                        else:
                            st.write(tab['content'])
            
            return selected_tab
            
        except Exception as e:
            self.logger.error(f"モバイルタブエラー: {e}")
            st.error(f"タブ表示エラー: {e}")
            return []
    
    def mobile_sidebar(self, content: Dict[str, Any]):
        """モバイル対応サイドバー"""
        try:
            with st.sidebar:
                if 'title' in content:
                    st.markdown(f"## {content['title']}")
                
                if 'filters' in content:
                    st.markdown("### フィルター")
                    for filter_config in content['filters']:
                        filter_type = filter_config.get('type', 'select')
                        label = filter_config.get('label', '')
                        key = filter_config.get('key', label.lower().replace(' ', '_'))
                        
                        if filter_type == 'select':
                            options = filter_config.get('options', [])
                            st.selectbox(label, options=options, key=key)
                        elif filter_type == 'slider':
                            min_val = filter_config.get('min', 0)
                            max_val = filter_config.get('max', 100)
                            st.slider(label, min_val, max_val, key=key)
                
                if 'actions' in content:
                    st.markdown("### アクション")
                    for action in content['actions']:
                        if st.button(action.get('label', 'Button'), key=action.get('key', '')):
                            if 'callback' in action:
                                action['callback']()
            
        except Exception as e:
            self.logger.error(f"モバイルサイドバーエラー: {e}")
            st.error(f"サイドバー表示エラー: {e}")

# グローバルインスタンス
mobile_components = MobileComponents()

# ユーティリティ関数
def is_mobile_device() -> bool:
    """モバイルデバイスかどうかを判定"""
    try:
        # Streamlitのセッション状態からデバイス情報を取得
        if 'device_info' in st.session_state:
            return st.session_state.device_info.get('is_mobile', False)
        
        # デフォルトではFalse
        return False
        
    except Exception:
        return False

def get_screen_size() -> str:
    """画面サイズを取得"""
    try:
        if 'device_info' in st.session_state:
            width = st.session_state.device_info.get('width', 1024)
            
            if width <= 768:
                return 'mobile'
            elif width <= 1024:
                return 'tablet'
            else:
                return 'desktop'
        
        return 'desktop'
        
    except Exception:
        return 'desktop'

def responsive_columns(columns: int) -> int:
    """レスポンシブなカラム数を取得"""
    screen_size = get_screen_size()
    
    if screen_size == 'mobile':
        return 1
    elif screen_size == 'tablet':
        return min(columns, 2)
    else:
        return columns