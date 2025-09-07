import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from app.config import settings
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

dp = Dispatcher()
# Если SOURCE_CHAT_ID не задан — запомним его при первом сообщении
dp["dynamic_source_chat_id"] = None


@dp.message(~F.text.startswith("/"))
async def handle_any_message(message: Message, bot: Bot):
    chat = message.chat
    message_text = message.text or "[медиа/файл/другое]"

    logger.info(
        "Сообщение получено | Пользователь = %s | Chat ID = %s | Тип = %s | Название = %s | Текст = %s",
        message.from_user.username,
        chat.id,
        chat.type,
        chat.title if chat.title else "нет",
        message_text,
    )

    # если SOURCE_CHAT_ID не задан — берем из первого сообщения
    if settings.SOURCE_CHAT_ID is None and dp["dynamic_source_chat_id"] is None:
        dp["dynamic_source_chat_id"] = chat.id
        logger.info("Установлен SOURCE_CHAT_ID = %s", dp["dynamic_source_chat_id"])

    target_source_id = (
        int(settings.SOURCE_CHAT_ID)
        if settings.SOURCE_CHAT_ID
        else dp["dynamic_source_chat_id"]
    )

    if target_source_id and chat.id == target_source_id:
        await bot.forward_message(
            chat_id=int(settings.DEST_CHAT_ID),
            from_chat_id=chat.id,
            message_id=message.message_id,
        )


async def main():
    logger.info("Бот запущен и ожидает сообщения...")

    bot = Bot(
        token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    # Убрал вывод логов от aiogram.event
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    asyncio.run(main())
