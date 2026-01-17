import anyio
import re
from core.agent import BaseAgent
from .client import run_add_tool


class Agent(BaseAgent):
    """MCP を使用してツールサーバーと通信するエージェント。"""

    def run(self, user_input):
        """ユーザー入力を解析し、MCP ツールを呼び出す。

        この実装では、簡易的な正規表現で数値を抽出し、
        MCP サーバーの 'add' ツールを呼び出します。
        """
        print(f"User: {user_input}")

        # 簡易的な数値抽出 (例: "3 + 5" -> [3, 5])
        numbers = re.findall(r"\d+", user_input)

        if len(numbers) >= 2:
            a = int(numbers[0])
            b = int(numbers[1])

            print(f"[Step 1] Recognizing task: add {a} and {b}")
            print(f"[Step 2] Executing via MCP Server...")

            # MCP ツールを非同期で呼び出す
            result = anyio.run(run_add_tool, a, b)

            print(f"[Step 3] Returning result...")
            print(f"Agent: 計算結果は {result} です。")
        else:
            print("Agent: 数値を2つ入力してください（例：3 + 5 を計算して）")


if __name__ == "__main__":
    agent = Agent()
    agent.run("3 + 5 を計算して")
