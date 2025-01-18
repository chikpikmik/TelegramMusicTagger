from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, APIC, TDRL, TORY, TXXX, TBPM, TEXT, TCOM, TCON #TDRS

from PIL import Image

from io import BytesIO
from typing import Optional

'''
class Audio:
    def __init__(self, 
                    song:Optional[str]=None,
                    musician:Optional[str]=None,
                    album:Optional[str]=None,
                    genre:Optional[str]=None,
                    released:Optional[str]=None,
                    composer:Optional[str]=None,
                    track_number:Optional[str]=None,
                    lyrics:Optional[str]=None,
                    cover_image:Optional[bytes]=None):
        """Инициализация объекта Audio."""
        self.song           = song
        self.musician       = musician
        self.album          = album
        self.released       = released
        self.genre          = genre
        self.track_number   = track_number
        self.composer       = composer
        self.lyrics         = lyrics
        self.cover_image    = cover_image

    def get_cover(self) -> Optional[bytes]:
        """Извлекает изображение обложки из ID3 тегов."""
        if not self.cover_image:
            cover_tags = self._tags.getall('APIC')
            return cover_tags[0].data if cover_tags else None
        else:
            return self.cover_image

    def get_file(self) -> Optional[bytes]:
        """Возвращает файл"""
        return self.file_data.getvalue()
'''


class AudioID3:
     
    @staticmethod
    def isItID3(file_data: BytesIO):
        file_beginning = file_data.read(3)
        file_data.seek(0)
        return file_beginning == b'ID3'

    def __init__(self, file_data: BytesIO):
        self.file_data = file_data
        #self.tags = ID3(io.BytesIO(file_data))
        if AudioID3.isItID3(self.file_data): self._tags = ID3(file_data)
        else: 
            self._tags = ID3()
            self._tags.save(self.file_data)

        self.musician       = self.get_tag('TPE1', 'TPE2')
        self.album          = self.get_tag('TALB')
        self.released       = self.get_tag('TDRL', 'TORY')
        self.genre          = self.get_tag('TCON')
        self.track_number   = self.get_tag('TRCK')
        self.composer       = self.get_tag('TCOM')
        self.song           = self.get_tag('TIT2')
        self.lyrics         = self.get_tag('TXXX', 'SYLT', 'USLT,' 'TSST', 'TIT3')
        self.cover_image    = None
        self.cover_image    = self.get_cover()

    def get_tag(self, *tags) -> Optional[str]:
        """Получает тег из файла по указанным тегам."""
        for tag in tags:
            tag_data = self._tags.getall(tag)
            if tag_data:
                return tag_data[0].text[0]
        return None

    def get_cover(self) -> Optional[bytes]:
        """Извлекает изображение обложки из ID3 тегов."""
        if not self.cover_image:
            cover_tags = self._tags.getall('APIC')
            return cover_tags[0].data if cover_tags else None
        else:
            return self.cover_image

    def get_file(self) -> Optional[bytes]:
        """Возвращает файл"""
        return self.file_data.getvalue()

    def create_cover_thumbnail(self) -> Optional[bytes]:
        """Создает уменьшенную версию обложки."""
        if self.cover_image:
            image = Image.open(BytesIO(self.get_cover()))
            image.thumbnail((90, 90))
            thumbnail = BytesIO()
            image.save(thumbnail, format='JPEG')
            return thumbnail.getvalue()
        return None

    def update_tags(self, 
                    song:Optional[str]=None,
                    musician:Optional[str]=None,
                    album:Optional[str]=None,
                    genre:Optional[str]=None,
                    released:Optional[str]=None,
                    composer:Optional[str]=None,
                    track_number:Optional[str]=None,
                    lyrics:Optional[str]=None,
                    cover_image:Optional[bytes]=None):
        """Обновляет теги аудиофайла на основе данных."""
        
        new_tags = ID3()

        if song or self.song:
            self.song = song or self.song
            new_tags.add(TIT2(encoding=3, text=self.song))
        
        if musician or self.musician:
            self.musician = musician or self.musician
            new_tags.add(TPE1(encoding=3, text=self.musician))
        
        if album or self.album:
            self.album = album or self.album
            new_tags.add(TALB(encoding=3, text=self.album))
        
        if genre or self.genre:
            self.genre = genre or self.genre
            new_tags.add(TCON(encoding=3, text=self.genre))
        
        if released or self.released:
            self.released = released or self.released
            new_tags.add(TDRL(encoding=3, text=self.released))
            #new_tags.add(TORY(encoding=3, text=self.released))
        
        if composer or self.composer:
            self.composer = composer or self.composer
            new_tags.add(TCOM(encoding=3, text=self.composer))
        
        if track_number or self.track_number:
            self.track_number = track_number or self.track_number
            new_tags.add(TRCK(encoding=3, text=self.track_number))
        
        if lyrics or self.lyrics:
            self.lyrics = lyrics or self.lyrics
            new_tags.add(TXXX(encoding=3, text=self.lyrics))
            # 'SYLT', 'USLT,' 'TSST', 'TIT3'

        if cover_image or self.cover_image:
            self.cover_image = cover_image or self.cover_image
            new_tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=self.cover_image))

        self._tags.delete(self.file_data)
        new_tags.save(self.file_data)
        self._tags = new_tags