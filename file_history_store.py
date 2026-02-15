import os
import json
from typing import List, Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


def get_history(session_id: str):
    return FileChatMessageHistory(session_id,"./chat_history")
class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, storage_path: str):
        # 初始化会话ID和存储路径
        self.session_id = session_id
        self.storage_path = storage_path
        # 拼接完整的文件路径
        self.file_path = os.path.join(self.storage_path, self.session_id)
        # 确保存储目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    @property
    def messages(self) -> List[BaseMessage]:
        # 从文件读取消息
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
            return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # 合并已有消息和新消息
        all_messages = list(self.messages)
        all_messages.extend(messages)
        # 将消息转为字典并写入文件
        new_messages = [message_to_dict(msg) for msg in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        # 清空消息
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)