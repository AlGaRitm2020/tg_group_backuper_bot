import asyncio
import datetime
import logging
import random
import re
import secrets
import sys
from datetime import timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import ChatPermissions, Message
from aiogram.utils.chat_member import ADMINS

from app.config import settings
from app.logging_config import setup_logging
from app.utils import get_random_top_shortik

setup_logging()
logger = logging.getLogger(__name__)

dp = Dispatcher()
# Если SOURCE_CHAT_ID не задан — запомним его при первом сообщении
dp["dynamic_source_chat_id"] = None


@dp.message(Command("roll"))
async def roll(message: Message):
    args = message.text.split()[1:]
    low, high = 1, 100
    try:
        if len(args) == 1:
            low, high = 1, int(args[0])
        elif len(args) == 2:  # noqa: PLR2004
            low, high = int(args[0]), int(args[1])
        if high > 100_000_000_000:
            await message.answer("Ага и корову 🐄 в дом 🏠")
            return
        if low > high:
            low, high = high, low
        number = secrets.randbelow(high - low + 1) + low
        text = f"🎲 Выпал результат: <b>{number}</b>\n📊 Диапазон: {low} — {high}"
        await message.answer(text)
    except ValueError:
        await message.answer(
            "❌ Использование: /roll [min] [max]\nПример: /roll 10 1000"
        )


@dp.message(Command("mute"))
async def mute(message: Message):
    if not message.reply_to_message:
        await message.answer(
            "❌ Нужно ответить на сообщение пользователя, которого хочешь замутить."
        )
        return

    if (username := message.reply_to_message.from_user.username) in ADMINS:
        await message.answer(f"🛡 Пользователь @{username} имеет иммунитет от мута.")
        return

    member = await message.chat.get_member(message.reply_to_message.from_user.id)
    if member.status in {"administrator", "creator"}:
        await message.answer("🛡 Нельзя замутить администратора или создателя группы.")
        return

    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer(
            "❌ Использование: /mute <минуты>\nПример: /mute 1m или /mute 5m"
        )
        return

    duration = args[0]
    match = re.match(r"^(\d+)m$", duration)
    if not match:
        await message.answer("❌ Неверный формат. Используй только минуты: 1m … 14400m")
        return

    minutes = min(int(match.group(1)), 14400)
    if not 1 <= minutes <= 14400:
        await message.answer("⚠️ Допустимое время мута — от 1 до 14400 минут.")
        return

    target = message.reply_to_message.from_user
    until_date = message.date + timedelta(minutes=minutes)

    try:
        await message.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
        await message.answer(
            f"🔇 Пользователь @{target.username or target.full_name} замучен на {minutes} мин."
        )
    except Exception:
        logger.exception(
            "Ошибка при mute: target=%s chat=%s", target.username, message.chat.id
        )
        await message.answer("❌ Ошибка")


@dp.message(Command("unmute"))
async def unmute(message: Message):
    if not message.reply_to_message:
        await message.answer(
            "❌ Нужно ответить на сообщение пользователя, которого хочешь размутить."
        )
        return

    target = message.reply_to_message.from_user

    try:
        await message.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_change_info=True,
            ),
        )
        await message.answer(
            f"🔊 Пользователь @{target.username or target.full_name} размучен!"
        )
    except TelegramBadRequest as e:
        await message.answer(
            "🛡 Пользователь является администратором — мут не применялся."
        )
        logger.warning("TelegramBadRequest при unmute: %s", e)
    except Exception:
        logger.exception(
            "Ошибка при unmute: target=%s chat=%s", target.username, message.chat.id
        )
        await message.answer("❌ Произошла ошибка при снятии мута.")


@dp.message(Command("anekdot"))
async def anekdot(message: Message):
    joke = await get_random_top_shortik()
    await message.answer(joke)


@dp.message(Command(settings.TG_COMMAND))
async def tg_command(message: Message):
    random_user = random.choice(settings.CHAT_USERS)  # noqa: S311
    await message.answer(f"{random_user} - {settings.RANK}")


@dp.message(Command(settings.TG_COMMAND1))
async def tg_command1(message: Message):
    random_user = settings.CHAT_USERS[
        hash(str(datetime.datetime.now().timetuple().tm_yday)) % len(settings.CHAT_USERS)
    ]
    await message.answer(f"Сегодняшний {settings.RANK} это {random_user}")


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
