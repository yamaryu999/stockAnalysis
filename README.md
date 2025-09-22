# 日本株価分析ツール 📈

[![E2E Playwright](https://github.com/yamaryu999/stockAnalysis/actions/workflows/e2e-playwright.yml/badge.svg)](https://github.com/yamaryu999/stockAnalysis/actions/workflows/e2e-playwright.yml)
[![Unit Tests](https://github.com/yamaryu999/stockAnalysis/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/yamaryu999/stockAnalysis/actions/workflows/unit-tests.yml)
[![Build](https://github.com/yamaryu999/stockAnalysis/actions/workflows/build.yml/badge.svg)](https://github.com/yamaryu999/stockAnalysis/actions/workflows/build.yml)
[![Integration & Slow](https://github.com/yamaryu999/stockAnalysis/actions/workflows/integration-slow.yml/badge.svg)](https://github.com/yamaryu999/stockAnalysis/actions/workflows/integration-slow.yml)

東京証券取引所の全銘柄を分析し、AI推奨機能付きの株価分析ツールです。

## 🚀 機能

### 主要機能
- **全銘柄分析**: 東京証券取引所の最大1000銘柄を並列処理で高速分析
- **AI推奨機能**: 最新ニュース分析による投資戦略の自動提案
- **詳細根拠表示**: 分析結果の根拠を詳細に表示
- **リアルタイム分析**: Yahoo Finance APIを使用した最新データ取得
- **ニュース駆動スコアリング**: 経済ニュースとセンチメントを組み合わせた銘柄ランク付け

### 分析指標
- **PER (株価収益率)**: 企業の収益性評価
- **PBR (株価純資産倍率)**: 企業の資産価値評価
- **ROE (自己資本利益率)**: 企業の収益効率評価
- **配当利回り**: 配当収益の評価
- **負債比率**: 企業の財務健全性評価

### 投資戦略
- **バリュー投資**: 割安株の発見
- **グロース投資**: 成長株の特定
- **配当投資**: 安定配当株の選別
- **バランス型**: リスク分散投資
- **ディフェンシブ**: 保守的投資
- **アグレッシブ**: 積極的投資
- **ニュースモメンタム**: 最新のニュースセンチメントと話題性で短期注目銘柄を抽出

## 🛠️ 技術スタック

- **Python 3.12+**
- **Streamlit**: Webアプリケーションフレームワーク
- **yfinance**: 株価データ取得
- **Pandas/NumPy**: データ分析
- **Plotly**: データ可視化
- **BeautifulSoup4**: ニュース取得
- **Concurrent.futures**: 並列処理

## 📦 インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/yamaryu999/stockAnalysis.git
cd stockAnalysis
```

### 2. 仮想環境の作成とアクティベート
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. アプリケーションの起動
```bash
# 自動起動スクリプトを使用
./run.sh

# または手動で起動
streamlit run app.py
```

## 🎯 使用方法

### 1. 基本分析
1. ブラウザで `http://localhost:8501` にアクセス
2. 「分析実行」ボタンをクリック

### 2. AI推奨機能
1. 投資戦略を「AI自動提案」に設定
2. 「🔍 最新市場分析を実行」ボタンをクリック
3. AI推奨条件が自動適用されます
4. 「🔍 分析根拠を表示」で詳細根拠を確認

### 3. 分析結果の確認
- **銘柄一覧**: 条件に合致する銘柄のリスト
- **財務指標グラフ**: 各指標の分布と上位銘柄
- **セクター別分析**: 業種別の分析結果
- **詳細根拠**: AI分析の詳細な根拠データ

### 4. ニュース駆動インサイト
1. ナビゲーションから `📰 ニュース分析` を選択（または `?page=news` を付けて直接アクセス）
2. 何も入力しない場合は最新ニュースから自動的に注目銘柄を抽出（任意で銘柄コードを指定可能）
3. 「ニューススコアを生成」を押せばセンチメント・ニュース勢い・ファンダメンタル傾向を統合したランキングが表示されます
4. 上位候補としてニューススコアと株価モメンタムを統合した「上昇ポテンシャル候補」が表示され、イベントタグ（決算/規制/M&A など）と主要ヘッドラインを確認可能

## 📊 分析対象市場

- **プライム市場**: 大型株中心
- **スタンダード市場**: 中堅企業
- **グロース市場**: 成長企業
- **投資信託**: 1300番台

## ⚡ パフォーマンス

- **並列処理**: 最大3スレッドで高速データ取得
- **バッチ処理**: 50銘柄ずつ効率的に処理
- **レート制限対応**: Yahoo Finance APIの制限を考慮
- **メモリ最適化**: 最大1000銘柄でメモリ使用量を制限

## 🔍 AI分析機能

### ニュース分析
- **センチメント分析**: ポジティブ/ネガティブ/ニュートラル
- **キーワード検出**: 市場に影響するキーワードの特定
- **セクター分析**: 業種別の言及回数分析
- **信頼度評価**: 分析結果の信頼性を数値化

### 推奨戦略
- **市場状況に応じた戦略選択**
- **リスクレベルに応じた条件設定**
- **セクター別推奨銘柄の提案**

## 📈 可視化機能

- **財務指標の分布グラフ**
- **ROE上位銘柄の棒グラフ**
- **セクター別言及回数グラフ**
- **インタラクティブなチャート表示**

## 🛡️ エラーハンドリング

- **レート制限対応**: API制限を適切に処理
- **データ取得エラー**: 個別銘柄のエラーを適切に処理
- **フォールバック機能**: エラー時の代替データ提供

## 🧪 PlaywrightによるE2Eテスト

1. 依存関係をインストール
   ```bash
   pip install -r requirements.txt
   ```
2. Playwrightのブラウザバイナリを準備
   ```bash
   python -m playwright install --with-deps
   ```
3. 別ターミナルでStreamlitアプリを起動
   ```bash
   streamlit run app.py
   ```
4. テストを実行（デフォルトURLは `http://localhost:8501`）
   ```bash
   pytest -m playwright --app-url http://localhost:8501
   ```

CLIオプション `--app-url` または環境変数 `APP_URL` を使って検証対象のエンドポイントを切り替えられます。

### CI でのテスト構成
- Build: 依存関係インストールとバイトコードコンパイル
- Unit Tests: `not playwright and not e2e and not integration and not slow`
- E2E Playwright: アプリ起動後にUIのスモークを実行（トレース保存）
- Integration & Slow（夜間/手動）:
  - 既定では WebSocket サーバーのみ起動（`START_WEBSOCKET=true`）
  - 必要に応じて環境変数で制御:
    - `START_STREAMLIT=true`（Streamlit を同時起動しHTTPヘルスチェック）
    - `START_MCP=true`（MCP Browser Server を起動）
    - `START_NEWS_MOCK=true`（ニュースAPIモックを起動し `NEWS_MOCK_URL` を注入）

### ニュースAPIモックをローカルで起動
```bash
python tests/mocks/news_mock_server.py 9100 &
export NEWS_MOCK_URL=http://localhost:9100
```
NewsAnalyzer は `NEWS_MOCK_URL` が設定されている場合、外部サイトの代わりにモックの `/news` を利用します。

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

## 📞 サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。

---

**注意**: このツールは投資アドバイスではありません。投資判断は自己責任で行ってください。
