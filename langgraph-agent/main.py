import os
import operator
from typing import Annotated, TypedDict, cast, Any
from pydantic import SecretStr

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    AIMessage,
)
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core.agent import BaseAgent
from core.utils import validate_openai_api_key

# .env ファイルから環境変数を読み込む
load_dotenv()

# --- Tools ---


@tool
def calculate(expression: str) -> str:
    """与えられた数式を計算するツール。

    Python の eval 関数を使用して、文字列として受け取った数式を直接評価（計算）します。
    デモ目的のため、__builtins__ を制限して実行されます。

    Args:
        expression: 計算する数式 (例: "3 + 5")
    """
    print(f"[Tool] Calculating: {expression}")
    try:
        # evalは安全ではないが、デモ目的で制限付きで実行
        result = eval(expression, {"__builtins__": None}, {})
        return f"{result} 🚀"
    except Exception as e:
        return f"Error: {str(e)}"


# --- State ---


class AgentState(TypedDict):
    """グラフの状態を管理する。"""

    # メッセージ履歴。Annotated[..., operator.add] を使うことで、
    # 新しいメッセージがリストに追加されるようになる。
    messages: Annotated[list[BaseMessage], operator.add]


# --- Nodes ---


class Planner:
    """LLMを用いて次のアクションを決定するノード。"""

    def __init__(self, model: ChatOpenAI):
        self.model = model.bind_tools([calculate])

    def __call__(self, state: AgentState) -> dict[str, list[BaseMessage]]:
        print("[Planner] Planning next step...")
        response = self.model.invoke(state["messages"])
        return {"messages": [cast(BaseMessage, response)]}


def tool_node(state: AgentState) -> dict[str, list[BaseMessage]]:
    """ツールを実行するノード。"""
    print("[Tool] Executing tools...")
    last_message = cast(AIMessage, state["messages"][-1])

    if not last_message.tool_calls:
        return {"messages": []}

    results: list[BaseMessage] = []
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "calculate":
            print(
                f"[Tool] Executing {tool_call['name']} with args: {tool_call['args']}"
            )
            result = calculate.invoke(tool_call["args"])
            results.append(
                ToolMessage(tool_call_id=tool_call["id"], content=str(result))
            )

    return {"messages": results}


def result_node(state: AgentState) -> dict[str, list[BaseMessage]]:
    """最終回答を生成するノード。"""
    print("[Result] Finalizing result...")
    # ツール実行結果を含めて再度LLMを呼び出し、自然言語の回答を得る
    # ここでは単純に最後のメッセージを表示するのではなく、
    # ツール結果を解釈した最終的なメッセージを生成する
    model = ChatOpenAI(model="gpt-4o")
    response = model.invoke(state["messages"])
    return {"messages": [cast(BaseMessage, response)]}


# --- Router ---


def should_continue(state: AgentState) -> str:
    """ツール呼び出しが必要かどうかを判断するルーター。"""
    last_message = cast(AIMessage, state["messages"][-1])
    if last_message.tool_calls:
        return "tool"
    return "result"


# --- Agent Class ---


class Agent(BaseAgent):
    """LangGraph を使用して状態遷移型エージェントを構成するクラス。"""

    def __init__(self, api_key_val: str):
        self.model = ChatOpenAI(
            api_key=cast(SecretStr, cast(object, api_key_val)), model="gpt-4o"
        )

        # グラフの定義
        workflow = StateGraph(cast(Any, AgentState))

        # ノードの追加
        workflow.add_node("planner", cast(Any, Planner(self.model)))
        workflow.add_node("tool", cast(Any, tool_node))
        workflow.add_node("result", cast(Any, result_node))

        # エッジの設定
        workflow.set_entry_point("planner")

        # 条件付きエッジ: Planner の後はツール実行か最終回答か
        workflow.add_conditional_edges(
            "planner", should_continue, {"tool": "tool", "result": "result"}
        )

        # ツール実行の後は再度 Planner に戻って判断（ループを許容）
        # ただし今回の要件 [Input] -> [Planner] -> [Tool] -> [Result] に合わせると
        # Tool の後は Result に行くのがシンプルだが、一般的なLangGraphの構成は再帰的
        # 今回の要件図を優先し、Tool -> Result とつなぐ
        workflow.add_edge("tool", "result")

        # Result の後は終了
        workflow.add_edge("result", END)

        # グラフのコンパイル
        self.app: CompiledStateGraph = workflow.compile()

    def run(self, user_input: str) -> None:
        print(f"User: {user_input}")

        system_message = SystemMessage(
            content="あなたはLangGraph構造で実装された計算エージェントです。状態遷移（Node）を意識して動作します。ツールから返された結果（🚀を含む）はそのまま最終回答に含めてください。"
        )
        user_message = HumanMessage(content=user_input)

        inputs: dict[str, list[BaseMessage]] = {
            "messages": [
                system_message,
                user_message,
            ]
        }

        # グラフの実行
        final_result = None
        for output in self.app.stream(cast(Any, inputs), stream_mode="updates"):
            # output は {node_name: {state_update}} の形式
            for node_name, state_update in output.items():
                print(f"--- Node: {node_name} ---")
                if "messages" in state_update and state_update["messages"]:
                    final_result = state_update["messages"][-1]

        if final_result:
            print(f"Agent: {final_result.content}")


if __name__ == "__main__":
    if validate_openai_api_key():
        openai_api_key = os.getenv("OPENAI_API_KEY")
        agent = Agent(api_key_val=openai_api_key)
        agent.run("3 + 5 を計算して")
