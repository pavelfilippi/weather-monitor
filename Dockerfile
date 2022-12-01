FROM python:3.10.8

WORKDIR /weather-monitor

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

COPY . /weather-monitor

ENV PYTHOHNPATH=${PYTHOHNPATH}:$PWD

EXPOSE 80

RUN pip install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main
