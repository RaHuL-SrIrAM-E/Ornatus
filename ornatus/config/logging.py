"""Logging setup, shared by the CLI and any future trigger entrypoints."""

import logging

from ornatus.config.settings import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
