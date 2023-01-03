FROM python:3.10-slim-buster

ENV host=value
ENV username=value
ENV password=value
ENV database=value

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind=0.0.0.0${PORT} manage:app