# MCP Agent

MCP (Model Context Protocol) によるツールサーバーとクライアントの Hello World 実装。

## 構成

MCP Server と MCP Client の最小構成で構築されています。

- **MCP Server**: `add(a, b)` ツールを定義し、JSON-RPC (stdio) を介して提供します。
- **MCP Client**: サーバーと通信し、ツールを実行します。
- **Agent**: クライアントを介してサーバーのツールを利用し、ユーザーの依頼を完遂します。

### アーキテクチャ

```mermaid
graph LR
    Agent --> MCP_Client
    MCP_Client <== JSON-RPC (stdio) ==> MCP_Server
    MCP_Server --> Tool[add]
```

## 実装のポイント

- **関心の分離**: 計算ロジック（Server）と、それをどう使うか（Agent/Client）が完全に分離されています。
- **標準化されたインターフェース**: モデルコンテキストプロトコルに基づいた標準的な通信手順を用いています。
- **ローカル実行**: `stdio` を使用したプロセス間通信により、ローカル環境でサーバーとクライアントが連携します。

## 実行方法

```bash
python -m mcp-agent.main
```
