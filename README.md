# 数学問題類題作成ツール（シンプル版）

中学数学の問題例を参考にして、類題を自動生成するAIツールです。問題検索機能を削除し、類題生成機能のみに特化したシンプルなバージョンです。改良版の料金計算機能付きで、リアルタイムでAPI使用料金を日本円で表示します。

## 🚀 主な機能

- **類題自動生成**: 既存問題を参考にした類題の自動生成
- **リアルタイム料金計算**: OpenAI APIの使用料金を日本円で表示
- **セッション統計**: 使用量と料金の詳細な統計管理
- **複数難易度対応**: 初級・中級・上級の難易度調整
- **対話モード**: インタラクティブな操作

## 📁 プロジェクト構成

```
math/
├── run_simple_tool.py           # シンプル版メイン実行ファイル
├── simple_math_generator.py     # シンプル版数学問題生成器
├── enhanced_cost_calculator.py  # 改良版料金計算器
├── test_enhanced_cost.py        # テストファイル
├── program_example.py           # プログラム使用例
├── README.md                    # このファイル
└── env/                         # Python仮想環境
```

**注意**: シンプル版では`math_problems`フォルダに問題を入れる必要はありません。ユーザーが直接問題文を入力して類題を生成します。

## 🛠️ セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install openai langchain-openai tiktoken requests python-dotenv
```

### 2. APIキーの設定

`.env`ファイルを作成してOpenAI APIキーを設定：

```bash
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
```

### 3. 環境のアクティベート

```bash
source env/bin/activate
```

## 🎯 使用方法

### 基本的な使用（デモモード）

```bash
python run_simple_tool.py
```

**デモモードの特徴:**
- 事前に設定された問題例で類題を自動生成
- 複数の例題（一次方程式、三角形の面積、一次関数）を表示
- 複数難易度での生成例も表示
- セッション統計を表示

### 対話モードでの使用

```bash
python run_simple_tool.py
# 対話モードを選択 (y)
# 1. 類題生成 を選択
# 問題文を入力（例: "x + 5 = 12 を解きなさい"）
# 難易度を選択（初級/中級/上級）
```

**対話モードの特徴:**
- ユーザーが自由に問題文を入力可能
- 難易度を選択して類題を生成
- リアルタイムで料金を表示
- シンプルなメニュー（類題生成・終了のみ）

### プログラムでの使用

```python
from simple_math_generator import SimpleMathProblemGenerator
from dotenv import load_dotenv
import os

# APIキーの設定
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 生成器の初期化
generator = SimpleMathProblemGenerator(api_key)

# 類題の生成
result = generator.generate_similar_problem("x + 5 = 12 を解きなさい", "中級")
print(result["generated_content"])

# 複数難易度での生成
results = generator.generate_multiple_problems("x + 3 = 8 を解きなさい", ["初級", "中級", "上級"])

# 料金の確認
generator.print_session_summary()
```

## 💰 料金例（2024年12月時点）

- **GPT-4o-mini**: 1回の類題生成で約¥0.02
- **月間使用量**: 1日10回使用で約¥6.00/月

## 🔧 機能詳細

### リアルタイム料金追跡
- LangChainのcallbackを活用した自動料金計算
- 日本円での料金表示（為替レート自動取得）
- シンプルなセッション統計（総使用量のみ）

### 類題生成
- 既存問題の解法パターンを分析
- 数値の適切な変更
- 難易度の調整（初級・中級・上級）
- 問題文、解答、解説、使用概念の4要素で構成

### 対話モード
- インタラクティブな操作
- 類題生成機能のみ
- シンプルなメニュー（類題生成・終了）

## 📊 テスト

```bash
python test_enhanced_cost.py
```

## 🎓 教育現場での活用

- **宿題問題の類題作成**: 同じ解法パターンの問題を自動生成
- **テスト問題のバリエーション**: 難易度を調整した類題作成
- **復習用問題の自動生成**: 大量の問題を効率的に作成
- **コスト管理**: 使用量をリアルタイムで監視

## ⚠️ 注意事項

- OpenAI APIキーが必要です
- インターネット接続が必要です（為替レート取得のため）
- **問題ファイルの準備は不要**: ユーザーが直接問題文を入力します
- 初回実行時は為替レート取得に数秒かかります

## 🔄 更新履歴

- v3.0: 問題検索機能を削除し、シンプル版に特化
- v2.0: 改良版料金計算機能を追加
- v1.0: 基本的な類題生成機能
