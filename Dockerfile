FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml requirements.lock requirements-build.lock .
COPY src ./src
COPY tests ./tests
COPY docs ./docs
COPY README.md .

RUN find src tests -name '*.py' -exec chmod a-x {} +

RUN pip --isolated install --no-cache-dir --require-hashes -r requirements-build.lock \
    && pip --isolated install --no-cache-dir --require-hashes -r requirements.lock \
    && python -c "from pathlib import Path; Path('/tmp/production.constraints').write_text(chr(10).join(line.split()[0] for line in Path('requirements.lock').read_text().splitlines() if line and line[0].isalnum()))" \
    && pip --isolated install --no-cache-dir --no-build-isolation -c /tmp/production.constraints -e ".[dev]"

COPY .env.example .

CMD ["python", "-m", "climaprev.runtime"]
