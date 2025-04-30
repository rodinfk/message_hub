from telethon import events
from core.models import PendingReply


async def handle_message(monitor, event):
    if not monitor._is_running or not monitor.client.is_connected():
        return

    try:
        message = event.message
        monitor.last_message_ids[event.chat_id] = message.id

        text = (message.text or '').lower()

        for group in monitor.chat_groups:
            if event.chat_id not in group.chat_ids:
                continue

            found_keywords = {kw for kw in group.keywords if kw in text}
            if found_keywords:
                await process_alert(monitor, event, group, found_keywords)
                break
    except Exception as e:
        monitor.logger.error(f"Message processing error: {e}")


async def process_alert(monitor, event, group, keywords):
    try:
        chat = await event.get_chat()
        sender = await event.message.get_sender()
        sender_name = getattr(sender, 'first_name', 'Unknown')

        reply_id = event.message.id
        chat_id = event.chat_id

        # Формируем ссылку на сообщение
        if str(chat_id).startswith('-100'):
            chat_id = int(str(chat_id)[4:])
        message_link = f"https://t.me/c/{chat_id}/{reply_id}"

        monitor.pending_replies[reply_id] = PendingReply(
            chat_id=event.chat_id,
            message_id=event.message.id,
            user_id=sender.id,
            user_name=sender_name
        )

        header = (
            f"Ключевые слова: {', '.join(f'#{kw}' for kw in keywords)}\n"
            f"Чат: {getattr(chat, 'title', 'Private')}\n"
            f"Отправитель: {sender_name} (ID: {sender.id})\n\n"
            f"Ответить:\n/reply {reply_id} текст"
        )

        # Send header separately
        await monitor.client.send_message(
            monitor.config['admin_chat_id'],
            header
        )

        # Forward original message
        await monitor.client.forward_messages(
            monitor.config['admin_chat_id'],
            event.message
        )

        for kw in keywords:
            monitor.stats[kw] += 1
        monitor.logger.info(f"Found {len(keywords)} keywords in {group.name}")
    except Exception as e:
        monitor.logger.error(f"Alert processing error: {e}")


def setup_message_handlers(monitor):
    monitor.client.add_event_handler(
        lambda e: handle_message(monitor, e),
        events.NewMessage(chats=monitor._get_all_monitored_chats())
    )