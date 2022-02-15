from pydub import AudioSegment
import math
import speech_recognition as speech_recog
import subprocess
import os
from loguru import logger

import nltk

nltk.download("punkt")
nltk.download("stopwords")
from nltk.tokenize import word_tokenize  # для токенизации по словам
from nltk.corpus import stopwords  # сборник стоп-слов
from string import punctuation  # сборник символов пунктуации
import pymorphy2  # для морфологическтого анализа текста


class SoundToText:
    SOUND_WAV = "sound.wav"
    SOUND_AAC = "sound.aac"

    @classmethod
    def video_to_sound(cls, name: str) -> None:
        subprocess.call(
            f"ffmpeg -i {name}.mp4 -c:a copy -vn -y {cls.SOUND_AAC}", shell=True
        )
        subprocess.call(f"ffmpeg -i {cls.SOUND_AAC} -y {cls.SOUND_WAV}", shell=True)

    @staticmethod
    def convert_audio_to_text(names: list, lang: str = "ru-RU") -> None:
        """ Converts sound from every file given into a list of words, deletes converted .wav file """
        words = set()

        for name in names:
            logger.info(f"Converting {name} into text...")
            sample_audio = speech_recog.AudioFile(name)

            r = speech_recog.Recognizer()
            with sample_audio as source:
                audio_content = r.record(source)

            try:
                response = r.recognize_google(audio_content, language=lang)
                token = word_tokenize(response)
                words.update(token)
            except speech_recog.UnknownValueError:
                pass
            finally:
                os.remove(name)

        return words

    @classmethod
    def clear_words(cls, words: set()) -> set:
        stopword = stopwords.words("russian") + [a for a in punctuation]
        morph = pymorphy2.MorphAnalyzer()
        return {
            morph.parse(word)[0].normal_form
            for word in words
            if word not in stopword and not word.isdigit()
        }


class SplitAudio:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.audio = AudioSegment.from_wav(self.filename)

    def single_split(self, from_min: int, to_min: int, split_filename: str) -> None:
        """ Cuts a piece from an audio by given minutes """

        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(split_filename, format="wav")

    def multiple_split(self, min_per_split: int = 1) -> list:
        """ Cuts a =n audio in fragments of the given length """

        total_mins = math.ceil(self.audio.duration_seconds / 60)
        names = []
        for i in range(0, total_mins, min_per_split):
            split_name = str(i) + "_" + self.filename
            names.append(split_name)
            self.single_split(i, i + min_per_split, split_name)
            logger.info(f" Video {i} cut from {self.filename}")
            if i == total_mins - min_per_split:
                logger.info("All splited successfully")

        return names
