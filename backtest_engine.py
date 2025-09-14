import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class BacktestEngine:
    """
    バックテストエンジン
    
    過去データを使用して投資戦略の検証を行います。
    """
    
    def __init__(self):
        self.initial_capital = 1000000  # 初期資本100万円
        self.commission_rate = 0.0015   # 手数料率0.15%
        self.slippage_rate = 0.0005     # スリッページ率0.05%
    
    def run_backtest(self, strategy: str, stock_data: Dict, 
                    start_date: str = None, end_date: str = None,
                    **strategy_params) -> Dict:
        """
        バックテストを実行
        
        Args:
            strategy: 戦略名
            stock_data: 株価データ
            start_date: 開始日
            end_date: 終了日
            **strategy_params: 戦略パラメータ
            
        Returns:
            バックテスト結果
        """
        if not stock_data or 'data' not in stock_data or stock_data['data'].empty:
            return None
        
        data = stock_data['data'].copy()
        symbol = stock_data['symbol']
        
        # 日付フィルタリング
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        
        if data.empty:
            return None
        
        # 戦略に応じてシグナルを生成
        signals = self._generate_signals(strategy, data, **strategy_params)
        
        # 取引を実行
        trades = self._execute_trades(data, signals)
        
        # パフォーマンスを計算
        performance = self._calculate_performance(trades, data)
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'start_date': data.index[0],
            'end_date': data.index[-1],
            'trades': trades,
            'performance': performance,
            'signals': signals
        }
    
    def _generate_signals(self, strategy: str, data: pd.DataFrame, **params) -> pd.DataFrame:
        """戦略に応じてシグナルを生成"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['signal'] = 0  # 0: ホールド, 1: 買い, -1: 売り
        
        if strategy == "moving_average_cross":
            short_window = params.get('short_window', 20)
            long_window = params.get('long_window', 50)
            
            signals['short_ma'] = data['Close'].rolling(window=short_window).mean()
            signals['long_ma'] = data['Close'].rolling(window=long_window).mean()
            
            # ゴールデンクロス・デッドクロス
            signals['signal'] = np.where(
                signals['short_ma'] > signals['long_ma'], 1, 0
            )
            signals['signal'] = signals['signal'].diff()
        
        elif strategy == "rsi_strategy":
            rsi_period = params.get('rsi_period', 14)
            oversold = params.get('oversold', 30)
            overbought = params.get('overbought', 70)
            
            signals['rsi'] = self._calculate_rsi(data['Close'], rsi_period)
            
            # RSI戦略
            signals['signal'] = np.where(
                signals['rsi'] < oversold, 1, 0
            )
            signals['signal'] = np.where(
                signals['rsi'] > overbought, -1, signals['signal']
            )
            signals['signal'] = signals['signal'].diff()
        
        elif strategy == "bollinger_bands":
            period = params.get('period', 20)
            std_dev = params.get('std_dev', 2)
            
            signals['bb_middle'] = data['Close'].rolling(window=period).mean()
            signals['bb_std'] = data['Close'].rolling(window=period).std()
            signals['bb_upper'] = signals['bb_middle'] + (signals['bb_std'] * std_dev)
            signals['bb_lower'] = signals['bb_middle'] - (signals['bb_std'] * std_dev)
            
            # ボリンジャーバンド戦略
            signals['signal'] = np.where(
                data['Close'] < signals['bb_lower'], 1, 0
            )
            signals['signal'] = np.where(
                data['Close'] > signals['bb_upper'], -1, signals['signal']
            )
            signals['signal'] = signals['signal'].diff()
        
        elif strategy == "momentum":
            period = params.get('period', 20)
            threshold = params.get('threshold', 0.02)
            
            signals['momentum'] = data['Close'].pct_change(period)
            
            # モメンタム戦略
            signals['signal'] = np.where(
                signals['momentum'] > threshold, 1, 0
            )
            signals['signal'] = np.where(
                signals['momentum'] < -threshold, -1, signals['signal']
            )
            signals['signal'] = signals['signal'].diff()
        
        elif strategy == "mean_reversion":
            period = params.get('period', 20)
            threshold = params.get('threshold', 2)
            
            signals['sma'] = data['Close'].rolling(window=period).mean()
            signals['std'] = data['Close'].rolling(window=period).std()
            signals['z_score'] = (data['Close'] - signals['sma']) / signals['std']
            
            # 平均回帰戦略
            signals['signal'] = np.where(
                signals['z_score'] < -threshold, 1, 0
            )
            signals['signal'] = np.where(
                signals['z_score'] > threshold, -1, signals['signal']
            )
            signals['signal'] = signals['signal'].diff()
        
        return signals
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSIを計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _execute_trades(self, data: pd.DataFrame, signals: pd.DataFrame) -> List[Dict]:
        """取引を実行"""
        trades = []
        position = 0  # ポジション（0: ノーポジション, 1: ロング, -1: ショート）
        cash = self.initial_capital
        shares = 0
        
        for date, row in signals.iterrows():
            signal = row['signal']
            price = row['price']
            
            if signal == 1 and position == 0:  # 買いシグナル
                # 全資金で買い
                shares = cash / (price * (1 + self.commission_rate + self.slippage_rate))
                cash = 0
                position = 1
                
                trades.append({
                    'date': date,
                    'action': 'BUY',
                    'price': price,
                    'shares': shares,
                    'value': shares * price,
                    'cash': cash,
                    'position': position
                })
            
            elif signal == -1 and position == 1:  # 売りシグナル
                # 全ポジションを売り
                cash = shares * price * (1 - self.commission_rate - self.slippage_rate)
                shares = 0
                position = 0
                
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'price': price,
                    'shares': shares,
                    'value': cash,
                    'cash': cash,
                    'position': position
                })
        
        # 最終日のポジションをクローズ
        if position == 1:
            final_price = data['Close'].iloc[-1]
            cash = shares * final_price * (1 - self.commission_rate - self.slippage_rate)
            
            trades.append({
                'date': data.index[-1],
                'action': 'SELL',
                'price': final_price,
                'shares': shares,
                'value': cash,
                'cash': cash,
                'position': 0
            })
        
        return trades
    
    def _calculate_performance(self, trades: List[Dict], data: pd.DataFrame) -> Dict:
        """パフォーマンスを計算"""
        if not trades:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': 0
            }
        
        # 最終資産価値
        final_value = trades[-1]['cash']
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # 年率リターン
        start_date = data.index[0]
        end_date = data.index[-1]
        years = (end_date - start_date).days / 365.25
        annualized_return = ((final_value / self.initial_capital) ** (1/years) - 1) * 100
        
        # 日次リターン
        daily_returns = data['Close'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100  # 年率ボラティリティ
        
        # シャープレシオ
        risk_free_rate = 0.01  # 1%と仮定
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 最大ドローダウン
        cumulative_returns = (1 + daily_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # 取引統計
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        
        total_trades = len(buy_trades)
        winning_trades = 0
        total_profit = 0
        total_loss = 0
        
        for i in range(len(buy_trades)):
            if i < len(sell_trades):
                buy_price = buy_trades[i]['price']
                sell_price = sell_trades[i]['price']
                profit = (sell_price - buy_price) / buy_price
                
                if profit > 0:
                    winning_trades += 1
                    total_profit += profit
                else:
                    total_loss += abs(profit)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': total_trades,
            'final_value': final_value,
            'initial_capital': self.initial_capital
        }
    
    def compare_strategies(self, strategies: List[str], stock_data: Dict, 
                          **strategy_params) -> pd.DataFrame:
        """複数戦略を比較"""
        results = []
        
        for strategy in strategies:
            result = self.run_backtest(strategy, stock_data, **strategy_params)
            if result:
                performance = result['performance']
                performance['strategy'] = strategy
                results.append(performance)
        
        if results:
            return pd.DataFrame(results)
        return pd.DataFrame()
    
    def optimize_parameters(self, strategy: str, stock_data: Dict, 
                           param_ranges: Dict) -> Dict:
        """パラメータ最適化"""
        best_performance = None
        best_params = None
        
        # グリッドサーチ（簡易版）
        for param_name, param_values in param_ranges.items():
            for param_value in param_values:
                params = {param_name: param_value}
                
                result = self.run_backtest(strategy, stock_data, **params)
                if result:
                    performance = result['performance']
                    
                    if (best_performance is None or 
                        performance['sharpe_ratio'] > best_performance['sharpe_ratio']):
                        best_performance = performance
                        best_params = params
        
        return {
            'best_params': best_params,
            'best_performance': best_performance
        }
    
    def generate_backtest_report(self, result: Dict) -> str:
        """バックテストレポートを生成"""
        if not result:
            return "バックテスト結果がありません。"
        
        performance = result['performance']
        trades = result['trades']
        
        report = f"""
# バックテストレポート

## 基本情報
- 銘柄: {result['symbol']}
- 戦略: {result['strategy']}
- 期間: {result['start_date'].strftime('%Y-%m-%d')} ～ {result['end_date'].strftime('%Y-%m-%d')}
- 初期資本: ¥{self.initial_capital:,.0f}

## パフォーマンス
- 総リターン: {performance['total_return']:.2f}%
- 年率リターン: {performance['annualized_return']:.2f}%
- ボラティリティ: {performance['volatility']:.2f}%
- シャープレシオ: {performance['sharpe_ratio']:.2f}
- 最大ドローダウン: {performance['max_drawdown']:.2f}%

## 取引統計
- 総取引数: {performance['total_trades']}回
- 勝率: {performance['win_rate']:.2f}%
- プロフィットファクター: {performance['profit_factor']:.2f}
- 最終資産価値: ¥{performance['final_value']:,.0f}

## 取引履歴
"""
        
        for trade in trades:
            report += f"- {trade['date'].strftime('%Y-%m-%d')}: {trade['action']} @ ¥{trade['price']:,.0f}\n"
        
        return report
