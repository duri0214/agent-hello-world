# OpenAI Agents 版 Hello World

このディレクトリには、OpenAI の Tool Calling 機能を中心とした、シンプルかつ標準的なエージェントの実装が含まれています。

## 実装のポイント
- **OpenAI Tool Calling**: LLM が「どのツールをどのような引数で呼び出すか」を判断する標準機能を利用しています。
- **1ステップ実行**: 複雑なループ構造を持たず、基本的には「プランニング（ツール選択）→ 実行 → 最終回答生成」という標準的なフローで完結します。
- **透明性**: `openai-agent/main.py` 1ファイルに全ロジックが集約されており、処理の流れが追いやすい構成になっています。

## 構成図（簡易版）
1. **User Input**: 「3 + 5 を計算して」
2. **Step 1 (Planning)**: LLM が `calculate` ツールが必要だと判断。
3. **Step 2 (Executing)**: コード側で `calculate` 関数を実行。
4. **Step 3 (Finalizing)**: 計算結果（8 🚀）を LLM に渡し、最終回答を生成。

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
python -m openai-agent.main
```

## 期待される出力
```text
User: 3 + 5 を計算して
[Step 1] Planning...
[Step 2] Executing tool: calculate with args: {'expression': '3 + 5'}
[Tool] Calculating: 3 + 5
[Step 3] Finalizing result...
Agent: 3 + 5 の計算結果は 8 です 🚀
```
