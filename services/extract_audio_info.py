import re

# TODO учесть composer в шаблонах

bs = '\\'

def extract_audio_info(file_name, musician=None, song=None, track_number=None, digits_in_song=False):
    """
    Основная функция для извлечения данных из имени файла.
    Возвращает данные: исполнитель, трек, песня и номер трека.
    """
    # Если номер трека в песне, извлекаем его
    if digits_in_song and song:
        track_number, song = extract_track_number_from_song(song)
    

    if not musician and not song:
        # Если нет данных о музыканте и песне, пытаемся извлечь их из имени файла
        musician, song, track_number = extract_musician_and_song(file_name, digits_in_song)
    
    elif (musician or song) and not (musician and song):
        # Если одна из частей известна, пытаемся извлечь неизвестную часть
        musician, song, track_number = extract_missing_part(file_name, musician, song, track_number, digits_in_song)
    
    else:
        # Если обе части известны, просто передаем их
        musician, song = musician or '', song or ''
    
    return musician, song, track_number


def extract_musician_and_song(file_name, digits_in_song):
    """
    Извлекает имя исполнителя, песню и номер трека из имени файла.
    _<musician>_-_<track_number>_<song>_
    _<musician>_-_<song>_
    Первое тире будет разделителем
    """
    if digits_in_song:
        pattern = r"^\s*(.*?)\s*-\s*0?(\d*)\s*(.*)\s*$"
    else:
        pattern = r"^\s*(.*?)\s*-\s*(.*)\s*$"
    
    match = re.match(pattern, file_name)
    if match:
        if digits_in_song:
            musician, track_number, song = match.groups()
        else:
            musician, song = match.groups()
        return musician, song, track_number
    
    else:
        # нельзя расчленить название, причем обе части неизвестны
        return '', '', ''


def extract_missing_part(file_name, musician, song, track_number, digits_in_song):
    """
    Если только одна из частей известна, пытаемся извлечь недостающую.
    """
    if digits_in_song:
        # _<musician>_-_<track_number>?_<song>_ или _<musician>_<track_number>_<song>_
        # _<track_number>_<song>_-_<musician>_ или _<track_number>?_<song>_<musician>_
        pattern = rf"^\s*({musician or '.*'})\s*-?\s*0?({track_number or bs+'d*'})?\s*({song or '.*'})\s*$"
        reversed_pattern = rf"^\s*0?({track_number or bs+'d*'})?\s*({song or '.*'})\s*-?\s*({musician or '.*'})\s*$"
    else:
        # _<musician>_-_<song>_ или _<musician>_<song>_
        # _<song>_-_<musician>_ или _<song>_<musician>_
        pattern = rf"^\s*({musician or '.*'})\s*-?\s*({song or '.*'})\s*$"
        reversed_pattern = rf"^\s*({song or '.*'})\s*-?\s*({musician or '.*'})\s*$"
    
    match          = re.match(pattern,          file_name, re.IGNORECASE)
    reversed_match = re.match(reversed_pattern, file_name, re.IGNORECASE)
    
    if match:
        if digits_in_song:
            musician, track_number, song = match.groups()
        else:
            musician, song = match.groups()
    
    elif reversed_match:
        if digits_in_song:
            track_number, song, musician = reversed_match.groups()
        else:
            song, musician = reversed_match.groups()
    
    elif file_name.count('-') > 0:
        # Если нет совпадений, пробуем разделить на две части
        musician, song = file_name.split('-', 1)
        musician, song = musician.strip(), song.strip()
    
    else:
        # Если не удается разделить, неизветсная часть берет все
        musician, song = musician or file_name.strip(), song or file_name.strip()

    return musician, song, track_number


def extract_track_number_from_song(song):
    """
    Извлекает номер трека из названия песни, если он есть.
    """
    pattern = r"^\s*0?(\d*)\s*(.*)\s*$"
    match = re.match(pattern, song, re.IGNORECASE)
    if match:
        track_number, song = match.groups()
        return track_number, song
    return '', song
