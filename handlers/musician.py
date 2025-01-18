from aiogram import Router, filters
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from my_states import MyStates

router = Router()


@router.message(filters.Command('setmusician'))
async def handle_setmusician(message: Message, state: FSMContext):
    await message.answer("Введите исполнителя")
    await state.set_state(MyStates.musician)

@router.message(MyStates.musician)
async def set_musician(message: Message, state: FSMContext):
    # TODO добавь кнопку отмены т.е. await bot.set_state(message.from_user.id, "*", message.chat.id)
    if message.text:
        await state.update_data(musician = message.text)
        await state.set_state()
        await message.answer("Cохранено")
    else:
        await message.answer("Введите имя исполнителя, а не что то другое")

@router.message(filters.Command('resetmusician'))
async def reset_musician(message: Message, state: FSMContext):
    await state.set_state()
    await state.update_data(musician = None)
    await message.answer("Удалено")
