from os import rename
from pytube import YouTube
from pytube.cli import on_progress
from loguru import logger


class Youtube:
    @staticmethod
    def download(url: str, name: str = "video.mp4") -> str:
        """ Downloads video from youtube and reames it """

        if not name.endswith(".mp4"):
            raise Exception("Invalid file format")

        try:
            vid = YouTube(url, on_progress_callback=on_progress)
            if vid.length > 600:
                logger.info("Downloading video")
                vid.streams.first().download()
                rename(f"{vid.title}.mp4", name)
                logger.info("Video renamed successfully")
                return vid.title, name
            else:
                logger.warning("Video too short")
        except Exception:
            logger.error("Error while downloading video from Youtube")

        return None, name
