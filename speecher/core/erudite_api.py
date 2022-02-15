import requests
from loguru import logger
from datetime import datetime, timedelta

from settings import settings


class Erudite:
    ERUDITE_API_URL = "https://nvr.miem.hse.ru/api/erudite/records"
    ERUDITE_API_KEY = settings.erudite_api_key

    @classmethod
    def get_all_records_per_day(cls) -> list:
        today = datetime.today().date() - timedelta(2)
        fromdate = f"{today} 9:00:00"
        todate = f"{today} 21:00:00"
        page_number = 0
        all_records = []

        records = cls.get_records(fromdate, todate, page_number)
        all_records.extend(records)
        while records:
            page_number += 1
            records = cls.get_records(fromdate, todate, page_number)
            all_records.extend(records)

        return all_records

    @classmethod
    def get_records(cls, fromdate, todate, page_number) -> list:
        params = {"fromdate": fromdate, "todate": todate, "page_number": page_number}
        r = requests.get(cls.ERUDITE_API_URL, params=params)
        code = r.status_code
        if code == 200:
            return [record for record in r.json() if not record["keywords"]]
        elif code == 404:
            logger.warning(f"No records for {fromdate} found")
            return []
        else:
            logger.error(f"Erudite returned - {code}")
            return []

    @classmethod
    def patch_record(cls, keywords: list, record_id: str) -> None:
        data = {"keywords": keywords}
        r = requests.patch(
            f"{cls.ERUDITE_API_URL}/{record_id}",
            json=data,
            headers={"key": cls.ERUDITE_API_KEY},
        )
        code = r.status_code
        if code == 200:
            logger.info("Record updated successfully")
        elif code == 404:
            logger.warning(f"Record with id - {record_id} not found")
        else:
            logger.error(f"Erudite returned - {code}")

    @staticmethod
    def filter_records(records: list) -> list:
        offline = []
        zoom = []
        jitsi = []
        for record in records:
            if record["type"] == "Offline":
                offline.append(record)
            elif record["type"] == "Zoom":
                zoom.append(record)
            elif record["type"] == "Jitsi":
                jitsi.append(record)

        return offline, zoom, jitsi
