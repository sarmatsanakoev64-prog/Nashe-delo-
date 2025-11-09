import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8308147109:AAEXSt3tk-AZs9WMJzQe2nXj6zxju5XjLqo"
DATA_FILE = "users.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def load_users():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    admins = await context.bot.get_chat_administrators(chat.id)
    admin_ids = [admin.user.id for admin in admins]
    return user.id in admin_ids

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=(
        "Привет! Я бот для управления списком пользователей.\n"
        "Доступные команды:\n"
        "/add — добавить пользователя\n"
        "/remove — удалить пользователя\n"
        "/edit — изменить данные\n"
        "/list — показать список\n"
        "/clear — очистить список"
    )

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    if len(context.args) < 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=("Используй: /add Имя")
        return
    name = " ".join(context.args)
    users.append({"name": name})
    save_users(users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=(f"Пользователь {name} добавлен.")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    if len(context.args) < 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=("Используй: /remove Имя")
        return
    name = " ".join(context.args)
    users = [u for u in users if u["name"] != name]
    save_users(users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=(f" Пользователь {name} удалён.")

async def edit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    if len(context.args) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=("Используй: /edit СтароеИмя НовоеИмя")
        return
    old_name, new_name = context.args[0], " ".join(context.args[1:])
    for u in users:
        if u["name"] == old_name:
            u["name"] = new_name
            save_users(users)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=(f"✏️ Имя {old_name} изменено на {new_name}.")
            return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=("Пользователь не найден.")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    if not users:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=("Список пуст.")
        return
    text = "Список пользователей:\n"
    for i, u in enumerate(users, start=1):
        text += f"{i}. {u['name']}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=(text)

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=("У тебя нет прав для очистки списка.")
        return

    save_users([])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=("Список успешно очищен!")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("remove", remove_user))
    app.add_handler(CommandHandler("edit", edit_user))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("clear", clear_list))

    await app.bot.set_my_commands([
        ("start", "Запустить бота"),
        ("add", "Добавить пользователя"),
        ("remove", "Удалить пользователя"),
        ("edit", "Изменить пользователя"),
        ("list", "Показать список пользователей"),
        ("clear", "Очистить весь список")
    ])

    print("Бот запущен и работает...")
    await app.run_polling()
if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except RuntimeError:
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
