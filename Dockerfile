FROM python:3.8

RUN apt -y update && apt -y install ffmpeg

COPY ./speecher /speecher
COPY ./.env /
COPY ./requirements.txt /
RUN pip3 install -r requirements.txt

CMD ["python", "/speecher/main.py"]
