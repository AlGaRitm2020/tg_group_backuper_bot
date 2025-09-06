import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

TOKEN: str = getenv("TOKEN")
DEST_CHAT_ID: str = getenv("DEST_CHAT_ID")
SOURCE_CHAT_ID: str | None = getenv("SOURCE_CHAT_ID")

dp = Dispatcher()
# Если SOURCE_CHAT_ID не задан — запомним его при первом сообщении
dp["dynamic_source_chat_id"] = None

logger = logging.getLogger(__name__)


@dp.message(~F.text.startswith("/"))
async def handle_any_message(message: Message, bot: Bot):
    chat = message.chat
    message_text = message.text or "[медиа/файл/другое]"

    logger.info(
        "Сообщение получено | Chat ID=%s | Тип=%s | Название=%s | Текст=%s",
        chat.id,
        chat.type,
        chat.title if chat.title else "нет",
        message_text,
    )

    # если SOURCE_CHAT_ID не задан — берем из первого сообщения
    if SOURCE_CHAT_ID is None and dp["dynamic_source_chat_id"] is None:
        dp["dynamic_source_chat_id"] = chat.id
        logger.info("Установлен SOURCE_CHAT_ID = %s", dp["dynamic_source_chat_id"])

    target_source_id = (
        int(SOURCE_CHAT_ID) if SOURCE_CHAT_ID else dp["dynamic_source_chat_id"]
    )

    if target_source_id and chat.id == target_source_id:
        await bot.forward_message(
            chat_id=int(DEST_CHAT_ID),
            from_chat_id=chat.id,
            message_id=message.message_id,
        )


async def main():
    if not TOKEN:
        raise ValueError("Не установлена переменная окружения TOKEN")

    if not DEST_CHAT_ID:
        raise ValueError("Не установлена переменная окружения DEST_CHAT_ID")

    logger.info("Бот запущен и ожидает сообщения...")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
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
