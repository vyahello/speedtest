from __future__ import annotations

import pytest

from speedtest.core import measure_download, measure_latency, measure_upload
from speedtest.http_client import HttpTimings
from speedtest.models import SpeedTestSettings


def test_measure_latency_uses_multiple_samples(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_get(url: str, *, timeout_s: float, read_limit_bytes: int | None = None) -> HttpTimings:
        _ = (timeout_s, read_limit_bytes)
        calls.append(url)
        return HttpTimings(elapsed_s=0.01, transferred_bytes=0)

    monkeypatch.setattr("speedtest.core.http_get", fake_get)
    settings = SpeedTestSettings(latency_requests=3)
    stats = measure_latency(settings)
    assert len(calls) == 3
    assert stats.latency_ms > 0.0


def test_measure_download_calculates_bps(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, *, timeout_s: float, read_limit_bytes: int | None = None) -> HttpTimings:
        _ = (url, timeout_s, read_limit_bytes)
        return HttpTimings(elapsed_s=2.0, transferred_bytes=10_000_000)

    monkeypatch.setattr("speedtest.core.http_get", fake_get)
    settings = SpeedTestSettings(download_bytes=10_000_000)
    stats = measure_download(settings)
    assert stats.bps == (10_000_000 * 8) / 2.0


def test_measure_upload_calculates_bps(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url: str, *, timeout_s: float, body_bytes: int) -> HttpTimings:
        _ = (url, timeout_s)
        return HttpTimings(elapsed_s=4.0, transferred_bytes=body_bytes)

    monkeypatch.setattr("speedtest.core.http_post", fake_post)
    settings = SpeedTestSettings(upload_bytes=5_000_000)
    stats = measure_upload(settings)
    assert stats.bps == (5_000_000 * 8) / 4.0
