"""HTTP helpers (stdlib-only) for speedtest measurements."""

from __future__ import annotations

import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from time import perf_counter
from typing import Final

_UA: Final[str] = "speedtest-python-cli/0.1 (+https://github.com/vyahello/speedtest)"


@dataclass(frozen=True, slots=True)
class HttpTimings:
    """Request timings and transferred bytes."""

    elapsed_s: float
    transferred_bytes: int


class HttpError(RuntimeError):
    """Raised when HTTP request fails."""


def _ssl_context() -> ssl.SSLContext:
    """Create an SSL context for outbound HTTPS requests."""

    return ssl.create_default_context()


def http_get(url: str, *, timeout_s: float, read_limit_bytes: int | None = None) -> HttpTimings:
    """Perform a GET and read (optionally limited) response body."""

    req = urllib.request.Request(url, method="GET", headers={"User-Agent": _UA})
    start = perf_counter()
    transferred = 0
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=_ssl_context()) as resp:
            if read_limit_bytes is None:
                data = resp.read()
                transferred = len(data)
            else:
                remaining = read_limit_bytes
                while remaining > 0:
                    chunk = resp.read(min(remaining, 64 * 1024))
                    if not chunk:
                        break
                    transferred += len(chunk)
                    remaining -= len(chunk)
    except (urllib.error.URLError, OSError) as exc:
        raise HttpError(str(exc)) from exc
    elapsed = perf_counter() - start
    return HttpTimings(elapsed_s=elapsed, transferred_bytes=transferred)


def http_post(url: str, *, timeout_s: float, body_bytes: int) -> HttpTimings:
    """Perform a POST with a binary body of given size."""

    payload = os.urandom(body_bytes)
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"User-Agent": _UA, "Content-Type": "application/octet-stream"},
    )
    start = perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=_ssl_context()) as resp:
            _ = resp.read(1)
    except (urllib.error.URLError, OSError) as exc:
        raise HttpError(str(exc)) from exc
    elapsed = perf_counter() - start
    return HttpTimings(elapsed_s=elapsed, transferred_bytes=len(payload))
