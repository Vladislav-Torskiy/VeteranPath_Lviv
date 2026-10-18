"""
Telegram-бот для платформи VeteranPath Lviv
Система ролей:
  - Надавач послуг (service_provider):
      * Подає нову пропозицію (вакансію, курс, грант) -> вона потрапляє на розгляд адміну
      * Переглядає всі активні програми на платформі
      * Може подати запит на деактивацію/видалення своєї пропозиції
      * Залишає відгуки та пропозиції
  - Адміністратор (admin):
      * Модерує пропозиції (підтвердити / відхилити з вказанням причини)
      * Переглядає всі пропозиції в базі
      * Може ВИДАЛЯТИ будь-яку пропозицію/вакансію з бази із обов'язковим вказанням причини
      * Додає пропозиції напряму
      * Переглядає всі зауваження та звернення
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
    PARTNER_REQUEST_DELETE,
    ADMIN_DELETE_REASON,
    ADMIN_PENDING,
    ADMIN_REJECT_REASON,
) = range(13)

USER_ROLES = {}   # chat_id -> "service_provider" | "admin"
TEMP_DATA  = {}   # chat_id -> dict з тимчасовими даними

# ── Клавіатури ───────────────────────────────────────────────────────────────

def kb_service_provider():
    return ReplyKeyboardMarkup([
        ["➕ Подати нову пропозицію"],
        ["📋 Активні програми на платформі"],
        ["🗑️ Запит адміністратору на видалення"],
        ["✍️ Залишити зауваження/відгук"],
        ["🚪 Вийти"],
    ], resize_keyboard=True)

def kb_admin():
    return ReplyKeyboardMarkup([
        ["🔔 Пропозиції на розгляді (модерація)"],
        ["📊 Керування пропозиціями (перегляд/видалення)"],
        ["📨 Зауваження та відгуки користувачів"],
        ["➕ Додати пропозицію напряму"],
        ["🚪 Вийти"],
    ], resize_keyboard=True)

# ── Авторизація ──────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    USER_ROLES.pop(chat_id, None)
    TEMP_DATA.pop(chat_id, None)
    await update.message.reply_text(
        "🇺🇦 *Вітаємо в Telegram-боті VeteranPath Lviv!*\n\n"
        "Введіть пароль для входу:\n"
        "• Якщо ви партнер / надавач послуг — введіть пароль *надавача*\n"
        "• Якщо ви адміністратор платформи — введіть пароль *адміністратора*",
        parse_mode="Markdown"
    )
    return AUTH

async def handle_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    pwd = update.message.text.strip()

    if pwd == settings.TELEGRAM_ADMIN_PASSWORD:
        USER_ROLES[chat_id] = "admin"
        await update.message.reply_text(
            "✅ *Авторизовано як Адміністратор платформи!*\n"
            "Вам доступне повне керування, затвердження та видалення вакансій/програм.",
            reply_markup=kb_admin(), parse_mode="Markdown"
        )
        return MENU
    elif pwd == settings.TELEGRAM_PARTNER_PASSWORD:
        USER_ROLES[chat_id] = "service_provider"
        await update.message.reply_text(
            "✅ *Авторизовано як Надавач послуг (Партнер)!*\n"
            "Ви можете подавати нові програми та вакансії на модерацію адміністратору.",
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

    if text == "🚪 Вийти":
        USER_ROLES.pop(chat_id, None)
        TEMP_DATA.pop(chat_id, None)
        await update.message.reply_text(
            "Ви вийшли з кабінету. Введіть /start для нового входу.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # ─── Надавач послуг ───
    if text == "➕ Подати нову пропозицію":
        TEMP_DATA[chat_id] = {}
        await update.message.reply_text(
            "Введіть *назву* вакансії, курсу або гранту:\n_(наприклад: «Координатор логістики» або «Грант на обладнання»)_",
            reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown"
        )
        return ADD_TITLE

    if text in ["📋 Активні програми на платформі", "📋 Мої пропозиції (редагувати/видалити)"]:
        return await show_all_active(update, context)

    if text == "🗑️ Запит адміністратору на видалення":
        await update.message.reply_text(
            "Вкажіть назву вашої вакансії/програми та *причину видалення*:\n"
            "_(Адміністратор отримає запит і деактивує пропозицію в системі)_",
            reply_markup=ReplyKeyboardRemove()
        )
        return PARTNER_REQUEST_DELETE

    if text == "✍️ Залишити зауваження/відгук":
        await update.message.reply_text(
            "Напишіть ваше зауваження, побажання або запитання:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADD_FEEDBACK

    # ─── Адміністратор ───
    if text in ["🔔 Пропозиції на розгляді (модерація)", "🔔 Пропозиції на розгляді (підтвердити/відхилити)"]:
        if role != "admin":
            await update.message.reply_text("⛔ Доступно лише адміністратору.")
            return MENU
        return await show_pending(update, context)

    if text in ["📊 Керування пропозиціями (перегляд/видалення)", "📊 Всі активні пропозиції в базі"]:
        if role != "admin":
            return await show_all_active(update, context)
        return await admin_show_manageable_opportunities(update, context)

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

# ── Перегляд та видалення для Адміністратора ──────────────────────────────────

async def admin_show_manageable_opportunities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    with SessionLocal() as db:
        items = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.is_pending == False
        ).order_by(Opportunity.created_at.desc()).limit(20).all()

        if not items:
            await update.message.reply_text(
                "Наразі немає активних пропозицій у базі даних.",
                reply_markup=kb_admin()
            )
            return MENU

        msg = "📊 *Керування пропозиціями на платформі:*\n\nОберіть пропозицію, яку потрібно видалити:\n\n"
        keyboards = []
        for i, item in enumerate(items, 1):
            msg += f"{i}. *{item.title}*\n   Партнер: _{item.partner_name}_ | {item.location}\n\n"
            keyboards.append([
                InlineKeyboardButton(f"🗑️ Видалити: {item.title[:24]}", callback_data=f"adm_del:{item.id}")
            ])

        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboards) if keyboards else None
        )
    return MENU

async def handle_admin_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    _, opp_id = query.data.split(":", 1)

    with SessionLocal() as db:
        item = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
        if not item:
            await query.edit_message_text("⛔ Пропозицію вже не знайдено.")
            return MENU
        title = item.title

    TEMP_DATA[chat_id] = {"admin_del_id": opp_id, "admin_del_title": title}
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"⚠️ Ви обрали видалення: *«{title}»*.\n\n"
            f"Вкажіть *причину видалення* (напишіть повідомленням у чат):"
        ),
        parse_mode="Markdown"
    )
    return ADMIN_DELETE_REASON

async def handle_admin_delete_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    reason = update.message.text.strip()
    data = TEMP_DATA.get(chat_id, {})
    opp_id = data.get("admin_del_id")
    title = data.get("admin_del_title", "пропозиція")

    partner_chat_id = None
    if opp_id:
        with SessionLocal() as db:
            item = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if item:
                item.is_active = False
                item.is_pending = False
                item.delete_reason = reason
                partner_chat_id = item.submitted_by_chat_id
                title = item.title
                db.commit()

    await update.message.reply_text(
        f"🗑️ Пропозицію *«{title}»* успішно деактивовано з сайту та бази!\n"
        f"📝 Причина зафіксована: _{reason}_",
        parse_mode="Markdown",
        reply_markup=kb_admin()
    )

    if partner_chat_id:
        try:
            await context.bot.send_message(
                chat_id=partner_chat_id,
                text=(
                    f"ℹ️ Вашу вакансію/програму *«{title}»* було знято з публікації адміністратором.\n\n"
                    f"*Причина:* {reason}"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass

    return MENU

# ── Запит на видалення від надавача послуг ────────────────────────────────────

async def handle_partner_request_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    user_name = update.effective_user.username or update.effective_user.first_name or f"ID:{chat_id}"
    req_text = update.message.text.strip()

    with SessionLocal() as db:
        fb = FeedbackItem(
            sender_name=f"Партнер {user_name}",
            sender_contact=f"@{update.effective_user.username}" if update.effective_user.username else f"tg:{chat_id}",
            category="deletion_request",
            message=f"[ЗАПИТ НА ВИДАЛЕННЯ]: {req_text}",
            source="telegram_bot"
        )
        db.add(fb)
        db.commit()

    await update.message.reply_text(
        "✅ Ваш запит на видалення успішно надіслано адміністратору платформи.\n"
        "Адміністратор перевірить заявку та деактивує пропозицію.",
        reply_markup=kb_service_provider()
    )
    return MENU

# ── Перегляд пропозицій на розгляді (Адмін модерація) ────────────────────────

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
        await show_pending_item(update, context, items[0])
    return ADMIN_PENDING

async def show_pending_item(update, context, item):
    text = (
        f"📩 *Заявка на модерацію:*\n\n"
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
                partner_chat_id = item.submitted_by_chat_id
                title = item.title
                db.commit()
            else:
                title = "пропозиція"
                partner_chat_id = None

        await query.edit_message_text(f"✅ Пропозицію «{title}» схвалено та опубліковано на сайті!")
        if partner_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=partner_chat_id,
                    text=f"🎉 Ваша пропозиція *«{title}»* підтверджена адміністратором та вже опублікована для ветеранів!",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    elif action == "reject":
        TEMP_DATA[chat_id] = TEMP_DATA.get(chat_id, {})
        TEMP_DATA[chat_id]["reject_opp_id"] = opp_id
        await context.bot.send_message(
            chat_id=chat_id,
            text="Вкажіть *причину відхилення* (вона збережеться і буде передана надавачу):",
            parse_mode="Markdown"
        )
        return ADMIN_REJECT_REASON

    # Перевірка наступних заявок
    data = TEMP_DATA.get(chat_id, {})
    idx = data.get("pending_index", 0) + 1
    pending_ids = data.get("pending_ids", [])

    if idx < len(pending_ids):
        TEMP_DATA[chat_id]["pending_index"] = idx
        with SessionLocal() as db:
            next_item = db.query(Opportunity).filter(Opportunity.id == pending_ids[idx]).first()
            if next_item and next_item.is_pending:
                text = (
                    f"📩 *Наступна заявка ({idx + 1}/{len(pending_ids)}):*\n\n"
                    f"📌 *{next_item.title}* від *{next_item.partner_name}*\n"
                    f"📂 {next_item.type} | 📍 {next_item.location}\n"
                    f"📝 {next_item.description[:180]}...\n"
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
            text="✅ Всі заявки з черги розглянуто!",
            reply_markup=kb_admin()
        )

    return MENU

async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    reason = update.message.text.strip()
    opp_id = TEMP_DATA.get(chat_id, {}).get("reject_opp_id")

    partner_chat_id = None
    title = "пропозиція"
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
        f"❌ Пропозицію «{title}» відхилено. Причина збережена: _{reason}_",
        parse_mode="Markdown",
        reply_markup=kb_admin()
    )

    if partner_chat_id:
        try:
            await context.bot.send_message(
                chat_id=partner_chat_id,
                text=(
                    f"❌ Вашу пропозицію *«{title}»* відхилено адміністратором.\n\n"
                    f"*Причина:* {reason}\n\n"
                    f"Ви можете внести корективи та подати нову заявку."
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass

    return MENU

# ── Перегляд активних програм (для надавача) ──────────────────────────────────

async def show_all_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    role = USER_ROLES.get(chat_id)
    with SessionLocal() as db:
        items = db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.is_pending == False
        ).order_by(Opportunity.created_at.desc()).limit(15).all()

        if not items:
            await update.message.reply_text("Наразі немає активних пропозицій у базі.")
            return MENU

        msg = "📋 *Активні вакансії та програми на платформі:*\n\n"
        for i, item in enumerate(items, 1):
            msg += f"{i}. *{item.title}* ({item.partner_name})\n"
            msg += f"   Тип: {item.type} | Локація: {item.location} | З/П або Грант: {item.salary_range or 'За домовленістю'}\n\n"

    kb = kb_admin() if role == "admin" else kb_service_provider()
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)
    return MENU

# ── Зауваження та відгуки (для адміна) ────────────────────────────────────────

async def show_feedbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    with SessionLocal() as db:
        items = db.query(FeedbackItem).order_by(FeedbackItem.created_at.desc()).limit(15).all()
        if not items:
            await update.message.reply_text("Зауважень та звернень поки немає!", reply_markup=kb_admin())
            return MENU

        msg = "📨 *Останні звернення, відгуки та запити:*\n\n"
        for f in items:
            cat_emoji = {
                "suggestion": "💡",
                "bug": "🐛",
                "partner": "🤝",
                "general": "❓",
                "deletion_request": "🗑️"
            }.get(f.category, "📩")
            msg += f"{cat_emoji} *[{f.category.upper()}]* від *{f.sender_contact or f.sender_name or 'Користувач'}*\n"
            msg += f'  "{f.message}"\n'
            msg += f"  Час: {f.created_at.strftime('%d.%m %H:%M')} | Джерело: {f.source}\n\n"

        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb_admin())
    return MENU

# ── Покроковий майстер додавання пропозиції ──────────────────────────────────

async def step_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    TEMP_DATA[chat_id] = TEMP_DATA.get(chat_id, {})
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
        "Вкажіть *ветеранські переваги*:\n_(гнучкий графік, ментор з бойовим досвідом, допомога з житлом тощо)_",
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
        msg = "🎉 *Опубліковано!* Ваша пропозиція вже активна на сайті."
    else:
        msg = (
            "📤 *Заявку подано на модерацію!* Адміністратор платформи перегляне її.\n"
            "Після схвалення вона одразу з'явиться для ветеранів, і ви отримаєте повідомлення в боті."
        )

    await update.message.reply_text(msg, reply_markup=kb, parse_mode="Markdown")
    return MENU

# ── Зауваження від партнера ───────────────────────────────────────────────────

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
    await update.message.reply_text("🙏 Дякуємо! Ваше звернення передано адміністратору платформи.", reply_markup=kb)
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
            AUTH:                   [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_auth)],
            MENU:                   [
                CallbackQueryHandler(handle_admin_delete_callback, pattern=r"^adm_del:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)
            ],
            ADD_TITLE:              [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_title)],
            ADD_PARTNER:            [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_partner)],
            ADD_TYPE:               [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_type)],
            ADD_DESC:               [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_desc)],
            ADD_BENEFITS:           [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_benefits)],
            ADD_SALARY:             [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_salary)],
            ADD_FEEDBACK:           [MessageHandler(filters.TEXT & ~filters.COMMAND, step_add_feedback)],
            PARTNER_REQUEST_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_partner_request_delete)],
            ADMIN_DELETE_REASON:    [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_delete_reason)],
            ADMIN_PENDING:          [CallbackQueryHandler(handle_pending_callback, pattern=r"^(approve|reject):")],
            ADMIN_REJECT_REASON:    [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reject_reason)],
        },
        fallbacks=[CommandHandler("start", start)],
        per_user=True,
        per_chat=True,
    )

    app.add_handler(conv)

    logger.info("Telegram-бот VeteranPath Lviv запущено!")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
