import os
import pickle
from io import FileIO
from loguru import logger

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

from settings import settings


class Drive:
    CREDS_PATH = settings.creds_path
    TOKEN_PATH = settings.token_path
    SCOPES = "https://www.googleapis.com/auth/drive"

    def __init__(self) -> None:
        self.refresh_token()
        self.service = build("drive", "v3", credentials=self.creds)

    def refresh_token(self) -> None:
        self.creds = None
        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, "rb") as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDS_PATH, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open(self.TOKEN_PATH, "wb") as token:
                pickle.dump(self.creds, token)
        if self.creds:
            logger.info("Creds created sucssessfully")

    def download(self, video_id: str, name: str = "video.mp4") -> str:
        """ Downloads a video from Google Drive with given video_id to the name "video.mp4" if not specified """

        self.file_name = name
        try:
            request = self.service.files().get_media(fileId=video_id)
            file_downloaded = FileIO(name, "wb")
            downloader = MediaIoBaseDownload(file_downloaded, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"Download - {int(status.progress() * 100)}% done")
        except HttpError:
            logger.error(f"File with id - {video_id} not found")
        return name
