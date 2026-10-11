"""
Telegram-бот для партнерів та адміністратора платформи VeteranPath Lviv
- Партнери (після введення пароля): розміщують нові вакансії та програми для ветеранів
- Адміністратор (після введення пароля): бачить всі пропозиції та читає зауваження/відгуки
"""

import logging
import uuid
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import Opportunity, FeedbackItem

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Стани діалогу
AUTH, MENU, ADD_TITLE, ADD_PARTNER, ADD_TYPE, ADD_DESC, ADD_BENEFITS, ADD_SALARY, ADD_FEEDBACK = range(9)

USER_ROLES = {} # chat_id -> "partner" | "admin"
TEMP_DATA = {} # chat_id -> dict

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    USER_ROLES.pop(chat_id, None)
    
    welcome_text = (
        "🇺🇦 **Вітаємо в офіційному Telegram-боті VeteranPath Lviv!**\n\n"
        "Цей бот створено для:\n"
        "1. **Роботодавців та Партнерів:** розміщення вакансій, грантів та курсів для ветеранів.\n"
        "2. **Адміністраторів:** моніторинг пропозицій та перегляд зауважень користувачів.\n\n"
        "🔐 **Введіть пароль доступу** (пароль партнера або пароль адміністратора):"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")
    return AUTH

async def handle_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    password = update.message.text.strip()

    if password == settings.TELEGRAM_ADMIN_PASSWORD:
        USER_ROLES[chat_id] = "admin"
        await update.message.reply_text(
            "✅ **Авторизовано як Адміністратор платформи!**",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
        return MENU
    elif password == settings.TELEGRAM_PARTNER_PASSWORD:
        USER_ROLES[chat_id] = "partner"
        await update.message.reply_text(
            "✅ **Авторизовано як Партнер/Роботодавець!**",
            reply_markup=get_partner_keyboard(),
            parse_mode="Markdown"
        )
        return MENU
    else:
        await update.message.reply_text(
            "❌ Невірний пароль. Спробуйте ще раз або зверніться до координатора проекту:"
        )
        return AUTH

def get_partner_keyboard():
    keyboard = [
        ["➕ Додати пропозицію для ветеранів"],
        ["📋 Мої активні пропозиції"],
        ["✍️ Залишити зауваження/відгук"],
        ["🚪 Вийти"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        ["📊 Всі пропозиції в базі"],
        ["📨 Переглянути зауваження та відгуки"],
        ["➕ Додати нову пропозицію"],
        ["🚪 Вийти"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    role = USER_ROLES.get(chat_id)

    if text == "🚪 Вийти":
        USER_ROLES.pop(chat_id, None)
        await update.message.reply_text("Ви вийшли з кабінету. Введіть /start для нового входу.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    if text in ["➕ Додати пропозицію для ветеранів", "➕ Додати нову пропозицію"]:
        TEMP_DATA[chat_id] = {}
        await update.message.reply_text(
            "Введіть **назву посади або програми** (наприклад: *Координатор логістики* або *Грант на обладнання*):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return ADD_TITLE

    elif text == "📋 Мої активні пропозиції" or text == "📊 Всі пропозиції в базі":
        with SessionLocal() as db:
            items = db.query(Opportunity).filter(Opportunity.is_active == True).order_by(Opportunity.created_at.desc()).limit(10).all()
            if not items:
                await update.message.reply_text("Наразі немає активних пропозицій у базі.")
                return MENU
            
            msg = "📋 **Активні вакансії та програми:**\n\n"
            for idx, item in enumerate(items, 1):
                msg += f"{idx}. **{item.title}** ({item.partner_name})\n"
                msg += f"   Категорія: {item.category} | З/П: {item.salary_range or 'За домовленістю'}\n"
                msg += f"   Місто: {item.location}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return MENU

    elif text == "📨 Переглянути зауваження та відгуки":
        if role != "admin":
            await update.message.reply_text("Доступно лише для адміністратора.")
            return MENU

        with SessionLocal() as db:
            feedbacks = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).limit(10).all()
            if not feedbacks:
                await update.message.reply_text("Зауважень поки немає! Все працює чудово.")
                return MENU

            msg = "📨 **Останні зауваження та відгуки користувачів:**\n\n"
            for f in feedbacks:
                msg += f"• **[{f.category.upper()}]** від: {f.sender_contact or 'Анонімно'}\n"
                msg += f"  \"{f.message}\"\n"
                msg += f"  Час: {f.created_at.strftime('%d.%m %H:%M')} | Джерело: {f.source}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return MENU

    elif text == "✍️ Залишити зауваження/відгук":
        await update.message.reply_text("Напишіть текст вашого зауваження, побажання або ідеї для проекту:", reply_markup=ReplyKeyboardRemove())
        return ADD_FEEDBACK

    return MENU

# Покроковий майстер додавання вакансії/програми
async def step_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["title"] = update.message.text.strip()
    await update.message.reply_text("Введіть **назву вашої організації/компанії** (наприклад: *Meest Пошта Львів* або *Ветеранський фонд*):")
    return ADD_PARTNER

async def step_add_partner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["partner_name"] = update.message.text.strip()
    keyboard = [["vacancy", "course"], ["grant", "rehab"]]
    await update.message.reply_text(
        "Оберіть **тип пропозиції**:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return ADD_TYPE

async def step_add_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["type"] = update.message.text.strip()
    await update.message.reply_text(
        "Введіть **короткий опис** обов'язків або умов участі:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ADD_DESC

async def step_add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["description"] = update.message.text.strip()
    await update.message.reply_text("Вкажіть **ветеранські переваги** (наприклад: *Ментор з бойовим досвідом, гнучкий графік, допомога з житлом*):")
    return ADD_BENEFITS

async def step_add_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["benefits"] = update.message.text.strip()
    await update.message.reply_text("Вкажіть **зарплату або розмір гранту** (або напишіть 'За домовленістю'):")
    return ADD_SALARY

async def step_add_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    data = TEMP_DATA.get(chat_id, {})
    data["salary_range"] = update.message.text.strip()

    # Збереження в базу даних
    with SessionLocal() as db:
        new_opp = Opportunity(
            id=f"opp-bot-{uuid.uuid4().hex[:8]}",
            partner_id=f"part-{chat_id}",
            partner_name=data.get("partner_name", "Партнер"),
            title=data.get("title", "Вакансія"),
            type=data.get("type", "vacancy"),
            category="IT" if "it" in data.get("title", "").lower() else "logistics" if "логіст" in data.get("title", "").lower() else "business",
            location="Львів",
            description=data.get("description", ""),
            benefits=data.get("benefits", ""),
            salary_range=data.get("salary_range", ""),
            source="telegram_bot",
            is_active=True
        )
        db.add(new_opp)
        db.commit()

    role = USER_ROLES.get(chat_id)
    kb = get_admin_keyboard() if role == "admin" else get_partner_keyboard()
    await update.message.reply_text(
        "🎉 **Успішно опубліковано!** Ваша пропозиція вже відображається ветеранам на сайті платформи.",
        reply_markup=kb,
        parse_mode="Markdown"
    )
    return MENU

async def step_add_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username or update.effective_user.first_name or f"ID:{chat_id}"
    msg_text = update.message.text.strip()

    with SessionLocal() as db:
        fb = FeedbackItem(
            sender_name=user_name,
            sender_contact=f"tg: @{update.effective_user.username}" if update.effective_user.username else f"tg:{chat_id}",
            category="partner",
            message=msg_text,
            source="telegram_bot"
        )
        db.add(fb)
        db.commit()

    role = USER_ROLES.get(chat_id)
    kb = get_admin_keyboard() if role == "admin" else get_partner_keyboard()
    await update.message.reply_text(
        "🙏 Дякуємо! Ваше зауваження передано адміністратору платформи.",
        reply_markup=kb
    )
    return MENU

def run_bot():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or token == "your_telegram_bot_token":
        logger.warning("TELEGRAM_BOT_TOKEN не задано в .env. Бот не запускається.")
        return

    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auth)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_title)],
            ADD_PARTNER: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_partner)],
            ADD_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_type)],
            ADD_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_desc)],
            ADD_BENEFITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_benefits)],
            ADD_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_salary)],
            ADD_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_feedback)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)
    logger.info("Telegram-бот запущено!")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
