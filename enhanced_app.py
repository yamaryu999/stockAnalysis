"""
Enhanced Stock Analysis Application
強化された株価分析アプリケーション - 全機能統合版
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# 強化されたモジュールをインポート
try:
    from enhanced_data_sources import multi_data_source_manager
    from advanced_ml_pipeline import advanced_ml_pipeline
    from enhanced_realtime_engine import enhanced_realtime_engine
    from intelligent_performance_optimizer import intelligent_performance_optimizer
    from security_manager import security_manager
    from advanced_visualization import advanced_visualization
    from enhanced_ui_system import enhanced_ui_system
    from restful_api import start_server
    from database_manager import DatabaseManager
    from cache_manager import cache_manager
except ImportError as e:
    st.error(f"モジュールのインポートエラー: {e}")
    st.info("必要なモジュールが不足している可能性があります。")

# ページ設定
st.set_page_config(
    page_title="🚀 強化された日本株価分析ツール v6.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yamaryu999/stockAnalysis',
        'Report a bug': 'https://github.com/yamaryu999/stockAnalysis/issues',
        'About': "🚀 強化された日本株価分析ツール v6.0 - 全機能統合版"
    }
)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class EnhancedStockAnalysisApp:
    """強化された株価分析アプリケーション"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_id = "default_user"
        self.screen_size = "desktop"
        
        # システムの初期化
        self._initialize_systems()
    
    def _initialize_systems(self):
        """システムを初期化"""
        try:
            # UIシステムを初期化
            enhanced_ui_system.initialize_ui(self.user_id, self.screen_size)
            
            # パフォーマンス最適化を開始
            intelligent_performance_optimizer.start_auto_optimization()
            
            # データベースを初期化
            self.db_manager = DatabaseManager()
            
            self.logger.info("システム初期化完了")
            
        except Exception as e:
            self.logger.error(f"システム初期化エラー: {e}")
            st.error("システムの初期化中にエラーが発生しました")
    
    def run(self):
        """アプリケーションを実行"""
        try:
            # メインナビゲーション
            self._create_navigation()
            
            # ページコンテンツを表示
            page = st.session_state.get('current_page', 'dashboard')
            
            if page == 'dashboard':
                self._show_dashboard()
            elif page == 'analysis':
                self._show_analysis()
            elif page == 'realtime':
                self._show_realtime()
            elif page == 'ml':
                self._show_ml_analysis()
            elif page == 'visualization':
                self._show_visualization()
            elif page == 'security':
                self._show_security()
            elif page == 'performance':
                self._show_performance()
            elif page == 'api':
                self._show_api_info()
            
        except Exception as e:
            self.logger.error(f"アプリケーション実行エラー: {e}")
            st.error("アプリケーションの実行中にエラーが発生しました")
    
    def _create_navigation(self):
        """ナビゲーションを作成"""
        with st.sidebar:
            st.title("🚀 株価分析ツール")
            
            # ページ選択
            pages = {
                "📊 ダッシュボード": "dashboard",
                "📈 分析": "analysis",
                "⚡ リアルタイム": "realtime",
                "🤖 AI分析": "ml",
                "📊 可視化": "visualization",
                "🔒 セキュリティ": "security",
                "⚙️ パフォーマンス": "performance",
                "🔌 API": "api"
            }
            
            for page_name, page_key in pages.items():
                if st.button(page_name, key=f"nav_{page_key}"):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            # 現在のページを表示
            current_page_name = [name for name, key in pages.items() if key == st.session_state.get('current_page', 'dashboard')][0]
            st.info(f"現在のページ: {current_page_name}")
    
    def _show_dashboard(self):
        """ダッシュボードを表示"""
        st.title("📊 強化されたダッシュボード")
        
        # サンプルデータを準備
        sample_data = {
            'metrics': {
                '総銘柄数': 1000,
                '分析済み': 850,
                'AI予測精度': '92.5%',
                'リアルタイム更新': '有効'
            },
            'charts': {
                '市場概要': {
                    'figure': self._create_sample_chart()
                }
            }
        }
        
        # 強化されたUIシステムでダッシュボードを作成
        enhanced_ui_system.create_enhanced_dashboard(
            self.user_id, sample_data, self.screen_size
        )
    
    def _show_analysis(self):
        """分析ページを表示"""
        st.title("📈 高度な株価分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # シンボル選択
            symbol = st.selectbox(
                "分析対象銘柄を選択",
                options=['7203.T', '6758.T', '9984.T', '9434.T', '6861.T'],
                index=0
            )
            
            # 期間選択
            period = st.selectbox(
                "分析期間",
                options=['1mo', '3mo', '6mo', '1y', '2y'],
                index=3
            )
            
            # 分析実行ボタン
            if st.button("🔍 分析実行", type="primary"):
                with st.spinner("分析を実行中..."):
                    self._perform_analysis(symbol, period)
        
        with col2:
            st.subheader("📊 分析オプション")
            
            # 分析タイプ
            analysis_types = st.multiselect(
                "分析タイプ",
                options=['テクニカル', 'ファンダメンタル', 'センチメント', 'リスク'],
                default=['テクニカル', 'ファンダメンタル']
            )
            
            # データソース
            data_sources = st.multiselect(
                "データソース",
                options=['Yahoo Finance', 'Alpha Vantage', 'IEX Cloud'],
                default=['Yahoo Finance']
            )
    
    def _show_realtime(self):
        """リアルタイム分析ページを表示"""
        st.title("⚡ リアルタイム分析")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # リアルタイム分析の状態
            if enhanced_realtime_engine.running:
                st.success("🟢 リアルタイム分析が実行中です")
                
                # 分析結果を表示
                results = enhanced_realtime_engine.get_all_results()
                if results:
                    for symbol, result in results.items():
                        with st.expander(f"📊 {symbol} の分析結果"):
                            st.json(result)
            else:
                st.warning("🔴 リアルタイム分析が停止中です")
        
        with col2:
            st.subheader("⚙️ リアルタイム制御")
            
            # 分析開始/停止ボタン
            if st.button("▶️ 分析開始"):
                symbols = ['7203.T', '6758.T', '9984.T']
                enhanced_realtime_engine.start_analysis(symbols)
                st.success("リアルタイム分析を開始しました")
                st.rerun()
            
            if st.button("⏹️ 分析停止"):
                enhanced_realtime_engine.stop_analysis()
                st.success("リアルタイム分析を停止しました")
                st.rerun()
            
            # アラート表示
            alerts = enhanced_realtime_engine.get_active_alerts()
            if alerts:
                st.subheader("🚨 アクティブアラート")
                for alert in alerts[:5]:  # 最新5件
                    st.warning(f"{alert.symbol}: {alert.message}")
    
    def _show_ml_analysis(self):
        """機械学習分析ページを表示"""
        st.title("🤖 AI分析・予測")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 予測設定
            symbol = st.selectbox(
                "予測対象銘柄",
                options=['7203.T', '6758.T', '9984.T', '9434.T', '6861.T'],
                index=0,
                key="ml_symbol"
            )
            
            model_type = st.selectbox(
                "使用モデル",
                options=['ensemble', 'random_forest', 'gradient_boosting', 'neural_network'],
                index=0
            )
            
            days_ahead = st.slider("予測日数", 1, 30, 5)
            
            if st.button("🔮 予測実行", type="primary"):
                with st.spinner("AI予測を実行中..."):
                    self._perform_ml_prediction(symbol, model_type, days_ahead)
        
        with col2:
            st.subheader("📊 モデル性能")
            
            # モデルインサイトを表示
            try:
                insights = advanced_ml_pipeline.get_model_insights(symbol)
                if insights:
                    st.json(insights)
            except Exception as e:
                st.error(f"モデルインサイト取得エラー: {e}")
    
    def _show_visualization(self):
        """可視化ページを表示"""
        st.title("📊 高度な可視化")
        
        # 可視化タイプ選択
        viz_type = st.selectbox(
            "可視化タイプ",
            options=['ローソク足', '出来高', 'テクニカル指標', '相関分析', '3D可視化', 'アニメーション'],
            index=0
        )
        
        # サンプルチャートを表示
        if viz_type == 'ローソク足':
            chart = advanced_visualization['chart_generator'].create_candlestick_chart(
                self._get_sample_data()
            )
            st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == '出来高':
            chart = advanced_visualization['chart_generator'].create_volume_chart(
                self._get_sample_data()
            )
            st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == 'テクニカル指標':
            chart = advanced_visualization['chart_generator'].create_technical_indicators_chart(
                self._get_sample_data()
            )
            st.plotly_chart(chart, use_container_width=True)
        
        elif viz_type == '相関分析':
            # サンプル相関データ
            correlation_data = self._get_sample_correlation_data()
            chart = advanced_visualization['chart_generator'].create_correlation_heatmap(
                correlation_data
            )
            st.plotly_chart(chart, use_container_width=True)
    
    def _show_security(self):
        """セキュリティページを表示"""
        st.title("🔒 セキュリティ管理")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🔐 認証")
            
            # ログイン
            with st.form("login_form"):
                user_id = st.text_input("ユーザーID")
                password = st.text_input("パスワード", type="password")
                submitted = st.form_submit_button("ログイン")
                
                if submitted:
                    try:
                        success, session_id = security_manager.authenticate_user(
                            user_id, password, "127.0.0.1", "Streamlit"
                        )
                        if success:
                            st.success("ログイン成功")
                            st.session_state.user_id = user_id
                            st.session_state.session_id = session_id
                        else:
                            st.error("ログイン失敗")
                    except Exception as e:
                        st.error(f"認証エラー: {e}")
        
        with col2:
            st.subheader("📊 セキュリティレポート")
            
            if st.button("レポート生成"):
                try:
                    report = security_manager.get_security_report(7)
                    st.json(report)
                except Exception as e:
                    st.error(f"レポート生成エラー: {e}")
    
    def _show_performance(self):
        """パフォーマンスページを表示"""
        st.title("⚙️ パフォーマンス管理")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # パフォーマンスメトリクス
            try:
                metrics = intelligent_performance_optimizer.get_performance_report()
                if metrics:
                    st.subheader("📊 システムメトリクス")
                    st.json(metrics)
            except Exception as e:
                st.error(f"メトリクス取得エラー: {e}")
        
        with col2:
            st.subheader("🔧 最適化")
            
            optimization_type = st.selectbox(
                "最適化タイプ",
                options=['memory', 'cpu', 'cache', 'all'],
                index=0
            )
            
            if st.button("最適化実行"):
                try:
                    result = intelligent_performance_optimizer.manual_optimize(optimization_type)
                    st.success("最適化完了")
                    st.json(result)
                except Exception as e:
                    st.error(f"最適化エラー: {e}")
    
    def _show_api_info(self):
        """API情報ページを表示"""
        st.title("🔌 RESTful API")
        
        st.subheader("📚 API仕様")
        st.info("""
        **API Base URL**: `http://localhost:8000`
        
        **主要エンドポイント**:
        - `GET /api/v1/stock/{symbol}` - 株価データ取得
        - `POST /api/v1/ml/predict` - AI予測
        - `GET /api/v1/realtime/results` - リアルタイム分析結果
        - `GET /api/v1/visualization/chart/{type}` - チャートデータ
        
        **認証**: Bearer Token
        **ドキュメント**: `/docs` (Swagger UI)
        """)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🚀 APIサーバー起動"):
                st.info("APIサーバーを起動中...")
                st.code("python restful_api.py", language="bash")
        
        with col2:
            if st.button("📖 APIドキュメント"):
                st.info("APIドキュメントを開く")
                st.markdown("[Swagger UI](http://localhost:8000/docs)")
    
    def _perform_analysis(self, symbol: str, period: str):
        """分析を実行"""
        try:
            # 株価データを取得
            stock_data = multi_data_source_manager.get_stock_data(symbol, period)
            if stock_data:
                st.success(f"{symbol} のデータを取得しました")
                
                # データを表示
                st.subheader("📊 株価データ")
                st.dataframe(stock_data.data.tail(10))
                
                # 財務指標を取得
                financial_metrics = multi_data_source_manager.get_financial_metrics(symbol)
                if financial_metrics:
                    st.subheader("💰 財務指標")
                    st.json(financial_metrics)
            else:
                st.error("データの取得に失敗しました")
                
        except Exception as e:
            st.error(f"分析エラー: {e}")
    
    def _perform_ml_prediction(self, symbol: str, model_type: str, days_ahead: int):
        """機械学習予測を実行"""
        try:
            # 株価データを取得
            stock_data = multi_data_source_manager.get_stock_data(symbol, "1y")
            if not stock_data:
                st.error("データの取得に失敗しました")
                return
            
            # 財務指標を取得
            financial_metrics = multi_data_source_manager.get_financial_metrics(symbol)
            
            # 特徴量を準備
            features, target = advanced_ml_pipeline.prepare_features(
                stock_data.data, financial_metrics
            )
            
            if features.empty:
                st.error("予測に十分なデータがありません")
                return
            
            # モデルを訓練（必要に応じて）
            if not advanced_ml_pipeline.load_models(symbol):
                advanced_ml_pipeline.train_models(features, target, symbol)
            
            # 予測を実行
            prediction = advanced_ml_pipeline.predict(
                symbol, features.tail(1), model_type
            )
            
            st.success("予測完了")
            st.subheader("🔮 予測結果")
            st.json({
                "symbol": prediction.symbol,
                "predictions": prediction.predictions,
                "model_used": prediction.model_used,
                "confidence": prediction.performance_metrics.r2 if prediction.performance_metrics else 0
            })
            
        except Exception as e:
            st.error(f"予測エラー: {e}")
    
    def _create_sample_chart(self):
        """サンプルチャートを作成"""
        import plotly.graph_objects as go
        
        # サンプルデータ
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
        
        fig = go.Figure(data=go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='サンプル価格',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title="サンプル株価チャート",
            xaxis_title="日付",
            yaxis_title="価格",
            template="plotly_white"
        )
        
        return fig
    
    def _get_sample_data(self) -> pd.DataFrame:
        """サンプルデータを取得"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        data = pd.DataFrame({
            'Open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'High': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5) + np.random.rand(len(dates)) * 2,
            'Low': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5) - np.random.rand(len(dates)) * 2,
            'Close': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        return data
    
    def _get_sample_correlation_data(self) -> pd.DataFrame:
        """サンプル相関データを取得"""
        np.random.seed(42)
        n = 100
        
        data = pd.DataFrame({
            'Stock_A': np.random.randn(n),
            'Stock_B': np.random.randn(n) + 0.5 * np.random.randn(n),
            'Stock_C': np.random.randn(n) - 0.3 * np.random.randn(n),
            'Stock_D': np.random.randn(n) + 0.2 * np.random.randn(n)
        })
        
        return data

def main():
    """メイン関数"""
    try:
        # アプリケーションを作成して実行
        app = EnhancedStockAnalysisApp()
        app.run()
        
    except Exception as e:
        st.error(f"アプリケーションエラー: {e}")
        logger.error(f"アプリケーションエラー: {e}")

if __name__ == "__main__":
    main()
