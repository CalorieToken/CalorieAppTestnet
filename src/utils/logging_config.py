"""Central logging configuration for XRPL Test Currency Issuer.

Usage:
    from src.utils.logging_config import configure_logging
    configure_logging(level="INFO")

This sets consistent formatting and reduces noisy third-party loggers.
"""

from __future__ import annotations

import logging
from typing import Literal

NOISY_LOGGERS = ["httpx", "httpcore", "urllib3", "websockets"]

LevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def configure_logging(level: LevelName = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
    logging.getLogger(__name__).debug("Logging initialized at %s", level)
