FROM python:3.11-slim-buster

ENV DOCKER_RUN  'true'
ENV PG_CONN     'postgresql://app:app@localhost:5432/postgres'
ENV I18N_DIR    '.'
ENV I18N_LOCALE 'ru-RU'
ENV TZ          'Europe/Moscow'

RUN apt update && apt install zbar-tools -y

WORKDIR /python-docker

COPY requirenments.txt .
RUN pip3 install -r requirenments.txt

COPY i18n/*.yaml ./

CMD [ "python3", "-u", "main.py"]