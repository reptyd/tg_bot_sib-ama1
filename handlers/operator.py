from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ticket_db import (
    get_open_tickets,
    get_ticket_by_id,
    close_ticket_by_user_id,
    delete_ticket_by_user_id,
    get_tickets_by_category
)
from config import OPERATOR_IDS

router = Router()

class Operator(StatesGroup):
    replying_to = State()

CATEGORY_MAP = {
    "common": "Общие вопросы",
    "payment": "Вопрос по оплате",
    "quality": "Качество сервиса"
}

def operator_actions(ticket_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответить", callback_data=f"reply_{ticket_id}")],
        [InlineKeyboardButton(text="Закрыть", callback_data=f"close_{ticket_id}")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"delete_{ticket_id}")]
    ])

@router.callback_query(F.data.startswith("reply_"))
async def reply_ticket(call: CallbackQuery, state: FSMContext):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await call.answer("Тикет не найден.")
        return

    await state.set_state(Operator.replying_to)
    await state.update_data(ticket=ticket)
    await call.message.answer(f"✍️ Напишите ответ пользователю @{ticket['username'] or 'Без username'}")
    await call.answer()

@router.message(Operator.replying_to)
async def send_operator_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket = data.get("ticket")
    if ticket:
        await message.bot.send_message(
            ticket["user_id"],
            f"<b>Оператор Дуся:</b>\n{message.text}"
        )
        await message.answer("✅ Ответ отправлен пользователю.")
    await state.clear()

@router.callback_query(F.data.startswith("close_"))
async def close_ticket(call: CallbackQuery):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await call.answer("Тикет не найден.")
        return
    close_ticket_by_user_id(ticket["user_id"])
    await call.message.edit_text("Обращение закрыто.")
    await call.answer("Закрыто.")

@router.callback_query(F.data.startswith("delete_"))
async def delete_ticket(call: CallbackQuery):
    ticket_id = int(call.data.split("_")[1])
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await call.answer("Тикет не найден.")
        return
    delete_ticket_by_user_id(ticket["user_id"])
    await call.message.edit_text("Обращение удалено.")
    await call.answer("Удалено.")

@router.message(F.text.startswith("/view "))
async def view_ticket(message: Message):
    if message.chat.id not in OPERATOR_IDS:
        return

    try:
        ticket_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат. Используйте /view <id>")
        return

    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await message.answer("❌ Тикет с таким ID не найден.")
        return

    caption = (
        f"<b>Тикет #{ticket['id']}</b>\n"
        f"Категория: {CATEGORY_MAP.get(ticket['category'], ticket['category'])}\n"
        f"Пользователь: @{ticket['username']}\n"
        f"Статус: {ticket['status']}\n"
        f"Создан: {ticket['created_at']}\n\n"
        f"{ticket['text']}"
    )

    reply_markup = operator_actions(ticket["id"])

    if ticket["photo"]:
        await message.bot.send_photo(message.chat.id, photo=ticket["photo"], caption=caption, reply_markup=reply_markup)
    else:
        await message.answer(caption, reply_markup=reply_markup)

@router.message(F.text == "/list")
async def list_tickets(message: Message):
    if message.chat.id not in OPERATOR_IDS:
        return

    tickets = get_open_tickets()
    if not tickets:
        await message.answer("Нет открытых обращений.")
        return

    text = "\n\n".join([
        f"#{t['id']} | @{t['username']} | {CATEGORY_MAP.get(t['category'], t['category'])}\n{t['text'][:100]}..."
        for t in tickets
    ])
    await message.answer(f"<b>Открытые обращения:</b>\n\n{text}")

@router.message(F.text == "/архив")
async def archive_menu(message: Message):
    if message.chat.id not in OPERATOR_IDS:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Общие вопросы", callback_data="archive_common")],
        [InlineKeyboardButton(text="Вопрос по оплате", callback_data="archive_payment")],
        [InlineKeyboardButton(text="Качество сервиса", callback_data="archive_quality")],
    ])
    await message.answer("📁 Архив обращений:\nВыберите категорию:", reply_markup=kb)

@router.callback_query(F.data.startswith("archive_"))
async def show_category_archive(call: CallbackQuery):
    category_key = call.data.replace("archive_", "")
    tickets = get_tickets_by_category(category_key)
    if not tickets:
        await call.message.answer("Обращений по этой категории пока нет.")
        await call.answer()
        return

    text = f"📂 <b>{CATEGORY_MAP.get(category_key, category_key)}</b>\n\n"
    for t in tickets:
        text += f"#{t['id']} | @{t['username']} | {t['text'][:60]}...\n/view {t['id']}\n\n"

    await call.message.answer(text)
    await call.answer()
