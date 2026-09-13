FROM python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

FROM base AS production-deps
COPY requirements.lock .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip --isolated install --no-cache-dir --require-hashes -r requirements.lock

FROM base AS build
COPY requirements-build.lock .
RUN pip --isolated install --no-cache-dir --require-hashes -r requirements-build.lock
COPY pyproject.toml README.md .
COPY src ./src
RUN pip --isolated wheel --no-build-isolation --no-deps --wheel-dir /wheels .

FROM production-deps AS package
COPY --from=build /wheels /wheels
RUN /opt/venv/bin/pip --isolated install --no-deps --no-index /wheels/*.whl

FROM base AS dev
ENV PATH=/opt/venv/bin:$PATH PYTHONPATH=/app/src
COPY --from=package /opt/venv /opt/venv
COPY requirements.lock requirements-build.lock pyproject.toml README.md .
COPY src ./src
RUN pip --isolated install --no-cache-dir --require-hashes -r requirements-build.lock \
    && python -c "from pathlib import Path; Path('/tmp/production.constraints').write_text(chr(10).join(line.split()[0] for line in Path('requirements.lock').read_text().splitlines() if line and line[0].isalnum()))" \
    && pip --isolated install --no-cache-dir --no-build-isolation -c /tmp/production.constraints -e ".[dev]"
COPY tests ./tests
COPY docs ./docs
COPY .env.example .
CMD ["python", "-m", "climaprev.runtime"]

FROM base AS runtime
ENV PATH=/opt/venv/bin:$PATH
COPY --from=package /opt/venv /opt/venv
USER 10001:10001
CMD ["python", "-m", "climaprev.runtime"]
