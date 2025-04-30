import yaml
import asyncio
from collections import defaultdict
from telethon import TelegramClient
from .connection import ConnectionManager
from .models import ChatGroup, PendingReply  # Добавлен импорт PendingReply
from handlers import setup_message_handlers, setup_admin_handlers
import logging

class TelegramMonitor:
    def __init__(self):
        self.config = self._load_config()
        self.client = TelegramClient(
            'monitor_session',
            self.config['api_id'],
            self.config['api_hash']
        )
        self.connection_manager = ConnectionManager(self.client)
        self.chat_groups = self._init_chat_groups()
        self.stats = defaultdict(int)
        self._is_running = False
        self.pending_replies = {}  # Теперь использует PendingReply напрямую
        self.last_message_ids = {}
        self.logger = logging.getLogger('TelegramMonitor')


    def _load_config(self):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _init_chat_groups(self) -> list[ChatGroup]:
        return [
            ChatGroup(
                name=name,
                keywords=set(k.lower() for k in data['keywords']),
                chat_ids=set(data['chats'])
            )
            for name, data in self.config['chat_groups'].items()
        ]

    def _get_all_monitored_chats(self) -> list[int]:
        return [chat_id for group in self.chat_groups for chat_id in group.chat_ids]

    async def start(self):
        self._is_running = True
        asyncio.create_task(self.connection_manager.maintain_connection())

        try:
            await self.client.start(bot_token=self.config['bot_token'])
            setup_message_handlers(self)
            setup_admin_handlers(self)
            self.logger.info(f"Bot started. Monitoring {len(self._get_all_monitored_chats())} chats")

            while self._is_running:
                await asyncio.sleep(1)
        finally:
            await self.shutdown()

    async def shutdown(self):
        self._is_running = False
        await self.client.disconnect()
        self.logger.info("Bot stopped")