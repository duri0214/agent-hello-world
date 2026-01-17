from mcp.server import Server
import mcp.types as types
from mcp.server.stdio import stdio_server

# MCP Server のインスタンス作成
app = Server("hello-world-server")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """利用可能なツールの一覧を返す。"""
    return [
        types.Tool(
            name="add",
            description="2つの数値を加算する",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        )
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """ツールを実行する。"""
    if name == "add":
        if not arguments:
            raise ValueError("引数がありません")

        a = arguments.get("a")
        b = arguments.get("b")

        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("引数は数値である必要があります")

        result = a + b
        return [types.TextContent(type="text", text=str(result))]

    raise ValueError(f"不明なツール: {name}")


async def main():
    """標準入出力を使用してサーバーを実行する。"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import anyio

    anyio.run(main)  # type: ignore
