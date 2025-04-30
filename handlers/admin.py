import re
from telethon import events


async def handle_admin_reply(monitor, event):
    if not event.message.text or not event.message.text.startswith('/reply'):
        return

    try:
        match = re.match(r'/reply\s+(\d+)\s+(.*)', event.message.text)
        if not match:
            await event.reply("Неверный формат. Используйте: /reply <ID> <текст>")
            return

        reply_id = int(match.group(1))
        reply_text = match.group(2)

        if reply_id not in monitor.pending_replies:
            await event.reply("Ошибка: сообщение с таким ID не найдено или устарело")
            return

        pending = monitor.pending_replies[reply_id]

        response = (
            f"{reply_text}"
        )

        await monitor.client.send_message(
            entity=pending.chat_id,
            message=response,
            reply_to=pending.message_id
        )

        await event.reply(f"✅ Ответ отправлен пользователю {pending.user_name}")
        del monitor.pending_replies[reply_id]

    except Exception as e:
        monitor.logger.error(f"Ошибка обработки ответа админа: {e}")
        await event.reply(f"⚠️ Ошибка: {str(e)}")


def setup_admin_handlers(monitor):
    monitor.client.add_event_handler(
        lambda e: handle_admin_reply(monitor, e),
        events.NewMessage(chats=monitor.config['admin_chat_id'])
    )