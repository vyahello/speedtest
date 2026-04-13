"""CLI entrypoint for the speedtest utility."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from rich.console import Console
from rich.table import Table

from speedtest.core import run_speedtest
from speedtest.models import SpeedTestResult, SpeedTestSettings

_PROFILES: dict[str, SpeedTestSettings] = {
    "fast": SpeedTestSettings(
        timeout_s=3.0,
        latency_requests=2,
        download_bytes=1_000_000,
        upload_bytes=500_000,
        warmup_bytes=0,
    ),
    "medium": SpeedTestSettings(
        timeout_s=6.0,
        latency_requests=7,
        download_bytes=8_000_000,
        upload_bytes=4_000_000,
        warmup_bytes=100_000,
    ),
    "standard": SpeedTestSettings(),
    "extended": SpeedTestSettings(
        timeout_s=15.0,
        latency_requests=20,
        download_bytes=25_000_000,
        upload_bytes=10_000_000,
        warmup_bytes=200_000,
    ),
}


def _build_parser() -> argparse.ArgumentParser:
    """Build an argparse parser for the CLI."""

    parser = argparse.ArgumentParser(
        prog="speedtest",
        description="Measure network latency, download, and upload speed.",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(_PROFILES.keys()),
        default="standard",
        help="Measurement profile (default: standard)",
    )
    parser.add_argument("--server", default=None, help="Base server URL")
    parser.add_argument("--timeout", type=float, default=None, help="HTTP timeout (s)")
    parser.add_argument("--latency-requests", type=int, default=None)
    parser.add_argument("--download-bytes", type=int, default=None)
    parser.add_argument("--upload-bytes", type=int, default=None)
    parser.add_argument("--warmup-bytes", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    return parser


def _result_table(settings: SpeedTestSettings, result: SpeedTestResult) -> Table:
    """Render results as a Rich table."""

    table = Table(title="Speedtest results", show_lines=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Server", settings.server)
    table.add_row("Latency", f"{result.latency.latency_ms:.1f} ms")
    table.add_row("Jitter", f"{result.latency.jitter_ms:.1f} ms")
    table.add_row("Download", f"{result.download.mbps:.2f} Mbps")
    table.add_row("Upload", f"{result.upload.mbps:.2f} Mbps")
    return table


def main(argv: list[str] | None = None) -> None:
    """Run the CLI."""

    args = _build_parser().parse_args(argv)
    base = _PROFILES[str(args.profile)]
    settings = SpeedTestSettings(
        server=base.server if args.server is None else str(args.server),
        timeout_s=base.timeout_s if args.timeout is None else float(args.timeout),
        latency_requests=(
            base.latency_requests if args.latency_requests is None else int(args.latency_requests)
        ),
        download_bytes=(
            base.download_bytes if args.download_bytes is None else int(args.download_bytes)
        ),
        upload_bytes=base.upload_bytes if args.upload_bytes is None else int(args.upload_bytes),
        warmup_bytes=base.warmup_bytes if args.warmup_bytes is None else int(args.warmup_bytes),
    )

    console = Console()
    try:
        # Show a visual indicator while measurements run, but keep the final output
        # limited to either JSON or the results table.
        with console.status("Running speedtest…", spinner="dots"):
            result = run_speedtest(settings)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        console.print(f"[bold red]error:[/bold red] {exc}")
        raise SystemExit(2) from exc

    if args.json:
        payload = {"settings": asdict(settings), "result": asdict(result)}
        console.print(json.dumps(payload, indent=2, sort_keys=True))
        return

    console.print(_result_table(settings, result))


if __name__ == "__main__":
    main(sys.argv[1:])
