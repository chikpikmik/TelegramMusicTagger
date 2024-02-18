# -*- coding: cp1251 -*-

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMedia, InputMediaPhoto, Message, InputMediaAudio
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot.types import InputFile

from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, APIC, TDRL, TORY, TXXX, TBPM, TEXT, TCOM, TCON #TDRS
from PIL import Image

import io
import os
import re

from setting import TOKEN

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage())

global message_quque
message_quque = {}

class MyStates(StatesGroup):
    cover = State()
    musician  = State()
    song = State()
    audios = State()

# TODO Сделать одну команду для set и reset
# Добавить установщики/сбрасыватели всех настроек

@bot.message_handler(commands='setcover')
async def handle_setcover(message: Message):
    await bot.set_state(message.from_user.id, MyStates.cover, message.chat.id)
    await bot.reply_to(message, "Пришлите фото обложки")

@bot.message_handler(state=MyStates.cover,content_types='photo')
async def set_cover(message: Message):
    # TODO стирка изображений по таймеру
    big_file_info    = await bot.get_file(message.photo[-1].file_id)
    little_file_info = await bot.get_file(message.photo[0].file_id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cover']     = await bot.download_file(big_file_info.file_path)
        data['cover_id']  = big_file_info.file_id
        data['thumbnail'] = await bot.download_file(little_file_info.file_path)

    await bot.reply_to(message, "Обложка сохранена")
    await bot.set_state(message.from_user.id, "*", message.chat.id)

@bot.message_handler(state=MyStates.cover)
async def set_cover_incorrect(message: Message):
    # TODO добавь кнопку отмены т.е. await bot.set_state(message.from_user.id, "*", message.chat.id)
    await bot.reply_to(message, "Пришлите фото обложки, а не что то другое")

@bot.message_handler(commands='resetcover')
async def reset_cover(message: Message):
    await bot.set_state(message.from_user.id, "*", message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cover']     = None
            data['cover_id']  = None
            data['thumbnail'] = None
    await bot.reply_to(message, "Удалено")

@bot.message_handler(commands='sendcover')
async def handle_sendcover(message):
    # TODO обработка ситуации когда еще не было set_state
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        cover_id = data.get('cover_id')
    if cover_id:
        await bot.send_photo(message.chat.id, cover_id)
    else:
        await bot.reply_to(message, "Обложка не задана")



@bot.message_handler(commands='setmusician')
async def handle_setmusician(message: Message):
    await bot.reply_to(message, "Введите исполнителя")
    await bot.set_state(message.from_user.id, MyStates.musician, message.chat.id)

@bot.message_handler(state=MyStates.musician)
async def set_musician(message: Message):
    # TODO добавь кнопку отмены т.е. await bot.set_state(message.from_user.id, "*", message.chat.id)
    if message.content_type == 'text':
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['musician'] = message.text
        await bot.set_state(message.from_user.id, "*", message.chat.id)
        await bot.reply_to(message, "Cохранено")
    else:
        await bot.reply_to(message, "Введите имя исполнителя, а не что то другое")

@bot.message_handler(commands='resetmusician')
async def reset_musician(message: Message):
    await bot.set_state(message.from_user.id, "*", message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['musician'] = None
    await bot.reply_to(message, "Удалено")



@bot.message_handler(commands='renamenext')
async def handle_setnext(message: Message):
    await bot.reply_to(message, "Введите название композиции")
    await bot.set_state(message.from_user.id, MyStates.song, message.chat.id)

@bot.message_handler(state=MyStates.song)
async def set_next(message: Message):
    if message.content_type == 'text':
        async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['song'] = message.text
        await bot.set_state(message.from_user.id, "*", message.chat.id)
        await bot.reply_to(message, "а теперь саму композицию")
    else:
        await bot.reply_to(message, "Введите название композиции, а не что то другое")

   
 
@bot.message_handler(content_types='audio')
async def handle_audio(message: Message):
    # TODO учет последовательности (можно добавить опцию для контроля, взамен скорость)
    # добавить сообщение которое будет говорить о загрузке /-\|/-\|
    await bot.set_state(message.from_user.id, "*", message.chat.id)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
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
        send_in_quque  = data.get('send_in_quque')  # отсылать в том же порядке что и присланы
        song           = data.get('song')
        if song: data['song'] = None
    
    if send_in_quque:
        global message_quque; # {chat:{user:[message]}}
        message_quque.setdefault(message.chat.id, {}).setdefault(message.from_user.id, []).append(message.id)
        
    file_name = message.audio.file_name.replace('_',' ').replace('.mp3','')
    file_path = await bot.get_file(message.audio.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)
    file_beginning = downloaded_file[:3]
    
    downloaded_file = io.BytesIO(downloaded_file)
    
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
            track_number, song_ = match.groups()
    
        cover_ = tags.getall('APIC');                        cover_ = cover_[0].data if cover_ else None
        if cover_ and  (not cover):
            thumbnail = Image.open(io.BytesIO(cover_))
            thumbnail.thumbnail((128, 128))
            thumbnail.save(thumbnail, format='JPEG')
            thumbnail = thumbnail.getvalue()
        if cover and cover_:
            cover_ = None
        
        tags.delete(downloaded_file)
        
        song         = song if song else song_
        musician     = musician if musician else musician_
        cover        = cover if cover else cover_
    
    if  (not musician) and (not song):
        # _<musician>_-_<track_number>_<song>_
        # _<musician>_-_<song>_
        # Первое тире будет разделителем
        if not digits_in_song: pattern = r"^\s*(.*?)\s*-\s*0?(\d*)\s*(.*)\s*$"
        else:                  pattern = r"^\s*(.*?)\s*-\s*(.*)\s*$"
        
        match = re.match(pattern, file_name, re.IGNORECASE)
        if match:
            if not digits_in_song: musician, track_number, song = match.groups()
            else:                  musician, song = match.groups()
        else:
            # нельзя расчленить название, причем обе части неизвестны
            await bot.reply_to(message, "Установите исполнителя или отправьте файл с названием вида: <Исполнитель> - <Композиция>. Если в одной из частей есть '-' то установите исполнителя или комопзицию в ручную")
            return
    
    elif (musician or song) and not (musician and song):
        # через название файла и извеcтную часть ищем неизвестную вторую часть
        if not digits_in_song:
            # _<musician>_-_<album_track_number>_<song>_ или _<musician>_<album_track_number>_<song>_
            # _<track_number>_<song>_-_<musician>_ или _<track_number>_<song>_<musician>_
            pattern = rf"^\s*({musician if musician else '.*'})\s*-?\s*0?({track_number if track_number else bs+'d*'})\s*({song if song else '.*'})\s*$"
            reversed_pattern = rf"^\s*0?({track_number if track_number else bs+'d*'})\s*({song if song else '.*'})\s*-?\s*({musician if musician else '.*'})\s*$"
        else:
            # _<musician>_-_<song>_ или _<musician>_<song>_
            # _<song>_-_<musician>_ или _<song>_<musician>_
            pattern = rf"^\s*({musician if musician else '.*'})\s*-?\s*({song if song else '.*'})\s*$"
            reversed_pattern = rf"^\s*({song if song else '.*'})\s*-?\s*({musician if musician else '.*'})\s*$"
        
        match = re.match(pattern, file_name, re.IGNORECASE)
        reversed_match = re.match(reversed_pattern, file_name, re.IGNORECASE)
        if match:
            if not digits_in_song: musician, track_number, song = match.groups()
            else:                  musician, song = match.groups()
        elif reversed_match:
            if not digits_in_song: track_number, song, musician  = match.groups()
            else:                  song, musician  = match.groups()
            
        elif file_name.count('-') > 0:
            # указываемое название не совпало с названием из файла
            m,s = file_name.split('-',1)
            musician = musician if musician else m.strip()
            song = song if song else s.strip()
        else:
            # нельзя расчленить название, поэтому неизвестная часть будет целиком названием
            musician = musician if musician else file_name.strip()
            song = song if song else file_name.strip()
    
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
    downloaded_file.seek(0)
    
    #.!;%+^@$_ доступны при более чем ~40 символов, остальные схлопываются в _ как и пробелы
    # или среднем количестве символов в слове > 6, а вообще ни то ни другое. хз как
    downloaded_file.name = f'{musician} - {song}.mp3'
    
    if send_in_quque:
        while message.id!=message_quque[message.chat.id][message.from_user.id][0]:
            await asyncio.sleep(2)
    
    await bot.send_audio(
        chat_id   = message.chat.id,
        audio     = downloaded_file,
        thumbnail = thumbnail
        )
    
    downloaded_file.close()
    
    if send_in_quque:
        message_quque[message.chat.id][message.from_user.id].remove(message.id)
    

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

import asyncio
asyncio.run(bot.polling())