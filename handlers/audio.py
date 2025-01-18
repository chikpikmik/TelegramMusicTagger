from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from services import download_file_BytesIo, AudioID3, MessageQueue, extract_audio_info
import asyncio


router = Router()

message_queue = MessageQueue()
 
@router.message(F.audio)
async def handle_audio(message: Message, state: FSMContext):

    await state.set_state()
    data = await state.get_data()

    send_in_queue  = True #data.get('send_in_queue')  # отсылать в том же порядке что и присланы


    if send_in_queue: message_queue.add_message(message.chat.id, message.from_user.id, message.message_id)

        
    file_name = message.audio.file_name.replace('_',' ').replace('.mp3','')
    downloaded_file = await download_file_BytesIo(message.audio.file_id)
    
    #if AudioID3.isItID3(downloaded_file): 
    audio = AudioID3(downloaded_file)

    #else: await message.answer(f"{file_name} это не подходящий формат аудиофайла"); return
    
    cover          = data.get('cover')          or audio.cover_image
    thumbnail      = data.get('thumbnail')      or audio.create_cover_thumbnail()

    musician       = data.get('musician')       or audio.musician
    composer       = data.get('composer')       or audio.composer

    released       = data.get('released')       or audio.released # год выпуска
    genre          = data.get('genre')          or audio.genre
    lyrics         = data.get('lyrics')         or audio.lyrics


    album          = data.get('album')          or audio.album
    track_number   = data.get('track_number')   or audio.track_number # номер трека в альбоме
    send_in_track_number_order \
                   = False #data.get('send_in_track_number_order')
    
    digits_in_song = True #data.get('digits_in_song') # может ли начало трека содержать число
    
    song           = data.get('song')           or audio.song



    if data.get('song'): await state.update_data(song = None)

    musician, song, track_number = extract_audio_info(file_name, musician, song, track_number, digits_in_song)

    # Если данные не удалось извлечь, отправляем запрос пользователю
    if not musician or not song:
        message_queue.remove_next_message(message.chat.id, message.from_user.id)
        await message.answer(message, "Установите исполнителя или отправьте файл с названием вида: <Исполнитель> - <Композиция>.")
        return

    audio.update_tags(song, musician, album, genre, released, composer, track_number, lyrics, cover)
    
    if send_in_queue:
        while message.message_id != message_queue.get_next_message(message.chat.id, message.from_user.id):
            await asyncio.sleep(2)
    
    await message.answer_audio(
        audio     = BufferedInputFile(audio.get_file(), filename=f'{musician} - {song}.mp3'),
        thumbnail = BufferedInputFile(thumbnail, filename='thumbnail')
        )
    
    if send_in_queue: message_queue.remove_next_message(message.chat.id, message.from_user.id)



