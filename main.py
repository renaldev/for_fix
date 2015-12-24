import json
import random

import asyncio
import abc


class Music:

    def __init__(self, style_name, actions):
        """
        Инициализация
        style_name (str): название стиля
        actions (list string): возможные движения
        """
        self.style = style_name
        self.actions = actions

    def __eq__(self, other):
        return self.style == other.style

    def __str__(self):
        return self.style


class NightClub:

    def __init__(self, music_styles):
        """
        Инициализация
        music_styles (list Music): список музыкальных стилей
        """
        self.music_styles = music_styles
        self.music_playlist = []
        self.persons_activity = []

        self.current_music = self.music_styles[-1]
        self.open = True
        self.loop = None

    def init_random_playlist(self, song_count = 3):
        """
        Инициализация случайного плейлиста вечеринки
        song_count (int): колличество композиций
        """
        while song_count:
            self.music_playlist.append(random.randint(0, len(self.music_styles) - 1))
            song_count -= 1

    def invite_random_persons(self, person_type, count = 5):
        """
        Приглашение случайных персон
        person_type (class_object(Person)): класс персоны
        count(int): колличество
        """
        for i in range(count):
            one_person = person_type(random.choice(self.music_styles),
                                 "Person " + str(i))
            self.persons_activity.append(
                one_person.activity()
            )

    @asyncio.coroutine
    def dj(self, period=10):
        for music_idx in self.music_playlist:
            self.current_music = self.music_styles[music_idx]
            print("DJ сменил музыку на {}".format(self.current_music))
            yield from asyncio.sleep(period)

        self.open = False

    def music_around(self, activity):
        """
        Декоратор - музыкальное окружение
        """
        def wrapped(*args, **kwargs):
            return activity(club = self,
                            period = random.randint(2,7),
                            *args, **kwargs)
        return wrapped

    def run_party(self):
        self.loop = asyncio.get_event_loop()

        self.persons_activity.append(self.dj())
        self.loop.run_until_complete(asyncio.wait(self.persons_activity))

        print("Вечеринка закончилась ...")
        self.loop.close()


class Person(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        """Инициализация"""

    @abc.abstractmethod
    def activity(self, *args, **kwargs):
        """Действие"""


def main():
    music_styles = []
    with open('music.json') as styles_data:
        for key, value in json.load(styles_data).items():
            music_styles.append(Music(key, value))

    nc = NightClub(music_styles)
    nc.init_random_playlist(song_count=5)

    class Visitor(Person):

        def __init__(self, music_style, name = "Visitor"):
            self.music_style = music_style
            self.name = name + " ({})".format(music_style)

        @asyncio.coroutine
        @nc.music_around
        def activity(self, club, period = 2):
            while club.open:
                if self.music_style == club.current_music:
                    print(self.name + ": {} под {}".format(random.choice(self.music_style.actions), club.current_music))
                else:
                    print(self.name + ": пьет водку ... под {}".format(club.current_music))
                yield from asyncio.sleep(period)
            print(self.name + ": покинул клуб ...")

    class Girl(Visitor):

        def __init__(self, music_style, name = "Visitor"):
            super().__init__(music_style, name)
            self.name = "Девушка " + self.name

    class Boy(Visitor):

        def __init__(self, music_style, name = "Visitor"):
            super().__init__(music_style, name)
            self.name = "Парень " + self.name

    nc.invite_random_persons(Girl)
    nc.invite_random_persons(Boy)
    nc.run_party()

if __name__ == '__main__':
    main()