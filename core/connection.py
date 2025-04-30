import asyncio
import random
import logging


class ConnectionManager:
    def __init__(self, client):
        self.client = client
        self._is_running = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5
        self.logger = logging.getLogger('ConnectionManager')

    async def maintain_connection(self):
        self._is_running = True
        while self._is_running:
            if not await self._check_connection():
                await self._reconnect()
            await asyncio.sleep(10)

    async def _check_connection(self) -> bool:
        try:
            if not self.client.is_connected():
                return False
            await self.client.get_me()
            self._reconnect_attempts = 0
            return True
        except Exception as e:
            self.logger.warning(f"Connection check failed: {e}")
            return False

    async def _reconnect(self):
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self.logger.error("Max reconnection attempts reached")
            self._is_running = False
            return

        self._reconnect_attempts += 1
        delay = self._reconnect_delay * (1 + random.random())

        self.logger.warning(
            f"Reconnection attempt {self._reconnect_attempts}/{self._max_reconnect_attempts} in {delay:.1f} sec...")

        try:
            await asyncio.sleep(delay)
            await self.client.disconnect()
            await self.client.connect()

            if not self.client.is_connected():
                raise ConnectionError("Connection failed")

            self.logger.info("Connection restored")
            self._reconnect_attempts = 0
        except Exception as e:
            self.logger.error(f"Reconnection error: {e}")