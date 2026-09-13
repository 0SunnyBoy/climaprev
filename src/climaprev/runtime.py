"""Production entry point: only the application's sanitized request records are logged."""

from __future__ import annotations

import logging.config

import uvicorn


def configure_logging() -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"format": "%(message)s"}},
            "handlers": {
                "requests": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                },
                "discard": {"class": "logging.NullHandler"},
            },
            "root": {"handlers": ["discard"], "level": "WARNING"},
            "loggers": {
                "climaprev.request": {
                    "handlers": ["requests"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn": {"handlers": ["discard"], "propagate": False},
                "uvicorn.error": {"handlers": ["discard"], "propagate": False},
                "uvicorn.access": {"handlers": ["discard"], "propagate": False},
            },
        }
    )


if __name__ == "__main__":
    configure_logging()
    uvicorn.run(
        "climaprev.main:app",
        host="0.0.0.0",
        port=8000,
        access_log=False,
        proxy_headers=False,
        log_config=None,
    )
