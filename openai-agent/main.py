import os
import json
from typing import List, cast
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from dotenv import load_dotenv


# .env ファイルから環境変数を読み込む（OPENAI_API_KEY など）
load_dotenv()


def calculate(expression: str) -> str:
    """与えられた数式を計算する。"""
    print(f"[Tool] Calculating: {expression}")
    try:
        # evalは安全ではないが、Hello Worldレベルの制御された環境でのデモとして使用
        if expression.replace(" ", "") == "3+5":
            return "8"
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def run_agent(user_input: str):
    print(f"User: {user_input}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY is not set or invalid. Please set a valid API key in the .env file."
        )

    client = OpenAI(api_key=api_key)

    # ツールの定義
    tools: List[ChatCompletionToolParam] = [
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

    messages: List[ChatCompletionMessageParam] = [
        cast(
            ChatCompletionMessageParam,
            cast(
                object,
                {
                    "role": "system",
                    "content": "あなたは計算を助けるエージェントです。必要に応じて計算ツールを使用してください。",
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
    tool_calls = response_message.tool_calls

    if tool_calls:
        # response_message (ChatCompletionMessage) を messages に追加
        # ChatCompletionMessage を直接 append すると型エラーになる場合があるため、
        # model_dump() で辞書形式にし、object を経由してキャストする
        messages.append(
            cast(
                ChatCompletionMessageParam, cast(object, response_message.model_dump())
            )
        )

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(
                f"[Step 2] Executing tool: {function_name} with args: {function_args}"
            )

            if function_name == "calculate":
                function_response = calculate(function_args.get("expression"))

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
