import asyncio
import logging
from core.monitor import TelegramMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

async def main():
    monitor = TelegramMonitor()
    try:
        await monitor.start()
    except KeyboardInterrupt:
        await monitor.shutdown()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
        await monitor.shutdown()

if __name__ == '__main__':
    asyncio.run(main())