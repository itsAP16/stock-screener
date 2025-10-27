"""Standalone example demonstrating direct usage of the data layer.

Run this module to fetch a handful of key valuation metrics for one or more
symbols. By default, the script queries a small basket of large-cap tech
stocks. You can pass ticker symbols on the command line to customise which
securities are retrieved.
"""
from __future__ import annotations

import argparse
from typing import Iterable

from stock_screener.data import DataRepository, InMemoryCache, YahooFinanceDataSource


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the example script."""
    parser = argparse.ArgumentParser(
        description="Fetch valuation metrics for tickers using the data layer",
    )
    parser.add_argument(
        "tickers",
        nargs="*",
        default=("AAPL", "MSFT", "GOOGL"),
        help="Ticker symbols to query (defaults to a few large-cap tech names)",
    )
    parser.add_argument(
        "--no-cache",
        dest="use_cache",
        action="store_false",
        help="Disable the in-memory cache and fetch each request from the datasource",
    )
    return parser.parse_args()


def fetch_financials(tickers: Iterable[str], use_cache: bool = True) -> None:
    """Fetch and print financial metrics for the provided tickers."""
    cache = InMemoryCache() if use_cache else None
    repository = DataRepository(YahooFinanceDataSource(), cache=cache)

    for ticker in tickers:
        result = repository.fetch(ticker)
        if result.financials is None:
            print(f"{ticker}: error fetching data -> {result.error}")
            continue

        financials = result.financials
        print(
            f"{financials.ticker}: "
            f"PE={financials.pe_ratio} "
            f"PB={financials.pb_ratio} "
            f"Dividend Yield={financials.dividend_yield} "
            f"Market Cap={financials.market_cap}"
        )


def main() -> None:
    args = parse_args()
    fetch_financials(args.tickers, use_cache=args.use_cache)


if __name__ == "__main__":
    main()
