import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os

class PerformanceTracker:
    """
    実績管理機能
    
    実際の取引結果を追跡・分析し、投資パフォーマンスを管理します。
    """
    
    def __init__(self, data_file: str = "performance_data.json"):
        self.data_file = data_file
        self.trades = self._load_trades()
        self.portfolios = self._load_portfolios()
    
    def _load_trades(self) -> List[Dict]:
        """取引データを読み込み"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('trades', [])
            except Exception as e:
                print(f"取引データ読み込みエラー: {e}")
                return []
        return []
    
    def _load_portfolios(self) -> List[Dict]:
        """ポートフォリオデータを読み込み"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('portfolios', [])
            except Exception as e:
                print(f"ポートフォリオデータ読み込みエラー: {e}")
                return []
        return []
    
    def _save_data(self):
        """データを保存"""
        try:
            data = {
                'trades': self.trades,
                'portfolios': self.portfolios,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"データ保存エラー: {e}")
    
    def add_trade(self, symbol: str, action: str, quantity: float, price: float,
                  date: datetime = None, commission: float = 0.0, notes: str = "") -> str:
        """
        取引を追加
        
        Args:
            symbol: 銘柄コード
            action: アクション ("BUY", "SELL")
            quantity: 数量
            price: 価格
            date: 取引日時
            commission: 手数料
            notes: メモ
            
        Returns:
            取引ID
        """
        if date is None:
            date = datetime.now()
        
        trade_id = f"trade_{symbol}_{date.strftime('%Y%m%d_%H%M%S')}"
        
        trade = {
            'id': trade_id,
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'date': date,
            'commission': commission,
            'notes': notes,
            'created_at': datetime.now()
        }
        
        self.trades.append(trade)
        self._save_data()
        
        return trade_id
    
    def get_trades(self, symbol: str = None, start_date: datetime = None, 
                   end_date: datetime = None) -> List[Dict]:
        """取引履歴を取得"""
        filtered_trades = self.trades.copy()
        
        if symbol:
            filtered_trades = [t for t in filtered_trades if t['symbol'] == symbol]
        
        if start_date:
            filtered_trades = [t for t in filtered_trades if t['date'] >= start_date]
        
        if end_date:
            filtered_trades = [t for t in filtered_trades if t['date'] <= end_date]
        
        # 日付順でソート
        filtered_trades.sort(key=lambda x: x['date'])
        
        return filtered_trades
    
    def calculate_position(self, symbol: str, date: datetime = None) -> Dict:
        """指定日時でのポジションを計算"""
        if date is None:
            date = datetime.now()
        
        trades = self.get_trades(symbol=symbol, end_date=date)
        
        position = 0
        total_cost = 0
        total_commission = 0
        
        for trade in trades:
            if trade['action'] == 'BUY':
                position += trade['quantity']
                total_cost += trade['quantity'] * trade['price']
                total_commission += trade['commission']
            elif trade['action'] == 'SELL':
                position -= trade['quantity']
                total_cost -= trade['quantity'] * trade['price']
                total_commission += trade['commission']
        
        avg_cost = total_cost / position if position != 0 else 0
        
        return {
            'symbol': symbol,
            'position': position,
            'total_cost': total_cost,
            'average_cost': avg_cost,
            'total_commission': total_commission,
            'date': date
        }
    
    def calculate_pnl(self, symbol: str, current_price: float, date: datetime = None) -> Dict:
        """損益を計算"""
        position = self.calculate_position(symbol, date)
        
        if position['position'] == 0:
            return {
                'symbol': symbol,
                'position': 0,
                'unrealized_pnl': 0,
                'realized_pnl': 0,
                'total_pnl': 0,
                'pnl_percentage': 0
            }
        
        # 未実現損益
        market_value = position['position'] * current_price
        unrealized_pnl = market_value - position['total_cost']
        unrealized_pnl_pct = (unrealized_pnl / position['total_cost']) * 100 if position['total_cost'] != 0 else 0
        
        # 実現損益（売却済み分）
        realized_pnl = self._calculate_realized_pnl(symbol, date)
        
        total_pnl = unrealized_pnl + realized_pnl
        
        return {
            'symbol': symbol,
            'position': position['position'],
            'market_value': market_value,
            'cost_basis': position['total_cost'],
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'realized_pnl': realized_pnl,
            'total_pnl': total_pnl,
            'current_price': current_price,
            'average_cost': position['average_cost']
        }
    
    def _calculate_realized_pnl(self, symbol: str, date: datetime = None) -> float:
        """実現損益を計算"""
        if date is None:
            date = datetime.now()
        
        trades = self.get_trades(symbol=symbol, end_date=date)
        
        realized_pnl = 0
        buy_trades = []
        
        for trade in trades:
            if trade['action'] == 'BUY':
                buy_trades.append(trade)
            elif trade['action'] == 'SELL':
                # FIFO方式で実現損益を計算
                remaining_sell = trade['quantity']
                
                while remaining_sell > 0 and buy_trades:
                    buy_trade = buy_trades[0]
                    
                    if buy_trade['quantity'] <= remaining_sell:
                        # 完全に売却
                        realized_pnl += (trade['price'] - buy_trade['price']) * buy_trade['quantity']
                        remaining_sell -= buy_trade['quantity']
                        buy_trades.pop(0)
                    else:
                        # 部分売却
                        realized_pnl += (trade['price'] - buy_trade['price']) * remaining_sell
                        buy_trade['quantity'] -= remaining_sell
                        remaining_sell = 0
        
        return realized_pnl
    
    def get_portfolio_summary(self, date: datetime = None) -> Dict:
        """ポートフォリオサマリーを取得"""
        if date is None:
            date = datetime.now()
        
        # 全銘柄のポジションを取得
        symbols = list(set([trade['symbol'] for trade in self.trades]))
        
        total_market_value = 0
        total_cost_basis = 0
        total_unrealized_pnl = 0
        total_realized_pnl = 0
        positions = []
        
        for symbol in symbols:
            position = self.calculate_position(symbol, date)
            if position['position'] != 0:
                # 現在価格を取得（実際の実装では外部APIから取得）
                current_price = self._get_current_price(symbol)
                pnl = self.calculate_pnl(symbol, current_price, date)
                
                total_market_value += pnl['market_value']
                total_cost_basis += pnl['cost_basis']
                total_unrealized_pnl += pnl['unrealized_pnl']
                total_realized_pnl += pnl['realized_pnl']
                
                positions.append(pnl)
        
        total_pnl = total_unrealized_pnl + total_realized_pnl
        total_pnl_pct = (total_pnl / total_cost_basis) * 100 if total_cost_basis != 0 else 0
        
        return {
            'date': date,
            'total_market_value': total_market_value,
            'total_cost_basis': total_cost_basis,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_realized_pnl': total_realized_pnl,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'positions': positions,
            'position_count': len(positions)
        }
    
    def _get_current_price(self, symbol: str) -> float:
        """現在価格を取得（簡易実装）"""
        # 実際の実装では、yfinanceやその他のAPIから取得
        # ここでは仮の価格を返す
        return 1000.0
    
    def calculate_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """パフォーマンス指標を計算"""
        # 期間内の取引を取得
        trades = self.get_trades(start_date=start_date, end_date=end_date)
        
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
        
        # 日次リターンを計算
        daily_returns = self._calculate_daily_returns(start_date, end_date)
        
        if len(daily_returns) == 0:
            return {
                'total_return': 0,
                'annualized_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_trades': len(trades)
            }
        
        # 基本指標
        total_return = (daily_returns.iloc[-1] / daily_returns.iloc[0] - 1) * 100
        
        # 年率リターン
        years = (end_date - start_date).days / 365.25
        annualized_return = ((daily_returns.iloc[-1] / daily_returns.iloc[0]) ** (1/years) - 1) * 100
        
        # ボラティリティ
        returns = daily_returns.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100
        
        # シャープレシオ
        risk_free_rate = 0.01  # 1%
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 最大ドローダウン
        cumulative_returns = (1 + returns).cumprod()
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
            'total_trades': total_trades
        }
    
    def _calculate_daily_returns(self, start_date: datetime, end_date: datetime) -> pd.Series:
        """日次リターンを計算"""
        # 簡易実装：実際の実装では、ポートフォリオの日次価値を計算
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 仮の日次リターン（実際の実装では、実際のポートフォリオ価値から計算）
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        cumulative_returns = (1 + returns).cumprod()
        
        return pd.Series(cumulative_returns, index=dates)
    
    def generate_performance_report(self, start_date: datetime, end_date: datetime) -> str:
        """パフォーマンスレポートを生成"""
        summary = self.get_portfolio_summary(end_date)
        metrics = self.calculate_performance_metrics(start_date, end_date)
        
        report = f"""
# 投資実績レポート

## 基本情報
- 期間: {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}
- レポート生成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## ポートフォリオサマリー
- 総市場価値: ¥{summary['total_market_value']:,.0f}
- 総コストベース: ¥{summary['total_cost_basis']:,.0f}
- 未実現損益: ¥{summary['total_unrealized_pnl']:,.0f} ({summary['total_pnl_pct']:.2f}%)
- 実現損益: ¥{summary['total_realized_pnl']:,.0f}
- 総損益: ¥{summary['total_pnl']:,.0f}
- 保有銘柄数: {summary['position_count']}銘柄

## パフォーマンス指標
- 総リターン: {metrics['total_return']:.2f}%
- 年率リターン: {metrics['annualized_return']:.2f}%
- ボラティリティ: {metrics['volatility']:.2f}%
- シャープレシオ: {metrics['sharpe_ratio']:.2f}
- 最大ドローダウン: {metrics['max_drawdown']:.2f}%
- 勝率: {metrics['win_rate']:.2f}%
- プロフィットファクター: {metrics['profit_factor']:.2f}
- 総取引数: {metrics['total_trades']}回

## 銘柄別損益
"""
        
        for position in summary['positions']:
            report += f"""
### {position['symbol']}
- ポジション: {position['position']}株
- 市場価値: ¥{position['market_value']:,.0f}
- コストベース: ¥{position['cost_basis']:,.0f}
- 未実現損益: ¥{position['unrealized_pnl']:,.0f} ({position['unrealized_pnl_pct']:.2f}%)
- 実現損益: ¥{position['realized_pnl']:,.0f}
- 総損益: ¥{position['total_pnl']:,.0f}
- 現在価格: ¥{position['current_price']:,.0f}
- 平均取得価格: ¥{position['average_cost']:,.0f}
"""
        
        return report
    
    def export_trades_to_csv(self, filename: str = None) -> str:
        """取引データをCSVにエクスポート"""
        if filename is None:
            filename = f"trades_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if self.trades:
            df = pd.DataFrame(self.trades)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            return filename
        return None
    
    def import_trades_from_csv(self, filename: str) -> bool:
        """CSVから取引データをインポート"""
        try:
            df = pd.read_csv(filename, encoding='utf-8-sig')
            
            for _, row in df.iterrows():
                trade = {
                    'id': row.get('id', f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    'symbol': row['symbol'],
                    'action': row['action'],
                    'quantity': float(row['quantity']),
                    'price': float(row['price']),
                    'date': pd.to_datetime(row['date']),
                    'commission': float(row.get('commission', 0)),
                    'notes': row.get('notes', ''),
                    'created_at': datetime.now()
                }
                self.trades.append(trade)
            
            self._save_data()
            return True
        except Exception as e:
            print(f"CSVインポートエラー: {e}")
            return False
