from __future__ import annotations

from speedtest.core import _percentile


def test_percentile_median() -> None:
    assert _percentile([10.0, 20.0, 30.0], 0.5) == 20.0
