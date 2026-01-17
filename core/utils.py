import os
import re


def validate_openai_api_key() -> bool:
    """OpenAI APIキーの存在と形式を検証する。

    APIキーが設定されていない場合や形式が不正な場合は、エラーメッセージを表示して False を返す。
    """
    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        print("Error: OPENAI_API_KEY is not set.")
        return False

    # OpenAI API Key: sk-proj-... (新しい形式) or sk-... (古い形式)
    # 最近は sk-proj- が多い。32文字以上。
    openai_pattern = re.compile(r"^sk-(?:proj-)?[a-zA-Z0-9_-]{32,}$")

    if not openai_pattern.match(openai_key):
        print("Error: OPENAI_API_KEY format is invalid.")
        return False

    return True
