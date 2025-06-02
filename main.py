import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === Получаем переменные из окружения ===
TOKEN = os.getenv("TOKEN")
DEST_CHAT_ID = os.getenv("DEST_CHAT_ID")        # Новое имя переменной
SOURCE_CHAT_ID = os.getenv("SOURCE_CHAT_ID")    # ID исходной группы (может быть None)

# Если SOURCE_CHAT_ID не задан — запомним его при первом сообщении
_DYNAMIC_SOURCE_CHAT_ID = None


async def log_and_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _DYNAMIC_SOURCE_CHAT_ID

    chat = update.message.chat
    message_text = update.message.text or "[медиа/файл/другое]"

    print("\n=== Получено сообщение ===")
    print(f"Chat ID: {chat.id}")
    print(f"Тип чата: {chat.type}")
    print(f"Название: {chat.title if chat.title else 'нет'}")
    print(f"Сообщение: {message_text}")
    print("============================")

    # Если SOURCE_CHAT_ID ещё не задан — устанавливаем его динамически
    if SOURCE_CHAT_ID is None and _DYNAMIC_SOURCE_CHAT_ID is None:
        _DYNAMIC_SOURCE_CHAT_ID = chat.id
        print(f"\n[INFO] Установлен SOURCE_CHAT_ID = {_DYNAMIC_SOURCE_CHAT_ID}\n"
              "Теперь бот будет пересылать сообщения из этой группы.")

    # Определяем, из какого чата принимать сообщения
    target_source_id = int(SOURCE_CHAT_ID) if SOURCE_CHAT_ID else _DYNAMIC_SOURCE_CHAT_ID

    # Проверяем, что сообщение из нужного чата
    if chat.id == target_source_id:
        await context.bot.forward_message(
            chat_id=int(DEST_CHAT_ID),
            from_chat_id=chat.id,
            message_id=update.message.message_id
        )


def main():
    if not TOKEN:
        raise ValueError("Не установлена переменная окружения TOKEN")

    if not DEST_CHAT_ID:
        raise ValueError("Не установлена переменная окружения DEST_CHAT_ID")

    print("Бот запущен и ожидает сообщения...")

    app = ApplicationBuilder().token(TOKEN).build()
    handler = MessageHandler(filters.ALL & ~filters.COMMAND, log_and_forward)
    app.add_handler(handler)

    app.run_polling()


if __name__ == "__main__":
    main()
