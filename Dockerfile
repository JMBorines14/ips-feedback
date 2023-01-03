FROM python:3.10-slim-buster

ENV host=localhost
ENV port=3306
ENV username=root
ENV password=password
ENV database=engg150_test

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind=0.0.0.0:5000 manage:app