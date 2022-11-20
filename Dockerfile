FROM python:3.10.8

RUN mkdir /weather-monitor
COPY src/ /weather-monitor/src
COPY pyproject.toml /weather-monitor/pyproject.toml

WORKDIR /weather-monitor
ENV PYTHOHNPATH=${PYTHOHNPATH}:$PWD

EXPOSE 80

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
