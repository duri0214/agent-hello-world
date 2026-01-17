import os
import json
from typing import cast
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from dotenv import load_dotenv


# .env ファイルから環境変数を読み込む（OPENAI_API_KEY など）
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
        # evalは安全ではないが、Hello Worldレベルの制御された環境でのデモとして使用
        result = eval(expression, {"__builtins__": None}, {})
        return f"{result} 🚀"
    except Exception as e:
        return f"Error: {str(e)}"


def run_agent(user_input: str):
    """OpenAI Agents SDK を使用して、ユーザー入力に基づいたタスクを実行する。

    以下の Planner-Executor ループ（1ループ構成）で処理が行われます。

    1. [Step 1] Planning (タスクの解釈とツール選択):
       `client.chat.completions.create` に `messages` と `tools`（計算機など）を一緒に渡します。
       LLM は入力を解析し、最適なツールと引数を決定します。
       この結果は `response.choices[0].message.tool_calls` に格納されます。
    2. [Step 2] Executing (ツールの実行):
       LLM から返された `tool_calls` は「実行すべきツールのリスト」です。
       例えば、10個のツールが定義されていても、LLM はその中から必要な数（例: 2個）だけを選択して返します。
       Executor（この関数）は、要求されたすべてのツールをループで回して順次実行し、
       その結果（`role: "tool"`）をメッセージ履歴に追加します。
    3. [Step 3] Finalizing (結果の集計と回答生成):
       実行結果を含む履歴を再度 LLM に投げ、最終的な回答（例: "8 🚀" を含む回答）を得ます。

    Args:
        user_input (str): ユーザーからの入力テキスト
    """
    print(f"User: {user_input}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY is not set or invalid. Please set a valid API key in the .env file."
        )

    client = OpenAI(api_key=api_key)

    # ツールの定義
    tools: list[ChatCompletionToolParam] = [
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

    messages: list[ChatCompletionMessageParam] = [
        cast(
            ChatCompletionMessageParam,
            cast(
                object,
                {
                    "role": "system",
                    "content": "あなたは計算を助けるエージェントです。必要に応じて計算ツールを使用してください。ツールから返された結果に含まれる絵文字などは、そのまま最終的な回答に含めてください。",
                },
            ),
        ),
        cast(
            ChatCompletionMessageParam,
            cast(object, {"role": "user", "content": user_input}),
        ),
    ]

    # ステップのログ出力
    print("[Step 1] Planning...")

    response = client.chat.completions.create(
        model="gpt-4o", messages=messages, tools=tools, tool_choice="auto"
    )

    response_message = response.choices[0].message
    # LLMが「ツールを使う」と判断した場合、ここに使用すべきツールのリストが入る
    tool_calls = response_message.tool_calls

    if tool_calls:
        # 1. LLMの返答（ツール呼び出し要求）を履歴に追加
        # ChatCompletionMessage を直接 append すると型エラーになる場合があるため、
        # model_dump() で辞書形式にし、object を経由してキャストする
        messages.append(
            cast(
                ChatCompletionMessageParam, cast(object, response_message.model_dump())
            )
        )

        # 2. 要求されたツールをすべて実行する
        # LLMは、定義されたツール群の中から必要なものを複数（あるいは1つ）選択して
        # 同時に使うよう指示することがあるため、ループで処理する。
        # 例えば、10個のツールがあっても、今の文脈に合う2個だけが返ってくる、といったイメージ。
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(
                f"[Step 2] Executing tool: {function_name} with args: {function_args}"
            )

            if function_name == "calculate":
                function_response = calculate(function_args.get("expression"))

                # 3. 実行結果を履歴に追加（どのツール呼び出しに対する結果かを tool_call_id で紐付け）
                messages.append(
                    cast(
                        ChatCompletionMessageParam,
                        cast(
                            object,
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": function_response,
                            },
                        ),
                    )
                )

        print("[Step 3] Finalizing result...")
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        final_content = second_response.choices[0].message.content
        print(f"Agent: {final_content}")
    else:
        print(f"Agent: {response_message.content}")


if __name__ == "__main__":
    run_agent("3 + 5 を計算して")
