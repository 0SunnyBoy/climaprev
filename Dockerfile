FROM python:3.12-alpine@sha256:5459054a89e9a1cda63864b0b2e9d31802256103f2f42af59fdc3ee11f65ddbd AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apk upgrade --no-cache

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
COPY requirements.lock requirements-build.lock requirements-dev.lock pyproject.toml README.md .
COPY src ./src
RUN pip --isolated install --no-cache-dir --require-hashes -r requirements-build.lock \
    && pip --isolated install --no-cache-dir --no-build-isolation --require-hashes -r requirements-dev.lock \
    && pip --isolated install --no-cache-dir --no-build-isolation --no-deps -e .
COPY tests ./tests
COPY docs ./docs
COPY .env.example requirements-load.lock .
CMD ["python", "-m", "climaprev.runtime"]

FROM dev AS load
RUN pip --isolated install --no-cache-dir --no-build-isolation --require-hashes -r requirements-load.lock

FROM base AS runtime
RUN mkdir -p /run/climaprev-logs /var/log/climaprev \
    && chown -R 10001:10001 /run/climaprev-logs /var/log/climaprev
ENV PATH=/opt/venv/bin:$PATH
COPY --from=package /opt/venv /opt/venv
USER 10001:10001
CMD ["python", "-m", "climaprev.runtime"]
