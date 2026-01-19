import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, ADMINS
import db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("cash.db")
cursor = conn.cursor()


def get_open_shift(admin_id):
    cursor.execute(
        "SELECT id FROM shifts WHERE admin_id=? AND is_open=1",
        (admin_id,)
    )
    return cursor.fetchone()


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    if msg.from_user.id not in ADMINS:
        await msg.answer("❌ У вас нет доступа")
        return

    await msg.answer(
        "💼 Кассовый бот\n\n"
        "/open — открыть смену\n"
        "/expense — добавить расход\n"
        "/close — закрыть смену"
    )


@dp.message_handler(commands=["open"])
async def open_shift(msg: types.Message):
    if get_open_shift(msg.from_user.id):
        await msg.answer("⚠️ Смена уже открыта")
        return

    await msg.answer("💵 Введите начальную сумму в кассе:")

    @dp.message_handler()
    async def save_start_cash(m: types.Message):
        try:
            cash = float(m.text)
        except:
            await m.answer("❌ Введите число")
            return

        cursor.execute(
            "INSERT INTO shifts (admin_id, start_cash, is_open) VALUES (?, ?, 1)",
            (m.from_user.id, cash)
        )
        conn.commit()

        await m.answer("✅ Смена открыта")


@dp.message_handler(commands=["expense"])
async def expense(msg: types.Message):
    shift = get_open_shift(msg.from_user.id)
    if not shift:
        await msg.answer("❌ Смена не открыта")
        return

    await msg.answer("💸 Введите сумму расхода:")

    @dp.message_handler()
    async def save_amount(m: types.Message):
        try:
            amount = float(m.text)
        except:
            await m.answer("❌ Введите число")
            return

        await m.answer("✏️ Напишите комментарий:")

        @dp.message_handler()
        async def save_comment(mm: types.Message):
            cursor.execute(
                "INSERT INTO expenses (shift_id, amount, comment) VALUES (?, ?, ?)",
                (shift[0], amount, mm.text)
            )
            conn.commit()

            await mm.answer("✅ Расход сохранён")


@dp.message_handler(commands=["close"])
async def close_shift(msg: types.Message):
    shift = get_open_shift(msg.from_user.id)
    if not shift:
        await msg.answer("❌ Нет открытой смены")
        return

    await msg.answer("💰 Введите конечную сумму в кассе:")

    @dp.message_handler()
    async def save_end_cash(m: types.Message):
        try:
            end_cash = float(m.text)
        except:
            await m.answer("❌ Введите число")
            return

        cursor.execute("SELECT start_cash FROM shifts WHERE id=?", (shift[0],))
        start_cash = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM expenses WHERE shift_id=?", (shift[0],))
        total_expense = cursor.fetchone()[0] or 0

        expected = start_cash - total_expense
        diff = end_cash - expected

        cursor.execute(
            "UPDATE shifts SET end_cash=?, is_open=0 WHERE id=?",
            (end_cash, shift[0])
        )
        conn.commit()

        await m.answer(
            f"📊 Отчёт смены\n\n"
            f"Начальная касса: {start_cash}\n"
            f"Расходы: {total_expense}\n"
            f"Ожидаемая касса: {expected}\n"
            f"Фактическая касса: {end_cash}\n"
            f"Разница: {diff}"
        )


if __name__ == "__main__":
    executor.start_polling(dp)
