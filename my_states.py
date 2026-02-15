from aiogram.fsm.state import State, StatesGroup

class MyStates(StatesGroup):
    cover = State()
    musician  = State()
    song = State()
    view_tags = State()