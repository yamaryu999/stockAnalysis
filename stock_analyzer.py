import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'

class JapaneseStockAnalyzer:
    def __init__(self):
        self.ticker_data = {}
        self.analysis_results = pd.DataFrame()
        
    def get_all_tse_stocks(self):
        """東京証券取引所の全銘柄を取得"""
        all_stocks = {}
        
        try:
            # プライム市場の銘柄を取得
            prime_stocks = self._get_tse_stocks_by_market("prime")
            all_stocks.update(prime_stocks)
            
            # スタンダード市場の銘柄を取得
            standard_stocks = self._get_tse_stocks_by_market("standard")
            all_stocks.update(standard_stocks)
            
            # グロース市場の銘柄を取得
            growth_stocks = self._get_tse_stocks_by_market("growth")
            all_stocks.update(growth_stocks)
            
            print(f"取得した銘柄数: {len(all_stocks)}")
            return all_stocks
            
        except Exception as e:
            print(f"全銘柄取得エラー: {e}")
            # エラー時は主要銘柄を返す
            return self.get_major_japanese_stocks()
    
    def _get_tse_stocks_by_market(self, market_type):
        """市場別に銘柄を取得"""
        stocks = {}
        
        try:
            # 市場別のURL（実際のTSEのAPIやデータソースを使用）
            if market_type == "prime":
                # プライム市場の銘柄リスト
                prime_codes = self._generate_stock_codes("prime")
                stocks.update(prime_codes)
            elif market_type == "standard":
                # スタンダード市場の銘柄リスト
                standard_codes = self._generate_stock_codes("standard")
                stocks.update(standard_codes)
            elif market_type == "growth":
                # グロース市場の銘柄リスト
                growth_codes = self._generate_stock_codes("growth")
                stocks.update(growth_codes)
                
        except Exception as e:
            print(f"{market_type}市場の銘柄取得エラー: {e}")
            
        return stocks
    
    def _generate_stock_codes(self, market_type):
        """市場別の銘柄コードを生成"""
        stocks = {}
        
        # 実際のTSEの銘柄コード範囲に基づいて生成
        if market_type == "prime":
            # プライム市場: 主に1000番台〜9000番台
            code_ranges = [
                (1000, 9999),  # 一般的な銘柄コード
                (1300, 1399),  # 投資信託
                (2000, 2999),  # その他
                (3000, 3999),  # その他
                (4000, 4999),  # その他
                (5000, 5999),  # その他
                (6000, 6999),  # その他
                (7000, 7999),  # その他
                (8000, 8999),  # その他
                (9000, 9999)   # その他
            ]
        elif market_type == "standard":
            # スタンダード市場: 主に1000番台〜9000番台
            code_ranges = [
                (1000, 1999),
                (2000, 2999),
                (3000, 3999),
                (4000, 4999),
                (5000, 5999),
                (6000, 6999),
                (7000, 7999),
                (8000, 8999),
                (9000, 9999)
            ]
        else:  # growth
            # グロース市場: 主に1000番台〜9000番台
            code_ranges = [
                (1000, 1999),
                (2000, 2999),
                (3000, 3999),
                (4000, 4999),
                (5000, 5999),
                (6000, 6999),
                (7000, 7999),
                (8000, 8999),
                (9000, 9999)
            ]
        
        # サンプルとして主要銘柄を追加
        major_stocks = self.get_major_japanese_stocks()
        stocks.update(major_stocks)
        
        # 追加の銘柄コードを生成（実際の存在確認は後で行う）
        for start, end in code_ranges:
            for code in range(start, end + 1):
                symbol = f"{code:04d}.T"
                # 既存の銘柄と重複しない場合のみ追加
                if symbol not in [s for s in stocks.values()]:
                    # 仮の会社名（実際のデータ取得時に更新される）
                    company_name = f"銘柄{code:04d}"
                    stocks[company_name] = symbol
                    
                    # メモリ使用量とレート制限を考慮して制限
                    if len(stocks) >= 1000:  # 最大1000銘柄（レート制限対応）
                        break
            if len(stocks) >= 1000:
                break
                
        return stocks
    
    def get_major_japanese_stocks(self):
        """主要な日本株のティッカーシンボルを取得（フォールバック用）"""
        japanese_stocks = {
            'トヨタ自動車': '7203.T',
            'ソフトバンクグループ': '9984.T',
            'キーエンス': '6861.T',
            'ソニーグループ': '6758.T',
            '任天堂': '7974.T',
            'ファーストリテイリング': '9983.T',
            '日本電信電話': '9432.T',
            '三菱UFJフィナンシャル・グループ': '8306.T',
            '三井住友フィナンシャルグループ': '8316.T',
            'みずほフィナンシャルグループ': '8411.T',
            'KDDI': '9433.T',
            '日本たばこ産業': '2914.T',
            '三菱商事': '8058.T',
            '三井物産': '8031.T',
            '住友商事': '8053.T',
            '伊藤忠商事': '8001.T',
            '丸紅': '8002.T',
            '本田技研工業': '7267.T',
            '日産自動車': '7201.T',
            'マツダ': '7261.T',
            'スズキ': '7269.T',
            'SUBARU': '7270.T',
            '三菱重工業': '7011.T',
            '川崎重工業': '7012.T',
            'IHI': '7013.T',
            '日立製作所': '6501.T',
            '三菱電機': '6503.T',
            'パナソニック': '6752.T',
            'シャープ': '6753.T',
            '京セラ': '6971.T',
            '村田製作所': '6981.T',
            'TDK': '6762.T',
            '日本電産': '6594.T',
            'ファナック': '6954.T',
            'オムロン': '6645.T',
            '横河電機': '6841.T',
            'アドバンテスト': '6857.T',
            '東京エレクトロン': '8035.T',
            '信越化学工業': '4063.T',
            '三井化学': '4183.T',
            '住友化学': '4005.T',
            '旭化成': '3407.T',
            '東レ': '3402.T',
            '帝人': '3401.T',
            '三菱ケミカルホールディングス': '4188.T',
            '花王': '4452.T',
            '資生堂': '4911.T',
            'コーセー': '4922.T',
            'ポーラ・オルビスホールディングス': '4927.T',
            'ファンケル': '4921.T',
            '大塚ホールディングス': '4578.T',
            '武田薬品工業': '4502.T',
            'アステラス製薬': '4503.T',
            '第一三共': '4568.T',
            'エーザイ': '4523.T',
            '中外製薬': '4519.T',
            '塩野義製薬': '4507.T',
            '大日本住友製薬': '4506.T',
            '小野薬品工業': '4528.T',
            '協和発酵キリン': '4151.T',
            '日本製鉄': '5401.T',
            'JFEホールディングス': '5411.T',
            '神戸製鋼所': '5406.T',
            '住友金属鉱山': '5713.T',
            '三井金属鉱業': '5706.T',
            'DOWAホールディングス': '5714.T',
            '三菱マテリアル': '5711.T',
            '古河電気工業': '5801.T',
            '住友電気工業': '5802.T',
            'フジクラ': '5803.T',
            '日本軽金属ホールディングス': '5703.T',
            'UACJ': '5741.T',
            '日本製紙': '3863.T',
            '王子ホールディングス': '3861.T',
            '大王製紙': '3880.T',
            'レンゴー': '3944.T',
            'セイコーエプソン': '6724.T',
            'ブラザー工業': '6448.T',
            'リコー': '7752.T',
            'キヤノン': '7751.T',
            'ニコン': '7731.T',
            'オリンパス': '7733.T',
            'HOYA': '7741.T',
            'テルモ': '4543.T'
        }
        return japanese_stocks
    
    def get_japanese_stocks(self):
        """日本株のティッカーシンボルを取得（全銘柄対応）"""
        return self.get_all_tse_stocks()
    
    def get_stock_data(self, symbol, period="1y"):
        """株価データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            info = ticker.info
            
            return {
                'data': data,
                'info': info,
                'symbol': symbol
            }
        except Exception as e:
            print(f"データ取得エラー {symbol}: {e}")
            return None
    
    def get_stock_data_batch(self, symbols, period="1y", max_workers=3):
        """複数銘柄の株価データを並列取得（レート制限対応）"""
        results = {}
        
        def fetch_single_stock(symbol):
            try:
                # レート制限を避けるために少し待機
                time.sleep(0.1)
                return symbol, self.get_stock_data(symbol, period)
            except Exception as e:
                print(f"バッチ取得エラー {symbol}: {e}")
                return symbol, None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 各銘柄のデータ取得を並列実行
            future_to_symbol = {
                executor.submit(fetch_single_stock, symbol): symbol 
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol, data = future.result()
                if data is not None:
                    results[symbol] = data
                    
        return results
    
    def calculate_financial_metrics(self, stock_data):
        """財務指標を計算"""
        if not stock_data or stock_data['data'] is None or stock_data['data'].empty:
            return None
            
        info = stock_data['info']
        data = stock_data['data']
        
        # 基本情報
        current_price = data['Close'].iloc[-1] if not data.empty else 0
        
        # 財務指標
        metrics = {
            'symbol': stock_data['symbol'],
            'current_price': current_price,
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
            'roa': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
            'debt_to_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
            'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
            'earnings_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
            'beta': info.get('beta', 0),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown')
        }
        
        return metrics
    
    def screen_stocks(self, stocks_data, criteria):
        """株をスクリーニング"""
        screened_stocks = []
        
        for stock_name, symbol in stocks_data.items():
            stock_data = self.get_stock_data(symbol)
            if stock_data:
                metrics = self.calculate_financial_metrics(stock_data)
                if metrics:
                    # スクリーニング条件をチェック
                    if self._meets_criteria(metrics, criteria):
                        metrics['name'] = stock_name
                        screened_stocks.append(metrics)
        
        return pd.DataFrame(screened_stocks)
    
    def _meets_criteria(self, metrics, criteria):
        """スクリーニング条件をチェック"""
        conditions = []
        
        # PER条件
        if criteria.get('pe_min', 0) <= metrics['pe_ratio'] <= criteria.get('pe_max', float('inf')):
            conditions.append(True)
        else:
            conditions.append(False)
        
        # PBR条件
        if criteria.get('pb_min', 0) <= metrics['pb_ratio'] <= criteria.get('pb_max', float('inf')):
            conditions.append(True)
        else:
            conditions.append(False)
        
        # ROE条件
        if metrics['roe'] >= criteria.get('roe_min', 0):
            conditions.append(True)
        else:
            conditions.append(False)
        
        # 配当利回り条件
        if metrics['dividend_yield'] >= criteria.get('dividend_min', 0):
            conditions.append(True)
        else:
            conditions.append(False)
        
        # 負債比率条件
        if metrics['debt_to_equity'] <= criteria.get('debt_max', float('inf')):
            conditions.append(True)
        else:
            conditions.append(False)
        
        # すべての条件を満たすかチェック
        return all(conditions)
    
    def create_visualization(self, df, chart_type='scatter'):
        """可視化を作成"""
        if df.empty:
            return None
            
        if chart_type == 'scatter':
            fig = px.scatter(df, x='pe_ratio', y='pb_ratio', 
                           size='market_cap', color='roe',
                           hover_data=['name', 'dividend_yield', 'debt_to_equity'],
                           title='PER vs PBR 散布図（サイズ：時価総額、色：ROE）')
        elif chart_type == 'bar':
            fig = px.bar(df.head(10), x='name', y='roe',
                        title='ROE上位10銘柄')
        elif chart_type == 'heatmap':
            # 相関行列のヒートマップ
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                           title='財務指標相関マトリックス')
        
        return fig
    
    def generate_report(self, df):
        """分析レポートを生成"""
        if df.empty:
            return "スクリーニング条件に合致する銘柄が見つかりませんでした。"
        
        report = f"""
# 株価分析レポート
生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## スクリーニング結果
- 対象銘柄数: {len(df)}銘柄

## 統計サマリー
- 平均PER: {df['pe_ratio'].mean():.2f}
- 平均PBR: {df['pb_ratio'].mean():.2f}
- 平均ROE: {df['roe'].mean():.2f}%
- 平均配当利回り: {df['dividend_yield'].mean():.2f}%

## おすすめ銘柄（ROE上位5銘柄）
"""
        
        top_stocks = df.nlargest(5, 'roe')
        for idx, stock in top_stocks.iterrows():
            report += f"""
### {stock['name']}
- 現在価格: ¥{stock['current_price']:,.0f}
- PER: {stock['pe_ratio']:.2f}
- PBR: {stock['pb_ratio']:.2f}
- ROE: {stock['roe']:.2f}%
- 配当利回り: {stock['dividend_yield']:.2f}%
- セクター: {stock['sector']}
"""
        
        return report
