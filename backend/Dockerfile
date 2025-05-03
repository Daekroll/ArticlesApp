FROM python:3.12


ENV POETRY_VERSION=2.1.2
ENV POETRY_HOME=/opt/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"


RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -


RUN poetry config virtualenvs.create false


WORKDIR /app/backend
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main --no-root


COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]