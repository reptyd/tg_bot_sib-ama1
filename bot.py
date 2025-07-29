import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import TOKEN
from handlers import user, operator

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
async def set_bot_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать обращение"),
        BotCommand(command="help", description="Как пользоваться ботом")
    ])
async def main():
    dp.include_router(user.router)
    dp.include_router(operator.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
