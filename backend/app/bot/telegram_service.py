"""
Telegram-бот для платформи VeteranPath Lviv
Система ролей:
  - Надавач послуг (service_provider): надсилає заявки на вакансії/курси/гранти → адмін підтверджує
    Може: редагувати/видаляти власні АКТИВНІ пропозиції (з обов'язковою причиною видалення)
  - Адміністратор (admin): підтверджує або відхиляє заявки, переглядає всі дані, відгуки, зауваження
"""

import logging
import uuid
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters, CallbackQueryHandler
)
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import Opportunity, FeedbackItem

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Стани діалогу ───────────────────────────────────────────────────────────
(
    AUTH,
    MENU,
    ADD_TITLE,
    ADD_PARTNER,
    ADD_TYPE,
    ADD_DESC,
    ADD_BENEFITS,
    ADD_SALARY,
    ADD_FEEDBACK,
    EDIT_SELECT,
    EDIT_FIELD,
    EDIT_VALUE,
    DELETE_REASON,
    ADMIN_PENDING,
    ADMIN_REJECT_REASON,
) = range(15)

USER_ROLES = {}   # chat_id -> "service_provider" | "admin"
TEMP_DATA  = {}   # chat_id -> dict з тимчасовими даними

# ── Клавіатури ───────────────────────────────────────────────────────────────

def kb_service_provider():
    return ReplyKeyboardMarkup([
        ["➕ Подати нову пропозицію"],
        ["📋 Мої пропозиції (редагувати/видалити)"],
        ["✍️ Залишити зауваження/відгук"],
        ["🚪 Вийти"],
    ], resize_keyboard=True)

def kb_admin():
    return ReplyKeyboardMarkup([
        ["🔔 Пропозиції на розгляді (підтвердити/відхилити)"],
        ["📊 Всі активні пропозиції в базі"],
        ["📨 Зауваження та відгуки користувачів"],
        ["➕ Додати пропозицію напряму"],
        ["🚪 Вийти"],
    ], resize_keyboard=True)

# ── Авторизація ──────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    USER_ROLES.pop(chat_id, None)
    await update.message.reply_text(
        "🇺🇦 *Вітаємо в Telegram-боті VeteranPath Lviv!*\n\n"
        "Введіть пароль для входу:\n"
        "• Якщо ви роботодавець / надавач послуг — пароль *надавача*\n"
        "• Якщо ви адміністратор платформи — пароль *адміністратора*",
        parse_mode="Markdown"
    )
    return AUTH

async def handle_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    pwd = update.message.text.strip()

    if pwd == settings.TELEGRAM_ADMIN_PASSWORD:
        USER_ROLES[chat_id] = "admin"
        await update.message.reply_text(
            "✅ *Авторизовано як Адміністратор платформи!*",
            reply_markup=kb_admin(), parse_mode="Markdown"
        )
        return MENU
    elif pwd == settings.TELEGRAM_PARTNER_PASSWORD:
        USER_ROLES[chat_id] = "service_provider"
        await update.message.reply_text(
            "✅ *Авторизовано як Надавач послуг!*\n"
            "Ваші нові пропозиції побачать ветерани після підтвердження адміністратором.",
            reply_markup=kb_service_provider(), parse_mode="Markdown"
        )
        return MENU
    else:
        await update.message.reply_text("❌ Невірний пароль. Спробуйте ще раз:")
        return AUTH

# ── Головне меню ─────────────────────────────────────────────────────────────

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    role = USER_ROLES.get(chat_id)

    # Вихід
    if text == "🚪 Вийти":
        USER_ROLES.pop(chat_id, None)
        await update.message.reply_text(
            "Ви вийшли. Введіть /start для нового входу.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # ─── Надавач послуг ───
    if text == "➕ Подати нову пропозицію":
        TEMP_DATA[chat_id] = {}
        await update.message.reply_text(
            "Введіть *назву* вакансії/курсу/гранту:\n_(наприклад: «Координатор логістики» або «Грант на обладнання»)_",
            reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown"
        )
        return ADD_TITLE

    if text == "📋 Мої пропозиції (редагувати/видалити)":
        return await show_my_opportunities(update, context)

    if text == "✍️ Залишити зауваження/відгук":
        await update.message.reply_text(
            "Напишіть ваше зауваження, ідею або пропозицію:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADD_FEEDBACK

    # ─── Адмін ───
    if text == "🔔 Пропозиції на розгляді (підтвердити/відхилити)":
        if role != "admin":
            await update.message.reply_text("⛔ Доступно лише адміністратору.")
            return MENU
        return await show_pending(update, context)

    if text in ["📊 Всі активні пропозиції в базі", "📋 Мої активні пропозиції"]:
        return await show_all_active(update, context)

    if text == "📨 Зауваження та відгуки користувачів":
        if role != "admin":
            await update.message.reply_text("⛔ Доступно лише адміністратору.")
            return MENU
        return await show_feedbacks(update, context)

    if text == "➕ Додати пропозицію напряму":
        TEMP_DATA[chat_id] = {"direct": True}
        await update.message.reply_text(
            "Введіть *назву* пропозиції:",
            reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown"
        )
        return ADD_TITLE

    return MENU

# ── Перегляд пропозицій на розгляді (Адмін) ─────────────────────────────────

async def show_pending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    with SessionLocal() as db:
        items = db.query(Opportunity).filter(
            Opportunity.is_pending == True
        ).order_by(Opportunity.created_at.desc()).all()

        if not items:
            await update.message.reply_text(
                "✅ Немає пропозицій на розгляді. Всі заявки вже оброблені.",
                reply_markup=kb_admin()
            )
            return MENU

        TEMP_DATA[chat_id] = {"pending_ids": [item.id for item in items], "pending_index": 0}

        # Показуємо першу заявку
        await show_pending_item(update, context, items[0])
    return ADMIN_PENDING

async def show_pending_item(update, context, item):
    text = (
        f"📩 *Нова заявка на розміщення:*\n\n"
        f"📌 *Назва:* {item.title}\n"
        f"🏢 *Організація:* {item.partner_name}\n"
        f"📂 *Тип:* {item.type}\n"
        f"📍 *Місто:* {item.location}\n"
        f"📝 *Опис:* {item.description}\n"
        f"🎖️ *Переваги:* {item.benefits or '—'}\n"
        f"💰 *Зарплата/грант:* {item.salary_range or 'За домовленістю'}\n\n"
        f"Оберіть дію:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Підтвердити", callback_data=f"approve:{item.id}"),
            InlineKeyboardButton("❌ Відхилити", callback_data=f"reject:{item.id}"),
        ]
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_pending_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    action, opp_id = query.data.split(":", 1)

    if action == "approve":
        with SessionLocal() as db:
            item = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if item:
                item.is_pending = False
                item.is_active = True
                db.commit()
                partner_chat_id = item.submitted_by_chat_id
                title = item.title
        await query.edit_message_text(f"✅ Пропозицію «{title}» підтверджено та опубліковано!")
        # Повідомляємо надавача послуг
        if partner_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=partner_chat_id,
                    text=f"🎉 Ваша пропозиція *«{title}»* підтверджена адміністратором та вже видна ветеранам на платформі!",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    elif action == "reject":
        TEMP_DATA[chat_id] = TEMP_DATA.get(chat_id, {})
        TEMP_DATA[chat_id]["reject_opp_id"] = opp_id
        await context.bot.send_message(
            chat_id=chat_id,
            text="Вкажіть *причину відхилення* (вона буде надіслана надавачу послуг):",
            parse_mode="Markdown"
        )
        return ADMIN_REJECT_REASON

    # Перевіряємо чи є ще заявки
    data = TEMP_DATA.get(chat_id, {})
    idx = data.get("pending_index", 0) + 1
    pending_ids = data.get("pending_ids", [])

    if idx < len(pending_ids):
        TEMP_DATA[chat_id]["pending_index"] = idx
        with SessionLocal() as db:
            next_item = db.query(Opportunity).filter(Opportunity.id == pending_ids[idx]).first()
            if next_item and next_item.is_pending:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"Залишилось ще {len(pending_ids) - idx} заявок. Наступна:"
                )
                # Надсилаємо як нове повідомлення
                text = (
                    f"📩 *Нова заявка:*\n\n"
                    f"📌 *{next_item.title}* від *{next_item.partner_name}*\n"
                    f"📂 {next_item.type} | 📍 {next_item.location}\n"
                    f"📝 {next_item.description[:200]}...\n"
                    f"💰 {next_item.salary_range or 'За домовленістю'}"
                )
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Підтвердити", callback_data=f"approve:{next_item.id}"),
                    InlineKeyboardButton("❌ Відхилити", callback_data=f"reject:{next_item.id}"),
                ]])
                await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Всі заявки оброблено!",
            reply_markup=kb_admin()
        )

    return MENU

async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    reason = update.message.text.strip()
    opp_id = TEMP_DATA.get(chat_id, {}).get("reject_opp_id")

    partner_chat_id = None
    title = "невідома"
    if opp_id:
        with SessionLocal() as db:
            item = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if item:
                partner_chat_id = item.submitted_by_chat_id
                title = item.title
                item.is_pending = False
                item.is_active = False
                item.delete_reason = reason
                db.commit()

    await update.message.reply_text(
        f"❌ Пропозицію «{title}» відхилено.",
        reply_markup=kb_admin()
    )

    if partner_chat_id:
        try:
            await context.bot.send_message(
                chat_id=partner_chat_id,
                text=(
                    f"❌ Вашу пропозицію *«{title}»* адміністратор відхилив.\n\n"
                    f"*Причина:* {reason}\n\n"
                    f"Ви можете подати виправлену версію через «➕ Подати нову пропозицію»."
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass

    return MENU

# ── Перегляд активних пропозицій ─────────────────────────────────────────────

async def show_all_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    role = USER_ROLES.get(chat_id)
    with SessionLocal() as db:
        query = db.query(Opportunity).filter(Opportunity.is_active == True, Opportunity.is_pending == False)
        items = query.order_by(Opportunity.created_at.desc()).limit(10).all()

        if not items:
            await update.message.reply_text("В базі поки немає активних пропозицій.")
            return MENU

        msg = "📋 *Активні вакансії та програми:*\n\n"
        for i, item in enumerate(items, 1):
            msg += f"{i}. *{item.title}* ({item.partner_name})\n"
            msg += f"   {item.type} | {item.location} | {item.salary_range or 'За домовленістю'}\n\n"

    kb = kb_admin() if role == "admin" else kb_service_provider()
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)
    return MENU

# ── Мої пропозиції (для надавача послуг) ─────────────────────────────────────

async def show_my_opportunities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    with SessionLocal() as db:
        items = db.query(Opportunity).filter(
            Opportunity.submitted_by_chat_id == chat_id
        ).order_by(Opportunity.created_at.desc()).limit(15).all()

        if not items:
            await update.message.reply_text(
                "У вас поки немає поданих пропозицій.\nСкористайтеся «➕ Подати нову пропозицію».",
                reply_markup=kb_service_provider()
            )
            return MENU

        msg = "📋 *Ваші пропозиції:*\n\n"
        keyboards = []
        for item in items:
            status = "🟡 На розгляді" if item.is_pending else ("🟢 Активна" if item.is_active else "🔴 Відхилена/Видалена")
            msg += f"• *{item.title}* — {status}\n  ID: `{item.id[:12]}...`\n\n"
            if item.is_active or item.is_pending:
                keyboards.append([
                    InlineKeyboardButton(f"✏️ {item.title[:25]}", callback_data=f"edit:{item.id}"),
                    InlineKeyboardButton("🗑️ Видалити", callback_data=f"delete:{item.id}"),
                ])

        await update.message.reply_text(
            msg, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboards) if keyboards else None
        )
    return MENU

async def handle_manage_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    action, opp_id = query.data.split(":", 1)

    if action == "delete":
        # Перевіряємо, що це власна пропозиція
        with SessionLocal() as db:
            item = db.query(Opportunity).filter(
                Opportunity.id == opp_id,
                Opportunity.submitted_by_chat_id == chat_id
            ).first()
            if not item:
                await query.edit_message_text("⛔ Пропозицію не знайдено або у вас немає прав.")
                return MENU
            title = item.title

        TEMP_DATA[chat_id] = {"delete_opp_id": opp_id, "delete_title": title}
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Ви збираєтесь видалити «*{title}*».\n\n⚠️ Вкажіть *причину видалення* (вона збережеться в системі, щоб відповісти ветеранам, якщо вони запитають):",
            parse_mode="Markdown"
        )
        return DELETE_REASON

    if action == "edit":
        with SessionLocal() as db:
            item = db.query(Opportunity).filter(
                Opportunity.id == opp_id,
                Opportunity.submitted_by_chat_id == chat_id
            ).first()
            if not item:
                await query.edit_message_text("⛔ Пропозицію не знайдено або у вас немає прав.")
                return MENU

        TEMP_DATA[chat_id] = {"edit_opp_id": opp_id}
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Назва", callback_data=f"editf:title:{opp_id}"),
             InlineKeyboardButton("📝 Опис", callback_data=f"editf:description:{opp_id}")],
            [InlineKeyboardButton("🎖️ Переваги", callback_data=f"editf:benefits:{opp_id}"),
             InlineKeyboardButton("💰 Зарплата", callback_data=f"editf:salary_range:{opp_id}")],
        ])
        await query.edit_message_text(
            "✏️ Що хочете відредагувати?",
            reply_markup=keyboard
        )
        return EDIT_FIELD

    return MENU

async def handle_edit_field_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    _, field, opp_id = query.data.split(":", 2)

    TEMP_DATA[chat_id] = TEMP_DATA.get(chat_id, {})
    TEMP_DATA[chat_id]["edit_opp_id"] = opp_id
    TEMP_DATA[chat_id]["edit_field"] = field

    field_names = {
        "title": "нову назву",
        "description": "новий опис",
        "benefits": "нові переваги для ветеранів",
        "salary_range": "нову зарплату/розмір гранту"
    }
    await query.edit_message_text(f"Введіть {field_names.get(field, field)}:")
    return EDIT_VALUE

async def handle_edit_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    new_value = update.message.text.strip()
    data = TEMP_DATA.get(chat_id, {})
    opp_id = data.get("edit_opp_id")
    field = data.get("edit_field")

    allowed_fields = {"title", "description", "benefits", "salary_range"}
    if not opp_id or field not in allowed_fields:
        await update.message.reply_text("Помилка. Почніть знову.", reply_markup=kb_service_provider())
        return MENU

    with SessionLocal() as db:
        item = db.query(Opportunity).filter(
            Opportunity.id == opp_id,
            Opportunity.submitted_by_chat_id == chat_id
        ).first()
        if not item:
            await update.message.reply_text("⛔ Пропозицію не знайдено.", reply_markup=kb_service_provider())
            return MENU
        setattr(item, field, new_value)
        title = item.title
        db.commit()

    await update.message.reply_text(
        f"✅ Пропозицію «{title}» оновлено!",
        reply_markup=kb_service_provider()
    )
    return MENU

async def handle_delete_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    reason = update.message.text.strip()
    data = TEMP_DATA.get(chat_id, {})
    opp_id = data.get("delete_opp_id")
    title = data.get("delete_title", "невідома")

    if opp_id:
        with SessionLocal() as db:
            item = db.query(Opportunity).filter(
                Opportunity.id == opp_id,
                Opportunity.submitted_by_chat_id == chat_id
            ).first()
            if item:
                item.is_active = False
                item.is_pending = False
                item.delete_reason = reason
                db.commit()

    await update.message.reply_text(
        f"🗑️ Пропозицію «{title}» видалено.\n📝 Причина збережена: «{reason}»",
        reply_markup=kb_service_provider()
    )
    return MENU

# ── Зауваження та відгуки ─────────────────────────────────────────────────────

async def show_feedbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    with SessionLocal() as db:
        items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).limit(15).all()
        if not items:
            await update.message.reply_text("Зауважень поки немає!", reply_markup=kb_admin())
            return MENU

        msg = "📨 *Останні зауваження та відгуки:*\n\n"
        for f in items:
            cat_emoji = {"suggestion": "💡", "bug": "🐛", "partner": "🤝", "general": "❓"}.get(f.category, "📩")
            msg += f"{cat_emoji} [{f.category.upper()}] від *{f.sender_contact or 'Анонімно'}*\n"
            msg += f'  "{f.message}"\n'
            msg += f"  {f.created_at.strftime('%d.%m %H:%M')} | {f.source}\n\n"
            if len(msg) > 3500:
                msg += "_(ще більше у веб-панелі партнера)_"
                break

        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb_admin())
    return MENU

# ── Покроковий майстер додавання ─────────────────────────────────────────────

async def step_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["title"] = update.message.text.strip()
    await update.message.reply_text(
        "Введіть *назву вашої організації/компанії*:\n_(наприклад: Meest Пошта або Ветеранський фонд)_",
        parse_mode="Markdown"
    )
    return ADD_PARTNER

async def step_add_partner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["partner_name"] = update.message.text.strip()
    await update.message.reply_text(
        "Оберіть *тип пропозиції*:",
        reply_markup=ReplyKeyboardMarkup(
            [["vacancy", "course"], ["grant", "rehab"]], resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    return ADD_TYPE

async def step_add_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["type"] = update.message.text.strip()
    await update.message.reply_text(
        "Введіть *короткий опис* (обов'язки, умови участі, вимоги):",
        reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown"
    )
    return ADD_DESC

async def step_add_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["description"] = update.message.text.strip()
    await update.message.reply_text(
        "Вкажіть *ветеранські переваги*:\n_(гнучкий графік, ментор, допомога з житлом тощо)_",
        parse_mode="Markdown"
    )
    return ADD_BENEFITS

async def step_add_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id]["benefits"] = update.message.text.strip()
    await update.message.reply_text("Вкажіть *зарплату або розмір гранту* (або «За домовленістю»):", parse_mode="Markdown")
    return ADD_SALARY

async def step_add_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    role = USER_ROLES.get(chat_id)
    data = TEMP_DATA.get(chat_id, {})
    data["salary_range"] = update.message.text.strip()

    opp_type = data.get("type", "vacancy")
    title_lower = data.get("title", "").lower()
    category = (
        "IT" if "it" in title_lower or "програм" in title_lower
        else "logistics" if "логіст" in title_lower or "водій" in title_lower
        else "health" if "реаб" in title_lower or "медик" in title_lower
        else "business"
    )

    # Пряме додавання (адмін без модерації)
    is_direct = data.get("direct") or role == "admin"

    with SessionLocal() as db:
        new_opp = Opportunity(
            id=f"opp-{uuid.uuid4().hex[:10]}",
            partner_id=f"part-{chat_id}",
            partner_name=data.get("partner_name", "Партнер"),
            title=data.get("title", "Вакансія"),
            type=opp_type,
            category=category,
            location="Львів",
            description=data.get("description", ""),
            benefits=data.get("benefits", ""),
            salary_range=data.get("salary_range", ""),
            source="telegram_bot",
            submitted_by_chat_id=chat_id,
            is_active=is_direct,
            is_pending=not is_direct,
        )
        db.add(new_opp)
        db.commit()

    kb = kb_admin() if role == "admin" else kb_service_provider()

    if is_direct:
        msg = "🎉 *Опубліковано!* Ваша пропозиція вже доступна ветеранам."
    else:
        msg = (
            "📤 *Заявку подано!* Адміністратор розгляне її найближчим часом.\n"
            "Після підтвердження ваша пропозиція з'явиться на сайті, і ви отримаєте повідомлення."
        )

    await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
    return MENU

# ── Зауваження від надавача ───────────────────────────────────────────────────

async def step_add_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    role = USER_ROLES.get(chat_id)
    user_name = update.effective_user.username or update.effective_user.first_name or f"ID:{chat_id}"

    with SessionLocal() as db:
        fb = FeedbackItem(
            sender_name=user_name,
            sender_contact=f"@{update.effective_user.username}" if update.effective_user.username else f"tg:{chat_id}",
            category="partner",
            message=update.message.text.strip(),
            source="telegram_bot"
        )
        db.add(fb)
        db.commit()

    kb = kb_admin() if role == "admin" else kb_service_provider()
    await update.message.reply_text("🙏 Дякуємо! Зауваження передано адміністратору.", reply_markup=kb)
    return MENU

# ── Запуск бота ───────────────────────────────────────────────────────────────

def run_bot():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or token == "your_telegram_bot_token":
        logger.warning("TELEGRAM_BOT_TOKEN не задано в .env. Бот не запускається.")
        return

    app = ApplicationBuilder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AUTH:              [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auth)],
            MENU:              [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            ADD_TITLE:         [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_title)],
            ADD_PARTNER:       [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_partner)],
            ADD_TYPE:          [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_type)],
            ADD_DESC:          [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_desc)],
            ADD_BENEFITS:      [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_benefits)],
            ADD_SALARY:        [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_salary)],
            ADD_FEEDBACK:      [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_feedback)],
            EDIT_VALUE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_value)],
            DELETE_REASON:     [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_reason)],
            ADMIN_PENDING:     [CallbackQueryHandler(handle_pending_callback, pattern=r"^(approve|reject):")],
            ADMIN_REJECT_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reject_reason)],
            EDIT_FIELD:        [CallbackQueryHandler(handle_edit_field_callback, pattern=r"^editf:")],
        },
        fallbacks=[CommandHandler("start", start)],
        per_user=True,
        per_chat=True,
    )

    # CallbackQueryHandlers для кнопок "Мої пропозиції"
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(handle_manage_callback, pattern=r"^(edit|delete):"))
    app.add_handler(CallbackQueryHandler(handle_edit_field_callback, pattern=r"^editf:"))

    logger.info("Telegram-бот VeteranPath Lviv запущено!")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
