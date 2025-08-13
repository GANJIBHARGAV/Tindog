from __future__ import annotations
import logging
import sys


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt='{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s","logger":"%(name)s"}',
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler.setFormatter(formatter)

    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)
    root.addHandler(handler)
