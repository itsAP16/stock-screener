"""Command line interface for the stock screener."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from .criteria import StockFilterCriteria
from .models import StockFinancials
from .screener import DEFAULT_TICKERS, screen_stocks


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    tickers = _resolve_tickers(args.tickers, args.ticker_file)
    if not tickers:
        parser.error("No tickers provided. Use --tickers or --ticker-file.")

    criteria = StockFilterCriteria(
        max_pe_ratio=args.max_pe,
        max_pb_ratio=args.max_pb,
        min_dividend_yield=args.min_dividend_yield,
        min_market_cap=args.min_market_cap,
    )

    matches, errors = screen_stocks(tickers, criteria)

    if matches:
        _print_table(matches)
    else:
        print("No stocks matched the provided criteria.")

    if errors:
        print("\nTickers with data issues:")
        for result in errors:
            assert result.financials is None
            print(f"  - {result.ticker}: {result.error}")

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Ticker symbols to screen (e.g. AAPL MSFT).",
    )
    parser.add_argument(
        "--ticker-file",
        type=Path,
        help="Path to a newline-delimited list of ticker symbols.",
    )
    parser.add_argument(
        "--max-pe",
        type=float,
        dest="max_pe",
        help="Maximum acceptable trailing P/E ratio.",
    )
    parser.add_argument(
        "--max-pb",
        type=float,
        dest="max_pb",
        help="Maximum acceptable price-to-book ratio.",
    )
    parser.add_argument(
        "--min-dividend-yield",
        type=float,
        help="Minimum dividend yield percentage (e.g. 2 for 2%).",
    )
    parser.add_argument(
        "--min-market-cap",
        type=float,
        help="Minimum market capitalization (in USD).",
    )
    return parser


def _resolve_tickers(
    tickers: Iterable[str] | None,
    ticker_file: Path | None,
) -> list[str]:
    if ticker_file is not None:
        if not ticker_file.exists():
            raise SystemExit(f"Ticker file not found: {ticker_file}")
        file_tickers = [line.strip() for line in ticker_file.read_text().splitlines() if line.strip()]
    else:
        file_tickers = []

    arg_tickers = [ticker.strip() for ticker in tickers or [] if ticker.strip()]

    combined = arg_tickers or file_tickers or list(DEFAULT_TICKERS)
    return [ticker.upper() for ticker in combined]


def _print_table(matches: Sequence[StockFinancials]) -> None:
    headers = ["Ticker", "P/E", "P/B", "Dividend Yield (%)", "Market Cap (USD)"]
    print("\t".join(headers))
    for financials in matches:
        row = [
            financials.ticker,
            _format_number(financials.pe_ratio),
            _format_number(financials.pb_ratio),
            _format_number(financials.dividend_yield),
            _format_number(financials.market_cap),
        ]
        print("\t".join(row))


def _format_number(value: float | None) -> str:
    if value is None:
        return "-"
    if abs(value) >= 1:
        return f"{value:,.2f}"
    return f"{value:.4f}"


if __name__ == "__main__":  # pragma: no cover - manual usage entrypoint
    raise SystemExit(main())
