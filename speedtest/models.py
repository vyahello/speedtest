"""Data models used by the speedtest utility."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpeedTestSettings:
    """Settings controlling what and how to measure."""

    server: str = "https://speed.cloudflare.com"
    # Defaults are a "standard" profile: a bit longer and more realistic.
    timeout_s: float = 10.0
    latency_requests: int = 5
    download_bytes: int = 10_000_000
    upload_bytes: int = 5_000_000
    warmup_bytes: int = 100_000


@dataclass(frozen=True, slots=True)
class LatencyStats:
    """Latency and jitter values (milliseconds)."""

    latency_ms: float
    jitter_ms: float


@dataclass(frozen=True, slots=True)
class BandwidthStats:
    """Bandwidth value (bits per second)."""

    bps: float

    @property
    def mbps(self) -> float:
        """Return bandwidth in megabits per second."""

        return self.bps / 1_000_000.0


@dataclass(frozen=True, slots=True)
class SpeedTestResult:
    """Complete speedtest results."""

    latency: LatencyStats
    download: BandwidthStats
    upload: BandwidthStats
