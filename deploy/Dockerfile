FROM python:3.11-slim-bookworm

RUN set -ex \
    # install system build deps
&&  apt update && apt install -y gcc \
    # install system runtime deps
&&  apt install -y libpq-dev curl\
    # install python app requirements
&&  pip install poetry

WORKDIR /srv/app

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi  \
  &&  rm -rf ~/.cache poetry.lock pyproject.toml \
    # remove system build deps
  &&  apt purge -y --autoremove gcc

COPY . .
RUN set -ex \
    # collect app static
&&  python manage.py collectstatic --noinput
