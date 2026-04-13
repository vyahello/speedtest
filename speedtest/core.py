"""Core speed test measurements.

Measurements are performed against Cloudflare's public endpoints:
- Download: https://speed.cloudflare.com/__down?bytes=N
- Upload:   https://speed.cloudflare.com/__up?bytes=N

The CLI is intended to be quick and give "instant" stats, not to perfectly
replicate Ookla's methodology.
"""

from __future__ import annotations

from statistics import median
from typing import Iterable

from speedtest.http_client import HttpError, http_get, http_post
from speedtest.models import BandwidthStats, LatencyStats, SpeedTestResult, SpeedTestSettings


def _percentile(values: list[float], percentile: float) -> float:
    """Return percentile using nearest-rank on sorted values."""

    if not values:
        raise ValueError("values must not be empty")
    if not 0.0 <= percentile <= 1.0:
        raise ValueError("percentile must be between 0 and 1")
    values_sorted = sorted(values)
    index = int(round((len(values_sorted) - 1) * percentile))
    return values_sorted[index]


def _jitter_ms(samples_ms: Iterable[float]) -> float:
    """Compute jitter as median absolute delta between consecutive samples."""

    values_ms = list(samples_ms)
    if len(values_ms) < 2:
        return 0.0
    diffs = [abs(next_ms - prev_ms) for prev_ms, next_ms in zip(values_ms, values_ms[1:])]
    return median(diffs)


def measure_latency(settings: SpeedTestSettings) -> LatencyStats:
    """Measure unloaded latency using GET requests with bytes=0."""

    url = f"{settings.server.rstrip('/')}/__down?bytes=0"
    samples_ms: list[float] = []
    for _ in range(settings.latency_requests):
        timings = http_get(url, timeout_s=settings.timeout_s, read_limit_bytes=1)
        samples_ms.append(timings.elapsed_s * 1000.0)
    return LatencyStats(latency_ms=_percentile(samples_ms, 0.5), jitter_ms=_jitter_ms(samples_ms))


def measure_download(settings: SpeedTestSettings) -> BandwidthStats:
    """Measure download bandwidth (Mbps) using a single request."""

    if settings.warmup_bytes > 0:
        warm_url = f"{settings.server.rstrip('/')}/__down?bytes={settings.warmup_bytes}"
        _ = http_get(warm_url, timeout_s=settings.timeout_s, read_limit_bytes=settings.warmup_bytes)

    url = f"{settings.server.rstrip('/')}/__down?bytes={settings.download_bytes}"
    timings = http_get(url, timeout_s=settings.timeout_s)
    if timings.elapsed_s <= 0:
        raise ValueError("download elapsed time must be > 0")
    bps = (timings.transferred_bytes * 8) / timings.elapsed_s
    return BandwidthStats(bps=bps)


def measure_upload(settings: SpeedTestSettings) -> BandwidthStats:
    """Measure upload bandwidth (Mbps) using a single request."""

    url = f"{settings.server.rstrip('/')}/__up?bytes={settings.upload_bytes}"
    timings = http_post(url, timeout_s=settings.timeout_s, body_bytes=settings.upload_bytes)
    if timings.elapsed_s <= 0:
        raise ValueError("upload elapsed time must be > 0")
    bps = (timings.transferred_bytes * 8) / timings.elapsed_s
    return BandwidthStats(bps=bps)


def run_speedtest(settings: SpeedTestSettings) -> SpeedTestResult:
    """Run latency + download + upload measurements."""

    try:
        latency = measure_latency(settings)
        download = measure_download(settings)
        upload = measure_upload(settings)
        return SpeedTestResult(latency=latency, download=download, upload=upload)
    except HttpError as exc:
        raise RuntimeError(f"Network measurement failed: {exc}") from exc
