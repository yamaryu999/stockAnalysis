import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from stock_analyzer import JapaneseStockAnalyzer
from news_analyzer import NewsAnalyzer
from investment_strategies import InvestmentStrategies
from stock_forecast import StockForecastAnalyzer
from advanced_fundamental_analyzer import AdvancedFundamentalAnalyzer
from valuation_analyzer import ValuationAnalyzer
from advanced_technical_analyzer import AdvancedTechnicalAnalyzer
from trend_analyzer import TrendAnalyzer
from risk_analyzer import RiskAnalyzer
from portfolio_analyzer import PortfolioAnalyzer
from ml_analyzer import MLAnalyzer
from personalization_analyzer import PersonalizationAnalyzer
from short_term_predictor import ShortTermPredictor
from trading_signal_analyzer import TradingSignalAnalyzer
from profit_maximizer import ProfitMaximizer
from risk_manager import RiskManager
from fundamental_screener import FundamentalScreener
from alert_system import AlertSystem
from backtest_engine import BacktestEngine
from performance_tracker import PerformanceTracker
from export_manager import ExportManager
from portfolio_manager import PortfolioManager
import time
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(
    page_title="日本株価分析ツール",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yamaryu999/stockAnalysis',
        'Report a bug': 'https://github.com/yamaryu999/stockAnalysis/issues',
        'About': "日本株価分析ツール v2.0 - 包括的な投資分析プラットフォーム"
    }
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .error-card {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f4e79;
        color: white;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 10px;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 10px;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stExpander {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .stExpander > div {
        border-radius: 10px;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%);
    }
    
    .stSpinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #1f4e79;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #1f4e79;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }
    
    .main-container {
        padding-bottom: 60px;
    }
    
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 10px;
            padding: 6px 8px;
            min-width: 60px;
        }
        
        .stButton > button {
            font-size: 12px;
            padding: 6px 12px;
        }
        
        .main-header h1 {
            font-size: 20px;
        }
        
        .main-header p {
            font-size: 12px;
        }
        
        .stMetric {
            padding: 0.5rem;
            font-size: 12px;
        }
        
        .stDataFrame {
            font-size: 10px;
        }
        
        .stExpander {
            font-size: 12px;
        }
        
        .stSelectbox > div > div {
            font-size: 12px;
        }
        
        .stNumberInput > div > div > input {
            font-size: 12px;
        }
        
        .stTextInput > div > div > input {
            font-size: 12px;
        }
        
        .stTextArea > div > div > textarea {
            font-size: 12px;
        }
        
        .stSlider > div > div > div {
            font-size: 12px;
        }
        
        .stCheckbox > label {
            font-size: 12px;
        }
        
        .stRadio > label {
            font-size: 12px;
        }
        
        .stMultiSelect > label {
            font-size: 12px;
        }
        
        .stFileUploader > label {
            font-size: 12px;
        }
        
        .stDownloadButton > button {
            font-size: 12px;
            padding: 6px 12px;
        }
        
        .stProgress > div > div > div {
            height: 4px;
        }
        
        .stSpinner {
            width: 30px;
            height: 30px;
        }
        
        .sidebar .sidebar-content {
            padding: 0.5rem;
        }
        
        .sidebar .sidebar-content .stSelectbox {
            margin-bottom: 0.5rem;
        }
        
        .sidebar .sidebar-content .stSlider {
            margin-bottom: 0.5rem;
        }
        
        .sidebar .sidebar-content .stNumberInput {
            margin-bottom: 0.5rem;
        }
        
        .sidebar .sidebar-content .stTextInput {
            margin-bottom: 0.5rem;
        }
        
        .sidebar .sidebar-content .stCheckbox {
            margin-bottom: 0.5rem;
        }
        
        .sidebar .sidebar-content .stButton {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container {
            padding: 0.5rem;
        }
        
        .main .block-container .stTabs {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stExpander {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stDataFrame {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stPlotlyChart {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stMetric {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stAlert {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stSuccess {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stWarning {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stError {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stInfo {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stSpinner {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stProgress {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stDownloadButton {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stFileUploader {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stForm {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stColumns {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stContainer {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stSidebar {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stMain {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stHeader {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stFooter {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stNavigation {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stBreadcrumbs {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stPagination {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stTooltip {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stPopover {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stModal {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stDrawer {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stAccordion {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stTabs {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stExpander {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stDataFrame {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stPlotlyChart {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stMetric {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stAlert {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stSuccess {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stWarning {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stError {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stInfo {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stSpinner {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stProgress {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stDownloadButton {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stFileUploader {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stForm {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stColumns {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stContainer {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stSidebar {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stMain {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stHeader {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stFooter {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stNavigation {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stBreadcrumbs {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stPagination {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stTooltip {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stPopover {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stModal {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stDrawer {
            margin-bottom: 0.5rem;
        }
        
        .main .block-container .stAccordion {
            margin-bottom: 0.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 8px;
            padding: 4px 6px;
            min-width: 50px;
        }
        
        .stButton > button {
            font-size: 10px;
            padding: 4px 8px;
        }
        
        .main-header h1 {
            font-size: 18px;
        }
        
        .main-header p {
            font-size: 10px;
        }
        
        .stMetric {
            padding: 0.3rem;
            font-size: 10px;
        }
        
        .stDataFrame {
            font-size: 8px;
        }
        
        .stExpander {
            font-size: 10px;
        }
        
        .stSelectbox > div > div {
            font-size: 10px;
        }
        
        .stNumberInput > div > div > input {
            font-size: 10px;
        }
        
        .stTextInput > div > div > input {
            font-size: 10px;
        }
        
        .stTextArea > div > div > textarea {
            font-size: 10px;
        }
        
        .stSlider > div > div > div {
            font-size: 10px;
        }
        
        .stCheckbox > label {
            font-size: 10px;
        }
        
        .stRadio > label {
            font-size: 10px;
        }
        
        .stMultiSelect > label {
            font-size: 10px;
        }
        
        .stFileUploader > label {
            font-size: 10px;
        }
        
        .stDownloadButton > button {
            font-size: 10px;
            padding: 4px 8px;
        }
        
        .stProgress > div > div > div {
            height: 3px;
        }
        
        .stSpinner {
            width: 25px;
            height: 25px;
        }
        
        .sidebar .sidebar-content {
            padding: 0.3rem;
        }
        
        .main .block-container {
            padding: 0.3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# メインヘッダー
st.markdown("""
<div class="main-header">
    <h1>📈 日本株価分析ツール v2.0</h1>
    <p>包括的な投資分析プラットフォーム - AI駆動の銘柄選定とリスク管理</p>
</div>
""", unsafe_allow_html=True)

# 分析器の初期化
@st.cache_data
def initialize_analyzer():
    return JapaneseStockAnalyzer()

@st.cache_data(ttl=300)  # 5分間キャッシュ
def initialize_news_analyzer():
    return NewsAnalyzer()

@st.cache_data
def initialize_investment_strategies():
    return InvestmentStrategies()

@st.cache_data
def initialize_forecast_analyzer():
    return StockForecastAnalyzer()

@st.cache_data
def initialize_advanced_fundamental_analyzer():
    return AdvancedFundamentalAnalyzer()

@st.cache_data
def initialize_valuation_analyzer():
    return ValuationAnalyzer()

@st.cache_data
def initialize_advanced_technical_analyzer():
    return AdvancedTechnicalAnalyzer()

@st.cache_data
def initialize_trend_analyzer():
    return TrendAnalyzer()

@st.cache_data
def initialize_risk_analyzer():
    return RiskAnalyzer()

@st.cache_data
def initialize_portfolio_analyzer():
    return PortfolioAnalyzer()

@st.cache_data
def initialize_ml_analyzer():
    return MLAnalyzer()

@st.cache_data
def initialize_personalization_analyzer():
    return PersonalizationAnalyzer()

@st.cache_data
def initialize_short_term_predictor():
    return ShortTermPredictor()

@st.cache_data
def initialize_trading_signal_analyzer():
    return TradingSignalAnalyzer()

@st.cache_data
def initialize_profit_maximizer():
    return ProfitMaximizer()

@st.cache_data
def initialize_risk_manager():
    return RiskManager()

@st.cache_data
def initialize_fundamental_screener():
    return FundamentalScreener()

@st.cache_data
def initialize_alert_system():
    return AlertSystem()

@st.cache_data
def initialize_backtest_engine():
    return BacktestEngine()

@st.cache_data
def initialize_performance_tracker():
    return PerformanceTracker()

@st.cache_data
def initialize_export_manager():
    return ExportManager()

@st.cache_data
def initialize_portfolio_manager():
    return PortfolioManager()

analyzer = initialize_analyzer()
news_analyzer = initialize_news_analyzer()
investment_strategies = initialize_investment_strategies()
forecast_analyzer = initialize_forecast_analyzer()
advanced_fundamental_analyzer = initialize_advanced_fundamental_analyzer()
valuation_analyzer = initialize_valuation_analyzer()
advanced_technical_analyzer = initialize_advanced_technical_analyzer()
trend_analyzer = initialize_trend_analyzer()
risk_analyzer = initialize_risk_analyzer()
portfolio_analyzer = initialize_portfolio_analyzer()
ml_analyzer = initialize_ml_analyzer()
personalization_analyzer = initialize_personalization_analyzer()
short_term_predictor = initialize_short_term_predictor()
trading_signal_analyzer = initialize_trading_signal_analyzer()
profit_maximizer = initialize_profit_maximizer()
risk_manager = initialize_risk_manager()
fundamental_screener = initialize_fundamental_screener()
alert_system = initialize_alert_system()
backtest_engine = initialize_backtest_engine()
performance_tracker = initialize_performance_tracker()
export_manager = initialize_export_manager()
portfolio_manager = initialize_portfolio_manager()

# サイドバーの改善
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; color: white;">
    <h3>🤖 AI推奨設定</h3>
    <p style="margin: 0; font-size: 14px;">市場分析に基づく投資戦略</p>
</div>
""", unsafe_allow_html=True)

# 投資戦略選択
strategy_options = {
    'auto': '🤖 AI自動提案',
    'value': '💰 バリュー投資',
    'growth': '📈 グロース投資', 
    'dividend': '💵 配当投資',
    'balanced': '⚖️ バランス型',
    'defensive': '🛡️ ディフェンシブ',
    'aggressive': '🚀 アグレッシブ'
}

selected_strategy = st.sidebar.selectbox(
    "投資戦略を選択",
    options=list(strategy_options.keys()),
    format_func=lambda x: strategy_options[x],
    index=0
)

# AI推奨条件の取得
if selected_strategy == 'auto':
    with st.sidebar:
        if st.button("🔍 最新市場分析を実行", type="primary"):
            with st.spinner("市場分析中..."):
                recommendations = news_analyzer.get_current_recommendations()
                st.session_state.ai_recommendations = recommendations
                st.session_state.apply_ai_recommendations = True  # AI推奨を自動適用
                st.success("分析完了！推奨条件を自動適用しました。")

    # AI推奨条件の表示
    if 'ai_recommendations' in st.session_state:
        rec = st.session_state.ai_recommendations
        st.sidebar.markdown("### 📊 AI推奨条件")
        
        # 市場センチメント表示
        sentiment = rec['sentiment_data']['overall_sentiment']
        sentiment_emoji = {'positive': '📈', 'negative': '📉', 'neutral': '➡️'}
        st.sidebar.metric("市場センチメント", f"{sentiment_emoji.get(sentiment, '➡️')} {sentiment}")
        
        # 推奨戦略表示
        strategy = rec['recommendations']['investment_strategy']
        st.sidebar.metric("推奨戦略", strategy)
        
        # 推奨理由表示
        st.sidebar.markdown("**推奨理由:**")
        st.sidebar.info(rec['recommendations']['reasoning'])
        
        # 推奨セクター表示
        if rec['recommendations']['recommended_sectors']:
            st.sidebar.markdown("**注目セクター:**")
            for sector in rec['recommendations']['recommended_sectors']:
                st.sidebar.write(f"• {sector}")
        
        # AI推奨条件の詳細表示
        st.sidebar.markdown("**推奨スクリーニング条件:**")
        ai_criteria = rec['recommendations']['criteria']
        st.sidebar.write(f"• PER: {ai_criteria['pe_min']:.1f} - {ai_criteria['pe_max']:.1f}")
        st.sidebar.write(f"• PBR: {ai_criteria['pb_min']:.1f} - {ai_criteria['pb_max']:.1f}")
        st.sidebar.write(f"• ROE: {ai_criteria['roe_min']:.1f}%以上")
        st.sidebar.write(f"• 配当利回り: {ai_criteria['dividend_min']:.1f}%以上")
        st.sidebar.write(f"• 負債比率: {ai_criteria['debt_max']:.1f}%以下")
        
        # 手動でAI推奨を適用するボタン
        if st.sidebar.button("🤖 AI推奨条件を適用", type="secondary"):
            st.session_state.apply_ai_recommendations = True
            st.sidebar.success("AI推奨条件を適用しました！")
        
        # 詳細根拠表示ボタン
        if st.sidebar.button("🔍 分析根拠を表示", type="secondary"):
            st.session_state.show_analysis_details = True

# 分析根拠の詳細表示
if 'show_analysis_details' in st.session_state and st.session_state.show_analysis_details:
    if 'ai_recommendations' in st.session_state:
        rec = st.session_state.ai_recommendations
        st.markdown("---")
        st.markdown("## 🔍 市場分析の詳細根拠")
        
        # センチメント分析の詳細
        sentiment_data = rec['sentiment_data']
        st.markdown("### 📊 センチメント分析")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("センチメントスコア", f"{sentiment_data['sentiment_score']:+.1f}")
        with col2:
            st.metric("信頼度", f"{sentiment_data['confidence_level']:.1f}%")
        with col3:
            st.metric("分析ニュース数", f"{sentiment_data['analysis_details']['total_news_analyzed']}件")
        
        # ニュース分析結果
        st.markdown("#### 📰 ニュース分析結果")
        
        # ポジティブニュース
        if sentiment_data['positive_news']:
            st.markdown("**✅ ポジティブニュース:**")
            for news in sentiment_data['positive_news']:
                with st.expander(f"📈 {news['title'][:50]}..."):
                    st.write(f"**ソース:** {news['source']}")
                    st.write(f"**キーワード:** {', '.join(news['keywords'])}")
        
        # ネガティブニュース
        if sentiment_data['negative_news']:
            st.markdown("**❌ ネガティブニュース:**")
            for news in sentiment_data['negative_news']:
                with st.expander(f"📉 {news['title'][:50]}..."):
                    st.write(f"**ソース:** {news['source']}")
                    st.write(f"**キーワード:** {', '.join(news['keywords'])}")
        
        # セクター分析
        if sentiment_data['sector_mentions']:
            st.markdown("#### 🏢 セクター別言及回数")
            sector_df = pd.DataFrame(list(sentiment_data['sector_mentions'].items()), 
                                   columns=['セクター', '言及回数'])
            sector_df = sector_df.sort_values('言及回数', ascending=False)
            
            fig_sector = px.bar(sector_df, x='セクター', y='言及回数', 
                              title='セクター別ニュース言及回数')
            st.plotly_chart(fig_sector, width="stretch")
        
        # キーワード分析
        st.markdown("#### 🔑 検出されたキーワード")
        col1, col2 = st.columns(2)
        
        with col1:
            if sentiment_data['analysis_details']['positive_keywords_found']:
                st.markdown("**ポジティブキーワード:**")
                for kw in sentiment_data['analysis_details']['positive_keywords_found']:
                    st.write(f"• {kw}")
        
        with col2:
            if sentiment_data['analysis_details']['negative_keywords_found']:
                st.markdown("**ネガティブキーワード:**")
                for kw in sentiment_data['analysis_details']['negative_keywords_found']:
                    st.write(f"• {kw}")
        
        # 推奨戦略の根拠
        st.markdown("### 🎯 推奨戦略の根拠")
        st.info(f"**推奨戦略:** {rec['recommendations']['investment_strategy']}")
        st.write(f"**根拠:** {rec['recommendations']['reasoning']}")
        
        # 分析統計
        st.markdown("### 📈 分析統計")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ポジティブニュース", sentiment_data['analysis_details']['positive_count'])
        with col2:
            st.metric("ネガティブニュース", sentiment_data['analysis_details']['negative_count'])
        with col3:
            st.metric("ニュートラルニュース", sentiment_data['analysis_details']['neutral_count'])
        
        # 閉じるボタン
        if st.button("❌ 詳細表示を閉じる"):
            st.session_state.show_analysis_details = False
            st.rerun()
    
    st.markdown("---")

# 投資戦略情報の表示
if selected_strategy != 'auto':
    strategy_info = investment_strategies.get_strategy(selected_strategy)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("投資戦略", strategy_info['name'])
        st.metric("適した投資期間", investment_strategies.get_time_horizon(selected_strategy))
    
    with col2:
        risk_profile = investment_strategies.get_risk_profile(selected_strategy)
        st.metric("リスクレベル", risk_profile['risk_level'])
        st.metric("期待リターン", risk_profile['expected_return'])
    
    with col3:
        st.metric("ボラティリティ", risk_profile['volatility'])
        st.metric("適性", strategy_info['suitable_for'])
    
    # 戦略の説明
    st.info(f"**{strategy_info['name']}**: {strategy_info['description']}")
    
    # 優先指標
    st.markdown("**優先指標:**")
    for factor in strategy_info['priority_factors']:
        st.write(f"• {factor}")
    
    st.markdown("---")

# サイドバーでスクリーニング条件を設定
st.sidebar.header("🔍 スクリーニング条件")

# スクリーニング条件の設定
st.sidebar.subheader("📊 財務指標フィルター")

# 戦略に基づく条件の取得
def get_criteria_by_strategy(strategy_name):
    if strategy_name == 'auto' and 'ai_recommendations' in st.session_state:
        return st.session_state.ai_recommendations['recommendations']['criteria']
    else:
        strategy_data = investment_strategies.get_strategy(strategy_name)
        return strategy_data['criteria']

# 現在の戦略に基づく条件を取得
current_criteria = get_criteria_by_strategy(selected_strategy)

# 条件適用ボタン
if st.sidebar.button("📋 選択戦略の条件を適用"):
    st.session_state.apply_strategy = True

# 条件の初期値設定
if ('apply_strategy' in st.session_state and st.session_state.apply_strategy) or \
   ('apply_ai_recommendations' in st.session_state and st.session_state.apply_ai_recommendations):
    
    # AI推奨条件を優先
    if selected_strategy == 'auto' and 'ai_recommendations' in st.session_state:
        ai_criteria = st.session_state.ai_recommendations['recommendations']['criteria']
        default_pe_min = ai_criteria['pe_min']
        default_pe_max = ai_criteria['pe_max']
        default_pb_min = ai_criteria['pb_min']
        default_pb_max = ai_criteria['pb_max']
        default_roe_min = ai_criteria['roe_min']
        default_dividend_min = ai_criteria['dividend_min']
        default_debt_max = ai_criteria['debt_max']
    else:
        # 通常の戦略条件
        default_pe_min = current_criteria['pe_min']
        default_pe_max = current_criteria['pe_max']
        default_pb_min = current_criteria['pb_min']
        default_pb_max = current_criteria['pb_max']
        default_roe_min = current_criteria['roe_min']
        default_dividend_min = current_criteria['dividend_min']
        default_debt_max = current_criteria['debt_max']
    
    # フラグをリセット
    st.session_state.apply_strategy = False
    st.session_state.apply_ai_recommendations = False
else:
    # デフォルト値またはセッション状態から取得
    if 'current_criteria' in st.session_state:
        default_pe_min = st.session_state.current_criteria.get('pe_min', 5.0)
        default_pe_max = st.session_state.current_criteria.get('pe_max', 20.0)
        default_pb_min = st.session_state.current_criteria.get('pb_min', 0.5)
        default_pb_max = st.session_state.current_criteria.get('pb_max', 2.0)
        default_roe_min = st.session_state.current_criteria.get('roe_min', 10.0)
        default_dividend_min = st.session_state.current_criteria.get('dividend_min', 2.0)
        default_debt_max = st.session_state.current_criteria.get('debt_max', 50.0)
    else:
        default_pe_min = 5.0
        default_pe_max = 20.0
        default_pb_min = 0.5
        default_pb_max = 2.0
        default_roe_min = 10.0
        default_dividend_min = 2.0
        default_debt_max = 50.0

# PER条件
pe_min = st.sidebar.number_input("PER 最小値", min_value=0.0, max_value=100.0, value=default_pe_min, step=0.5)
pe_max = st.sidebar.number_input("PER 最大値", min_value=0.0, max_value=100.0, value=default_pe_max, step=0.5)

# PBR条件
pb_min = st.sidebar.number_input("PBR 最小値", min_value=0.0, max_value=10.0, value=default_pb_min, step=0.1)
pb_max = st.sidebar.number_input("PBR 最大値", min_value=0.0, max_value=10.0, value=default_pb_max, step=0.1)

# ROE条件
roe_min = st.sidebar.number_input("ROE 最小値 (%)", min_value=0.0, max_value=50.0, value=default_roe_min, step=1.0)

# 配当利回り条件
dividend_min = st.sidebar.number_input("配当利回り 最小値 (%)", min_value=0.0, max_value=10.0, value=default_dividend_min, step=0.1)

# 負債比率条件
debt_max = st.sidebar.number_input("負債比率 最大値", min_value=0.0, max_value=200.0, value=default_debt_max, step=5.0)

# 現在の条件をセッション状態に保存
st.session_state.current_criteria = {
    'pe_min': pe_min,
    'pe_max': pe_max,
    'pb_min': pb_min,
    'pb_max': pb_max,
    'roe_min': roe_min,
    'dividend_min': dividend_min,
    'debt_max': debt_max
}

# セクターフィルター
st.sidebar.subheader("🏢 セクターフィルター")

# セクターオプション
sector_options = ["Technology", "Financial Services", "Consumer Cyclical", "Industrials", 
                 "Healthcare", "Consumer Defensive", "Energy", "Basic Materials", "Communication Services"]

# AI推奨セクターを取得
default_sectors = []
if selected_strategy == 'auto' and 'ai_recommendations' in st.session_state:
    ai_sectors = st.session_state.ai_recommendations['recommendations']['recommended_sectors']
    # セクター名をマッピング
    sector_mapping = {
        'IT・通信': 'Technology',
        '金融': 'Financial Services',
        '製造業': 'Industrials',
        'ヘルスケア': 'Healthcare',
        'エネルギー': 'Energy',
        '素材': 'Basic Materials',
        '通信': 'Communication Services'
    }
    default_sectors = [sector_mapping.get(sector, sector) for sector in ai_sectors if sector_mapping.get(sector) in sector_options]

sector_filter = st.sidebar.multiselect(
    "セクターを選択",
    sector_options,
    default=default_sectors
)

# 分析実行ボタン
if st.sidebar.button("🚀 分析実行", type="primary"):
    with st.spinner("株価データを取得中..."):
        # スクリーニング条件を設定
        criteria = {
            'pe_min': pe_min,
            'pe_max': pe_max,
            'pb_min': pb_min,
            'pb_max': pb_max,
            'roe_min': roe_min,
            'dividend_min': dividend_min,
            'debt_max': debt_max
        }
        
        # 高優先度銘柄のみを取得（レート制限対応）
        high_priority_symbols = analyzer.get_optimized_stock_list(max_stocks=50)
        japanese_stocks = {symbol: symbol for symbol in high_priority_symbols}
        
        # 高優先度銘柄の場合は並列処理で高速化
        if len(japanese_stocks) > 10:
            st.info(f"📊 高優先度銘柄分析中... ({len(japanese_stocks)}銘柄)")
            
            # 並列処理で株価データを取得
            symbols = list(japanese_stocks.values())
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("株価データを並列取得中...")
            
            # バッチサイズを制限（メモリ使用量を考慮）
            batch_size = 30
            screened_stocks = []
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(symbols))
                batch_symbols = symbols[start_idx:end_idx]
                
                status_text.text(f"バッチ {batch_idx + 1}/{total_batches} 処理中...")
                progress_bar.progress((batch_idx + 1) / total_batches)
                
                # 並列でデータ取得（レート制限対応）
                batch_data = analyzer.get_stock_data_batch(batch_symbols, max_workers=2)
                
                # 各銘柄の分析
                for symbol, stock_data in batch_data.items():
                    if stock_data and stock_data['data'] is not None and not stock_data['data'].empty:
                        metrics = analyzer.calculate_financial_metrics(stock_data)
                        if metrics and analyzer._meets_criteria(metrics, criteria):
                            # 銘柄名を取得
                            stock_name = next((name for name, sym in japanese_stocks.items() if sym == symbol), symbol)
                            metrics['name'] = stock_name
                            metrics['symbol'] = symbol
                            metrics['stock_data'] = stock_data  # 株価データも保存
                            screened_stocks.append(metrics)
        else:
            # 少数銘柄の場合は従来の処理
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            screened_stocks = []
            total_stocks = len(japanese_stocks)
            error_count = 0
            
            for i, (stock_name, symbol) in enumerate(japanese_stocks.items()):
                try:
                    status_text.text(f"分析中: {stock_name}")
                    progress_bar.progress((i + 1) / total_stocks)
                    
                    stock_data = analyzer.get_stock_data(symbol)
                    if stock_data and stock_data['data'] is not None and not stock_data['data'].empty:
                        metrics = analyzer.calculate_financial_metrics(stock_data)
                        if metrics and analyzer._meets_criteria(metrics, criteria):
                            metrics['name'] = stock_name
                            metrics['symbol'] = symbol
                            metrics['stock_data'] = stock_data  # 株価データも保存
                            screened_stocks.append(metrics)
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # 最初の5つのエラーのみ表示
                        print(f"エラー {stock_name} ({symbol}): {e}")
                    continue
        
        # 結果をセッション状態に保存
        st.session_state.screened_stocks = pd.DataFrame(screened_stocks)
        st.session_state.analysis_completed = True

# 分析結果の表示
if hasattr(st.session_state, 'analysis_completed') and st.session_state.analysis_completed:
    df = st.session_state.screened_stocks
    
    if not df.empty:
        st.success(f"✅ {len(df)}銘柄が条件に合致しました！")
        
        # タブで結果を表示
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18, tab19, tab20, tab21, tab22, tab23 = st.tabs(["📊 データ一覧", "📈 可視化", "📋 レポート", "🎯 おすすめ銘柄", "🔮 動向予想", "⚡ 短期予測", "🚦 トレーディングシグナル", "💰 利益最大化", "🛡️ リスク管理", "🏢 高度分析", "💰 企業価値", "📊 技術分析", "📈 トレンド分析", "⚠️ リスク分析", "📊 ポートフォリオ", "🤖 AI分析", "👤 パーソナライズ", "📋 ファンダメンタルズ選定", "🔔 アラート管理", "📊 バックテスト", "📈 実績管理", "💼 ポートフォリオ管理", "📰 リアルタイムニュース"])
        
        with tab1:
            st.subheader("スクリーニング結果")
            
            # データフレームの表示
            display_df = df[['name', 'current_price', 'pe_ratio', 'pb_ratio', 'roe', 
                           'dividend_yield', 'debt_to_equity', 'sector']].copy()
            display_df.columns = ['銘柄名', '現在価格', 'PER', 'PBR', 'ROE(%)', 
                                '配当利回り(%)', '負債比率', 'セクター']
            
            # 数値のフォーマット
            display_df['現在価格'] = display_df['現在価格'].apply(lambda x: f"¥{x:,.0f}")
            display_df['PER'] = display_df['PER'].apply(lambda x: f"{x:.2f}")
            display_df['PBR'] = display_df['PBR'].apply(lambda x: f"{x:.2f}")
            display_df['ROE(%)'] = display_df['ROE(%)'].apply(lambda x: f"{x:.2f}%")
            display_df['配当利回り(%)'] = display_df['配当利回り(%)'].apply(lambda x: f"{x:.2f}%")
            display_df['負債比率'] = display_df['負債比率'].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(display_df, width="stretch")
            
            # エクスポート機能
            export_manager.create_export_ui(display_df, 'dataframe', 'screening_results')
            
            # CSVダウンロード
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"stock_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with tab2:
            st.subheader("📈 可視化分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # PER vs PBR 散布図
                fig1 = px.scatter(df, x='pe_ratio', y='pb_ratio', 
                                size='market_cap', color='roe',
                                hover_data=['name', 'dividend_yield', 'debt_to_equity'],
                                title='PER vs PBR 散布図',
                                labels={'pe_ratio': 'PER', 'pb_ratio': 'PBR', 'roe': 'ROE(%)'})
                st.plotly_chart(fig1, width="stretch")
            
            with col2:
                # ROE上位10銘柄
                top_roe = df.nlargest(10, 'roe')
                fig2 = px.bar(top_roe, x='name', y='roe',
                            title='ROE上位10銘柄',
                            labels={'roe': 'ROE(%)', 'name': '銘柄名'})
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, width="stretch")
            
            # セクター別分析
            if len(df['sector'].unique()) > 1:
                st.subheader("🏢 セクター別分析")
                sector_analysis = df.groupby('sector').agg({
                    'roe': 'mean',
                    'pe_ratio': 'mean',
                    'dividend_yield': 'mean'
                }).round(2)
                
                fig3 = px.bar(sector_analysis, y=sector_analysis.index, x='roe',
                            title='セクター別平均ROE',
                            orientation='h',
                            labels={'roe': '平均ROE(%)', 'sector': 'セクター'})
                st.plotly_chart(fig3, width="stretch")
        
        with tab3:
            st.subheader("📋 分析レポート")
            report = analyzer.generate_report(df)
            st.markdown(report)
        
        with tab4:
            st.subheader("🎯 おすすめ銘柄")
            
            # 総合スコア計算
            df['score'] = (
                (df['roe'] / df['roe'].max()) * 0.3 +
                (df['dividend_yield'] / df['dividend_yield'].max()) * 0.2 +
                (1 / (df['pe_ratio'] / df['pe_ratio'].min())) * 0.3 +
                (1 / (df['pb_ratio'] / df['pb_ratio'].min())) * 0.2
            )
            
            # スコア上位5銘柄
            top_picks = df.nlargest(5, 'score')
            
            for idx, stock in top_picks.iterrows():
                with st.expander(f"🥇 {stock['name']} (スコア: {stock['score']:.3f})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("現在価格", f"¥{stock['current_price']:,.0f}")
                        st.metric("PER", f"{stock['pe_ratio']:.2f}")
                        st.metric("PBR", f"{stock['pb_ratio']:.2f}")
                    
                    with col2:
                        st.metric("ROE", f"{stock['roe']:.2f}%")
                        st.metric("配当利回り", f"{stock['dividend_yield']:.2f}%")
                        st.metric("負債比率", f"{stock['debt_to_equity']:.1f}")
                    
                    with col3:
                        st.metric("セクター", stock['sector'])
                        st.metric("業界", stock['industry'])
                        st.metric("ベータ", f"{stock['beta']:.2f}")
        
        with tab5:
            st.subheader("🔮 銘柄動向予想")
            
            # 動向分析ボタン
            if st.button("🔍 動向分析を実行", type="primary"):
                with st.spinner("銘柄の動向分析中..."):
                    # スクリーニング結果から既存のデータを再利用
                    stock_data_dict = {}
                    metrics_dict = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        
                        # 保存された株価データを取得
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            stock_data_dict[symbol] = stock['stock_data']
                            
                            # 財務指標を再計算（動向分析用に最適化）
                            metrics = {
                                'per': stock.get('pe_ratio', 0),
                                'pbr': stock.get('pb_ratio', 0),
                                'roe': stock.get('roe', 0),
                                'debt_ratio': stock.get('debt_to_equity', 0),
                                'dividend_yield': stock.get('dividend_yield', 0)
                            }
                            metrics_dict[symbol] = metrics
                    
                    # 動向分析を実行
                    if stock_data_dict and metrics_dict:
                        try:
                            forecasts = forecast_analyzer.analyze_multiple_stocks(stock_data_dict, metrics_dict)
                            st.session_state.forecasts = forecasts
                            st.success(f"✅ {len(forecasts)}銘柄の動向分析が完了しました！")
                        except Exception as e:
                            st.error(f"❌ 動向分析中にエラーが発生しました: {str(e)}")
                    else:
                        st.warning("⚠️ 動向分析に必要なデータが一部不足しています。")
                        st.info("💡 ヒント: スクリーニングを再実行してから動向分析を試してください。")
            
            # 動向分析結果の表示
            if 'forecasts' in st.session_state and st.session_state.forecasts:
                forecasts = st.session_state.forecasts
                
                # 予想サマリー
                st.markdown("### 📊 予想サマリー")
                bullish_count = len([f for f in forecasts if f['forecast'] in ['bullish', 'strong_bullish']])
                bearish_count = len([f for f in forecasts if f['forecast'] in ['bearish', 'strong_bearish']])
                neutral_count = len([f for f in forecasts if f['forecast'] == 'neutral'])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📈 上昇予想", bullish_count)
                with col2:
                    st.metric("📉 下落予想", bearish_count)
                with col3:
                    st.metric("➡️ 横ばい予想", neutral_count)
                with col4:
                    avg_confidence = sum([f['confidence'] for f in forecasts]) / len(forecasts)
                    st.metric("🎯 平均信頼度", f"{avg_confidence:.1f}%")
                
                # 銘柄別詳細分析
                st.markdown("### 🔍 銘柄別詳細分析")
                
                for forecast in forecasts:
                    # 予想方向のアイコン
                    if forecast['forecast'] in ['strong_bullish', 'bullish']:
                        icon = "📈"
                        color = "green"
                    elif forecast['forecast'] in ['strong_bearish', 'bearish']:
                        icon = "📉"
                        color = "red"
                    else:
                        icon = "➡️"
                        color = "gray"
                    
                    # 信頼度の色分け
                    if forecast['confidence'] >= 70:
                        confidence_color = "🟢"
                    elif forecast['confidence'] >= 50:
                        confidence_color = "🟡"
                    else:
                        confidence_color = "🔴"
                    
                    with st.expander(f"{icon} {forecast['symbol']} - {forecast['direction']}予想 {confidence_color}{forecast['confidence']:.0f}%"):
                        # 基本情報
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**予想方向:** {forecast['direction']}")
                            st.markdown(f"**推奨アクション:** {forecast['action']}")
                        with col2:
                            st.markdown(f"**総合スコア:** {forecast['total_score']:.2f}")
                            st.markdown(f"**分析日時:** {forecast['analysis_date']}")
                        with col3:
                            st.markdown(f"**信頼度:** {forecast['confidence']:.1f}%")
                            if forecast['risk_factors']:
                                st.markdown(f"**リスク要因:** {', '.join(forecast['risk_factors'])}")
                        
                        # 技術分析
                        st.markdown("#### 📊 技術分析")
                        tech = forecast['technical_analysis']
                        st.markdown(f"**トレンド:** {tech['trend']} (スコア: {tech['score']})")
                        for reason in tech['reasons']:
                            st.write(f"• {reason}")
                        
                        # ファンダメンタル分析
                        st.markdown("#### 💰 ファンダメンタル分析")
                        fund = forecast['fundamental_analysis']
                        st.markdown(f"**強度:** {fund['strength']} (スコア: {fund['score']})")
                        for reason in fund['reasons']:
                            st.write(f"• {reason}")
                        
                        # 市場環境分析
                        st.markdown("#### 🌍 市場環境分析")
                        market = forecast['market_analysis']
                        st.markdown(f"**環境:** {market['environment']} (スコア: {market['score']})")
                        for reason in market['reasons']:
                            st.write(f"• {reason}")
                        
                        if 'nikkei_change' in market:
                            st.markdown(f"**日経平均変化:** {market['nikkei_change']:.2f}%")
                        if 'volatility' in market:
                            st.markdown(f"**市場ボラティリティ:** {market['volatility']:.1f}%")
                
                # 予想分布チャート
                st.markdown("### 📊 予想分布")
                forecast_counts = {}
                for forecast in forecasts:
                    direction = forecast['direction']
                    forecast_counts[direction] = forecast_counts.get(direction, 0) + 1
                
                if forecast_counts:
                    fig_forecast = px.pie(
                        values=list(forecast_counts.values()),
                        names=list(forecast_counts.keys()),
                        title="予想方向の分布",
                        color_discrete_map={
                            '上昇': '#2E8B57',
                            '下落': '#DC143C',
                            '横ばい': '#808080'
                        }
                    )
                    st.plotly_chart(fig_forecast, width="stretch")
                
                # 信頼度分布
                st.markdown("### 🎯 信頼度分布")
                confidence_data = [f['confidence'] for f in forecasts]
                fig_confidence = px.histogram(
                    x=confidence_data,
                    nbins=10,
                    title="信頼度の分布",
                    labels={'x': '信頼度 (%)', 'y': '銘柄数'}
                )
                st.plotly_chart(fig_confidence, width="stretch")
        
        with tab6:
            st.subheader("⚡ 短期予測分析（1日〜1週間）")
            
            # 予測期間選択
            col1, col2 = st.columns(2)
            with col1:
                prediction_days = st.selectbox(
                    "予測期間を選択",
                    [1, 3, 5],
                    format_func=lambda x: f"{x}日後",
                    index=0
                )
            
            with col2:
                if st.button("🔍 短期予測を実行", type="primary"):
                    with st.spinner("短期予測分析中..."):
                        # スクリーニング結果から既存のデータを再利用
                        stock_data_dict = {}
                        
                        for idx, stock in df.iterrows():
                            symbol = stock['symbol']
                            
                            # 保存された株価データを取得
                            if 'stock_data' in stock and stock['stock_data'] is not None:
                                stock_data_dict[symbol] = stock['stock_data']
                        
                        # 短期予測を実行
                        if stock_data_dict:
                            try:
                                predictions = short_term_predictor.analyze_multiple_stocks(stock_data_dict)
                                st.session_state.short_term_predictions = predictions
                                st.success(f"✅ {len(predictions)}銘柄の短期予測が完了しました！")
                            except Exception as e:
                                st.error(f"❌ 短期予測中にエラーが発生しました: {str(e)}")
                        else:
                            st.warning("⚠️ 短期予測に必要なデータが不足しています。")
            
            # 短期予測結果の表示
            if 'short_term_predictions' in st.session_state and st.session_state.short_term_predictions:
                predictions = st.session_state.short_term_predictions
                
                # 予測サマリー
                st.markdown("### 📊 短期予測サマリー")
                
                # 各モデルの予測結果を集計
                model_summaries = {}
                for symbol, pred_data in predictions.items():
                    if 'predictions' in pred_data:
                        for model_name, model_pred in pred_data['predictions'].items():
                            if 'predicted_return' in model_pred:
                                if model_name not in model_summaries:
                                    model_summaries[model_name] = {'bullish': 0, 'bearish': 0, 'neutral': 0}
                                
                                return_val = model_pred['predicted_return']
                                if return_val > 0.02:  # 2%以上上昇
                                    model_summaries[model_name]['bullish'] += 1
                                elif return_val < -0.02:  # 2%以上下落
                                    model_summaries[model_name]['bearish'] += 1
                                else:
                                    model_summaries[model_name]['neutral'] += 1
                
                # モデル別サマリー表示
                for model_name, summary in model_summaries.items():
                    st.markdown(f"#### {model_name}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("上昇予想", summary['bullish'])
                    with col2:
                        st.metric("下落予想", summary['bearish'])
                    with col3:
                        st.metric("横ばい予想", summary['neutral'])
                
                # 詳細予測結果
                st.markdown("### 📈 詳細予測結果")
                
                for symbol, pred_data in predictions.items():
                    if 'predictions' in pred_data:
                        with st.expander(f"📊 {symbol} - 現在価格: ¥{pred_data.get('current_price', 0):,.0f}"):
                            for model_name, model_pred in pred_data['predictions'].items():
                                if 'predicted_price' in model_pred:
                                    current_price = pred_data.get('current_price', 0)
                                    predicted_price = model_pred['predicted_price']
                                    predicted_return = model_pred['predicted_return']
                                    confidence = model_pred.get('confidence', 0)
                                    
                                    # 予想方向のアイコン
                                    if predicted_return > 0:
                                        direction_icon = "📈"
                                        direction_text = "上昇"
                                        color = "green"
                                    elif predicted_return < 0:
                                        direction_icon = "📉"
                                        direction_text = "下落"
                                        color = "red"
                                    else:
                                        direction_icon = "➡️"
                                        direction_text = "横ばい"
                                        color = "gray"
                                    
                                    st.markdown(f"**{model_name}** {direction_icon}")
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric(
                                            "予想価格",
                                            f"¥{predicted_price:,.0f}",
                                            f"{predicted_return*100:+.2f}%"
                                        )
                                    
                                    with col2:
                                        st.metric("信頼度", f"{confidence*100:.1f}%")
                                    
                                    with col3:
                                        st.markdown(f"**方向:** <span style='color:{color}'>{direction_text}</span>", unsafe_allow_html=True)
                                    
                                    st.markdown("---")
                
                # チャート表示（最初の銘柄）
                if predictions:
                    first_symbol = list(predictions.keys())[0]
                    first_pred = predictions[first_symbol]
                    
                    if 'predictions' in first_pred:
                        # 株価データを取得
                        for idx, stock in df.iterrows():
                            if stock['symbol'] == first_symbol and 'stock_data' in stock:
                                stock_data = stock['stock_data']
                                if stock_data and stock_data['data'] is not None:
                                    chart = short_term_predictor.create_prediction_chart(stock_data['data'], first_pred)
                                    st.plotly_chart(chart, width="stretch")
                                break
        
        with tab7:
            st.subheader("🚦 トレーディングシグナル分析")
            
            # シグナル分析ボタン
            if st.button("🔍 シグナル分析を実行", type="primary"):
                with st.spinner("トレーディングシグナル分析中..."):
                    # スクリーニング結果から既存のデータを再利用
                    stock_data_dict = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        
                        # 保存された株価データを取得
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            stock_data_dict[symbol] = stock['stock_data']
                    
                    # シグナル分析を実行
                    if stock_data_dict:
                        try:
                            signals = trading_signal_analyzer.analyze_multiple_stocks(stock_data_dict)
                            st.session_state.trading_signals = signals
                            st.success(f"✅ {len(signals)}銘柄のシグナル分析が完了しました！")
                        except Exception as e:
                            st.error(f"❌ シグナル分析中にエラーが発生しました: {str(e)}")
                    else:
                        st.warning("⚠️ シグナル分析に必要なデータが不足しています。")
            
            # シグナル分析結果の表示
            if 'trading_signals' in st.session_state and st.session_state.trading_signals:
                signals = st.session_state.trading_signals
                
                # シグナルサマリー
                st.markdown("### 📊 シグナルサマリー")
                
                buy_count = len([s for s in signals.values() if s.get('overall_signal') == 'BUY'])
                sell_count = len([s for s in signals.values() if s.get('overall_signal') == 'SELL'])
                hold_count = len([s for s in signals.values() if s.get('overall_signal') == 'HOLD'])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🟢 BUY", buy_count)
                with col2:
                    st.metric("🔴 SELL", sell_count)
                with col3:
                    st.metric("🟡 HOLD", hold_count)
                with col4:
                    avg_confidence = np.mean([s.get('confidence', 0) for s in signals.values() if 'confidence' in s])
                    st.metric("平均信頼度", f"{avg_confidence*100:.1f}%")
                
                # シグナル分布チャート
                signal_data = {
                    'BUY': buy_count,
                    'SELL': sell_count,
                    'HOLD': hold_count
                }
                
                fig_signal = go.Figure(data=[
                    go.Pie(
                        labels=list(signal_data.keys()),
                        values=list(signal_data.values()),
                        marker_colors=['green', 'red', 'yellow']
                    )
                ])
                fig_signal.update_layout(title="シグナル分布")
                st.plotly_chart(fig_signal, width="stretch")
                
                # 詳細シグナル結果
                st.markdown("### 🚦 詳細シグナル結果")
                
                # シグナル別にソート
                sorted_signals = sorted(
                    signals.items(),
                    key=lambda x: x[1].get('confidence', 0) if 'confidence' in x[1] else 0,
                    reverse=True
                )
                
                for symbol, signal_data in sorted_signals:
                    if 'overall_signal' in signal_data:
                        overall_signal = signal_data['overall_signal']
                        confidence = signal_data.get('confidence', 0)
                        current_price = signal_data.get('current_price', 0)
                        
                        # シグナルアイコン
                        if overall_signal == 'BUY':
                            signal_icon = "🟢"
                            signal_color = "green"
                        elif overall_signal == 'SELL':
                            signal_icon = "🔴"
                            signal_color = "red"
                        else:
                            signal_icon = "🟡"
                            signal_color = "orange"
                        
                        with st.expander(f"{signal_icon} {symbol} - {overall_signal} (信頼度: {confidence*100:.1f}%) - ¥{current_price:,.0f}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### 📊 シグナル詳細")
                                st.metric("総合判定", overall_signal)
                                st.metric("信頼度", f"{confidence*100:.1f}%")
                                st.metric("買いスコア", f"{signal_data.get('buy_score', 0):.2f}")
                                st.metric("売りスコア", f"{signal_data.get('sell_score', 0):.2f}")
                            
                            with col2:
                                st.markdown("#### 📈 価格情報")
                                st.metric("現在価格", f"¥{current_price:,.0f}")
                                st.metric("分析日時", signal_data.get('analysis_date', 'N/A'))
                            
                            # 買いシグナル
                            if signal_data.get('buy_signals'):
                                st.markdown("#### 🟢 買いシグナル")
                                for signal in signal_data['buy_signals']:
                                    st.markdown(f"• **{signal['type']}** (強度: {signal['strength']:.1f}) - {signal['description']}")
                            
                            # 売りシグナル
                            if signal_data.get('sell_signals'):
                                st.markdown("#### 🔴 売りシグナル")
                                for signal in signal_data['sell_signals']:
                                    st.markdown(f"• **{signal['type']}** (強度: {signal['strength']:.1f}) - {signal['description']}")
                            
                            # ニュートラルシグナル
                            if signal_data.get('neutral_signals'):
                                st.markdown("#### 🟡 ニュートラルシグナル")
                                for signal in signal_data['neutral_signals']:
                                    st.markdown(f"• **{signal['type']}** (強度: {signal['strength']:.1f}) - {signal['description']}")
                
                # チャート表示（最初の銘柄）
                if signals:
                    first_symbol = list(signals.keys())[0]
                    first_signal = signals[first_symbol]
                    
                    if 'overall_signal' in first_signal:
                        # 株価データを取得
                        for idx, stock in df.iterrows():
                            if stock['symbol'] == first_symbol and 'stock_data' in stock:
                                stock_data = stock['stock_data']
                                if stock_data and stock_data['data'] is not None:
                                    chart = trading_signal_analyzer.create_signal_chart(stock_data['data'], first_signal)
                                    st.plotly_chart(chart, width="stretch")
                                break
        
        with tab8:
            st.subheader("💰 利益最大化分析")
            
            # 利益最大化分析ボタン
            if st.button("🔍 利益最大化分析を実行", type="primary"):
                with st.spinner("利益最大化分析中..."):
                    # スクリーニング結果から既存のデータを再利用
                    stock_data_dict = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        
                        # 保存された株価データを取得
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            stock_data_dict[symbol] = stock['stock_data']
                    
                    # 利益最大化分析を実行
                    if stock_data_dict:
                        try:
                            profit_opportunities = profit_maximizer.analyze_multiple_stocks(stock_data_dict)
                            st.session_state.profit_opportunities = profit_opportunities
                            st.success(f"✅ {len(profit_opportunities)}銘柄の利益最大化分析が完了しました！")
                        except Exception as e:
                            st.error(f"❌ 利益最大化分析中にエラーが発生しました: {str(e)}")
                    else:
                        st.warning("⚠️ 利益最大化分析に必要なデータが不足しています。")
            
            # 利益最大化分析結果の表示
            if 'profit_opportunities' in st.session_state and st.session_state.profit_opportunities:
                opportunities = st.session_state.profit_opportunities
                
                # 分析サマリー
                st.markdown("### 📊 利益機会サマリー")
                
                # 戦略別統計
                strategy_stats = {}
                best_opportunities = []
                
                for symbol, opp_data in opportunities.items():
                    if 'best_strategy' in opp_data:
                        strategy_name = opp_data['best_strategy'][0]
                        confidence = opp_data['best_strategy'][1]['confidence']
                        
                        if strategy_name not in strategy_stats:
                            strategy_stats[strategy_name] = 0
                        strategy_stats[strategy_name] += 1
                        
                        best_opportunities.append({
                            'symbol': symbol,
                            'strategy': strategy_name,
                            'confidence': confidence,
                            'data': opp_data['best_strategy'][1]
                        })
                
                # 戦略別統計表示
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("モメンタム", strategy_stats.get('momentum', 0))
                with col2:
                    st.metric("平均回帰", strategy_stats.get('mean_reversion', 0))
                with col3:
                    st.metric("ブレイクアウト", strategy_stats.get('breakout', 0))
                with col4:
                    st.metric("スイング", strategy_stats.get('swing', 0))
                
                # 戦略分布チャート
                if strategy_stats:
                    fig_strategy = go.Figure(data=[
                        go.Pie(
                            labels=list(strategy_stats.keys()),
                            values=list(strategy_stats.values()),
                            title="戦略別分布"
                        )
                    ])
                    st.plotly_chart(fig_strategy, width="stretch")
                
                # 最適機会ランキング
                st.markdown("### 🏆 最適利益機会ランキング")
                
                # 信頼度順にソート
                best_opportunities.sort(key=lambda x: x['confidence'], reverse=True)
                
                for i, opp in enumerate(best_opportunities[:10]):  # 上位10銘柄
                    symbol = opp['symbol']
                    strategy = opp['strategy']
                    confidence = opp['confidence']
                    data = opp['data']
                    
                    # 戦略アイコン
                    strategy_icons = {
                        'momentum': '🚀',
                        'mean_reversion': '🔄',
                        'breakout': '💥',
                        'scalping': '⚡',
                        'swing': '🌊'
                    }
                    
                    strategy_icon = strategy_icons.get(strategy, '📈')
                    
                    with st.expander(f"{i+1}. {strategy_icon} {symbol} - {strategy} (信頼度: {confidence*100:.1f}%)"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 📊 戦略詳細")
                            st.metric("戦略", strategy)
                            st.metric("信頼度", f"{confidence*100:.1f}%")
                            if 'risk_reward_ratio' in data:
                                st.metric("リスクリワード比", f"{data['risk_reward_ratio']:.2f}")
                        
                        with col2:
                            st.markdown("#### 💰 価格目標")
                            if 'target_price' in data:
                                st.metric("目標価格", f"¥{data['target_price']:,.0f}")
                            if 'stop_loss' in data:
                                st.metric("ストップロス", f"¥{data['stop_loss']:,.0f}")
                        
                        # エントリー条件
                        if data.get('entry_conditions'):
                            st.markdown("#### ✅ エントリー条件")
                            for condition in data['entry_conditions']:
                                st.markdown(f"• {condition}")
                        
                        # エグジット条件
                        if data.get('exit_conditions'):
                            st.markdown("#### ❌ エグジット条件")
                            for condition in data['exit_conditions']:
                                st.markdown(f"• {condition}")
                        
                        # 利益計算
                        if 'target_price' in data and 'stop_loss' in data:
                            current_price = data.get('current_price', 0)
                            if current_price > 0:
                                profit_potential = (data['target_price'] - current_price) / current_price * 100
                                loss_potential = (current_price - data['stop_loss']) / current_price * 100
                                
                                st.markdown("#### 💡 利益・損失予想")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("利益予想", f"+{profit_potential:.1f}%")
                                with col2:
                                    st.metric("損失予想", f"-{loss_potential:.1f}%")
                
                # チャート表示（最上位の銘柄）
                if best_opportunities:
                    top_symbol = best_opportunities[0]['symbol']
                    top_opportunity = opportunities[top_symbol]
                    
                    if 'best_strategy' in top_opportunity:
                        # 株価データを取得
                        for idx, stock in df.iterrows():
                            if stock['symbol'] == top_symbol and 'stock_data' in stock:
                                stock_data = stock['stock_data']
                                if stock_data and stock_data['data'] is not None:
                                    chart = profit_maximizer.create_profit_chart(stock_data['data'], top_opportunity)
                                    st.plotly_chart(chart, width="stretch")
                                break
        
        with tab9:
            st.subheader("🛡️ リスク管理分析")
            
            # リスク管理設定
            col1, col2, col3 = st.columns(3)
            with col1:
                account_balance = st.number_input(
                    "口座残高 (円)",
                    min_value=100000,
                    max_value=100000000,
                    value=1000000,
                    step=100000
                )
            with col2:
                risk_level = st.selectbox(
                    "リスクレベル",
                    ['conservative', 'moderate', 'aggressive'],
                    format_func=lambda x: {
                        'conservative': '保守的 (1%損失)',
                        'moderate': '中程度 (2%損失)',
                        'aggressive': '積極的 (5%損失)'
                    }[x],
                    index=1
                )
            with col3:
                if st.button("🔍 リスク管理分析を実行", type="primary"):
                    with st.spinner("リスク管理分析中..."):
                        # スクリーニング結果から既存のデータを再利用
                        stock_data_dict = {}
                        
                        for idx, stock in df.iterrows():
                            symbol = stock['symbol']
                            
                            # 保存された株価データを取得
                            if 'stock_data' in stock and stock['stock_data'] is not None:
                                stock_data_dict[symbol] = stock['stock_data']
                        
                        # リスク管理分析を実行
                        if stock_data_dict:
                            try:
                                risk_analyses = risk_manager.analyze_multiple_stocks(
                                    stock_data_dict, account_balance, risk_level
                                )
                                st.session_state.risk_analyses = risk_analyses
                                st.success(f"✅ {len(risk_analyses)}銘柄のリスク管理分析が完了しました！")
                            except Exception as e:
                                st.error(f"❌ リスク管理分析中にエラーが発生しました: {str(e)}")
                        else:
                            st.warning("⚠️ リスク管理分析に必要なデータが不足しています。")
            
            # リスク管理分析結果の表示
            if 'risk_analyses' in st.session_state and st.session_state.risk_analyses:
                risk_analyses = st.session_state.risk_analyses
                
                # リスクサマリー
                st.markdown("### 📊 リスク管理サマリー")
                
                # リスク指標の集計
                total_risk_score = 0
                total_volatility = 0
                total_max_drawdown = 0
                valid_analyses = 0
                
                for symbol, analysis in risk_analyses.items():
                    if 'risk_metrics' in analysis:
                        total_risk_score += analysis['risk_metrics']['risk_score']
                        total_volatility += analysis['risk_metrics']['volatility']
                        total_max_drawdown += abs(analysis['risk_metrics']['max_drawdown'])
                        valid_analyses += 1
                
                if valid_analyses > 0:
                    avg_risk_score = total_risk_score / valid_analyses
                    avg_volatility = total_volatility / valid_analyses
                    avg_max_drawdown = total_max_drawdown / valid_analyses
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("平均リスクスコア", f"{avg_risk_score:.1f}")
                    with col2:
                        st.metric("平均ボラティリティ", f"{avg_volatility*100:.1f}%")
                    with col3:
                        st.metric("平均最大ドローダウン", f"{avg_max_drawdown*100:.1f}%")
                    with col4:
                        st.metric("分析銘柄数", valid_analyses)
                
                # リスクレベル別分布
                risk_levels = {'低リスク': 0, '中リスク': 0, '高リスク': 0}
                for symbol, analysis in risk_analyses.items():
                    if 'risk_metrics' in analysis:
                        risk_score = analysis['risk_metrics']['risk_score']
                        if risk_score < 30:
                            risk_levels['低リスク'] += 1
                        elif risk_score < 70:
                            risk_levels['中リスク'] += 1
                        else:
                            risk_levels['高リスク'] += 1
                
                # リスク分布チャート
                fig_risk = go.Figure(data=[
                    go.Pie(
                        labels=list(risk_levels.keys()),
                        values=list(risk_levels.values()),
                        marker_colors=['green', 'orange', 'red']
                    )
                ])
                fig_risk.update_layout(title="リスクレベル分布")
                st.plotly_chart(fig_risk, width="stretch")
                
                # 詳細リスク分析結果
                st.markdown("### 🛡️ 詳細リスク分析結果")
                
                # リスクスコア順にソート
                sorted_analyses = sorted(
                    risk_analyses.items(),
                    key=lambda x: x[1].get('risk_metrics', {}).get('risk_score', 100),
                    reverse=False  # 低リスクから表示
                )
                
                for symbol, analysis in sorted_analyses:
                    if 'risk_metrics' in analysis:
                        risk_metrics = analysis['risk_metrics']
                        current_price = analysis.get('current_price', 0)
                        risk_score = risk_metrics['risk_score']
                        
                        # リスクレベルアイコン
                        if risk_score < 30:
                            risk_icon = "🟢"
                            risk_color = "green"
                        elif risk_score < 70:
                            risk_icon = "🟡"
                            risk_color = "orange"
                        else:
                            risk_icon = "🔴"
                            risk_color = "red"
                        
                        with st.expander(f"{risk_icon} {symbol} - リスクスコア: {risk_score:.1f} - ¥{current_price:,.0f}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### 📊 リスク指標")
                                st.metric("リスクスコア", f"{risk_score:.1f}")
                                st.metric("ボラティリティ", f"{risk_metrics['volatility']*100:.1f}%")
                                st.metric("シャープレシオ", f"{risk_metrics['sharpe_ratio']:.2f}")
                                st.metric("最大ドローダウン", f"{risk_metrics['max_drawdown']*100:.1f}%")
                            
                            with col2:
                                st.markdown("#### 💰 リスク管理")
                                if 'stop_loss_analysis' in analysis and 'recommended_stop_loss' in analysis['stop_loss_analysis']:
                                    stop_loss = analysis['stop_loss_analysis']['recommended_stop_loss'][1]
                                    st.metric("推奨ストップロス", f"¥{stop_loss['price']:,.0f}")
                                
                                if 'take_profit_analysis' in analysis and 'recommended_take_profit' in analysis['take_profit_analysis']:
                                    take_profit = analysis['take_profit_analysis']['recommended_take_profit'][1]
                                    st.metric("推奨テイクプロフィット", f"¥{take_profit['price']:,.0f}")
                                
                                if 'position_analysis' in analysis and 'recommended_shares' in analysis['position_analysis']:
                                    position = analysis['position_analysis']
                                    st.metric("推奨株数", f"{position['recommended_shares']:,}株")
                                    st.metric("推奨投資額", f"¥{position['recommended_amount']:,.0f}")
                            
                            # ストップロス詳細
                            if 'stop_loss_analysis' in analysis and 'stop_losses' in analysis['stop_loss_analysis']:
                                st.markdown("#### 🛑 ストップロス戦略")
                                stop_losses = analysis['stop_loss_analysis']['stop_losses']
                                for method, details in stop_losses.items():
                                    st.markdown(f"• **{details['method']}**: ¥{details['price']:,.0f} - {details['description']}")
                            
                            # テイクプロフィット詳細
                            if 'take_profit_analysis' in analysis and 'take_profits' in analysis['take_profit_analysis']:
                                st.markdown("#### 🎯 テイクプロフィット戦略")
                                take_profits = analysis['take_profit_analysis']['take_profits']
                                for method, details in take_profits.items():
                                    st.markdown(f"• **{details['method']}**: ¥{details['price']:,.0f} - {details['description']}")
                            
                            # VaR情報
                            st.markdown("#### ⚠️ リスク指標詳細")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("95% VaR", f"{risk_metrics['var_95']*100:.2f}%")
                            with col2:
                                st.metric("99% VaR", f"{risk_metrics['var_99']*100:.2f}%")
                
                # チャート表示（最上位の銘柄）
                if sorted_analyses:
                    top_symbol = sorted_analyses[0][0]
                    top_analysis = sorted_analyses[0][1]
                    
                    if 'risk_metrics' in top_analysis:
                        # 株価データを取得
                        for idx, stock in df.iterrows():
                            if stock['symbol'] == top_symbol and 'stock_data' in stock:
                                stock_data = stock['stock_data']
                                if stock_data and stock_data['data'] is not None:
                                    chart = risk_manager.create_risk_chart(stock_data['data'], top_analysis)
                                    st.plotly_chart(chart, width="stretch")
                                break
        
        with tab10:
            st.subheader("🏢 高度ファンダメンタル分析")
            
            if st.button("🔍 高度分析を実行", type="primary"):
                with st.spinner("高度ファンダメンタル分析中..."):
                    advanced_analyses = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            # 高度ファンダメンタル分析を実行
                            advanced_analysis = advanced_fundamental_analyzer.comprehensive_fundamental_analysis(
                                stock['stock_data'], 
                                {
                                    'pe_ratio': stock.get('pe_ratio', 0),
                                    'pb_ratio': stock.get('pb_ratio', 0),
                                    'roe': stock.get('roe', 0),
                                    'debt_to_equity': stock.get('debt_to_equity', 0),
                                    'dividend_yield': stock.get('dividend_yield', 0)
                                },
                                stock.get('sector', '製造業')
                            )
                            
                            if advanced_analysis:
                                advanced_analyses[symbol] = advanced_analysis
                    
                    if advanced_analyses:
                        st.session_state.advanced_analyses = advanced_analyses
                        st.success(f"✅ {len(advanced_analyses)}銘柄の高度分析が完了しました！")
                    else:
                        st.warning("⚠️ 高度分析に必要なデータが不足しています。")
            
            if 'advanced_analyses' in st.session_state and st.session_state.advanced_analyses:
                analyses = st.session_state.advanced_analyses
                
                # 分析サマリー
                st.markdown("### 📊 分析サマリー")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    strong_buy = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'strong_buy')
                    st.metric("強く推奨", strong_buy)
                
                with col2:
                    buy = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'buy')
                    st.metric("推奨", buy)
                
                with col3:
                    hold = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'hold')
                    st.metric("保有", hold)
                
                with col4:
                    avg_score = sum(analysis['overall_score'] for analysis in analyses.values()) / len(analyses)
                    st.metric("平均スコア", f"{avg_score:.1f}")
                
                # 銘柄別詳細分析
                st.markdown("### 🔍 銘柄別詳細分析")
                
                for symbol, analysis in analyses.items():
                    stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                    
                    with st.expander(f"📈 {stock_name} ({symbol}) - スコア: {analysis['overall_score']:.1f}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**総合評価**: {analysis['recommendation_description']}")
                            st.markdown(f"**分析日時**: {analysis['analysis_date']}")
                            
                            # 財務健全性
                            if analysis['financial_health']:
                                health = analysis['financial_health']
                                st.markdown(f"**財務健全性**: {health['health_description']} ({health['total_score']:.1f}点)")
                                
                                # 個別スコア
                                st.markdown("**個別スコア**:")
                                for metric, score in health['individual_scores'].items():
                                    st.markdown(f"- {metric}: {score:.1f}点")
                        
                        with col2:
                            # 業界比較
                            if analysis['industry_comparison']:
                                industry = analysis['industry_comparison']
                                st.markdown(f"**業界ランキング**: {industry['industry_ranking']}")
                                st.markdown(f"**競争ポジション**: {industry['competitive_position']}")
                            
                            # 成長分析
                            if analysis['growth_analysis']:
                                growth = analysis['growth_analysis']
                                st.markdown(f"**成長トレンド**: {growth['trend_description']}")
                                st.markdown(f"**1年成長率**: {growth['growth_1y']:.1f}%")
        
        with tab7:
            st.subheader("💰 企業価値評価")
            
            if st.button("🔍 企業価値分析を実行", type="primary"):
                with st.spinner("企業価値評価中..."):
                    valuation_analyses = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            # 企業価値評価を実行
                            valuation_analysis = valuation_analyzer.comprehensive_valuation_analysis(
                                stock['stock_data'],
                                {
                                    'pe_ratio': stock.get('pe_ratio', 0),
                                    'pb_ratio': stock.get('pb_ratio', 0),
                                    'roe': stock.get('roe', 0),
                                    'debt_to_equity': stock.get('debt_to_equity', 0),
                                    'dividend_yield': stock.get('dividend_yield', 0),
                                    'market_cap': stock.get('market_cap', 0),
                                    'current_price': stock.get('current_price', 0)
                                },
                                stock.get('sector', '製造業')
                            )
                            
                            if valuation_analysis:
                                valuation_analyses[symbol] = valuation_analysis
                    
                    if valuation_analyses:
                        st.session_state.valuation_analyses = valuation_analyses
                        st.success(f"✅ {len(valuation_analyses)}銘柄の企業価値評価が完了しました！")
                    else:
                        st.warning("⚠️ 企業価値評価に必要なデータが不足しています。")
            
            if 'valuation_analyses' in st.session_state and st.session_state.valuation_analyses:
                valuations = st.session_state.valuation_analyses
                
                # 評価サマリー
                st.markdown("### 📊 評価サマリー")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    undervalued = sum(1 for val in valuations.values() 
                                    if val['dcf_analysis'] and val['dcf_analysis']['valuation_status'] == 'undervalued')
                    st.metric("割安銘柄", undervalued)
                
                with col2:
                    overvalued = sum(1 for val in valuations.values() 
                                   if val['dcf_analysis'] and val['dcf_analysis']['valuation_status'] == 'overvalued')
                    st.metric("割高銘柄", overvalued)
                
                with col3:
                    avg_score = sum(val['overall_score'] for val in valuations.values()) / len(valuations)
                    st.metric("平均評価スコア", f"{avg_score:.1f}")
                
                with col4:
                    strong_buy = sum(1 for val in valuations.values() if val['recommendation'] == 'strong_buy')
                    st.metric("強く推奨", strong_buy)
                
                # 銘柄別詳細評価
                st.markdown("### 🔍 銘柄別詳細評価")
                
                for symbol, valuation in valuations.items():
                    stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                    
                    with st.expander(f"💰 {stock_name} ({symbol}) - 評価スコア: {valuation['overall_score']:.1f}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**投資推奨**: {valuation['recommendation_description']}")
                            st.markdown(f"**評価日時**: {valuation['analysis_date']}")
                            
                            # DCF分析
                            if valuation['dcf_analysis']:
                                dcf = valuation['dcf_analysis']
                                st.markdown(f"**DCF理論価格**: ¥{dcf['theoretical_price']:,.0f}")
                                st.markdown(f"**現在価格**: ¥{dcf['current_price']:,.0f}")
                                st.markdown(f"**評価**: {dcf['valuation_description']}")
                                st.markdown(f"**安全マージン**: {dcf['margin_of_safety']:.1f}%")
                        
                        with col2:
                            # 相対評価
                            if valuation['relative_analysis']:
                                relative = valuation['relative_analysis']
                                st.markdown(f"**相対評価**: {relative['relative_description']}")
                                st.markdown(f"**業界平均価格**: ¥{relative['fair_price_avg']:,.0f}")
                            
                            # 配当分析
                            if valuation['dividend_analysis']:
                                dividend = valuation['dividend_analysis']
                                st.markdown(f"**配当持続性**: {dividend['sustainability_description']}")
                                st.markdown(f"**持続性スコア**: {dividend['sustainability_score']:.1f}点")
        
        with tab8:
            st.subheader("📊 高度技術分析")
            
            if st.button("🔍 技術分析を実行", type="primary"):
                with st.spinner("高度技術分析中..."):
                    technical_analyses = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            # 高度技術分析を実行
                            technical_analysis = advanced_technical_analyzer.comprehensive_technical_analysis(
                                stock['stock_data']
                            )
                            
                            if technical_analysis:
                                technical_analyses[symbol] = technical_analysis
                    
                    if technical_analyses:
                        st.session_state.technical_analyses = technical_analyses
                        st.success(f"✅ {len(technical_analyses)}銘柄の技術分析が完了しました！")
                    else:
                        st.warning("⚠️ 技術分析に必要なデータが不足しています。")
            
            if 'technical_analyses' in st.session_state and st.session_state.technical_analyses:
                analyses = st.session_state.technical_analyses
                
                # 分析サマリー
                st.markdown("### 📊 技術分析サマリー")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    strong_buy = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'strong_buy')
                    st.metric("強く推奨", strong_buy)
                
                with col2:
                    buy = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'buy')
                    st.metric("推奨", buy)
                
                with col3:
                    hold = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'hold')
                    st.metric("保有", hold)
                
                with col4:
                    avg_score = sum(analysis['overall_score'] for analysis in analyses.values()) / len(analyses)
                    st.metric("平均スコア", f"{avg_score:.1f}")
                
                # 銘柄別詳細技術分析
                st.markdown("### 🔍 銘柄別詳細技術分析")
                
                for symbol, analysis in analyses.items():
                    stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                    
                    with st.expander(f"📊 {stock_name} ({symbol}) - 技術スコア: {analysis['overall_score']:.1f}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**技術推奨**: {analysis['recommendation_description']}")
                            st.markdown(f"**総合シグナル**: {analysis['overall_signal']}")
                            st.markdown(f"**分析日時**: {analysis['analysis_date']}")
                            
                            # RSI
                            if analysis['technical_signals']['rsi']:
                                rsi = analysis['technical_signals']['rsi']
                                st.markdown(f"**RSI**: {rsi['value']:.1f} - {rsi['description']}")
                            
                            # MACD
                            if analysis['technical_signals']['macd']:
                                macd = analysis['technical_signals']['macd']
                                st.markdown(f"**MACD**: {macd['description']}")
                        
                        with col2:
                            # ボリンジャーバンド
                            if analysis['technical_signals']['bollinger_bands']:
                                bb = analysis['technical_signals']['bollinger_bands']
                                st.markdown(f"**ボリンジャーバンド**: {bb['description']}")
                            
                            # ストキャスティクス
                            if analysis['technical_signals']['stochastic']:
                                stoch = analysis['technical_signals']['stochastic']
                                st.markdown(f"**ストキャスティクス**: {stoch['description']}")
                            
                            # ボラティリティ
                            if analysis['technical_signals']['atr']:
                                atr = analysis['technical_signals']['atr']
                                st.markdown(f"**ボラティリティ**: {atr['volatility']}")
        
        with tab9:
            st.subheader("📈 トレンド分析")
            
            if st.button("🔍 トレンド分析を実行", type="primary"):
                with st.spinner("トレンド分析中..."):
                    trend_analyses = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            # トレンド分析を実行
                            trend_analysis = trend_analyzer.comprehensive_trend_analysis(
                                stock['stock_data']
                            )
                            
                            if trend_analysis:
                                trend_analyses[symbol] = trend_analysis
                    
                    if trend_analyses:
                        st.session_state.trend_analyses = trend_analyses
                        st.success(f"✅ {len(trend_analyses)}銘柄のトレンド分析が完了しました！")
                    else:
                        st.warning("⚠️ トレンド分析に必要なデータが不足しています。")
            
            if 'trend_analyses' in st.session_state and st.session_state.trend_analyses:
                analyses = st.session_state.trend_analyses
                
                # 分析サマリー
                st.markdown("### 📊 トレンド分析サマリー")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    uptrend = sum(1 for analysis in analyses.values() 
                                if analysis['overall_trend']['trend'] == 'uptrend')
                    st.metric("上昇トレンド", uptrend)
                
                with col2:
                    downtrend = sum(1 for analysis in analyses.values() 
                                  if analysis['overall_trend']['trend'] == 'downtrend')
                    st.metric("下降トレンド", downtrend)
                
                with col3:
                    sideways = sum(1 for analysis in analyses.values() 
                                 if analysis['overall_trend']['trend'] == 'sideways')
                    st.metric("横ばい", sideways)
                
                with col4:
                    avg_confidence = sum(analysis['overall_trend']['confidence'] for analysis in analyses.values()) / len(analyses)
                    st.metric("平均信頼度", f"{avg_confidence:.1f}%")
                
                # 銘柄別詳細トレンド分析
                st.markdown("### 🔍 銘柄別詳細トレンド分析")
                
                for symbol, analysis in analyses.items():
                    stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                    
                    with st.expander(f"📈 {stock_name} ({symbol}) - {analysis['overall_trend']['description']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**総合トレンド**: {analysis['overall_trend']['description']}")
                            st.markdown(f"**信頼度**: {analysis['overall_trend']['confidence']:.1f}%")
                            st.markdown(f"**トレンド強度**: {analysis['overall_trend']['strength']:.1f}")
                            st.markdown(f"**推奨**: {analysis['recommendation_description']}")
                            
                            # 時間軸整合性
                            consistency = analysis['timeframe_consistency']
                            st.markdown(f"**時間軸整合性**: {consistency['description']}")
                        
                        with col2:
                            # 各時間軸のトレンド
                            st.markdown("**時間軸別トレンド**:")
                            daily = analysis['multi_timeframe']['daily_trend']
                            weekly = analysis['multi_timeframe']['weekly_trend']
                            monthly = analysis['multi_timeframe']['monthly_trend']
                            
                            st.markdown(f"- 日足: {daily['trend_description']} (強度: {daily['strength']:.1f})")
                            st.markdown(f"- 週足: {weekly['trend_description']} (強度: {weekly['strength']:.1f})")
                            st.markdown(f"- 月足: {monthly['trend_description']} (強度: {monthly['strength']:.1f})")
                            
                            # ブレイクアウトパターン
                            if analysis['breakout_patterns'] and analysis['breakout_patterns']['breakout_signals']:
                                st.markdown("**ブレイクアウトシグナル**:")
                                for signal in analysis['breakout_patterns']['breakout_signals']:
                                    st.markdown(f"- {signal['description']}")
        
        with tab10:
            st.subheader("⚠️ リスク分析")
            
            if st.button("🔍 リスク分析を実行", type="primary"):
                with st.spinner("リスク分析中..."):
                    risk_analyses = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            # リスク分析を実行
                            risk_analysis = risk_analyzer.comprehensive_risk_analysis(
                                stock['stock_data'],
                                {
                                    'pe_ratio': stock.get('pe_ratio', 0),
                                    'pb_ratio': stock.get('pb_ratio', 0),
                                    'roe': stock.get('roe', 0),
                                    'debt_to_equity': stock.get('debt_to_equity', 0),
                                    'dividend_yield': stock.get('dividend_yield', 0)
                                }
                            )
                            
                            if risk_analysis:
                                risk_analyses[symbol] = risk_analysis
                    
                    if risk_analyses:
                        st.session_state.risk_analyses = risk_analyses
                        st.success(f"✅ {len(risk_analyses)}銘柄のリスク分析が完了しました！")
                    else:
                        st.warning("⚠️ リスク分析に必要なデータが不足しています。")
            
            if 'risk_analyses' in st.session_state and st.session_state.risk_analyses:
                analyses = st.session_state.risk_analyses
                
                # 分析サマリー
                st.markdown("### 📊 リスク分析サマリー")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    low_risk = sum(1 for analysis in analyses.values() 
                                 if analysis['overall_risk_level'] in ['very_low', 'low'])
                    st.metric("低リスク銘柄", low_risk)
                
                with col2:
                    high_risk = sum(1 for analysis in analyses.values() 
                                  if analysis['overall_risk_level'] in ['high', 'very_high'])
                    st.metric("高リスク銘柄", high_risk)
                
                with col3:
                    avg_risk_score = sum(analysis['overall_risk_score'] for analysis in analyses.values()) / len(analyses)
                    st.metric("平均リスクスコア", f"{avg_risk_score:.1f}")
                
                with col4:
                    excellent = sum(1 for analysis in analyses.values() if analysis['recommendation'] == 'excellent')
                    st.metric("優良投資先", excellent)
                
                # 銘柄別詳細リスク分析
                st.markdown("### 🔍 銘柄別詳細リスク分析")
                
                for symbol, analysis in analyses.items():
                    stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                    
                    with st.expander(f"⚠️ {stock_name} ({symbol}) - リスクレベル: {analysis['overall_risk_description']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**総合リスク**: {analysis['overall_risk_description']} ({analysis['overall_risk_score']:.1f}点)")
                            st.markdown(f"**投資推奨**: {analysis['recommendation_description']}")
                            st.markdown(f"**分析日時**: {analysis['analysis_date']}")
                            
                            # VaR分析
                            if analysis['var_analysis']:
                                var = analysis['var_analysis']
                                st.markdown(f"**VaR(95%)**: {var['var_results']['var_95']['average']:.3f}")
                                st.markdown(f"**最大ドローダウン**: {var['max_drawdown']['max_drawdown']:.3f}")
                                st.markdown(f"**シャープレシオ**: {var['sharpe_ratio']:.2f}")
                        
                        with col2:
                            # ベータ分析
                            if analysis['beta_analysis']:
                                beta = analysis['beta_analysis']
                                st.markdown(f"**ベータ**: {beta['beta']:.2f}")
                                st.markdown(f"**市場感応度**: {beta['beta_interpretation']['description']}")
                                st.markdown(f"**相関係数**: {beta['correlation']:.3f}")
                            
                            # 流動性分析
                            if analysis['liquidity_analysis']:
                                liquidity = analysis['liquidity_analysis']
                                st.markdown(f"**流動性レベル**: {liquidity['liquidity_level']}")
                                st.markdown(f"**流動性スコア**: {liquidity['liquidity_score']:.1f}点")
        
        with tab11:
            st.subheader("📊 ポートフォリオ分析")
            
            if st.button("🔍 ポートフォリオ分析を実行", type="primary"):
                with st.spinner("ポートフォリオ分析中..."):
                    # スクリーニング結果からポートフォリオデータを準備
                    stock_data_dict = {}
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            stock_data_dict[symbol] = stock['stock_data']
                    
                    if len(stock_data_dict) >= 2:
                        # ポートフォリオ分析を実行
                        portfolio_analysis = portfolio_analyzer.comprehensive_portfolio_analysis(stock_data_dict)
                        
                        if portfolio_analysis:
                            st.session_state.portfolio_analysis = portfolio_analysis
                            st.success("✅ ポートフォリオ分析が完了しました！")
                        else:
                            st.warning("⚠️ ポートフォリオ分析に失敗しました。")
                    else:
                        st.warning("⚠️ ポートフォリオ分析には最低2銘柄が必要です。")
            
            if 'portfolio_analysis' in st.session_state and st.session_state.portfolio_analysis:
                analysis = st.session_state.portfolio_analysis
                
                # ポートフォリオ指標
                st.markdown("### 📊 ポートフォリオ指標")
                portfolio_metrics = analysis['portfolio_metrics']['portfolio_metrics']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("年率リターン", f"{portfolio_metrics['annual_return']:.2%}")
                
                with col2:
                    st.metric("年率ボラティリティ", f"{portfolio_metrics['annual_volatility']:.2%}")
                
                with col3:
                    st.metric("シャープレシオ", f"{portfolio_metrics['sharpe_ratio']:.2f}")
                
                with col4:
                    st.metric("最大ドローダウン", f"{portfolio_metrics['max_drawdown']:.2%}")
                
                # 相関分析
                if analysis['correlation_analysis']:
                    st.markdown("### 📈 相関分析")
                    correlation = analysis['correlation_analysis']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**平均相関**: {correlation['average_correlation']:.3f}")
                        st.markdown(f"**相関レベル**: {correlation['correlation_interpretation']['description']}")
                        st.markdown(f"**分散投資効果**: {correlation['correlation_interpretation']['recommendation']}")
                    
                    with col2:
                        if correlation['diversification_benefit']:
                            benefit = correlation['diversification_benefit']
                            st.markdown(f"**分散投資効果**: {benefit['diversification_benefit_percentage']:.1f}%")
                            st.markdown(f"**リスク削減**: {benefit['risk_reduction']:.3f}")
                
                # 最適化結果
                if analysis['optimization_result']:
                    st.markdown("### 🎯 ポートフォリオ最適化")
                    optimization = analysis['optimization_result']
                    
                    st.markdown(f"**最適化タイプ**: {optimization['optimization_type']}")
                    
                    # 最適化された重み
                    st.markdown("**最適化された重み**:")
                    optimal_weights = optimization['optimal_weights']
                    for symbol, weight in optimal_weights.items():
                        stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                        st.markdown(f"- {stock_name} ({symbol}): {weight:.1%}")
                
                # 効率的フロンティア
                if analysis['efficient_frontier']:
                    st.markdown("### 📊 効率的フロンティア")
                    frontier = analysis['efficient_frontier']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**最大シャープレシオポートフォリオ**:")
                        max_sharpe = frontier['max_sharpe_portfolio']
                        st.markdown(f"- リターン: {max_sharpe['return']:.2%}")
                        st.markdown(f"- ボラティリティ: {max_sharpe['volatility']:.2%}")
                        st.markdown(f"- シャープレシオ: {max_sharpe['sharpe_ratio']:.2f}")
                    
                    with col2:
                        st.markdown("**最小分散ポートフォリオ**:")
                        min_vol = frontier['min_volatility_portfolio']
                        st.markdown(f"- リターン: {min_vol['return']:.2%}")
                        st.markdown(f"- ボラティリティ: {min_vol['volatility']:.2%}")
                        st.markdown(f"- シャープレシオ: {min_vol['sharpe_ratio']:.2f}")
        
        with tab12:
            st.subheader("🤖 AI機械学習分析")
            
            if st.button("🔍 AI分析を実行", type="primary"):
                with st.spinner("AI機械学習分析中..."):
                    ml_analyses = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        if 'stock_data' in stock and stock['stock_data'] is not None:
                            # AI分析を実行
                            ml_analysis = ml_analyzer.comprehensive_ml_analysis(
                                stock['stock_data'],
                                {
                                    'pe_ratio': stock.get('pe_ratio', 0),
                                    'pb_ratio': stock.get('pb_ratio', 0),
                                    'roe': stock.get('roe', 0),
                                    'debt_to_equity': stock.get('debt_to_equity', 0),
                                    'dividend_yield': stock.get('dividend_yield', 0)
                                }
                            )
                            
                            if ml_analysis:
                                ml_analyses[symbol] = ml_analysis
                    
                    if ml_analyses:
                        st.session_state.ml_analyses = ml_analyses
                        st.success(f"✅ {len(ml_analyses)}銘柄のAI分析が完了しました！")
                    else:
                        st.warning("⚠️ AI分析に必要なデータが不足しています。")
            
            if 'ml_analyses' in st.session_state and st.session_state.ml_analyses:
                analyses = st.session_state.ml_analyses
                
                # 分析サマリー
                st.markdown("### 📊 AI分析サマリー")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_ml_score = sum(analysis['ml_score'] for analysis in analyses.values()) / len(analyses)
                    st.metric("平均AIスコア", f"{avg_ml_score:.1f}")
                
                with col2:
                    high_ml_score = sum(1 for analysis in analyses.values() if analysis['ml_score'] >= 70)
                    st.metric("高AIスコア銘柄", high_ml_score)
                
                with col3:
                    pattern_detected = sum(1 for analysis in analyses.values() 
                                         if analysis['pattern_analysis'] and analysis['pattern_analysis']['pattern_count'] > 0)
                    st.metric("パターン検出銘柄", pattern_detected)
                
                with col4:
                    predictions_available = sum(1 for analysis in analyses.values() 
                                              if analysis['future_predictions'])
                    st.metric("予測可能銘柄", predictions_available)
                
                # 銘柄別詳細AI分析
                st.markdown("### 🔍 銘柄別詳細AI分析")
                
                for symbol, analysis in analyses.items():
                    stock_name = next((stock['name'] for _, stock in df.iterrows() if stock['symbol'] == symbol), symbol)
                    
                    with st.expander(f"🤖 {stock_name} ({symbol}) - AIスコア: {analysis['ml_score']:.1f}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**AI分析スコア**: {analysis['ml_score']:.1f}/100")
                            st.markdown(f"**分析日時**: {analysis['analysis_date']}")
                            
                            # 価格予測モデル
                            if analysis['price_prediction_model']:
                                price_model = analysis['price_prediction_model']
                                st.markdown(f"**価格予測モデル**: {price_model['best_model_name']}")
                                st.markdown(f"**予測精度(RMSE)**: {price_model['best_model']['rmse']:.4f}")
                            
                            # 方向予測モデル
                            if analysis['direction_prediction_model']:
                                direction_model = analysis['direction_prediction_model']
                                st.markdown(f"**方向予測モデル**: {direction_model['best_model_name']}")
                                st.markdown(f"**予測精度**: {direction_model['best_model']['accuracy']:.3f}")
                        
                        with col2:
                            # パターン認識
                            if analysis['pattern_analysis']:
                                patterns = analysis['pattern_analysis']['patterns']
                                st.markdown("**検出されたパターン**:")
                                for pattern_name, detected in patterns.items():
                                    if detected:
                                        st.markdown(f"- {pattern_name}: 検出")
                            
                            # 将来予測
                            if analysis['future_predictions']:
                                predictions = analysis['future_predictions']
                                st.markdown("**将来予測**:")
                                if 'price' in predictions:
                                    price_pred = predictions['price']
                                    st.markdown(f"- 価格予測: {price_pred['prediction']:.4f}")
                                    st.markdown(f"- 信頼度: {price_pred['confidence']:.3f}")
        
        with tab13:
            st.subheader("👤 パーソナライズ分析")
            
            # ユーザー行動データの収集（簡易版）
            st.markdown("### 📊 あなたの投資傾向分析")
            
            # 投資戦略の選択履歴
            if 'selected_strategies' not in st.session_state:
                st.session_state.selected_strategies = []
            
            # 選択された銘柄の履歴
            if 'selected_stocks_history' not in st.session_state:
                st.session_state.selected_stocks_history = []
            
            # 現在の選択を履歴に追加
            current_strategy = st.session_state.get('selected_strategy', 'balanced')
            if current_strategy not in st.session_state.selected_strategies:
                st.session_state.selected_strategies.append(current_strategy)
            
            # パーソナライズ分析を実行
            if st.button("🔍 パーソナライズ分析を実行", type="primary"):
                with st.spinner("パーソナライズ分析中..."):
                    # ユーザー行動データを準備
                    user_interactions = {
                        'strategy_selections': {strategy: st.session_state.selected_strategies.count(strategy) 
                                              for strategy in set(st.session_state.selected_strategies)},
                        'selected_stocks': [dict(stock) for _, stock in df.iterrows() if stock.get('selected', False)],
                        'risk_indicators': {
                            'high_risk_selections': len([s for s in st.session_state.selected_strategies if s in ['aggressive', 'growth']]),
                            'total_selections': len(st.session_state.selected_strategies),
                            'volatility_tolerance': 0.6,  # デフォルト値
                            'loss_tolerance': 0.5  # デフォルト値
                        }
                    }
                    
                    # ユーザー行動分析
                    user_behavior = personalization_analyzer.analyze_user_behavior(user_interactions)
                    
                    # パーソナライズ推奨生成
                    available_stocks = [dict(stock) for _, stock in df.iterrows()]
                    personalized_recommendations = personalization_analyzer.generate_personalized_recommendations(
                        user_behavior, available_stocks
                    )
                    
                    st.session_state.user_behavior = user_behavior
                    st.session_state.personalized_recommendations = personalized_recommendations
                    st.success("✅ パーソナライズ分析が完了しました！")
            
            if 'user_behavior' in st.session_state and 'personalized_recommendations' in st.session_state:
                user_behavior = st.session_state.user_behavior
                recommendations = st.session_state.personalized_recommendations
                
                # ユーザープロファイル
                st.markdown("### 👤 あなたの投資プロファイル")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 投資戦略選好
                    strategy_prefs = user_behavior['strategy_preferences']
                    st.markdown(f"**好みの投資戦略**: {strategy_prefs['preferred_strategy']}")
                    st.markdown(f"**信頼度**: {strategy_prefs['confidence']:.1%}")
                    
                    # リスク許容度
                    risk_tolerance = user_behavior['risk_tolerance']
                    st.markdown(f"**リスク許容度**: {risk_tolerance['risk_level']}")
                    st.markdown(f"**リスクスコア**: {risk_tolerance['risk_score']:.1f}")
                
                with col2:
                    # 投資期間
                    investment_horizon = user_behavior['investment_horizon']
                    st.markdown(f"**投資期間**: {investment_horizon['preferred_horizon']}")
                    st.markdown(f"**平均保有期間**: {investment_horizon.get('avg_holding_period', 0):.0f}日")
                    
                    # セクター選好
                    sector_prefs = user_behavior['sector_preferences']
                    if sector_prefs['preferred_sectors']:
                        st.markdown(f"**好みのセクター**: {', '.join(sector_prefs['preferred_sectors'])}")
                    else:
                        st.markdown("**好みのセクター**: 未特定")
                
                # パーソナライズ推奨
                st.markdown("### 🎯 あなたに最適な銘柄")
                
                if recommendations['recommendations']:
                    st.markdown(f"**推奨理由**: {recommendations['reasoning']}")
                    st.markdown(f"**パーソナライズ信頼度**: {recommendations['personalization_confidence']:.1%}")
                    
                    # 推奨銘柄一覧
                    for i, rec in enumerate(recommendations['recommendations'][:5], 1):
                        stock = rec['stock']
                        score = rec['personalization_score']
                        reasons = rec['match_reasons']
                        
                        with st.expander(f"#{i} {stock.get('name', 'Unknown')} - 適合度: {score:.1%}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**銘柄コード**: {stock.get('symbol', 'N/A')}")
                                st.markdown(f"**現在価格**: ¥{stock.get('current_price', 0):,.0f}")
                                st.markdown(f"**PER**: {stock.get('pe_ratio', 0):.2f}")
                                st.markdown(f"**PBR**: {stock.get('pb_ratio', 0):.2f}")
                            
                            with col2:
                                st.markdown(f"**ROE**: {stock.get('roe', 0):.2f}%")
                                st.markdown(f"**配当利回り**: {stock.get('dividend_yield', 0):.2f}%")
                                st.markdown(f"**セクター**: {stock.get('sector', 'N/A')}")
                                
                                if reasons:
                                    st.markdown("**適合理由**:")
                                    for reason in reasons:
                                        st.markdown(f"- {reason}")
                else:
                    st.warning("パーソナライズ推奨を生成できませんでした。")
        
        with tab18:
            st.header("📋 ファンダメンタルズ銘柄選定")
            st.write("包括的な財務指標分析に基づいて、投資価値の高い銘柄を選定します。")
            
            # 分析設定
            col1, col2 = st.columns(2)
            
            with col1:
                min_score = st.slider(
                    "最小スコア", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=60.0, 
                    step=5.0,
                    help="このスコア以上の銘柄のみを表示します"
                )
            
            with col2:
                analysis_type = st.selectbox(
                    "分析タイプ",
                    ["総合分析", "収益性重視", "成長性重視", "財務健全性重視", "バリュエーション重視"],
                    help="分析の重点を選択してください"
                )
            
            # 分析実行ボタン
            if st.button("🔍 ファンダメンタルズ分析を実行", type="primary"):
                if 'screened_stocks' in st.session_state and not st.session_state.screened_stocks.empty:
                    with st.spinner("ファンダメンタルズ分析を実行中..."):
                        try:
                            # スクリーニング結果から株価データを取得
                            stock_data_dict = {}
                            for idx, row in st.session_state.screened_stocks.iterrows():
                                symbol = row['symbol']
                                if 'stock_data' in row and row['stock_data'] is not None:
                                    stock_data_dict[symbol] = row['stock_data']
                            
                            if stock_data_dict:
                                # ファンダメンタルズ分析を実行
                                fundamental_results = fundamental_screener.screen_stocks_by_fundamentals(
                                    stock_data_dict, 
                                    min_score=min_score
                                )
                                
                                if not fundamental_results.empty:
                                    st.session_state.fundamental_results = fundamental_results
                                    
                                    # 結果サマリー
                                    st.success(f"分析完了！{len(fundamental_results)}銘柄が条件を満たしました。")
                                    
                                    # スコア分布
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("平均スコア", f"{fundamental_results['total_score'].mean():.1f}点")
                                    with col2:
                                        st.metric("最高スコア", f"{fundamental_results['total_score'].max():.1f}点")
                                    with col3:
                                        st.metric("A級銘柄数", len(fundamental_results[fundamental_results['grade'].str.startswith('A')]))
                                    
                                    # グレード分布
                                    grade_counts = fundamental_results['grade'].value_counts().sort_index()
                                    fig_grade = px.pie(
                                        values=grade_counts.values, 
                                        names=grade_counts.index,
                                        title="グレード分布"
                                    )
                                    st.plotly_chart(fig_grade, width="stretch")
                                    
                                    # スコア分布
                                    fig_score = px.histogram(
                                        fundamental_results, 
                                        x='total_score',
                                        title="スコア分布",
                                        nbins=20
                                    )
                                    st.plotly_chart(fig_score, width="stretch")
                                    
                                    # 詳細結果テーブル
                                    st.subheader("📊 詳細分析結果")
                                    
                                    # 表示する列を選択
                                    display_columns = [
                                        'company_name', 'symbol', 'sector', 'total_score', 'grade', 
                                        'recommendation', 'confidence', 'current_price', 'target_price',
                                        'pe_ratio', 'pb_ratio', 'roe', 'roa', 'debt_to_equity',
                                        'profit_margin', 'revenue_growth', 'dividend_yield', 'risk_level'
                                    ]
                                    
                                    display_df = fundamental_results[display_columns].copy()
                                    display_df.columns = [
                                        '会社名', 'シンボル', 'セクター', '総合スコア', 'グレード',
                                        '推奨', '信頼度', '現在価格', '目標価格',
                                        'PER', 'PBR', 'ROE', 'ROA', '負債比率',
                                        '利益率', '売上成長率', '配当利回り', 'リスクレベル'
                                    ]
                                    
                                    st.dataframe(
                                        display_df,
                                        width="stretch",
                                        height=400
                                    )
                                    
                                    # エクスポート機能
                                    export_manager.create_export_ui(display_df, 'dataframe', 'fundamental_analysis')
                                    
                                    # トップ5銘柄の詳細分析
                                    st.subheader("🏆 トップ5銘柄の詳細分析")
                                    
                                    top_5 = fundamental_results.head(5)
                                    
                                    for idx, (_, stock) in enumerate(top_5.iterrows(), 1):
                                        with st.expander(f"{idx}. {stock['company_name']} ({stock['symbol']}) - {stock['grade']}級"):
                                            col1, col2 = st.columns(2)
                                            
                                            with col1:
                                                st.write("**基本情報**")
                                                st.write(f"- セクター: {stock['sector']}")
                                                st.write(f"- 業界: {stock['industry']}")
                                                st.write(f"- 現在価格: ¥{stock['current_price']:,.0f}")
                                                st.write(f"- 目標価格: ¥{stock['target_price']:,.0f}")
                                                st.write(f"- 時価総額: ¥{stock['market_cap']:,.0f}")
                                                
                                                st.write("**投資判断**")
                                                st.write(f"- 総合スコア: {stock['total_score']:.1f}点")
                                                st.write(f"- グレード: {stock['grade']}")
                                                st.write(f"- 推奨: {stock['recommendation']}")
                                                st.write(f"- 信頼度: {stock['confidence']}")
                                                st.write(f"- リスクレベル: {stock['risk_level']}")
                                            
                                            with col2:
                                                st.write("**財務指標**")
                                                st.write(f"- PER: {stock['pe_ratio']:.2f}")
                                                st.write(f"- PBR: {stock['pb_ratio']:.2f}")
                                                st.write(f"- ROE: {stock['roe']:.2f}%")
                                                st.write(f"- ROA: {stock['roa']:.2f}%")
                                                st.write(f"- 負債比率: {stock['debt_to_equity']:.2f}")
                                                st.write(f"- 流動比率: {stock['current_ratio']:.2f}")
                                                st.write(f"- 利益率: {stock['profit_margin']:.2f}%")
                                                st.write(f"- 売上成長率: {stock['revenue_growth']:.2f}%")
                                                st.write(f"- 配当利回り: {stock['dividend_yield']:.2f}%")
                                                st.write(f"- ベータ: {stock['beta']:.2f}")
                                    
                                    # レポート生成
                                    st.subheader("📋 分析レポート")
                                    
                                    if st.button("📄 レポートを生成"):
                                        # 詳細分析結果を準備
                                        detailed_results = []
                                        for idx, (_, stock) in enumerate(fundamental_results.iterrows()):
                                            # 各銘柄の詳細分析を実行
                                            stock_data = None
                                            for _, row in st.session_state.screened_stocks.iterrows():
                                                if row['symbol'] == stock['symbol'] and 'stock_data' in row:
                                                    stock_data = row['stock_data']
                                                    break
                                            
                                            if stock_data:
                                                analysis = fundamental_screener.analyze_fundamentals(stock_data)
                                                if analysis:
                                                    detailed_results.append(analysis)
                                        
                                        if detailed_results:
                                            report = fundamental_screener.generate_fundamental_report(detailed_results)
                                            st.text_area("ファンダメンタルズ分析レポート", report, height=400)
                                            
                                            # レポートダウンロード
                                            st.download_button(
                                                label="📥 レポートをダウンロード",
                                                data=report,
                                                file_name=f"fundamental_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                                mime="text/plain"
                                            )
                                else:
                                    st.warning(f"スコア{min_score}以上の銘柄が見つかりませんでした。条件を緩和してください。")
                            else:
                                st.error("分析に必要な株価データがありません。先にスクリーニングを実行してください。")
                                
                        except Exception as e:
                            st.error(f"ファンダメンタルズ分析中にエラーが発生しました: {str(e)}")
                else:
                    st.warning("先にスクリーニングを実行してから、ファンダメンタルズ分析を行ってください。")
            
            # 過去の分析結果を表示
            if 'fundamental_results' in st.session_state and not st.session_state.fundamental_results.empty:
                st.subheader("📊 過去の分析結果")
                
                # 結果の要約
                results = st.session_state.fundamental_results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("分析銘柄数", len(results))
                with col2:
                    st.metric("平均スコア", f"{results['total_score'].mean():.1f}点")
                with col3:
                    st.metric("A級銘柄", len(results[results['grade'].str.startswith('A')]))
                with col4:
                    st.metric("買い推奨", len(results[results['recommendation'].str.contains('買い')]))
                
                # 簡易結果表示
                st.dataframe(
                    results[['company_name', 'symbol', 'total_score', 'grade', 'recommendation']].head(10),
                    width="stretch"
                )
        
        with tab19:
            st.header("🔔 アラート管理")
            st.write("価格、シグナル、リスクのアラートを設定・管理します。")
            
            # アラートサマリー
            alert_summary = alert_system.get_alert_summary()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("総アラート数", alert_summary['total_alerts'])
            with col2:
                st.metric("アクティブ", alert_summary['active_alerts'])
            with col3:
                st.metric("トリガー済み", alert_summary['triggered_alerts'])
            with col4:
                st.metric("価格アラート", alert_summary['type_counts'].get('price', 0))
            
            # アラート設定
            st.subheader("📝 新しいアラートを設定")
            
            alert_type = st.selectbox(
                "アラートタイプ",
                ["価格アラート", "シグナルアラート", "リスクアラート"],
                help="設定したいアラートの種類を選択してください"
            )
            
            if alert_type == "価格アラート":
                col1, col2 = st.columns(2)
                
                with col1:
                    symbol = st.text_input("銘柄コード", placeholder="例: 7203.T", key="symbol_input_1")
                    target_price = st.number_input("目標価格", min_value=0.0, value=1000.0, step=10.0, key="price_1")
                
                with col2:
                    condition = st.selectbox(
                        "条件",
                        ["above", "below", "cross_up", "cross_down"],
                        format_func=lambda x: {
                            "above": "価格が目標価格以上",
                            "below": "価格が目標価格以下", 
                            "cross_up": "価格が目標価格を上抜け",
                            "cross_down": "価格が目標価格を下抜け"
                        }[x]
                    )
                    description = st.text_input("説明（任意）", placeholder="アラートの説明を入力", key="description_1")
                
                if st.button("🔔 価格アラートを設定", type="primary"):
                    if symbol:
                        alert_id = alert_system.add_price_alert(
                            symbol=symbol,
                            target_price=target_price,
                            condition=condition,
                            description=description
                        )
                        st.success(f"✅ 価格アラートを設定しました！ID: {alert_id}")
                    else:
                        st.error("銘柄コードを入力してください。")
            
            elif alert_type == "シグナルアラート":
                col1, col2 = st.columns(2)
                
                with col1:
                    symbol = st.text_input("銘柄コード", placeholder="例: 7203.T", key="symbol_input_2")
                    signal_type = st.selectbox(
                        "シグナルタイプ",
                        ["buy", "sell", "hold"],
                        format_func=lambda x: {
                            "buy": "買いシグナル",
                            "sell": "売りシグナル",
                            "hold": "ホールドシグナル"
                        }[x]
                    )
                
                with col2:
                    description = st.text_input("説明（任意）", placeholder="アラートの説明を入力", key="description_2")
                
                if st.button("🔔 シグナルアラートを設定", type="primary"):
                    if symbol:
                        alert_id = alert_system.add_signal_alert(
                            symbol=symbol,
                            signal_type=signal_type,
                            description=description
                        )
                        st.success(f"✅ シグナルアラートを設定しました！ID: {alert_id}")
                    else:
                        st.error("銘柄コードを入力してください。")
            
            elif alert_type == "リスクアラート":
                col1, col2 = st.columns(2)
                
                with col1:
                    symbol = st.text_input("銘柄コード", placeholder="例: 7203.T", key="symbol_input_3")
                    risk_type = st.selectbox(
                        "リスクタイプ",
                        ["volatility", "drawdown", "beta"],
                        format_func=lambda x: {
                            "volatility": "ボラティリティ",
                            "drawdown": "ドローダウン",
                            "beta": "ベータ値"
                        }[x]
                    )
                
                with col2:
                    threshold = st.number_input("閾値", min_value=0.0, value=0.2, step=0.01)
                    description = st.text_input("説明（任意）", placeholder="アラートの説明を入力", key="description_3")
                
                if st.button("🔔 リスクアラートを設定", type="primary"):
                    if symbol:
                        alert_id = alert_system.add_risk_alert(
                            symbol=symbol,
                            risk_type=risk_type,
                            threshold=threshold,
                            description=description
                        )
                        st.success(f"✅ リスクアラートを設定しました！ID: {alert_id}")
                    else:
                        st.error("銘柄コードを入力してください。")
            
            # アラート一覧
            st.subheader("📋 アラート一覧")
            
            # フィルター
            filter_type = st.selectbox(
                "フィルター",
                ["すべて", "アクティブ", "トリガー済み", "価格アラート", "シグナルアラート", "リスクアラート"]
            )
            
            # アラートを取得
            if filter_type == "すべて":
                display_alerts = alert_system.alerts
            elif filter_type == "アクティブ":
                display_alerts = alert_system.get_active_alerts()
            elif filter_type == "トリガー済み":
                display_alerts = alert_system.get_triggered_alerts()
            elif filter_type == "価格アラート":
                display_alerts = [a for a in alert_system.alerts if a['type'] == 'price']
            elif filter_type == "シグナルアラート":
                display_alerts = [a for a in alert_system.alerts if a['type'] == 'signal']
            elif filter_type == "リスクアラート":
                display_alerts = [a for a in alert_system.alerts if a['type'] == 'risk']
            
            if display_alerts:
                # アラートを表示
                for alert in display_alerts:
                    with st.expander(f"🔔 {alert['symbol']} - {alert['type']} ({alert['status']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ID**: {alert['id']}")
                            st.write(f"**タイプ**: {alert['type']}")
                            st.write(f"**銘柄**: {alert['symbol']}")
                            st.write(f"**ステータス**: {alert['status']}")
                            st.write(f"**作成日時**: {alert['created_at']}")
                        
                        with col2:
                            if alert['type'] == 'price':
                                st.write(f"**目標価格**: ¥{alert['target_price']:,.0f}")
                                st.write(f"**条件**: {alert['condition']}")
                                if alert['triggered_at']:
                                    st.write(f"**トリガー日時**: {alert['triggered_at']}")
                                    st.write(f"**トリガー価格**: ¥{alert['triggered_price']:,.0f}")
                            
                            elif alert['type'] == 'signal':
                                st.write(f"**シグナルタイプ**: {alert['signal_type']}")
                                if alert['triggered_at']:
                                    st.write(f"**トリガー日時**: {alert['triggered_at']}")
                                    st.write(f"**トリガーシグナル**: {alert['triggered_signal']}")
                            
                            elif alert['type'] == 'risk':
                                st.write(f"**リスクタイプ**: {alert['risk_type']}")
                                st.write(f"**閾値**: {alert['threshold']}")
                                if alert['triggered_at']:
                                    st.write(f"**トリガー日時**: {alert['triggered_at']}")
                                    st.write(f"**トリガー値**: {alert['triggered_value']}")
                            
                            if alert['description']:
                                st.write(f"**説明**: {alert['description']}")
                        
                        # アラート操作ボタン
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"🗑️ 削除", key=f"delete_{alert['id']}"):
                                if alert_system.delete_alert(alert['id']):
                                    st.success("アラートを削除しました。")
                                    st.rerun()
                        
                        with col2:
                            if alert['status'] == 'active':
                                if st.button(f"⏸️ 無効化", key=f"deactivate_{alert['id']}"):
                                    if alert_system.update_alert(alert['id'], {'status': 'inactive'}):
                                        st.success("アラートを無効化しました。")
                                        st.rerun()
                            elif alert['status'] == 'inactive':
                                if st.button(f"▶️ 有効化", key=f"activate_{alert['id']}"):
                                    if alert_system.update_alert(alert['id'], {'status': 'active'}):
                                        st.success("アラートを有効化しました。")
                                        st.rerun()
            else:
                st.info("該当するアラートがありません。")
            
            # アラートテスト機能
            st.subheader("🧪 アラートテスト")
            
            if st.button("🔍 アラートをテスト", type="secondary"):
                if 'screened_stocks' in st.session_state and not st.session_state.screened_stocks.empty:
                    with st.spinner("アラートをテスト中..."):
                        triggered_count = 0
                        
                        for idx, row in st.session_state.screened_stocks.iterrows():
                            symbol = row['symbol']
                            if 'stock_data' in row and row['stock_data'] is not None:
                                stock_data = row['stock_data']
                                
                                # アラートを処理
                                triggered = alert_system.process_alerts(symbol, stock_data)
                                triggered_count += len(triggered)
                        
                        if triggered_count > 0:
                            st.success(f"✅ {triggered_count}個のアラートがトリガーされました！")
                        else:
                            st.info("トリガーされたアラートはありません。")
                else:
                    st.warning("先にスクリーニングを実行してから、アラートテストを行ってください。")
            
            # アラートクリーンアップ
            st.subheader("🧹 アラートクリーンアップ")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cleanup_days = st.number_input("古いアラートを削除（日数）", min_value=1, max_value=365, value=30)
            
            with col2:
                if st.button("🗑️ 古いアラートを削除", type="secondary"):
                    old_count = len(alert_system.alerts)
                    alert_system.cleanup_old_alerts(cleanup_days)
                    new_count = len(alert_system.alerts)
                    deleted_count = old_count - new_count
                    
                    if deleted_count > 0:
                        st.success(f"✅ {deleted_count}個の古いアラートを削除しました。")
                    else:
                        st.info("削除対象のアラートはありませんでした。")
        
        with tab20:
            st.header("📊 バックテスト")
            st.write("過去データを使用して投資戦略の検証を行います。")
            
            # バックテスト設定
            st.subheader("⚙️ バックテスト設定")
            
            col1, col2 = st.columns(2)
            
            with col1:
                strategy = st.selectbox(
                    "戦略",
                    ["moving_average_cross", "rsi_strategy", "bollinger_bands", "momentum", "mean_reversion"],
                    format_func=lambda x: {
                        "moving_average_cross": "移動平均クロス",
                        "rsi_strategy": "RSI戦略",
                        "bollinger_bands": "ボリンジャーバンド",
                        "momentum": "モメンタム",
                        "mean_reversion": "平均回帰"
                    }[x]
                )
                
                # 戦略パラメータ
                if strategy == "moving_average_cross":
                    short_window = st.number_input("短期移動平均期間", min_value=5, max_value=50, value=20)
                    long_window = st.number_input("長期移動平均期間", min_value=20, max_value=200, value=50)
                    strategy_params = {"short_window": short_window, "long_window": long_window}
                
                elif strategy == "rsi_strategy":
                    rsi_period = st.number_input("RSI期間", min_value=5, max_value=30, value=14)
                    oversold = st.number_input("オーバーソールド", min_value=10, max_value=40, value=30)
                    overbought = st.number_input("オーバーボート", min_value=60, max_value=90, value=70)
                    strategy_params = {"rsi_period": rsi_period, "oversold": oversold, "overbought": overbought}
                
                elif strategy == "bollinger_bands":
                    period = st.number_input("期間", min_value=10, max_value=50, value=20)
                    std_dev = st.number_input("標準偏差", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
                    strategy_params = {"period": period, "std_dev": std_dev}
                
                elif strategy == "momentum":
                    period = st.number_input("モメンタム期間", min_value=5, max_value=50, value=20)
                    threshold = st.number_input("閾値", min_value=0.01, max_value=0.1, value=0.02, step=0.01)
                    strategy_params = {"period": period, "threshold": threshold}
                
                elif strategy == "mean_reversion":
                    period = st.number_input("平均回帰期間", min_value=10, max_value=50, value=20)
                    threshold = st.number_input("Zスコア閾値", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
                    strategy_params = {"period": period, "threshold": threshold}
            
            with col2:
                start_date = st.date_input("開始日", value=datetime.now() - timedelta(days=365), key="start_date_1")
                end_date = st.date_input("終了日", value=datetime.now(), key="end_date_1")
                
                initial_capital = st.number_input("初期資本（円）", min_value=100000, max_value=10000000, value=1000000, step=100000)
                commission_rate = st.number_input("手数料率（%）", min_value=0.0, max_value=1.0, value=0.15, step=0.01, key="commission_1") / 100
                slippage_rate = st.number_input("スリッページ率（%）", min_value=0.0, max_value=1.0, value=0.05, step=0.01) / 100
            
            # バックテスト実行
            if st.button("🚀 バックテストを実行", type="primary"):
                if 'screened_stocks' in st.session_state and not st.session_state.screened_stocks.empty:
                    with st.spinner("バックテストを実行中..."):
                        try:
                            # バックテストエンジンの設定を更新
                            backtest_engine.initial_capital = initial_capital
                            backtest_engine.commission_rate = commission_rate
                            backtest_engine.slippage_rate = slippage_rate
                            
                            # 各銘柄でバックテストを実行
                            backtest_results = []
                            
                            for idx, row in st.session_state.screened_stocks.iterrows():
                                symbol = row['symbol']
                                if 'stock_data' in row and row['stock_data'] is not None:
                                    stock_data = row['stock_data']
                                    
                                    result = backtest_engine.run_backtest(
                                        strategy=strategy,
                                        stock_data=stock_data,
                                        start_date=start_date.strftime('%Y-%m-%d'),
                                        end_date=end_date.strftime('%Y-%m-%d'),
                                        **strategy_params
                                    )
                                    
                                    if result:
                                        backtest_results.append(result)
                            
                            if backtest_results:
                                st.session_state.backtest_results = backtest_results
                                st.success(f"✅ {len(backtest_results)}銘柄のバックテストが完了しました！")
                                
                                # 結果サマリー
                                st.subheader("📊 バックテスト結果サマリー")
                                
                                # パフォーマンス指標の集計
                                total_returns = [r['performance']['total_return'] for r in backtest_results]
                                annualized_returns = [r['performance']['annualized_return'] for r in backtest_results]
                                sharpe_ratios = [r['performance']['sharpe_ratio'] for r in backtest_results]
                                max_drawdowns = [r['performance']['max_drawdown'] for r in backtest_results]
                                win_rates = [r['performance']['win_rate'] for r in backtest_results]
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("平均総リターン", f"{np.mean(total_returns):.2f}%")
                                with col2:
                                    st.metric("平均年率リターン", f"{np.mean(annualized_returns):.2f}%")
                                with col3:
                                    st.metric("平均シャープレシオ", f"{np.mean(sharpe_ratios):.2f}")
                                with col4:
                                    st.metric("平均最大ドローダウン", f"{np.mean(max_drawdowns):.2f}%")
                                
                                # 結果テーブル
                                st.subheader("📋 詳細結果")
                                
                                results_data = []
                                for result in backtest_results:
                                    perf = result['performance']
                                    results_data.append({
                                        '銘柄': result['symbol'],
                                        '総リターン(%)': f"{perf['total_return']:.2f}",
                                        '年率リターン(%)': f"{perf['annualized_return']:.2f}",
                                        'シャープレシオ': f"{perf['sharpe_ratio']:.2f}",
                                        '最大ドローダウン(%)': f"{perf['max_drawdown']:.2f}",
                                        '勝率(%)': f"{perf['win_rate']:.2f}",
                                        '取引数': perf['total_trades'],
                                        '最終資産価値(円)': f"¥{perf['final_value']:,.0f}"
                                    })
                                
                                results_df = pd.DataFrame(results_data)
                                st.dataframe(results_df, width="stretch")
                                
                                # エクスポート機能
                                export_manager.create_export_ui(results_df, 'dataframe', 'backtest_results')
                                
                                # パフォーマンス分布
                                st.subheader("📈 パフォーマンス分布")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    fig_returns = px.histogram(
                                        x=total_returns,
                                        title="総リターン分布",
                                        nbins=20
                                    )
                                    st.plotly_chart(fig_returns, width="stretch")
                                
                                with col2:
                                    fig_sharpe = px.histogram(
                                        x=sharpe_ratios,
                                        title="シャープレシオ分布",
                                        nbins=20
                                    )
                                    st.plotly_chart(fig_sharpe, width="stretch")
                                
                                # トップパフォーマー
                                st.subheader("🏆 トップパフォーマー")
                                
                                # シャープレシオでソート
                                top_performers = sorted(backtest_results, key=lambda x: x['performance']['sharpe_ratio'], reverse=True)[:5]
                                
                                for i, result in enumerate(top_performers, 1):
                                    with st.expander(f"{i}. {result['symbol']} - シャープレシオ: {result['performance']['sharpe_ratio']:.2f}"):
                                        perf = result['performance']
                                        
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            st.write("**パフォーマンス指標**")
                                            st.write(f"- 総リターン: {perf['total_return']:.2f}%")
                                            st.write(f"- 年率リターン: {perf['annualized_return']:.2f}%")
                                            st.write(f"- シャープレシオ: {perf['sharpe_ratio']:.2f}")
                                            st.write(f"- 最大ドローダウン: {perf['max_drawdown']:.2f}%")
                                        
                                        with col2:
                                            st.write("**取引統計**")
                                            st.write(f"- 勝率: {perf['win_rate']:.2f}%")
                                            st.write(f"- 取引数: {perf['total_trades']}回")
                                            st.write(f"- プロフィットファクター: {perf['profit_factor']:.2f}")
                                            st.write(f"- 最終資産価値: ¥{perf['final_value']:,.0f}")
                                        
                                        # 取引履歴
                                        if result['trades']:
                                            st.write("**取引履歴**")
                                            trades_df = pd.DataFrame(result['trades'])
                                            st.dataframe(trades_df[['date', 'action', 'price', 'shares']], width="stretch")
                                
                                # レポート生成
                                st.subheader("📄 バックテストレポート")
                                
                                if st.button("📋 レポートを生成"):
                                    report = f"""
# バックテストレポート

## 基本情報
- 戦略: {strategy}
- 期間: {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}
- 初期資本: ¥{initial_capital:,.0f}
- 手数料率: {commission_rate*100:.2f}%
- スリッページ率: {slippage_rate*100:.2f}%

## 全体サマリー
- テスト銘柄数: {len(backtest_results)}銘柄
- 平均総リターン: {np.mean(total_returns):.2f}%
- 平均年率リターン: {np.mean(annualized_returns):.2f}%
- 平均シャープレシオ: {np.mean(sharpe_ratios):.2f}
- 平均最大ドローダウン: {np.mean(max_drawdowns):.2f}%
- 平均勝率: {np.mean(win_rates):.2f}%

## 戦略パラメータ
"""
                                    for param, value in strategy_params.items():
                                        report += f"- {param}: {value}\n"
                                    
                                    report += "\n## 銘柄別結果\n"
                                    
                                    for result in backtest_results:
                                        perf = result['performance']
                                        report += f"""
### {result['symbol']}
- 総リターン: {perf['total_return']:.2f}%
- 年率リターン: {perf['annualized_return']:.2f}%
- シャープレシオ: {perf['sharpe_ratio']:.2f}
- 最大ドローダウン: {perf['max_drawdown']:.2f}%
- 勝率: {perf['win_rate']:.2f}%
- 取引数: {perf['total_trades']}回
- 最終資産価値: ¥{perf['final_value']:,.0f}
"""
                                    
                                    st.text_area("バックテストレポート", report, height=400)
                                    
                                    # レポートダウンロード
                                    st.download_button(
                                        label="📥 レポートをダウンロード",
                                        data=report,
                                        file_name=f"backtest_report_{strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                        mime="text/plain"
                                    )
                            else:
                                st.warning("バックテスト結果がありませんでした。")
                                
                        except Exception as e:
                            st.error(f"バックテスト実行中にエラーが発生しました: {str(e)}")
                else:
                    st.warning("先にスクリーニングを実行してから、バックテストを行ってください。")
            
            # 過去のバックテスト結果を表示
            if 'backtest_results' in st.session_state and st.session_state.backtest_results:
                st.subheader("📊 過去のバックテスト結果")
                
                results = st.session_state.backtest_results
                
                # 簡易サマリー
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("テスト銘柄数", len(results))
                with col2:
                    avg_return = np.mean([r['performance']['total_return'] for r in results])
                    st.metric("平均総リターン", f"{avg_return:.2f}%")
                with col3:
                    avg_sharpe = np.mean([r['performance']['sharpe_ratio'] for r in results])
                    st.metric("平均シャープレシオ", f"{avg_sharpe:.2f}")
                
                # 簡易結果表示
                simple_data = []
                for result in results:
                    perf = result['performance']
                    simple_data.append({
                        '銘柄': result['symbol'],
                        '総リターン(%)': f"{perf['total_return']:.2f}",
                        'シャープレシオ': f"{perf['sharpe_ratio']:.2f}",
                        '勝率(%)': f"{perf['win_rate']:.2f}"
                    })
                
                simple_df = pd.DataFrame(simple_data)
                st.dataframe(simple_df, width="stretch")
        
        with tab21:
            st.header("📈 実績管理")
            st.write("実際の取引結果を追跡・分析し、投資パフォーマンスを管理します。")
            
            # 実績管理メニュー
            menu_option = st.selectbox(
                "メニューを選択",
                ["取引記録", "ポートフォリオ状況", "パフォーマンス分析", "データ管理"],
                help="実績管理の機能を選択してください"
            )
            
            if menu_option == "取引記録":
                st.subheader("📝 取引記録")
                
                # 新しい取引を追加
                with st.expander("➕ 新しい取引を追加"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        symbol = st.text_input("銘柄コード", placeholder="例: 7203.T", key="symbol_input_4")
                        action = st.selectbox("アクション", ["BUY", "SELL"])
                        quantity = st.number_input("数量", min_value=0.01, value=1.0, step=0.01)
                    
                    with col2:
                        price = st.number_input("価格（円）", min_value=0.0, value=1000.0, step=10.0, key="price_2")
                        commission = st.number_input("手数料（円）", min_value=0.0, value=0.0, step=10.0, key="commission_2")
                        trade_date = st.date_input("取引日", value=datetime.now())
                    
                    notes = st.text_area("メモ（任意）", placeholder="取引に関するメモを入力")
                    
                    if st.button("💾 取引を記録", type="primary"):
                        if symbol:
                            trade_id = performance_tracker.add_trade(
                                symbol=symbol,
                                action=action,
                                quantity=quantity,
                                price=price,
                                date=datetime.combine(trade_date, datetime.min.time()),
                                commission=commission,
                                notes=notes
                            )
                            st.success(f"✅ 取引を記録しました！ID: {trade_id}")
                            st.rerun()
                        else:
                            st.error("銘柄コードを入力してください。")
                
                # 取引履歴
                st.subheader("📋 取引履歴")
                
                # フィルター
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filter_symbol = st.text_input("銘柄でフィルター", placeholder="例: 7203.T")
                
                with col2:
                    filter_start_date = st.date_input("開始日", value=datetime.now() - timedelta(days=30), key="start_date_2")
                
                with col3:
                    filter_end_date = st.date_input("終了日", value=datetime.now(), key="end_date_2")
                
                # 取引履歴を取得・表示
                trades = performance_tracker.get_trades(
                    symbol=filter_symbol if filter_symbol else None,
                    start_date=datetime.combine(filter_start_date, datetime.min.time()),
                    end_date=datetime.combine(filter_end_date, datetime.max.time())
                )
                
                if trades:
                    # 取引履歴テーブル
                    trades_data = []
                    for trade in trades:
                        trades_data.append({
                            '日付': trade['date'].strftime('%Y-%m-%d'),
                            '銘柄': trade['symbol'],
                            'アクション': trade['action'],
                            '数量': f"{trade['quantity']:.2f}",
                            '価格': f"¥{trade['price']:,.0f}",
                            '金額': f"¥{trade['quantity'] * trade['price']:,.0f}",
                            '手数料': f"¥{trade['commission']:,.0f}",
                            'メモ': trade['notes']
                        })
                    
                    trades_df = pd.DataFrame(trades_data)
                    st.dataframe(trades_df, width="stretch")
                    
                    # 取引統計
                    st.subheader("📊 取引統計")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("総取引数", len(trades))
                    with col2:
                        buy_trades = [t for t in trades if t['action'] == 'BUY']
                        st.metric("買い取引", len(buy_trades))
                    with col3:
                        sell_trades = [t for t in trades if t['action'] == 'SELL']
                        st.metric("売り取引", len(sell_trades))
                    with col4:
                        total_commission = sum([t['commission'] for t in trades])
                        st.metric("総手数料", f"¥{total_commission:,.0f}")
                else:
                    st.info("該当する取引履歴がありません。")
            
            elif menu_option == "ポートフォリオ状況":
                st.subheader("💼 ポートフォリオ状況")
                
                # ポートフォリオサマリー
                summary = performance_tracker.get_portfolio_summary()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("総市場価値", f"¥{summary['total_market_value']:,.0f}")
                with col2:
                    st.metric("総コストベース", f"¥{summary['total_cost_basis']:,.0f}")
                with col3:
                    st.metric("未実現損益", f"¥{summary['total_unrealized_pnl']:,.0f}")
                with col4:
                    st.metric("総損益率", f"{summary['total_pnl_pct']:.2f}%")
                
                # 銘柄別損益
                if summary['positions']:
                    st.subheader("📊 銘柄別損益")
                    
                    positions_data = []
                    for position in summary['positions']:
                        positions_data.append({
                            '銘柄': position['symbol'],
                            'ポジション': f"{position['position']:.2f}株",
                            '市場価値': f"¥{position['market_value']:,.0f}",
                            'コストベース': f"¥{position['cost_basis']:,.0f}",
                            '未実現損益': f"¥{position['unrealized_pnl']:,.0f}",
                            '損益率': f"{position['unrealized_pnl_pct']:.2f}%",
                            '実現損益': f"¥{position['realized_pnl']:,.0f}",
                            '現在価格': f"¥{position['current_price']:,.0f}",
                            '平均取得価格': f"¥{position['average_cost']:,.0f}"
                        })
                    
                    positions_df = pd.DataFrame(positions_data)
                    st.dataframe(positions_df, width="stretch")
                    
                    # 損益分布
                    st.subheader("📈 損益分布")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        pnl_values = [p['unrealized_pnl'] for p in summary['positions']]
                        fig_pnl = px.histogram(
                            x=pnl_values,
                            title="未実現損益分布",
                            nbins=20
                        )
                        st.plotly_chart(fig_pnl, width="stretch")
                    
                    with col2:
                        pnl_pct_values = [p['unrealized_pnl_pct'] for p in summary['positions']]
                        fig_pnl_pct = px.histogram(
                            x=pnl_pct_values,
                            title="損益率分布",
                            nbins=20
                        )
                        st.plotly_chart(fig_pnl_pct, width="stretch")
                else:
                    st.info("現在保有している銘柄がありません。")
            
            elif menu_option == "パフォーマンス分析":
                st.subheader("📊 パフォーマンス分析")
                
                # 分析期間設定
                col1, col2 = st.columns(2)
                
                with col1:
                    analysis_start_date = st.date_input("分析開始日", value=datetime.now() - timedelta(days=365), key="start_date_3")
                
                with col2:
                    analysis_end_date = st.date_input("分析終了日", value=datetime.now(), key="end_date_3")
                
                if st.button("📈 パフォーマンス分析を実行", type="primary"):
                    with st.spinner("パフォーマンス分析中..."):
                        try:
                            metrics = performance_tracker.calculate_performance_metrics(
                                datetime.combine(analysis_start_date, datetime.min.time()),
                                datetime.combine(analysis_end_date, datetime.max.time())
                            )
                            
                            st.subheader("📊 パフォーマンス指標")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("総リターン", f"{metrics['total_return']:.2f}%")
                            with col2:
                                st.metric("年率リターン", f"{metrics['annualized_return']:.2f}%")
                            with col3:
                                st.metric("シャープレシオ", f"{metrics['sharpe_ratio']:.2f}")
                            with col4:
                                st.metric("最大ドローダウン", f"{metrics['max_drawdown']:.2f}%")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("ボラティリティ", f"{metrics['volatility']:.2f}%")
                            with col2:
                                st.metric("勝率", f"{metrics['win_rate']:.2f}%")
                            with col3:
                                st.metric("プロフィットファクター", f"{metrics['profit_factor']:.2f}")
                            with col4:
                                st.metric("総取引数", f"{metrics['total_trades']}回")
                            
                            # パフォーマンスレポート生成
                            st.subheader("📄 パフォーマンスレポート")
                            
                            if st.button("📋 レポートを生成"):
                                report = performance_tracker.generate_performance_report(
                                    datetime.combine(analysis_start_date, datetime.min.time()),
                                    datetime.combine(analysis_end_date, datetime.max.time())
                                )
                                
                                st.text_area("パフォーマンスレポート", report, height=400)
                                
                                # レポートダウンロード
                                st.download_button(
                                    label="📥 レポートをダウンロード",
                                    data=report,
                                    file_name=f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                                
                        except Exception as e:
                            st.error(f"パフォーマンス分析中にエラーが発生しました: {str(e)}")
            
            elif menu_option == "データ管理":
                st.subheader("💾 データ管理")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📤 データエクスポート")
                    
                    if st.button("📊 取引データをCSVエクスポート"):
                        filename = performance_tracker.export_trades_to_csv()
                        if filename:
                            st.success(f"✅ 取引データをエクスポートしました: {filename}")
                            
                            # ダウンロードボタン
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="📥 CSVファイルをダウンロード",
                                    data=f.read(),
                                    file_name=filename,
                                    mime="text/csv"
                                )
                        else:
                            st.warning("エクスポートする取引データがありません。")
                
                with col2:
                    st.markdown("### 📥 データインポート")
                    
                    uploaded_file = st.file_uploader(
                        "CSVファイルをアップロード",
                        type=['csv'],
                        help="取引データのCSVファイルをアップロードしてください"
                    )
                    
                    if uploaded_file is not None:
                        if st.button("📊 取引データをインポート"):
                            # 一時ファイルに保存
                            temp_filename = f"temp_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            with open(temp_filename, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # インポート実行
                            if performance_tracker.import_trades_from_csv(temp_filename):
                                st.success("✅ 取引データをインポートしました！")
                                st.rerun()
                            else:
                                st.error("❌ インポートに失敗しました。CSVファイルの形式を確認してください。")
                            
                            # 一時ファイルを削除
                            os.remove(temp_filename)
                
                # データ統計
                st.subheader("📊 データ統計")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("総取引数", len(performance_tracker.trades))
                with col2:
                    unique_symbols = len(set([t['symbol'] for t in performance_tracker.trades]))
                    st.metric("取引銘柄数", unique_symbols)
                with col3:
                    if performance_tracker.trades:
                        first_trade_date = min([t['date'] for t in performance_tracker.trades])
                        st.metric("最初の取引", first_trade_date.strftime('%Y-%m-%d'))
                    else:
                        st.metric("最初の取引", "なし")
        
        with tab22:
            st.header("💼 ポートフォリオ管理")
            st.write("ポートフォリオの構築、最適化、リバランスを行います。")
            
            # ポートフォリオ管理メニュー
            portfolio_menu = st.selectbox(
                "メニューを選択",
                ["ポートフォリオ一覧", "新規ポートフォリオ作成", "ポートフォリオ分析", "リバランス提案", "ポートフォリオ最適化"],
                help="ポートフォリオ管理の機能を選択してください"
            )
            
            if portfolio_menu == "ポートフォリオ一覧":
                st.subheader("📋 ポートフォリオ一覧")
                
                portfolios = portfolio_manager.get_all_portfolios()
                
                if portfolios:
                    for portfolio in portfolios:
                        with st.expander(f"💼 {portfolio['name']} ({portfolio['strategy']})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**基本情報**")
                                st.write(f"- ID: {portfolio['id']}")
                                st.write(f"- 戦略: {portfolio['strategy']}")
                                st.write(f"- 作成日: {portfolio['created_at'].strftime('%Y-%m-%d')}")
                                st.write(f"- 最終更新: {portfolio['last_updated'].strftime('%Y-%m-%d')}")
                                st.write(f"- ポジション数: {len(portfolio['positions'])}銘柄")
                                
                                if portfolio['description']:
                                    st.write(f"- 説明: {portfolio['description']}")
                            
                            with col2:
                                st.write("**パフォーマンス**")
                                perf = portfolio.get('performance', {})
                                st.write(f"- 総リターン: {perf.get('total_return', 0):.2f}%")
                                st.write(f"- 年率リターン: {perf.get('annualized_return', 0):.2f}%")
                                st.write(f"- シャープレシオ: {perf.get('sharpe_ratio', 0):.2f}")
                                st.write(f"- 最大ドローダウン: {perf.get('max_drawdown', 0):.2f}%")
                            
                            # ポジション一覧
                            if portfolio['positions']:
                                st.write("**ポジション一覧**")
                                positions_data = []
                                for pos in portfolio['positions']:
                                    positions_data.append({
                                        '銘柄': pos['symbol'],
                                        'ウェイト': f"{pos['weight']:.1%}",
                                        '目標価格': f"¥{pos.get('target_price', 0):,.0f}" if pos.get('target_price') else "未設定",
                                        'メモ': pos.get('notes', '')
                                    })
                                
                                positions_df = pd.DataFrame(positions_data)
                                st.dataframe(positions_df, width="stretch")
                            
                            # 操作ボタン
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button(f"📊 分析", key=f"analyze_{portfolio['id']}"):
                                    st.session_state.selected_portfolio_id = portfolio['id']
                                    st.rerun()
                            
                            with col2:
                                if st.button(f"🔄 クローン", key=f"clone_{portfolio['id']}"):
                                    new_name = f"{portfolio['name']}_コピー"
                                    new_id = portfolio_manager.clone_portfolio(portfolio['id'], new_name)
                                    if new_id:
                                        st.success(f"ポートフォリオをクローンしました: {new_name}")
                                        st.rerun()
                            
                            with col3:
                                if st.button(f"🗑️ 削除", key=f"delete_{portfolio['id']}"):
                                    if portfolio_manager.delete_portfolio(portfolio['id']):
                                        st.success("ポートフォリオを削除しました")
                                        st.rerun()
                else:
                    st.info("ポートフォリオがありません。新規作成してください。")
            
            elif portfolio_menu == "新規ポートフォリオ作成":
                st.subheader("➕ 新規ポートフォリオ作成")
                
                with st.form("create_portfolio"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        portfolio_name = st.text_input("ポートフォリオ名", placeholder="例: バランス型ポートフォリオ")
                        strategy = st.selectbox(
                            "投資戦略",
                            ["balanced", "growth", "value", "dividend", "aggressive"],
                            format_func=lambda x: {
                                "balanced": "⚖️ バランス型",
                                "growth": "📈 成長重視",
                                "value": "💰 バリュー重視",
                                "dividend": "💎 配当重視",
                                "aggressive": "🚀 アグレッシブ"
                            }[x]
                        )
                    
                    with col2:
                        description = st.text_area("説明（任意）", placeholder="ポートフォリオの説明を入力")
                    
                    if st.form_submit_button("💼 ポートフォリオを作成", type="primary"):
                        if portfolio_name:
                            portfolio_id = portfolio_manager.create_portfolio(
                                name=portfolio_name,
                                description=description,
                                strategy=strategy
                            )
                            st.success(f"✅ ポートフォリオを作成しました！ID: {portfolio_id}")
                            st.rerun()
                        else:
                            st.error("ポートフォリオ名を入力してください。")
            
            elif portfolio_menu == "ポートフォリオ分析":
                st.subheader("📊 ポートフォリオ分析")
                
                portfolios = portfolio_manager.get_all_portfolios()
                
                if portfolios:
                    portfolio_names = {p['id']: p['name'] for p in portfolios}
                    selected_portfolio_id = st.selectbox(
                        "分析するポートフォリオを選択",
                        list(portfolio_names.keys()),
                        format_func=lambda x: portfolio_names[x]
                    )
                    
                    if selected_portfolio_id:
                        portfolio = portfolio_manager.get_portfolio(selected_portfolio_id)
                        
                        if portfolio:
                            # 現在価格を取得（簡易版）
                            current_prices = {}
                            for pos in portfolio['positions']:
                                current_prices[pos['symbol']] = 1000.0  # 仮の価格
                            
                            # ポートフォリオメトリクスを計算
                            metrics = portfolio_manager.calculate_portfolio_metrics(selected_portfolio_id, current_prices)
                            
                            # メトリクス表示
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("総ポジション数", metrics['position_count'])
                            with col2:
                                st.metric("総ウェイト", f"{metrics['total_weight']:.1%}")
                            with col3:
                                st.metric("分散化スコア", f"{metrics['diversification_score']:.2f}")
                            with col4:
                                st.metric("リスクスコア", f"{metrics['risk_score']:.2f}")
                            
                            # アロケーション表示
                            st.subheader("📈 アロケーション")
                            
                            if metrics['current_allocation']:
                                allocation_data = []
                                for symbol, weight in metrics['current_allocation'].items():
                                    allocation_data.append({
                                        '銘柄': symbol,
                                        'ウェイト': f"{weight:.1%}",
                                        'ウェイト値': weight
                                    })
                                
                                allocation_df = pd.DataFrame(allocation_data)
                                st.dataframe(allocation_df, width="stretch")
                                
                                # アロケーション円グラフ
                                fig = px.pie(
                                    allocation_df, 
                                    values='ウェイト値', 
                                    names='銘柄',
                                    title="ポートフォリオアロケーション"
                                )
                                st.plotly_chart(fig, width="stretch")
                            
                            # レポート生成
                            st.subheader("📄 ポートフォリオレポート")
                            
                            if st.button("📋 レポートを生成"):
                                report = portfolio_manager.generate_portfolio_report(selected_portfolio_id, current_prices)
                                st.text_area("ポートフォリオレポート", report, height=400)
                                
                                # レポートダウンロード
                                st.download_button(
                                    label="📥 レポートをダウンロード",
                                    data=report,
                                    file_name=f"portfolio_report_{portfolio['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                else:
                    st.info("分析するポートフォリオがありません。")
            
            elif portfolio_menu == "リバランス提案":
                st.subheader("🔄 リバランス提案")
                
                portfolios = portfolio_manager.get_all_portfolios()
                
                if portfolios:
                    portfolio_names = {p['id']: p['name'] for p in portfolios}
                    selected_portfolio_id = st.selectbox(
                        "リバランス対象のポートフォリオを選択",
                        list(portfolio_names.keys()),
                        format_func=lambda x: portfolio_names[x]
                    )
                    
                    if selected_portfolio_id:
                        # 現在価格を取得（簡易版）
                        portfolio = portfolio_manager.get_portfolio(selected_portfolio_id)
                        current_prices = {}
                        for pos in portfolio['positions']:
                            current_prices[pos['symbol']] = 1000.0  # 仮の価格
                        
                        # リバランス提案を生成
                        rebalance_suggestion = portfolio_manager.suggest_rebalance(selected_portfolio_id, current_prices)
                        
                        if rebalance_suggestion['rebalance_needed']:
                            st.warning(f"🔄 リバランスが必要です（閾値: {rebalance_suggestion['threshold']:.1%}）")
                            
                            st.subheader("📋 リバランスアクション")
                            
                            for action in rebalance_suggestion['actions']:
                                with st.expander(f"{action['symbol']} - {action['action']}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write(f"**現在ウェイト**: {action['current_weight']:.1%}")
                                        st.write(f"**目標ウェイト**: {action['target_weight']:.1%}")
                                        st.write(f"**調整量**: {action['adjustment']:.1%}")
                                    
                                    with col2:
                                        st.write(f"**理由**: {action['reason']}")
                            
                            # リバランス実行ボタン
                            if st.button("🔄 リバランスを実行", type="primary"):
                                st.info("リバランス機能は実装中です。")
                        else:
                            st.success("✅ 現在のアロケーションは適切です。リバランスは不要です。")
                            
                            # 現在のメトリクス表示
                            metrics = rebalance_suggestion['portfolio_metrics']
                            st.subheader("📊 現在のポートフォリオ状況")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("分散化スコア", f"{metrics['diversification_score']:.2f}")
                            with col2:
                                st.metric("リスクスコア", f"{metrics['risk_score']:.2f}")
                            with col3:
                                st.metric("期待リターン", f"{metrics['expected_return']:.1%}")
                else:
                    st.info("リバランス対象のポートフォリオがありません。")
            
            elif portfolio_menu == "ポートフォリオ最適化":
                st.subheader("🎯 ポートフォリオ最適化")
                
                portfolios = portfolio_manager.get_all_portfolios()
                
                if portfolios:
                    portfolio_names = {p['id']: p['name'] for p in portfolios}
                    selected_portfolio_id = st.selectbox(
                        "最適化対象のポートフォリオを選択",
                        list(portfolio_names.keys()),
                        format_func=lambda x: portfolio_names[x]
                    )
                    
                    if selected_portfolio_id:
                        # リスク許容度設定
                        risk_tolerance = st.slider(
                            "リスク許容度",
                            min_value=0.0,
                            max_value=1.0,
                            value=0.5,
                            step=0.1,
                            help="0.0: 保守的、1.0: アグレッシブ"
                        )
                        
                        if st.button("🎯 ポートフォリオを最適化", type="primary"):
                            optimization_result = portfolio_manager.optimize_portfolio(selected_portfolio_id, risk_tolerance)
                            
                            if optimization_result:
                                st.success("✅ ポートフォリオ最適化が完了しました！")
                                
                                st.subheader("📊 最適化結果")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("リスク許容度", f"{optimization_result['risk_tolerance']:.1f}")
                                with col2:
                                    st.metric("最大ウェイト", f"{optimization_result['max_weight']:.1%}")
                                with col3:
                                    st.metric("分散化改善度", f"{optimization_result['diversification_improvement']:.2f}")
                                
                                # 最適化されたウェイト表示
                                st.subheader("🎯 最適化されたアロケーション")
                                
                                optimized_data = []
                                for symbol, weight in optimization_result['optimized_weights'].items():
                                    optimized_data.append({
                                        '銘柄': symbol,
                                        '最適化ウェイト': f"{weight:.1%}",
                                        'ウェイト値': weight
                                    })
                                
                                optimized_df = pd.DataFrame(optimized_data)
                                st.dataframe(optimized_df, width="stretch")
                                
                                # 最適化されたアロケーション円グラフ
                                fig = px.pie(
                                    optimized_df, 
                                    values='ウェイト値', 
                                    names='銘柄',
                                    title="最適化されたポートフォリオアロケーション"
                                )
                                st.plotly_chart(fig, width="stretch")
                                
                                # 最適化適用ボタン
                                if st.button("💾 最適化を適用", type="secondary"):
                                    st.info("最適化適用機能は実装中です。")
                            else:
                                st.error("最適化に失敗しました。")
                else:
                    st.info("最適化対象のポートフォリオがありません。")
        
        with tab23:
            st.header("📰 リアルタイムニュース")
            st.write("最新の金融ニュースと市場動向をリアルタイムで追跡します。")
            
            # ニュース設定
            col1, col2 = st.columns(2)
            
            with col1:
                news_sources = st.multiselect(
                    "ニュースソース",
                    ["日経新聞", "東洋経済", "ダイヤモンド", "週刊エコノミスト", "Reuters", "Bloomberg"],
                    default=["日経新聞", "東洋経済"]
                )
                
                news_keywords = st.text_input(
                    "キーワード検索",
                    placeholder="例: 日本株, 日銀, インフレ",
                    help="特定のキーワードでニュースをフィルタリング"
                )
            
            with col2:
                news_categories = st.multiselect(
                    "カテゴリ",
                    ["経済", "株式", "為替", "債券", "商品", "暗号通貨", "政治", "企業業績"],
                    default=["経済", "株式"]
                )
                
                auto_refresh = st.checkbox("自動更新", value=True, help="5分ごとにニュースを自動更新")
            
            # ニュース取得ボタン
            if st.button("📰 最新ニュースを取得", type="primary"):
                with st.spinner("ニュースを取得中..."):
                    try:
                        # ニュース分析を実行
                        news_data = news_analyzer.get_latest_news(
                            sources=news_sources,
                            keywords=news_keywords.split(',') if news_keywords else [],
                            categories=news_categories
                        )
                        
                        if news_data and not news_data.empty:
                            st.session_state.latest_news = news_data
                            st.success(f"✅ {len(news_data)}件のニュースを取得しました！")
                        else:
                            st.warning("該当するニュースが見つかりませんでした。")
                            
                    except Exception as e:
                        st.error(f"ニュース取得中にエラーが発生しました: {str(e)}")
            
            # ニュース表示
            if 'latest_news' in st.session_state and not st.session_state.latest_news.empty:
                news_df = st.session_state.latest_news
                
                # ニュースサマリー
                st.subheader("📊 ニュースサマリー")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("総ニュース数", len(news_df))
                with col2:
                    positive_news = len(news_df[news_df.get('sentiment', 'neutral') == 'positive'])
                    st.metric("ポジティブ", positive_news)
                with col3:
                    negative_news = len(news_df[news_df.get('sentiment', 'neutral') == 'negative'])
                    st.metric("ネガティブ", negative_news)
                with col4:
                    neutral_news = len(news_df[news_df.get('sentiment', 'neutral') == 'neutral'])
                    st.metric("ニュートラル", neutral_news)
                
                # センチメント分析
                st.subheader("📈 センチメント分析")
                
                if 'sentiment' in news_df.columns:
                    sentiment_counts = news_df['sentiment'].value_counts()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_sentiment = px.pie(
                            values=sentiment_counts.values,
                            names=sentiment_counts.index,
                            title="センチメント分布"
                        )
                        st.plotly_chart(fig_sentiment, width="stretch")
                    
                    with col2:
                        # 時系列センチメント
                        if 'published_at' in news_df.columns:
                            news_df['date'] = pd.to_datetime(news_df['published_at']).dt.date
                            daily_sentiment = news_df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
                            
                            fig_timeline = px.bar(
                                daily_sentiment,
                                title="日別センチメント推移",
                                barmode='stack'
                            )
                            st.plotly_chart(fig_timeline, width="stretch")
                
                # ニュース一覧
                st.subheader("📰 ニュース一覧")
                
                # フィルター
                col1, col2 = st.columns(2)
                
                with col1:
                    sentiment_filter = st.selectbox(
                        "センチメントでフィルター",
                        ["すべて", "positive", "negative", "neutral"]
                    )
                
                with col2:
                    source_filter = st.selectbox(
                        "ソースでフィルター",
                        ["すべて"] + list(news_df.get('source', []).unique())
                    )
                
                # フィルタリング
                filtered_news = news_df.copy()
                
                if sentiment_filter != "すべて":
                    filtered_news = filtered_news[filtered_news.get('sentiment', 'neutral') == sentiment_filter]
                
                if source_filter != "すべて":
                    filtered_news = filtered_news[filtered_news.get('source', '') == source_filter]
                
                # ニュース表示
                for idx, (_, news) in enumerate(filtered_news.iterrows(), 1):
                    sentiment = news.get('sentiment', 'neutral')
                    sentiment_emoji = {
                        'positive': '😊',
                        'negative': '😟',
                        'neutral': '😐'
                    }.get(sentiment, '😐')
                    
                    with st.expander(f"{sentiment_emoji} {idx}. {news.get('title', 'No Title')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ソース**: {news.get('source', 'Unknown')}")
                            st.write(f"**公開日時**: {news.get('published_at', 'Unknown')}")
                            st.write(f"**センチメント**: {sentiment}")
                            
                            if 'relevance_score' in news:
                                st.write(f"**関連度スコア**: {news['relevance_score']:.2f}")
                        
                        with col2:
                            if 'url' in news and news['url']:
                                st.write(f"**URL**: [記事を読む]({news['url']})")
                            
                            if 'category' in news:
                                st.write(f"**カテゴリ**: {news['category']}")
                            
                            if 'keywords' in news:
                                st.write(f"**キーワード**: {', '.join(news['keywords'])}")
                        
                        # 記事内容
                        if 'content' in news and news['content']:
                            st.write("**記事内容**")
                            st.write(news['content'][:500] + "..." if len(news['content']) > 500 else news['content'])
                        
                        # 要約
                        if 'summary' in news and news['summary']:
                            st.write("**要約**")
                            st.write(news['summary'])
                
                # エクスポート機能
                st.subheader("📤 ニュースエクスポート")
                export_manager.create_export_ui(filtered_news, 'dataframe', 'news_data')
                
                # 自動更新設定
                if auto_refresh:
                    st.info("🔄 自動更新が有効です。5分ごとにニュースが更新されます。")
                    
                    # 自動更新の実装（簡易版）
                    if st.button("🔄 今すぐ更新"):
                        st.rerun()
            else:
                st.info("ニュースを取得してください。")
            
            # ニュース分析機能
            st.subheader("🔍 ニュース分析")
            
            if st.button("📊 ニュース分析を実行", type="secondary"):
                if 'latest_news' in st.session_state and not st.session_state.latest_news.empty:
                    with st.spinner("ニュース分析中..."):
                        try:
                            # ニュース分析を実行
                            analysis_result = news_analyzer.analyze_news_trends(st.session_state.latest_news)
                            
                            if analysis_result:
                                st.session_state.news_analysis = analysis_result
                                st.success("✅ ニュース分析が完了しました！")
                                
                                # 分析結果表示
                                st.subheader("📊 分析結果")
                                
                                # トレンド分析
                                if 'trends' in analysis_result:
                                    st.write("**主要トレンド**")
                                    for trend in analysis_result['trends'][:5]:
                                        st.write(f"- {trend}")
                                
                                # キーワード分析
                                if 'keywords' in analysis_result:
                                    st.write("**重要キーワード**")
                                    for keyword, count in list(analysis_result['keywords'].items())[:10]:
                                        st.write(f"- {keyword}: {count}回")
                                
                                # 市場への影響
                                if 'market_impact' in analysis_result:
                                    impact = analysis_result['market_impact']
                                    st.write("**市場への影響**")
                                    st.write(f"- 全体的なセンチメント: {impact.get('overall_sentiment', 'neutral')}")
                                    st.write(f"- 影響度スコア: {impact.get('impact_score', 0):.2f}")
                                    st.write(f"- 推奨アクション: {impact.get('recommended_action', '観察')}")
                            else:
                                st.warning("分析結果を取得できませんでした。")
                                
                        except Exception as e:
                            st.error(f"ニュース分析中にエラーが発生しました: {str(e)}")
                else:
                    st.warning("先にニュースを取得してください。")
            
            # 過去の分析結果
            if 'news_analysis' in st.session_state:
                st.subheader("📊 過去の分析結果")
                
                analysis = st.session_state.news_analysis
                
                # 簡易サマリー
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("分析ニュース数", len(st.session_state.latest_news))
                with col2:
                    st.metric("トレンド数", len(analysis.get('trends', [])))
                with col3:
                    st.metric("重要キーワード数", len(analysis.get('keywords', {})))
                
                # 詳細分析結果
                with st.expander("📋 詳細分析結果"):
                    st.json(analysis)
    
    else:
        st.warning("⚠️ 条件に合致する銘柄が見つかりませんでした。条件を緩和して再試行してください。")

# フッター
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(90deg, #1f4e79 0%, #2e7d32 100%); padding: 1rem; border-radius: 10px; text-align: center; color: white; margin-top: 2rem;'>
    <h4>📈 日本株価分析ツール v2.0</h4>
    <p style='margin: 0.5rem 0;'>包括的な投資分析プラットフォーム</p>
    <div style='display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;'>
        <a href='https://github.com/yamaryu999/stockAnalysis' style='color: white; text-decoration: none;'>📚 GitHub</a>
        <a href='https://github.com/yamaryu999/stockAnalysis/issues' style='color: white; text-decoration: none;'>🐛 バグ報告</a>
        <a href='https://github.com/yamaryu999/stockAnalysis/wiki' style='color: white; text-decoration: none;'>📖 ドキュメント</a>
    </div>
    <p style='margin: 1rem 0 0 0; font-size: 12px; opacity: 0.8;'>⚠️ 投資判断は自己責任でお願いします</p>
</div>
""", unsafe_allow_html=True)
