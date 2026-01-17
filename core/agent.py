from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """すべてのエージェントの基底クラス。"""

    @abstractmethod
    def run(self, user_input: str) -> None:
        """エージェントを実行する抽象メソッド。

        Args:
            user_input (str): ユーザーからの入力。
        """
        pass
