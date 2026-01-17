import os
import json

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from dotenv import load_dotenv
from core.agent import BaseAgent
from core.utils import validate_openai_api_key

# .env ファイルから環境変数を読み込む
load_dotenv()


def calculate(expression: str) -> str:
    """与えられた数式を計算するツール。

    Python の eval 関数を使用して、文字列として受け取った数式を直接評価（計算）します。
    デモ目的のため、__builtins__ を制限して実行されます。

    Args:
        expression (str): 計算する数式 (例: "3 + 5")

    Returns:
        str: 計算結果の文字列、またはエラーメッセージ
    """
    print(f"[Tool] Calculating: {expression}")
    try:
        # evalは安全ではないが、デモ目的で制限付きで実行
        result = eval(expression, {"__builtins__": None}, {})
        return f"{result} 🚀"
    except Exception as e:
        return f"Error: {str(e)}"


# --- ADK Components ---


class Memory:
    """エージェントの記憶（コンテキスト）を管理するクラス。"""

    def __init__(self):
        self.messages: list[ChatCompletionMessageParam] = []

    def add_message(
        self,
        role: str,
        content: str,
        tool_calls: list[object] | None = None,
        tool_call_id: str | None = None,
        name: str | None = None,
    ):
        message: dict[str, object] = {"role": role, "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        if tool_call_id:
            message["tool_call_id"] = tool_call_id
        if name:
            message["name"] = name
        self.messages.append(message)  # type: ignore

    def get_messages(self) -> list[ChatCompletionMessageParam]:
        return self.messages


class Planner:
    """LLMを用いて次のアクション（思考またはツール実行）を決定するクラス。"""

    def __init__(self, client: OpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model
        self.tools: list[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "数式を受け取り、その計算結果を返す。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "計算する数式 (例: '3 + 5')",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            }
        ]

    def plan(self, memory: Memory) -> object:
        print("[Planner] Planning next step...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=memory.get_messages(),
            tools=self.tools,
            tool_choice="auto",
        )
        return response.choices[0].message


class Executor:
    """Plannerが決定したツールを実行するクラス。"""

    @staticmethod
    def execute(tool_call: object) -> str:
        # tool_call は通常 ChatCompletionMessageToolCall オブジェクト
        # 型チェックを回避しつつ属性にアクセスするため getattr 等を使用するか、object として扱う
        function_name = getattr(getattr(tool_call, "function", None), "name", None)
        function_args_str = getattr(
            getattr(tool_call, "function", None), "arguments", "{}"
        )
        function_args = json.loads(function_args_str)

        print(f"[Executor] Executing tool: {function_name} with args: {function_args}")

        if function_name == "calculate":
            return calculate(function_args.get("expression", ""))
        else:
            return f"Error: Unknown tool {function_name}"


class Agent(BaseAgent):
    """Planner, Executor, Memory を統括し、エージェントループを制御するクラス。"""

    def __init__(self, client: OpenAI):
        self.memory = Memory()
        self.planner = Planner(client)
        self.executor = Executor()

        # システムプロンプトの初期化
        self.memory.add_message(
            "system",
            "あなたはADK構造で実装された計算エージェントです。Planner/Executor/Memoryの責務分離を意識して動作します。ツールから返された結果（🚀を含む）はそのまま最終回答に含めてください。",
        )

    def run(self, user_input: str):
        print(f"User: {user_input}")
        self.memory.add_message("user", user_input)

        # エージェントループ (最大5回)
        for i in range(5):
            print(f"--- Loop {i+1} ---")

            # 1. Planning
            response_message: object = self.planner.plan(self.memory)

            # LLMの回答を一旦メモリに追加（tool_callsが含まれる場合も含む）
            # OpenAI APIの仕様に合わせて辞書形式で保存
            self.memory.add_message(
                role=getattr(response_message, "role", "assistant"),
                content=getattr(response_message, "content", "") or "",
                tool_calls=(
                    [
                        t.model_dump()
                        for t in getattr(response_message, "tool_calls", [])
                    ]
                    if getattr(response_message, "tool_calls", None)
                    else None
                ),
            )

            # 2. Check if Tool Call is required
            tool_calls = getattr(response_message, "tool_calls", None)
            if not tool_calls:
                # ツール呼び出しがなければ終了（Final Answer）
                print(f"Agent: {getattr(response_message, 'content', '')}")
                break

            # 3. Execution
            for tool_call in tool_calls:
                result = self.executor.execute(tool_call)

                # 4. Memory update with a Tool result
                self.memory.add_message(
                    role="tool",
                    content=result,
                    tool_call_id=getattr(tool_call, "id", None),
                    name=getattr(getattr(tool_call, "function", None), "name", None),
                )
        else:
            print("Error: Maximum loop count reached.")


if __name__ == "__main__":
    if validate_openai_api_key():
        api_key = os.getenv("OPENAI_API_KEY")
        openai_client = OpenAI(api_key=api_key)
        agent = Agent(openai_client)
        agent.run("3 + 5 を計算して")
