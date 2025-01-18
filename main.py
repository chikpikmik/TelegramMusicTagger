import logging
import sys
from aiogram import Bot, Dispatcher
import asyncio

from setting import PRIVATE_SERVER_HOST, PRIVATE_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL, USE_WEBHOOK
from handlers import dp
from bot import bot



# Webhook startup handler
async def on_startup(bot: Bot) -> None:
    logging.info(f"Setting up webhook for bot: {bot}")
    await bot.set_webhook(
        url=BASE_WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET
    )
    logging.info(f"Webhook set at: {BASE_WEBHOOK_URL}")

# Polling handler
async def on_shutdown(dp: Dispatcher) -> None:
    logging.info("Shutting down...")
    await dp.storage.close()
    await dp.storage.wait_closed()

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    if USE_WEBHOOK:
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
        from aiohttp import web

        app = web.Application()
        
        dp.startup.register(on_startup)
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        setup_application(app, dp, bot=bot)

        logging.info(f"Running app at {PRIVATE_SERVER_HOST}:{PRIVATE_SERVER_PORT} with webhook.")
        web.run_app(
            app=app,
            host=PRIVATE_SERVER_HOST,
            port=PRIVATE_SERVER_PORT,
        )
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
