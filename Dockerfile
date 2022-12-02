FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./migrations /code/migrations

COPY ./alembic.ini /code/alembic.ini

COPY ./.env /code/.env

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./src /code/src