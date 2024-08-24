FROM python:3.10-slim

ENV PYTHONBUFFERED=1

WORKDIR /bestview

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .