from bot import bot
from io import BytesIO

async def download_file_BytesIo(file_id: str) -> BytesIO:
    #file_info = await bot.get_file(file_id)
    #return await bot.download_file(file_info.file_path)
    
    # TODO aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: file is too big
    return await bot.download(file_id)

async def download_file_bytes(file_id: str) -> bytes:
    return (await download_file_BytesIo(file_id)).getvalue()

