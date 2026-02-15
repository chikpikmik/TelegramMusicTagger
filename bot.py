from setting import TOKEN, USE_LOCAL_BOT_API, LOCAL_BOT_API_BASE

from aiogram import Bot


bot = Bot(token=TOKEN)

#if USE_LOCAL_BOT_API:
#    pass
    #from aiogram.client.session.aiohttp import AiohttpSession
    #from aiogram.client.telegram import TelegramAPIServer
    #session = AiohttpSession(api=TelegramAPIServer.from_base(LOCAL_BOT_API_BASE))
    #bot = Bot(token=TOKEN, session=session)
#else:
#    bot = Bot(token=TOKEN)
