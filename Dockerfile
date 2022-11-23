FROM python:3.10.8

RUN mkdir /weather-monitor
COPY . /weather-monitor

WORKDIR /weather-monitor
ENV PYTHOHNPATH=${PYTHOHNPATH}:$PWD

EXPOSE 80

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
