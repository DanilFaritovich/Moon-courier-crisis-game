"""Logging configuration shared by the API application."""

import logging

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    """Configure a useful default handler when the host has not configured one."""

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
