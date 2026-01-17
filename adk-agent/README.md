# ADK 版 Hello World

このディレクトリには、ADK（Agent Development Kit）の設計思想に基づいたエージェントの実装が含まれています。

## 構成要素
- **Planner**: LLM を用いて次のアクションを決定します。
- **Executor**: Planner が決定したツールを具体的に実行します。
- **Memory**: 過去の対話履歴を管理し、文脈を維持します。
- **Agent**: 上記コンポーネントを統合し、自律的なループを制御します。

## 実行手順

### 1. 依存関係のインストール
ルートディレクトリで以下を実行してください（済んでいる場合は不要です）。
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
ルートディレクトリの `.env` ファイルに `OPENAI_API_KEY` が設定されていることを確認してください。

### 3. エージェントの実行
```bash
python -m adk-agent.main
```

## 期待される出力
```text
User: 3 + 5 を計算して
--- Loop 1 ---
[Planner] Planning next step...
[Executor] Executing tool: calculate with args: {'expression': '3 + 5'}
[Tool] Calculating: 3 + 5
--- Loop 2 ---
[Planner] Planning next step...
Agent: 3 + 5 の計算結果は 8 です 🚀
```
