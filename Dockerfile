FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src ./src
COPY tests ./tests
COPY docs ./docs
COPY README.md .

RUN find src tests -name '*.py' -exec chmod a-x {} +

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[dev]"

COPY .env.example .

CMD ["python", "-m", "climaprev.runtime"]
