from aiogram import Router, filters
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from my_states import MyStates

router = Router()

@router.message(filters.Command('renamenext'))
async def handle_setnext(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get('song') or (await state.get_state()) == MyStates.song:
        await state.update_data(song = None)
        await state.set_state()
        await message.answer("Cброшено")
        return

    await message.answer(f"Введите название следующей композиции.\nДля сброса: /renamenext")
    await state.set_state(MyStates.song)

@router.message(MyStates.song)
async def set_next(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(song = message.text)
        await state.set_state()
        await message.answer("Название установлено.\nДля сброса: /renamenext")
    else:
        await message.answer("Введите название композиции, а не что то другое")

 