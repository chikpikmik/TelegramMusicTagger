from setting import TOKEN, USE_LOCAL_BOT_API, LOCAL_BOT_API_BASE

from aiogram import Bot
#from aiogram.client.session import AiohttpSession
#from aiogram.client.telegram import TelegramAPIServer

if USE_LOCAL_BOT_API:
    pass
    #session = AiohttpSession(
    #    api=TelegramAPIServer.from_base(LOCAL_BOT_API_BASE)
    #)
    #bot = Bot(token=TOKEN, session=session)
else:
    bot = Bot(token=TOKEN)
