"""Core speed test measurements.

Measurements are performed against Cloudflare's public endpoints:
- Download: https://speed.cloudflare.com/__down?bytes=N
- Upload:   https://speed.cloudflare.com/__up?bytes=N

The CLI is intended to be quick and give "instant" stats, not to perfectly
replicate Ookla's methodology.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import median
from dataclasses import dataclass
from typing import Iterable

from speedtest.http_client import HttpError, HttpTimings, http_get, http_post
from speedtest.models import BandwidthStats, LatencyStats, SpeedTestResult, SpeedTestSettings


class Transport(ABC):
    """Abstract transport for HTTP operations used by measurements."""

    @abstractmethod
    def get(
        self, _url: str, *, timeout_s: float, read_limit_bytes: int | None = None
    ) -> HttpTimings:
        """Perform an HTTP GET and return timings."""

        _ = (_url, timeout_s, read_limit_bytes)
        raise NotImplementedError

    @abstractmethod
    def post(self, _url: str, *, timeout_s: float, body_bytes: int) -> HttpTimings:
        """Perform an HTTP POST and return timings."""

        _ = (_url, timeout_s, body_bytes)
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class StdlibTransport(Transport):
    """Transport backed by module-level `http_get`/`http_post`.

    Note: we intentionally call the `speedtest.core` module globals so tests can
    monkeypatch `speedtest.core.http_get/http_post` and affect measurement code.
    """

    def get(
        self, url: str, *, timeout_s: float, read_limit_bytes: int | None = None
    ) -> HttpTimings:
        """Delegate GET to module-level `http_get`."""

        return http_get(url, timeout_s=timeout_s, read_limit_bytes=read_limit_bytes)

    def post(self, url: str, *, timeout_s: float, body_bytes: int) -> HttpTimings:
        """Delegate POST to module-level `http_post`."""

        return http_post(url, timeout_s=timeout_s, body_bytes=body_bytes)


@dataclass(frozen=True, slots=True)
class PercentileCalculator:
    """Percentile calculator using nearest-rank on sorted values."""

    def value(self, values: list[float], percentile: float) -> float:
        """Calculate percentile for a list of floats."""

        if not values:
            raise ValueError("values must not be empty")
        if not 0.0 <= percentile <= 1.0:
            raise ValueError("percentile must be between 0 and 1")
        values_sorted = sorted(values)
        index = int(round((len(values_sorted) - 1) * percentile))
        return values_sorted[index]


@dataclass(frozen=True, slots=True)
class JitterCalculator:
    """Jitter calculator (milliseconds)."""

    def median_abs_delta_ms(self, samples_ms: Iterable[float]) -> float:
        """Compute jitter as median absolute delta (ms) between consecutive samples."""

        values_ms = list(samples_ms)
        if len(values_ms) < 2:
            return 0.0
        diffs = [abs(next_ms - prev_ms) for prev_ms, next_ms in zip(values_ms, values_ms[1:])]
        return median(diffs)


@dataclass(frozen=True, slots=True)
class SpeedTester:
    """Runs speedtest measurements against a configured server."""

    settings: SpeedTestSettings
    transport: Transport
    percentiles: PercentileCalculator = PercentileCalculator()
    jitter: JitterCalculator = JitterCalculator()

    def _server(self) -> str:
        """Return server base URL without trailing slash."""

        return self.settings.server.rstrip("/")

    def measure_latency(self) -> LatencyStats:
        """Measure unloaded latency and jitter."""

        url = f"{self._server()}/__down?bytes=0"
        samples_ms: list[float] = []
        for _ in range(self.settings.latency_requests):
            timings = self.transport.get(url, timeout_s=self.settings.timeout_s, read_limit_bytes=1)
            samples_ms.append(timings.elapsed_s * 1000.0)
        return LatencyStats(
            latency_ms=self.percentiles.value(samples_ms, 0.5),
            jitter_ms=self.jitter.median_abs_delta_ms(samples_ms),
        )

    def measure_download(self) -> BandwidthStats:
        """Measure download bandwidth (bits per second)."""

        if self.settings.warmup_bytes > 0:
            warm_url = f"{self._server()}/__down?bytes={self.settings.warmup_bytes}"
            _ = self.transport.get(
                warm_url,
                timeout_s=self.settings.timeout_s,
                read_limit_bytes=self.settings.warmup_bytes,
            )

        url = f"{self._server()}/__down?bytes={self.settings.download_bytes}"
        timings = self.transport.get(url, timeout_s=self.settings.timeout_s)
        if timings.elapsed_s <= 0:
            raise ValueError("download elapsed time must be > 0")
        bps = (timings.transferred_bytes * 8) / timings.elapsed_s
        return BandwidthStats(bps=bps)

    def measure_upload(self) -> BandwidthStats:
        """Measure upload bandwidth (bits per second)."""

        url = f"{self._server()}/__up?bytes={self.settings.upload_bytes}"
        timings = self.transport.post(
            url, timeout_s=self.settings.timeout_s, body_bytes=self.settings.upload_bytes
        )
        if timings.elapsed_s <= 0:
            raise ValueError("upload elapsed time must be > 0")
        bps = (timings.transferred_bytes * 8) / timings.elapsed_s
        return BandwidthStats(bps=bps)

    def run(self) -> SpeedTestResult:
        """Run latency + download + upload measurements."""

        latency = self.measure_latency()
        download = self.measure_download()
        upload = self.measure_upload()
        return SpeedTestResult(latency=latency, download=download, upload=upload)


def _percentile(values: list[float], percentile: float) -> float:
    """Return percentile using nearest-rank on sorted values."""

    return PercentileCalculator().value(values, percentile)


def _jitter_ms(samples_ms: Iterable[float]) -> float:
    """Compute jitter as median absolute delta between consecutive samples."""

    return JitterCalculator().median_abs_delta_ms(samples_ms)


def measure_latency(settings: SpeedTestSettings) -> LatencyStats:
    """Measure unloaded latency using GET requests with bytes=0."""

    try:
        return SpeedTester(settings=settings, transport=StdlibTransport()).measure_latency()
    except HttpError as exc:
        raise RuntimeError(f"Network measurement failed: {exc}") from exc


def measure_download(settings: SpeedTestSettings) -> BandwidthStats:
    """Measure download bandwidth (Mbps) using a single request."""

    try:
        return SpeedTester(settings=settings, transport=StdlibTransport()).measure_download()
    except HttpError as exc:
        raise RuntimeError(f"Network measurement failed: {exc}") from exc


def measure_upload(settings: SpeedTestSettings) -> BandwidthStats:
    """Measure upload bandwidth (Mbps) using a single request."""

    try:
        return SpeedTester(settings=settings, transport=StdlibTransport()).measure_upload()
    except HttpError as exc:
        raise RuntimeError(f"Network measurement failed: {exc}") from exc


def run_speedtest(settings: SpeedTestSettings) -> SpeedTestResult:
    """Run latency + download + upload measurements."""

    try:
        return SpeedTester(settings=settings, transport=StdlibTransport()).run()
    except HttpError as exc:
        raise RuntimeError(f"Network measurement failed: {exc}") from exc
