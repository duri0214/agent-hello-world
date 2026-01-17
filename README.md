# AIエージェント基盤 Hello World 4連装

AIエージェント基盤のレイヤー構造を理解するための比較リポジトリです。
同一のタスク（3 + 5 の計算）を異なる4つの方式で実装し、設計思想・責務分離・実装構造を横断比較します。

## 構成・比較

各方式の詳細はそれぞれのディレクトリ配下の README を参照してください。

| 方式            | フォルダ             | 特徴・設計思想                          | 実行コマンド                         |
|---------------|------------------|----------------------------------|--------------------------------|
| OpenAI Agents | openai-agent/    | LLM標準のTool Callingを用いたシンプル構成     | python openai-agent/main.py    |
| ADK           | adk-agent/       | Planner/Executor/Memoryに責務分離した構造 | python adk-agent/main.py       |
| LangGraph     | langgraph-agent/ | グラフ表現によるステートフル制御                 | python langgraph-agent/main.py |
| MCP           | mcp-tool/        | Model Context Protocolによるツール標準化  | python mcp-tool/client.py      |

## 共通テーマ
- **ユーザー入力**: 「3 + 5 を計算して」
- **期待出力**: `8 🚀`
- **必須機能**: タスクの認識、計算ツールの実行、結果の返却

## セットアップ
```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
# .env ファイルを作成し、OPENAI_API_KEY を設定してください
cp .env.example .env
```
