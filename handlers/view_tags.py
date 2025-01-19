from aiogram import Router, filters, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from my_states import MyStates

from services import download_file_BytesIo, AudioID3


router = Router()


@router.message(filters.Command('view_tags'))
async def handle_set_view_tags(message: Message, state: FSMContext):
    await state.set_state(MyStates.view_tags)
    await message.answer("Установлен режим просмотра тегов")

@router.message(F.audio, MyStates.view_tags)
async def audio_view_tags(message: Message, state: FSMContext):
    
    downloaded_file = await download_file_BytesIo(message.audio.file_id)
    
    audio = AudioID3(downloaded_file)


    nocover = ""
    if audio.cover_image: 
        await message.answer_photo(
            photo=BufferedInputFile(audio.cover_image, filename='cover'),
            caption='cover :'
        )
    else: nocover = "cover : None\n"

    await message.answer(
        nocover +
        f"file name : {message.audio.file_name} \n" + 
        f"song : {audio.song} \n" + 
        f"musician: {audio.musician} \n" + 
        f"composer: {audio.composer} \n" + 
        f"album : {audio.album} \n" + 
        f"genre : {audio.genre} \n" + 
        f"released : {audio.released} \n" + 
        f"track_number: {audio.track_number} \n" + 
        f"lyrics: {audio.lyrics}"
        
    )




@router.message(filters.Command('reset_view_tags'))
async def reset_musician(message: Message, state: FSMContext):
    await state.set_state()
    await state.update_data(view_tags = None)
    await message.answer("Режим просмотра тегов сброшен")
