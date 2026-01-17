import sys
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_add_tool(a, b):
    """MCP Server に接続して add ツールを呼び出す。"""
    # サーバーの起動パラメータを設定
    env = dict(os.environ)
    env["PYTHONPATH"] = os.getcwd()
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-u", "-m", "mcp-agent.server"],  # -u でバッファリングを無効化
        env=env,  # type: ignore
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # セッションの初期化
            await session.initialize()

            # ツールの一覧を取得（デバッグ用）
            # tools = await session.list_tools()
            # print(f"Available tools: {tools}")

            # add ツールを呼び出す
            result = await session.call_tool("add", arguments={"a": a, "b": b})
            return result.content[0].text


if __name__ == "__main__":
    import anyio

    res = anyio.run(run_add_tool, 3, 5)
    print(f"Result: {res}")
