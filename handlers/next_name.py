from aiogram import Router, filters
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from my_states import MyStates

router = Router()

@router.message(filters.Command('renamenext'))
async def handle_setnext(message: Message, state: FSMContext):
    await message.answer("Введите название композиции")
    await state.set_state(MyStates.song)

@router.message(MyStates.song)
async def set_next(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(song = message.text)
        await state.set_state()
        await message.answer("следующая композиция будет так называться, или повторите команду для сброса")
    else:
        await message.answer("Введите название композиции, а не что то другое")

 