"""
データエクスポートシステム
分析結果・データの多様な形式でのエクスポート機能
"""

import pandas as pd
import numpy as np
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging
from dataclasses import dataclass, asdict
import os
from pathlib import Path
import zipfile
import io
import base64
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

@dataclass
class ExportConfig:
    """エクスポート設定クラス"""
    format: str  # 'csv', 'excel', 'json', 'sqlite', 'xml'
    filename: str
    include_charts: bool = False
    include_metadata: bool = True
    compression: Optional[str] = None  # 'zip', 'gzip'
    encoding: str = 'utf-8'
    delimiter: str = ','
    date_format: str = '%Y-%m-%d %H:%M:%S'

class DataExporter:
    """データエクスポータークラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.export_history = []
    
    def export_stock_data(self, symbols: List[str], config: ExportConfig, 
                        period: str = "1y") -> str:
        """株価データをエクスポート"""
        try:
            # データを取得
            all_data = {}
            metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'symbols': symbols,
                'period': period,
                'total_symbols': len(symbols)
            }
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period)
                    info = ticker.info
                    
                    if not data.empty:
                        all_data[symbol] = {
                            'price_data': data,
                            'info': info,
                            'metadata': {
                                'symbol': symbol,
                                'data_points': len(data),
                                'date_range': f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}"
                            }
                        }
                        
                except Exception as e:
                    self.logger.error(f"データ取得エラー {symbol}: {e}")
                    continue
            
            # エクスポート実行
            if config.format == 'csv':
                return self._export_to_csv(all_data, config, metadata)
            elif config.format == 'excel':
                return self._export_to_excel(all_data, config, metadata)
            elif config.format == 'json':
                return self._export_to_json(all_data, config, metadata)
            elif config.format == 'sqlite':
                return self._export_to_sqlite(all_data, config, metadata)
            elif config.format == 'xml':
                return self._export_to_xml(all_data, config, metadata)
            else:
                raise ValueError(f"未対応のフォーマット: {config.format}")
                
        except Exception as e:
            self.logger.error(f"株価データエクスポートエラー: {e}")
            return f"エクスポートエラー: {e}"
    
    def export_analysis_results(self, analysis_data: Dict[str, Any], 
                               config: ExportConfig) -> str:
        """分析結果をエクスポート"""
        try:
            metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'analysis_type': analysis_data.get('type', 'unknown'),
                'symbols_analyzed': analysis_data.get('symbols', []),
                'total_results': len(analysis_data.get('results', {}))
            }
            
            if config.format == 'csv':
                return self._export_analysis_to_csv(analysis_data, config, metadata)
            elif config.format == 'excel':
                return self._export_analysis_to_excel(analysis_data, config, metadata)
            elif config.format == 'json':
                return self._export_analysis_to_json(analysis_data, config, metadata)
            else:
                raise ValueError(f"未対応のフォーマット: {config.format}")
                
        except Exception as e:
            self.logger.error(f"分析結果エクスポートエラー: {e}")
            return f"エクスポートエラー: {e}"
    
    def export_portfolio_data(self, portfolio_data: Dict[str, Any], 
                             config: ExportConfig) -> str:
        """ポートフォリオデータをエクスポート"""
        try:
            metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'portfolio_name': portfolio_data.get('name', 'Unknown'),
                'total_value': portfolio_data.get('total_value', 0),
                'positions_count': len(portfolio_data.get('positions', []))
            }
            
            if config.format == 'csv':
                return self._export_portfolio_to_csv(portfolio_data, config, metadata)
            elif config.format == 'excel':
                return self._export_portfolio_to_excel(portfolio_data, config, metadata)
            elif config.format == 'json':
                return self._export_portfolio_to_json(portfolio_data, config, metadata)
            else:
                raise ValueError(f"未対応のフォーマット: {config.format}")
                
        except Exception as e:
            self.logger.error(f"ポートフォリオエクスポートエラー: {e}")
            return f"エクスポートエラー: {e}"
    
    def _export_to_csv(self, data: Dict[str, Any], config: ExportConfig, 
                      metadata: Dict[str, Any]) -> str:
        """CSV形式でエクスポート"""
        try:
            filename = f"{config.filename}.csv"
            
            # 全データを統合
            all_rows = []
            
            for symbol, symbol_data in data.items():
                price_data = symbol_data['price_data']
                info = symbol_data['info']
                symbol_metadata = symbol_data['metadata']
                
                for date, row in price_data.iterrows():
                    all_rows.append({
                        'symbol': symbol,
                        'date': date.strftime(config.date_format),
                        'open': row['Open'],
                        'high': row['High'],
                        'low': row['Low'],
                        'close': row['Close'],
                        'volume': row['Volume'],
                        'company_name': info.get('longName', ''),
                        'sector': info.get('sector', ''),
                        'industry': info.get('industry', ''),
                        'market_cap': info.get('marketCap', ''),
                        'pe_ratio': info.get('trailingPE', ''),
                        'dividend_yield': info.get('dividendYield', '')
                    })
            
            # CSVファイルに書き込み
            df = pd.DataFrame(all_rows)
            df.to_csv(filename, index=False, encoding=config.encoding)
            
            # メタデータファイル
            if config.include_metadata:
                metadata_filename = f"{config.filename}_metadata.json"
                with open(metadata_filename, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self._add_to_history(filename, config.format, len(all_rows))
            return f"CSVファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"CSVエクスポートエラー: {e}")
            return f"CSVエクスポートエラー: {e}"
    
    def _export_to_excel(self, data: Dict[str, Any], config: ExportConfig, 
                        metadata: Dict[str, Any]) -> str:
        """Excel形式でエクスポート"""
        try:
            filename = f"{config.filename}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 各銘柄のデータをシートに分けて保存
                for symbol, symbol_data in data.items():
                    price_data = symbol_data['price_data']
                    info = symbol_data['info']
                    
                    # 価格データ
                    price_data.to_excel(writer, sheet_name=f"{symbol}_price")
                    
                    # 基本情報
                    info_df = pd.DataFrame([info])
                    info_df.to_excel(writer, sheet_name=f"{symbol}_info", index=False)
                
                # サマリーシート
                summary_data = []
                for symbol, symbol_data in data.items():
                    price_data = symbol_data['price_data']
                    info = symbol_data['info']
                    
                    summary_data.append({
                        'Symbol': symbol,
                        'Company': info.get('longName', ''),
                        'Sector': info.get('sector', ''),
                        'Industry': info.get('industry', ''),
                        'Current Price': price_data['Close'].iloc[-1] if not price_data.empty else 0,
                        'Market Cap': info.get('marketCap', ''),
                        'PE Ratio': info.get('trailingPE', ''),
                        'Data Points': len(price_data)
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # メタデータシート
                if config.include_metadata:
                    metadata_df = pd.DataFrame([metadata])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            self._add_to_history(filename, config.format, len(data))
            return f"Excelファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"Excelエクスポートエラー: {e}")
            return f"Excelエクスポートエラー: {e}"
    
    def _export_to_json(self, data: Dict[str, Any], config: ExportConfig, 
                       metadata: Dict[str, Any]) -> str:
        """JSON形式でエクスポート"""
        try:
            filename = f"{config.filename}.json"
            
            export_data = {
                'metadata': metadata,
                'data': {}
            }
            
            for symbol, symbol_data in data.items():
                price_data = symbol_data['price_data']
                info = symbol_data['info']
                
                # データをJSONシリアライズ可能な形式に変換
                price_records = []
                for date, row in price_data.iterrows():
                    price_records.append({
                        'date': date.strftime(config.date_format),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    })
                
                export_data['data'][symbol] = {
                    'price_data': price_records,
                    'company_info': info,
                    'metadata': symbol_data['metadata']
                }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self._add_to_history(filename, config.format, len(data))
            return f"JSONファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"JSONエクスポートエラー: {e}")
            return f"JSONエクスポートエラー: {e}"
    
    def _export_to_sqlite(self, data: Dict[str, Any], config: ExportConfig, 
                         metadata: Dict[str, Any]) -> str:
        """SQLite形式でエクスポート"""
        try:
            filename = f"{config.filename}.db"
            
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            
            # テーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    company_name TEXT,
                    sector TEXT,
                    industry TEXT,
                    market_cap INTEGER,
                    pe_ratio REAL,
                    dividend_yield REAL
                )
            """)
            
            # データ挿入
            for symbol, symbol_data in data.items():
                price_data = symbol_data['price_data']
                info = symbol_data['info']
                
                for date, row in price_data.iterrows():
                    cursor.execute("""
                        INSERT INTO stock_data 
                        (symbol, date, open, high, low, close, volume, 
                         company_name, sector, industry, market_cap, pe_ratio, dividend_yield)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        date.strftime(config.date_format),
                        row['Open'],
                        row['High'],
                        row['Low'],
                        row['Close'],
                        row['Volume'],
                        info.get('longName', ''),
                        info.get('sector', ''),
                        info.get('industry', ''),
                        info.get('marketCap', ''),
                        info.get('trailingPE', ''),
                        info.get('dividendYield', '')
                    ))
            
            # メタデータテーブル
            if config.include_metadata:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS export_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        export_timestamp TEXT,
                        symbols TEXT,
                        period TEXT,
                        total_symbols INTEGER
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO export_metadata 
                    (export_timestamp, symbols, period, total_symbols)
                    VALUES (?, ?, ?, ?)
                """, (
                    metadata['export_timestamp'],
                    json.dumps(metadata['symbols']),
                    metadata['period'],
                    metadata['total_symbols']
                ))
            
            conn.commit()
            conn.close()
            
            self._add_to_history(filename, config.format, len(data))
            return f"SQLiteデータベースを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"SQLiteエクスポートエラー: {e}")
            return f"SQLiteエクスポートエラー: {e}"
    
    def _export_to_xml(self, data: Dict[str, Any], config: ExportConfig, 
                      metadata: Dict[str, Any]) -> str:
        """XML形式でエクスポート"""
        try:
            filename = f"{config.filename}.xml"
            
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += '<stock_data>\n'
            
            # メタデータ
            if config.include_metadata:
                xml_content += '  <metadata>\n'
                for key, value in metadata.items():
                    xml_content += f'    <{key}>{value}</{key}>\n'
                xml_content += '  </metadata>\n'
            
            # データ
            xml_content += '  <data>\n'
            
            for symbol, symbol_data in data.items():
                price_data = symbol_data['price_data']
                info = symbol_data['info']
                
                xml_content += f'    <symbol name="{symbol}">\n'
                xml_content += f'      <company_name>{info.get("longName", "")}</company_name>\n'
                xml_content += f'      <sector>{info.get("sector", "")}</sector>\n'
                xml_content += f'      <industry>{info.get("industry", "")}</industry>\n'
                
                xml_content += '      <price_history>\n'
                for date, row in price_data.iterrows():
                    xml_content += f'        <record date="{date.strftime(config.date_format)}">\n'
                    xml_content += f'          <open>{row["Open"]}</open>\n'
                    xml_content += f'          <high>{row["High"]}</high>\n'
                    xml_content += f'          <low>{row["Low"]}</low>\n'
                    xml_content += f'          <close>{row["Close"]}</close>\n'
                    xml_content += f'          <volume>{row["Volume"]}</volume>\n'
                    xml_content += '        </record>\n'
                xml_content += '      </price_history>\n'
                xml_content += '    </symbol>\n'
            
            xml_content += '  </data>\n'
            xml_content += '</stock_data>\n'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            self._add_to_history(filename, config.format, len(data))
            return f"XMLファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"XMLエクスポートエラー: {e}")
            return f"XMLエクスポートエラー: {e}"
    
    def _export_analysis_to_csv(self, analysis_data: Dict[str, Any], 
                               config: ExportConfig, metadata: Dict[str, Any]) -> str:
        """分析結果をCSV形式でエクスポート"""
        try:
            filename = f"{config.filename}.csv"
            
            # 分析結果をフラット化
            rows = []
            results = analysis_data.get('results', {})
            
            for symbol, result in results.items():
                if isinstance(result, dict):
                    row = {'symbol': symbol}
                    row.update(result)
                    rows.append(row)
                else:
                    rows.append({'symbol': symbol, 'result': str(result)})
            
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False, encoding=config.encoding)
            
            self._add_to_history(filename, config.format, len(rows))
            return f"分析結果CSVファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"分析結果CSVエクスポートエラー: {e}")
            return f"分析結果CSVエクスポートエラー: {e}"
    
    def _export_analysis_to_excel(self, analysis_data: Dict[str, Any], 
                                config: ExportConfig, metadata: Dict[str, Any]) -> str:
        """分析結果をExcel形式でエクスポート"""
        try:
            filename = f"{config.filename}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 分析結果シート
                results = analysis_data.get('results', {})
                if results:
                    results_df = pd.DataFrame(results).T
                    results_df.to_excel(writer, sheet_name='Analysis Results')
                
                # メタデータシート
                if config.include_metadata:
                    metadata_df = pd.DataFrame([metadata])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            self._add_to_history(filename, config.format, len(results))
            return f"分析結果Excelファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"分析結果Excelエクスポートエラー: {e}")
            return f"分析結果Excelエクスポートエラー: {e}"
    
    def _export_analysis_to_json(self, analysis_data: Dict[str, Any], 
                                config: ExportConfig, metadata: Dict[str, Any]) -> str:
        """分析結果をJSON形式でエクスポート"""
        try:
            filename = f"{config.filename}.json"
            
            export_data = {
                'metadata': metadata,
                'analysis_data': analysis_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self._add_to_history(filename, config.format, len(analysis_data.get('results', {})))
            return f"分析結果JSONファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"分析結果JSONエクスポートエラー: {e}")
            return f"分析結果JSONエクスポートエラー: {e}"
    
    def _export_portfolio_to_csv(self, portfolio_data: Dict[str, Any], 
                                config: ExportConfig, metadata: Dict[str, Any]) -> str:
        """ポートフォリオデータをCSV形式でエクスポート"""
        try:
            filename = f"{config.filename}.csv"
            
            positions = portfolio_data.get('positions', [])
            rows = []
            
            for position in positions:
                row = {
                    'symbol': position.get('symbol', ''),
                    'quantity': position.get('quantity', 0),
                    'average_price': position.get('average_price', 0),
                    'current_price': position.get('current_price', 0),
                    'market_value': position.get('market_value', 0),
                    'unrealized_pnl': position.get('unrealized_pnl', 0),
                    'unrealized_pnl_percent': position.get('unrealized_pnl_percent', 0),
                    'weight': position.get('weight', 0)
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False, encoding=config.encoding)
            
            self._add_to_history(filename, config.format, len(rows))
            return f"ポートフォリオCSVファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"ポートフォリオCSVエクスポートエラー: {e}")
            return f"ポートフォリオCSVエクスポートエラー: {e}"
    
    def _export_portfolio_to_excel(self, portfolio_data: Dict[str, Any], 
                                 config: ExportConfig, metadata: Dict[str, Any]) -> str:
        """ポートフォリオデータをExcel形式でエクスポート"""
        try:
            filename = f"{config.filename}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # ポジションシート
                positions = portfolio_data.get('positions', [])
                if positions:
                    positions_df = pd.DataFrame(positions)
                    positions_df.to_excel(writer, sheet_name='Positions', index=False)
                
                # サマリーシート
                summary_data = {
                    'Total Value': [portfolio_data.get('total_value', 0)],
                    'Total Cost': [portfolio_data.get('total_cost', 0)],
                    'Total PnL': [portfolio_data.get('total_pnl', 0)],
                    'Total PnL %': [portfolio_data.get('total_pnl_percent', 0)],
                    'Positions Count': [len(positions)]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # メタデータシート
                if config.include_metadata:
                    metadata_df = pd.DataFrame([metadata])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            self._add_to_history(filename, config.format, len(positions))
            return f"ポートフォリオExcelファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"ポートフォリオExcelエクスポートエラー: {e}")
            return f"ポートフォリオExcelエクスポートエラー: {e}"
    
    def _export_portfolio_to_json(self, portfolio_data: Dict[str, Any], 
                                 config: ExportConfig, metadata: Dict[str, Any]) -> str:
        """ポートフォリオデータをJSON形式でエクスポート"""
        try:
            filename = f"{config.filename}.json"
            
            export_data = {
                'metadata': metadata,
                'portfolio_data': portfolio_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self._add_to_history(filename, config.format, len(portfolio_data.get('positions', [])))
            return f"ポートフォリオJSONファイルを保存しました: {filename}"
            
        except Exception as e:
            self.logger.error(f"ポートフォリオJSONエクスポートエラー: {e}")
            return f"ポートフォリオJSONエクスポートエラー: {e}"
    
    def create_export_package(self, files: List[str], package_name: str) -> str:
        """複数ファイルをパッケージ化"""
        try:
            package_filename = f"{package_name}.zip"
            
            with zipfile.ZipFile(package_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            return f"エクスポートパッケージを作成しました: {package_filename}"
            
        except Exception as e:
            self.logger.error(f"パッケージ作成エラー: {e}")
            return f"パッケージ作成エラー: {e}"
    
    def _add_to_history(self, filename: str, format: str, record_count: int):
        """エクスポート履歴に追加"""
        self.export_history.append({
            'filename': filename,
            'format': format,
            'record_count': record_count,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """エクスポート履歴を取得"""
        return self.export_history
    
    def clear_export_history(self):
        """エクスポート履歴をクリア"""
        self.export_history = []

class DataImportManager:
    """データインポート管理クラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def import_csv(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """CSVファイルをインポート"""
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            self.logger.info(f"CSVファイルをインポート: {file_path} ({len(df)}行)")
            return df
            
        except Exception as e:
            self.logger.error(f"CSVインポートエラー: {e}")
            raise
    
    def import_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Excelファイルをインポート"""
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            self.logger.info(f"Excelファイルをインポート: {file_path} ({len(df)}行)")
            return df
            
        except Exception as e:
            self.logger.error(f"Excelインポートエラー: {e}")
            raise
    
    def import_json(self, file_path: str) -> Dict[str, Any]:
        """JSONファイルをインポート"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"JSONファイルをインポート: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"JSONインポートエラー: {e}")
            raise

# グローバルインスタンス
data_exporter = DataExporter()
data_import_manager = DataImportManager()