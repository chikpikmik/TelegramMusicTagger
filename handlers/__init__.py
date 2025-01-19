from aiogram import Dispatcher

from .cover     import router
from .musician  import router
from .audio     import router
from .next_name import router
# TODO вывод атрибутов без изменения
# альбом, жанр и другие атрибуты

dp = Dispatcher()

dp.include_router(cover.router)
dp.include_router(musician.router)
dp.include_router(audio.router)
dp.include_router(next_name.router)