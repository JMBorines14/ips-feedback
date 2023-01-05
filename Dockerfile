FROM python:3.10-slim-buster

ENV host=172.17.0.3
ENV port=3306
ENV username=root
ENV password=baeldung
ENV database=intearactivepsetDB

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install --no-cache-dir gevent

COPY . .

CMD gunicorn -k gevent --bind 0.0.0.0:5000 manage:app