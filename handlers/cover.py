from aiogram import F, Router, filters
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from my_states import MyStates
from services.file_service import download_file_bytes

router = Router()

#TODO режим удаления обложек с аудио

@router.message(filters.Command('setcover'))
async def handle_setcover(message: Message, state: FSMContext):
    await state.set_state(MyStates.cover)
    await message.answer("Пришлите фото обложки")

@router.message(F.photo, MyStates.cover)
async def set_cover(message: Message, state: FSMContext):
    # TODO стирка изображений по таймеру
    big_file_id    = message.photo[-1].file_id
    little_file_id = message.photo[0].file_id
    
    await state.update_data(
        cover     = await download_file_bytes(big_file_id),
        cover_id  = big_file_id,
        thumbnail = await download_file_bytes(little_file_id)
        )

    await message.answer("Обложка сохранена")
    await state.set_state()

@router.message(MyStates.cover)
async def set_cover_incorrect(message: Message):
    # TODO добавь кнопку отмены т.е. await bot.set_state(message.from_user.id, "*", message.chat.id)
    await message.answer("Пришлите фото обложки, а не что то другое")

@router.message(filters.Command('resetcover'))
async def reset_cover(message: Message, state: FSMContext):
    await state.set_state()
    await state.update_data(
        cover     = None,
        cover_id  = None,
        thumbnail = None
        )
    await message.answer("Удалено")

@router.message(filters.Command('sendcover'))
async def handle_sendcover(message: Message, state: FSMContext):
    # TODO обработка ситуации когда еще не было set_state
    cover_id = (await state.get_data()).get('cover_id')
    if cover_id:
        await message.answer_photo(cover_id)
    else:
        await message.answer("Обложка не задана")
