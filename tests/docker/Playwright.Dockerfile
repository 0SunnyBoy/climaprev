# Test-only runner: browsers and operating system are fixed by this digest.
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble@sha256:72bd171a9ffc2b4b59532aaa6210e21014d07093120dc25528870c0b840da1f0

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends libnss3-tools \
    && python -m pip install --no-cache-dir playwright==1.63.0 \
    && rm -rf /var/lib/apt/lists/*
