"""Compatibility shim for legacy builds.

This project is configured via `pyproject.toml` (PEP 621). `setup.py` is kept as a
minimal shim so tools expecting it won't crash.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
