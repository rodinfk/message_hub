from dataclasses import dataclass
from typing import Set, Dict

@dataclass
class ChatGroup:
    name: str
    keywords: Set[str]
    chat_ids: Set[int]

@dataclass
class PendingReply:
    chat_id: int
    message_id: int
    user_id: int
    user_name: str