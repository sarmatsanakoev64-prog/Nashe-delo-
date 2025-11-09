import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

DATA_FILE = "users.json"

def load_users():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_admins = await context.bot.get_chat_administrators(update.effective_chat.id)
    admin_ids = [admin.user.id for admin in chat_admins]
    return update.effective_user.id in admin_ids

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Привет! Я бот для управления списком 👋\n\n"
        "Доступные команды:\n"
        "/add <имя> <@username> — добавить в список\n"
        "/remove <@username> — удалить из списка\n"
        "/edit <@username> <новое имя> — изменить имя\n"
        "/list — показать список\n"
        "/clear — очистить список"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет прав для добавления.")
        return

    if len(context.args) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /add <имя> <@username>")
        return

    name = context.args[0]
    username = context.args[1]
    users = load_users()

    if any(u["username"] == username for u in users):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Такой пользователь уже есть!")
        return

    users.append({"username": username, "name": name})
    save_users(users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ Добавлен: {name}-{username}")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет прав для удаления.")
        return

    if len(context.args) < 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /remove <@username>")
        return

    username = context.args[0]
    users = load_users()
    new_users = [u for u in users if u["username"] != username]

    if len(new_users) == len(users):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Пользователь не найден.")
        return

    save_users(new_users)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Пользователь {username} удалён.")

async def edit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет прав для изменения.")
        return

    if len(context.args) < 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Использование: /edit <@username> <новое имя>")
        return

    username = context.args[0]
    new_name = context.args[1]
    users = load_users()

    for u in users:
        if u["username"] == username:
            u["name"] = new_name
            save_users(users)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✏️ Изменён: {new_name}-{username}")
            return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пользователь не найден.")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    if not users:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Список пуст 🕳️")
        return

    text = "📋 Список пользователей:\n\n"
    for i, u in enumerate(users, 1):
        username = u.get('username', 'без username')
        name = u.get('name', 'без имени')
        text += f"{i}. {name}-{username}\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def clear_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="У тебя нет прав для очистки списка.")
        return

    save_users([])
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🧹 Список успешно очищен!")

if __name__ == "__main__":
    app = ApplicationBuilder().token("8126569374:AAE6F9JriZCpYMTPKMYqITwMVxmriaF1Ntw").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("remove", remove_user))
    app.add_handler(CommandHandler("edit", edit_user))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("clear", clear_list))

    print("🤖 Бот запущен и работает...")
    app.run_polling()
