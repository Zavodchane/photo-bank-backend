FROM python:3.11 as python-base

RUN mkdir photo-bank-backend

WORKDIR  /photo-bank-backend

COPY /pyproject.toml /photo-bank-backend
COPY /poetry.lock /photo-bank-backend

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .

RUN chmod a+x docker/*.sh
