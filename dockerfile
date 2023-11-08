FROM debian:bookworm AS install-curl
RUN apt update
RUN apt install -y curl
RUN mkdir /app
RUN curl -sSL https://install.python-poetry.org -o /app/install-poetry.py

FROM python:3.7-slim AS install-deps
COPY --from=install-curl /app/install-poetry.py /app/install-poetry.py
ENV POETRY_VERSION=1.5.0
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"
RUN python /app/install-poetry.py
RUN rm /app/install-poetry.py
COPY ./poetry.lock /app/poetry.lock
COPY ./pyproject.toml /app/pyproject.toml
RUN poetry cache clear . --all
RUN rm poetry.lock
RUN poetry install

FROM python:3.7-slim
ENV PATH="/app/.venv:$PATH"
COPY --from=install-deps /app/.venv /app/.venv
COPY ./test.sh /app/test.sh
CMD ["/app/test"]