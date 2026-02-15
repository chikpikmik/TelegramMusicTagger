import logging

from bot import bot
from io import BytesIO
from aiogram.exceptions import TelegramBadRequest


async def download_file_BytesIo(file_id: str) -> BytesIO:
    try:
        file = await bot.get_file(file_id)
        buffer = BytesIO()
        await bot.download_file(file.file_path, buffer)
        buffer.seek(0)
        return buffer
    except TelegramBadRequest as e:
        if "too big" in str(e).lower():
            logging.warning("TelegramBotAPI: file is too big (file_id=%s)", file_id)
            raise
        raise

async def download_file_bytes(file_id: str) -> bytes:
    return (await download_file_BytesIo(file_id)).getvalue()

