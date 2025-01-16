from aiogram import F, Bot, Dispatcher, filters, Router
from aiogram.types import Message, BufferedInputFile, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, APIC, TDRL, TORY, TXXX, TBPM, TEXT, TCOM, TCON #TDRS
from PIL import Image
from typing import Dict, List

import asyncio
import logging

import io
import sys
import re

from setting import TOKEN, PRIVATE_SERVER_HOST, PRIVATE_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL

router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)

from aiohttp import web
app = web.Application()


global message_queue
message_queue: Dict[int, Dict[int, List[int]]] = {}

class MyStates(StatesGroup):
    cover = State()
    musician  = State()
    song = State()
    audios = State()

# TODO Сделать одну команду для set и reset
# Добавить установщики/сбрасыватели всех настроек
# обработка ошибок

@router.message(filters.Command('setcover'))
async def handle_setcover(message: Message, state: FSMContext):
    await state.set_state(MyStates.cover)
    await message.answer("Пришлите фото обложки")

@router.message(F.photo, MyStates.cover)
async def set_cover(message: Message, state: FSMContext):
    # TODO стирка изображений по таймеру
    big_file_info    = await bot.get_file(message.photo[-1].file_id)
    little_file_info = await bot.get_file(message.photo[0].file_id)
    
    await state.update_data(
        cover     = (await bot.download_file(big_file_info.file_path)).getvalue(),
        cover_id  = big_file_info.file_id,
        thumbnail = (await bot.download_file(little_file_info.file_path)).getvalue()
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
        await bot.reply_to(message, "Обложка не задана")



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

 
 
@router.message(F.audio)
async def handle_audio(message: Message, state: FSMContext):
    # TODO учет последовательности (можно добавить опцию для контроля, взамен скорость)
    # добавить сообщение которое будет говорить о загрузке /-\|/-\|
    await state.set_state()
    data = await state.get_data()
    
    cover          = data.get('cover')
    thumbnail      = data.get('thumbnail')
    musician       = data.get('musician')
    composer       = data.get('composer')
    album          = data.get('album')
    # TODO параметр автонумерации треков
    track_number   = data.get('track_number')   # номер трека в альбоме
    released       = data.get('released')       # год выпуска
    lyrics         = data.get('lyrics')
    genre          = data.get('genre')
    
    digits_in_song = data.get('digits_in_song') # может ли начало трека содержать число
    send_in_queue  = True #data.get('send_in_queue')  # отсылать в том же порядке что и присланы
    
    song           = data.get('song')
    if song: await state.update_data(song = None)
    
    if send_in_queue:
        # {chat:{user:[message]}}
        global message_queue
        message_queue.setdefault(message.chat.id, {}).setdefault(message.from_user.id, []).append(message.message_id)
        
    file_name = message.audio.file_name.replace('_',' ').replace('.mp3','')
    file_path = await bot.get_file(message.audio.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)
    
    file_beginning = downloaded_file.read(3); downloaded_file.seek(0)
    
    bs = '\\'
    
    # Проверяем наличие тегов в формате ID3
    if file_beginning == b'ID3':
        # Читаем теги файла
        tags = ID3(downloaded_file)
    
        musician_ = tags.getall('TPE1')+tags.getall('TPE2'); musician_ = musician_[0].text[0] if musician_ else None
        album_ = tags.getall('TALB');                        album_ = album_[0].text[0] if album_ else None
        released_ = tags.getall('TORY')+tags.getall('TDRL'); released_ = released_[0].text[0] if released_ else None
        genre_ = tags.getall('TCON');                        genre_ = genre_[0].text[0] if genre_ else None
        track_number_ = tags.getall('TRCK');                 track_number_ = track_number_[0].text[0] if track_number_ else None
        composer_ = tags.getall('TCOM');                     composer_ = composer_[0].text[0] if composer_ else None
        #lyrics_ TXXX SYLT USLT TSST TIT3

        song_ = tags.getall('TIT2');                         song_ = song_[0].text[0] if song_ else None
        # В названии может быть указан номер трека
        track_number = track_number if track_number else track_number_
        if not digits_in_song:
            pattern = rf"^\s*0?({track_number if track_number else bs+'d*'})\s*(.*)\s*$"
            match = re.match(pattern, song_, re.IGNORECASE)
            if match: track_number, song_ = match.groups()
    
        cover_ = tags.getall('APIC');                        cover_ = cover_[0].data if cover_ else None
        if cover_ and  (not cover):
            image = Image.open(io.BytesIO(cover_))
            image.thumbnail((90, 90))
            thumbnail = io.BytesIO()
            image.save(thumbnail, format='JPEG')
            thumbnail = thumbnail.getvalue()
            image.close()
        if cover and cover_:
            cover_ = None
        
        tags.delete(downloaded_file)
        
        song         = song         if song         else song_
        musician     = musician     if musician     else musician_
        cover        = cover        if cover        else cover_
    
    if  (not musician) and (not song):
        # _<musician>_-_<track_number>_<song>_
        # _<musician>_-_<song>_
        # Первое тире будет разделителем
        if not digits_in_song: pattern = r"^\s*(.*?)\s*-\s*0?(\d*)\s*(.*)\s*$"
        else:                  pattern = r"^\s*(.*?)\s*-\s*(.*)\s*$"
        
        match = re.match(pattern, file_name)
        if match:
            if not digits_in_song: musician, track_number, song = match.groups()
            else:                  musician, song = match.groups()
        else:
            # нельзя расчленить название, причем обе части неизвестны
            if send_in_queue:
                 message_queue[message.chat.id][message.from_user.id].remove(message.message_id)
            await bot.reply_to(message, "Установите исполнителя или отправьте файл с названием вида: <Исполнитель> - <Композиция>.")
            return
    
    elif (musician or song) and not (musician and song):
        # TODO учесть composer в шаблонах
        # через название файла и извеcтную часть ищем неизвестную вторую часть
        if not digits_in_song:
            # _<musician>_-_<track_number>?_<song>_ или _<musician>_<album_track_number>_<song>_
            # _<track_number>_<song>_-_<musician>_ или _<track_number>?_<song>_<musician>_
            pattern          = rf"^\s*({musician if musician else '.*'})\s*-?\s*0?({track_number if track_number else bs+'d*'})?\s*({song if song else '.*'})\s*$"
            reversed_pattern = rf"^\s*0?({track_number if track_number else bs+'d*'})?\s*({song if song else '.*'})\s*-?\s*({musician if musician else '.*'})\s*$"
        else:
            # _<musician>_-_<song>_ или _<musician>_<song>_
            # _<song>_-_<musician>_ или _<song>_<musician>_
            pattern          = rf"^\s*({musician if musician else '.*'})\s*-?\s*({song if song else '.*'})\s*$"
            reversed_pattern = rf"^\s*({song if song else '.*'})\s*-?\s*({musician if musician else '.*'})\s*$"
        
        match          = re.match(pattern,          file_name, re.IGNORECASE)
        reversed_match = re.match(reversed_pattern, file_name, re.IGNORECASE)
        
        if match:
            if not digits_in_song: musician_, track_number_, song_ = match.groups()
            else:                  musician_, song_                = match.groups()
        elif reversed_match:
            if not digits_in_song: track_number_, song_, musician_ = match.groups()
            else:                  song_, musician_                = match.groups()
            
        elif file_name.count('-') > 0:
            # указываемое название не совпало с названием из файла
            musician_, song_ = file_name.split('-',1)
            musician_, song_ = musician_.strip(), song_.strip()
        else:
            # нельзя расчленить название, поэтому неизвестная часть будет целиком названием
            musician_, song_ = file_name.strip(), file_name.strip()
        
        song         = song         if song         else song_
        musician     = musician     if musician     else musician_
        track_number = track_number if track_number else track_number_
    
    # создадим новые теги на основе имеющихся данных и заменим ими предыдущие
    tags = ID3()
    
    tags.add(TIT2(encoding=3, text=song))
    tags.add(TPE1(encoding=3, text=musician))
    if composer:     tags.add(TCOM(encoding=3, text=composer))
    if album:        tags.add(TALB(encoding=3, text=album))
    if genre:        tags.add(TCON(encoding=3, text=genre))
    if released:     tags.add(TDRL(encoding=3, text=released)); tags.add(TORY(encoding=3, text=released))
    if lyrics:       tags.add(TXXX(encoding=3, text=lyrics))
    if track_number: tags.add(TRCK(encoding=3, text=track_number))
    if cover:        tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=cover))
   
    tags.save(downloaded_file)
    
    downloaded_file=downloaded_file.getvalue()
    
    #.!;%+^@$_ доступны при более чем ~40 символов, остальные схлопываются в _ как и пробелы
    # или среднем количестве символов в слове > 6, а вообще ни то ни другое. хз как
    
    if send_in_queue:
        while message.message_id!=message_queue[message.chat.id][message.from_user.id][0]:
            await asyncio.sleep(2)
    
    await message.answer_audio(
        audio     = BufferedInputFile(downloaded_file, filename=f'{musician} - {song}.mp3'),
        thumbnail = BufferedInputFile(thumbnail, filename='thumbnail')
        )
    
    if send_in_queue:
        message_queue[message.chat.id][message.from_user.id].remove(message.message_id)
    





async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
            url=BASE_WEBHOOK_URL, 
            secret_token=WEBHOOK_SECRET
            )
    
    
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
def main():
    dp.startup.register(on_startup)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(
            app=app, 
            host=PRIVATE_SERVER_HOST, 
            port=PRIVATE_SERVER_PORT,
            )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
