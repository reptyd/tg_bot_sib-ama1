import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from config import TOKEN
from handlers import user, operator

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def set_bot_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать обращение"),
        BotCommand(command="help", description="Как пользоваться ботом")
    ])

async def start_bot():
    await set_bot_commands()
    dp.include_router(user.router)
    dp.include_router(operator.router)
    await dp.start_polling(bot)

# --- HTTP-заглушка для Render ---
async def handle(request):
    return web.Response(text="Telegram bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- Совместный запуск ---
async def main():
    await asyncio.gather(
        start_bot(),
        start_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
