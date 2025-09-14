import pandas as pd
import numpy as np
import json
import io
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st

class ExportManager:
    """
    データエクスポート管理機能
    
    分析結果を様々な形式でエクスポートします。
    """
    
    def __init__(self):
        self.supported_formats = ['csv', 'excel', 'json', 'txt']
    
    def export_dataframe(self, df: pd.DataFrame, format_type: str, filename: str = None) -> bytes:
        """
        DataFrameを指定形式でエクスポート
        
        Args:
            df: エクスポートするDataFrame
            format_type: エクスポート形式 ('csv', 'excel', 'json', 'txt')
            filename: ファイル名（オプション）
            
        Returns:
            エクスポートされたデータのバイト列
        """
        if df is None or df.empty:
            raise ValueError("エクスポートするデータがありません")
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"export_{timestamp}"
        
        if format_type == 'csv':
            return self._export_to_csv(df, filename)
        elif format_type == 'excel':
            return self._export_to_excel(df, filename)
        elif format_type == 'json':
            return self._export_to_json(df, filename)
        elif format_type == 'txt':
            return self._export_to_txt(df, filename)
        else:
            raise ValueError(f"サポートされていない形式: {format_type}")
    
    def _export_to_csv(self, df: pd.DataFrame, filename: str) -> bytes:
        """CSV形式でエクスポート"""
        output = io.StringIO()
        df.to_csv(output, index=True, encoding='utf-8-sig')
        return output.getvalue().encode('utf-8-sig')
    
    def _export_to_excel(self, df: pd.DataFrame, filename: str) -> bytes:
        """Excel形式でエクスポート"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=True)
            
            # ワークシートの書式設定
            worksheet = writer.sheets['Data']
            
            # 列幅の自動調整
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()
    
    def _export_to_json(self, df: pd.DataFrame, filename: str) -> bytes:
        """JSON形式でエクスポート"""
        # DataFrameを辞書に変換
        data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_records': len(df),
                'columns': list(df.columns)
            },
            'data': df.to_dict('records')
        }
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        return json_str.encode('utf-8')
    
    def _export_to_txt(self, df: pd.DataFrame, filename: str) -> bytes:
        """テキスト形式でエクスポート"""
        output = io.StringIO()
        
        # ヘッダー情報
        output.write(f"データエクスポート\n")
        output.write(f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        output.write(f"総レコード数: {len(df)}\n")
        output.write(f"列数: {len(df.columns)}\n")
        output.write("=" * 50 + "\n\n")
        
        # データをテキスト形式で出力
        output.write(df.to_string(index=True))
        
        return output.getvalue().encode('utf-8')
    
    def export_analysis_results(self, results: Dict, format_type: str, filename: str = None) -> bytes:
        """
        分析結果をエクスポート
        
        Args:
            results: 分析結果の辞書
            format_type: エクスポート形式
            filename: ファイル名
            
        Returns:
            エクスポートされたデータのバイト列
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_results_{timestamp}"
        
        if format_type == 'json':
            return self._export_analysis_to_json(results, filename)
        elif format_type == 'txt':
            return self._export_analysis_to_txt(results, filename)
        else:
            # 分析結果をDataFrameに変換してからエクスポート
            df = self._convert_results_to_dataframe(results)
            return self.export_dataframe(df, format_type, filename)
    
    def _export_analysis_to_json(self, results: Dict, filename: str) -> bytes:
        """分析結果をJSON形式でエクスポート"""
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'analysis_type': results.get('type', 'unknown'),
                'total_stocks': len(results.get('stocks', [])),
                'summary': results.get('summary', {})
            },
            'results': results
        }
        
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
        return json_str.encode('utf-8')
    
    def _export_analysis_to_txt(self, results: Dict, filename: str) -> bytes:
        """分析結果をテキスト形式でエクスポート"""
        output = io.StringIO()
        
        # ヘッダー情報
        output.write(f"分析結果エクスポート\n")
        output.write(f"エクスポート日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        output.write(f"分析タイプ: {results.get('type', 'unknown')}\n")
        output.write("=" * 50 + "\n\n")
        
        # サマリー情報
        if 'summary' in results:
            output.write("【サマリー】\n")
            for key, value in results['summary'].items():
                output.write(f"{key}: {value}\n")
            output.write("\n")
        
        # 詳細結果
        if 'stocks' in results:
            output.write("【詳細結果】\n")
            for i, stock in enumerate(results['stocks'], 1):
                output.write(f"{i}. {stock.get('name', 'Unknown')} ({stock.get('symbol', 'N/A')})\n")
                for key, value in stock.items():
                    if key not in ['name', 'symbol']:
                        output.write(f"   {key}: {value}\n")
                output.write("\n")
        
        return output.getvalue().encode('utf-8')
    
    def _convert_results_to_dataframe(self, results: Dict) -> pd.DataFrame:
        """分析結果をDataFrameに変換"""
        if 'stocks' in results:
            return pd.DataFrame(results['stocks'])
        else:
            # 結果が辞書形式の場合、フラット化
            flattened_data = []
            for key, value in results.items():
                if isinstance(value, dict):
                    row = {'key': key}
                    row.update(value)
                    flattened_data.append(row)
                else:
                    flattened_data.append({'key': key, 'value': value})
            return pd.DataFrame(flattened_data)
    
    def export_portfolio_data(self, portfolio_data: Dict, format_type: str, filename: str = None) -> bytes:
        """
        ポートフォリオデータをエクスポート
        
        Args:
            portfolio_data: ポートフォリオデータ
            format_type: エクスポート形式
            filename: ファイル名
            
        Returns:
            エクスポートされたデータのバイト列
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"portfolio_{timestamp}"
        
        # ポートフォリオデータをDataFrameに変換
        if 'positions' in portfolio_data:
            df = pd.DataFrame(portfolio_data['positions'])
        else:
            df = pd.DataFrame([portfolio_data])
        
        return self.export_dataframe(df, format_type, filename)
    
    def export_backtest_results(self, backtest_results: List[Dict], format_type: str, filename: str = None) -> bytes:
        """
        バックテスト結果をエクスポート
        
        Args:
            backtest_results: バックテスト結果のリスト
            format_type: エクスポート形式
            filename: ファイル名
            
        Returns:
            エクスポートされたデータのバイト列
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_results_{timestamp}"
        
        # バックテスト結果をDataFrameに変換
        results_data = []
        for result in backtest_results:
            row = {
                'symbol': result.get('symbol', ''),
                'strategy': result.get('strategy', ''),
                'start_date': result.get('start_date', ''),
                'end_date': result.get('end_date', ''),
            }
            
            # パフォーマンス指標を追加
            if 'performance' in result:
                perf = result['performance']
                row.update({
                    'total_return': perf.get('total_return', 0),
                    'annualized_return': perf.get('annualized_return', 0),
                    'volatility': perf.get('volatility', 0),
                    'sharpe_ratio': perf.get('sharpe_ratio', 0),
                    'max_drawdown': perf.get('max_drawdown', 0),
                    'win_rate': perf.get('win_rate', 0),
                    'profit_factor': perf.get('profit_factor', 0),
                    'total_trades': perf.get('total_trades', 0),
                    'final_value': perf.get('final_value', 0)
                })
            
            results_data.append(row)
        
        df = pd.DataFrame(results_data)
        return self.export_dataframe(df, format_type, filename)
    
    def create_export_ui(self, data: Any, data_type: str, filename_prefix: str = None) -> None:
        """
        エクスポートUIを作成
        
        Args:
            data: エクスポートするデータ
            data_type: データタイプ（'dataframe', 'analysis', 'portfolio', 'backtest'）
            filename_prefix: ファイル名のプレフィックス
        """
        st.subheader("📤 データエクスポート")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "エクスポート形式",
                self.supported_formats,
                format_func=lambda x: {
                    'csv': '📊 CSV',
                    'excel': '📈 Excel',
                    'json': '🔧 JSON',
                    'txt': '📄 テキスト'
                }[x]
            )
        
        with col2:
            if filename_prefix is None:
                filename_prefix = data_type
            
            custom_filename = st.text_input(
                "ファイル名（オプション）",
                value=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                help="ファイル名をカスタマイズできます"
            )
        
        if st.button("📥 エクスポート", type="primary"):
            try:
                with st.spinner("エクスポート中..."):
                    if data_type == 'dataframe':
                        export_data = self.export_dataframe(data, export_format, custom_filename)
                    elif data_type == 'analysis':
                        export_data = self.export_analysis_results(data, export_format, custom_filename)
                    elif data_type == 'portfolio':
                        export_data = self.export_portfolio_data(data, export_format, custom_filename)
                    elif data_type == 'backtest':
                        export_data = self.export_backtest_results(data, export_format, custom_filename)
                    else:
                        st.error("サポートされていないデータタイプです")
                        return
                    
                    # ファイル拡張子を追加
                    if not custom_filename.endswith(f'.{export_format}'):
                        custom_filename += f'.{export_format}'
                    
                    # ダウンロードボタンを表示
                    st.download_button(
                        label=f"📥 {custom_filename} をダウンロード",
                        data=export_data,
                        file_name=custom_filename,
                        mime=self._get_mime_type(export_format)
                    )
                    
                    st.success(f"✅ {export_format.upper()}形式でエクスポート準備完了！")
                    
            except Exception as e:
                st.error(f"エクスポート中にエラーが発生しました: {str(e)}")
    
    def _get_mime_type(self, format_type: str) -> str:
        """MIMEタイプを取得"""
        mime_types = {
            'csv': 'text/csv',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json',
            'txt': 'text/plain'
        }
        return mime_types.get(format_type, 'application/octet-stream')
    
    def export_multiple_datasets(self, datasets: Dict[str, Any], format_type: str, filename_prefix: str = None) -> bytes:
        """
        複数のデータセットを一つのファイルにエクスポート
        
        Args:
            datasets: データセットの辞書
            format_type: エクスポート形式
            filename_prefix: ファイル名のプレフィックス
            
        Returns:
            エクスポートされたデータのバイト列
        """
        if format_type == 'excel':
            return self._export_multiple_to_excel(datasets, filename_prefix)
        elif format_type == 'json':
            return self._export_multiple_to_json(datasets, filename_prefix)
        else:
            raise ValueError(f"複数データセットのエクスポートは {format_type} 形式ではサポートされていません")
    
    def _export_multiple_to_excel(self, datasets: Dict[str, Any], filename_prefix: str) -> bytes:
        """複数のデータセットをExcel形式でエクスポート"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, data in datasets.items():
                if isinstance(data, pd.DataFrame):
                    data.to_excel(writer, sheet_name=sheet_name, index=True)
                else:
                    # データをDataFrameに変換
                    df = self._convert_results_to_dataframe(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=True)
        
        output.seek(0)
        return output.getvalue()
    
    def _export_multiple_to_json(self, datasets: Dict[str, Any], filename_prefix: str) -> bytes:
        """複数のデータセットをJSON形式でエクスポート"""
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'total_datasets': len(datasets),
                'dataset_names': list(datasets.keys())
            },
            'datasets': {}
        }
        
        for name, data in datasets.items():
            if isinstance(data, pd.DataFrame):
                export_data['datasets'][name] = data.to_dict('records')
            else:
                export_data['datasets'][name] = data
        
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2, default=str)
        return json_str.encode('utf-8')
