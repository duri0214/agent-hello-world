# AIエージェント基盤 Hello World 4連装

AIエージェント基盤のレイヤー構造を理解するための検証リポジトリです。
同一のタスク（3 + 5 の計算）を異なる4つの方式で実装し、その設計思想を比較します。

## 比較対象
1. **OpenAI Agents**: LLM標準の Tool Calling を用いたシンプルな構成
2. **ADK（社内/Google ADK）**: (未実装)
3. **LangGraph**: (未実装)
4. **MCP (Model Context Protocol)**: (未実装)

---

## 1. OpenAI Agents 版

### 実装のポイント
- OpenAI の Chat Completions API と Tool Calling を使用。
- Planner（LLMがツールを選択）と Executor（コードがツールを実行）のループを明示的に記述。

### セットアップ
```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
# .env ファイルを作成し、OPENAI_API_KEY を設定してください
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 実行
```bash
python openai-agent/main.py
```

### 期待される出力
```text
User: 3 + 5 を計算して
[Step 1] Planning...
[Step 2] Executing tool: calculate with args: {'expression': '3 + 5'}
[Tool] Calculating: 3 + 5
[Step 3] Finalizing result...
Agent: 3 + 5 の計算結果は 8 です。
```
