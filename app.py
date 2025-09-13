import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from stock_analyzer import JapaneseStockAnalyzer
from news_analyzer import NewsAnalyzer
from investment_strategies import InvestmentStrategies
from stock_forecast import StockForecastAnalyzer
import time
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="日本株価分析ツール",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("📈 日本株価分析ツール")
st.markdown("---")

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

analyzer = initialize_analyzer()
news_analyzer = initialize_news_analyzer()
investment_strategies = initialize_investment_strategies()
forecast_analyzer = initialize_forecast_analyzer()

# 自動提案機能
st.sidebar.header("🤖 AI推奨設定")

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
            st.plotly_chart(fig_sector, use_container_width=True)
        
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
        
        # 日本株データを取得
        japanese_stocks = analyzer.get_japanese_stocks()
        
        # 全銘柄の場合は並列処理で高速化
        if len(japanese_stocks) > 100:
            st.info(f"📊 全銘柄分析中... ({len(japanese_stocks)}銘柄)")
            
            # 並列処理で株価データを取得
            symbols = list(japanese_stocks.values())
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("株価データを並列取得中...")
            
            # バッチサイズを制限（メモリ使用量を考慮）
            batch_size = 50
            screened_stocks = []
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(symbols))
                batch_symbols = symbols[start_idx:end_idx]
                
                status_text.text(f"バッチ {batch_idx + 1}/{total_batches} 処理中...")
                progress_bar.progress((batch_idx + 1) / total_batches)
                
                # 並列でデータ取得（レート制限対応）
                batch_data = analyzer.get_stock_data_batch(batch_symbols, max_workers=3)
                
                # 各銘柄の分析
                for symbol, stock_data in batch_data.items():
                    if stock_data and stock_data['data'] is not None and not stock_data['data'].empty:
                        metrics = analyzer.calculate_financial_metrics(stock_data)
                        if metrics and analyzer._meets_criteria(metrics, criteria):
                            # 銘柄名を取得
                            stock_name = next((name for name, sym in japanese_stocks.items() if sym == symbol), symbol)
                            metrics['name'] = stock_name
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 データ一覧", "📈 可視化", "📋 レポート", "🎯 おすすめ銘柄", "🔮 動向予想"])
        
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
            
            st.dataframe(display_df, use_container_width=True)
            
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
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # ROE上位10銘柄
                top_roe = df.nlargest(10, 'roe')
                fig2 = px.bar(top_roe, x='name', y='roe',
                            title='ROE上位10銘柄',
                            labels={'roe': 'ROE(%)', 'name': '銘柄名'})
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, use_container_width=True)
            
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
                st.plotly_chart(fig3, use_container_width=True)
        
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
                    # スクリーニング結果の銘柄データを取得
                    stock_data_dict = {}
                    metrics_dict = {}
                    
                    for idx, stock in df.iterrows():
                        symbol = stock['symbol']
                        # 株価データを取得
                        stock_data = analyzer.get_stock_data(symbol)
                        if stock_data and stock_data['data'] is not None:
                            stock_data_dict[symbol] = stock_data
                            # 財務指標を取得
                            metrics = analyzer.calculate_financial_metrics(stock_data)
                            if metrics:
                                metrics_dict[symbol] = metrics
                    
                    # 動向分析を実行
                    if stock_data_dict and metrics_dict:
                        forecasts = forecast_analyzer.analyze_multiple_stocks(stock_data_dict, metrics_dict)
                        st.session_state.forecasts = forecasts
                        st.success(f"✅ {len(forecasts)}銘柄の動向分析が完了しました！")
                    else:
                        st.error("❌ 動向分析に必要なデータが取得できませんでした。")
            
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
                    st.plotly_chart(fig_forecast, use_container_width=True)
                
                # 信頼度分布
                st.markdown("### 🎯 信頼度分布")
                confidence_data = [f['confidence'] for f in forecasts]
                fig_confidence = px.histogram(
                    x=confidence_data,
                    nbins=10,
                    title="信頼度の分布",
                    labels={'x': '信頼度 (%)', 'y': '銘柄数'}
                )
                st.plotly_chart(fig_confidence, use_container_width=True)
    
    else:
        st.warning("⚠️ 条件に合致する銘柄が見つかりませんでした。条件を緩和して再試行してください。")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📈 日本株価分析ツール | 投資判断は自己責任でお願いします</p>
</div>
""", unsafe_allow_html=True)
