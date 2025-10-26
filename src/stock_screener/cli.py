"""Command line interface for the stock screener."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from .criteria import StockFilterCriteria
from .formatting import format_number
from .models import StockFinancials
from .reporting import (
    EmailSettings,
    build_email_body,
    build_email_message,
    build_email_subject,
    send_email,
)
from .screener import DEFAULT_TICKERS, ScreeningResult, screen_stocks


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

    result = screen_stocks(tickers, criteria)

    if result.matches:
        _print_table(result.matches)
    else:
        print("No stocks matched the provided criteria.")

    if result.non_matches:
        print("\nStocks failing the criteria:")
        for financials in result.non_matches:
            print(f"  - {financials.ticker}")

    if result.errors:
        print("\nTickers with data issues:")
        for error in result.errors:
            assert error.financials is None
            print(f"  - {error.ticker}: {error.error}")

    if args.email_to:
        try:
            _send_email_report(args, criteria, result)
        except Exception as exc:  # pragma: no cover - network interactions
            parser.error(f"Failed to send email report: {exc}")

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
        help="Minimum dividend yield percentage (e.g. 2 for 2%%).",
    )
    parser.add_argument(
        "--min-market-cap",
        type=float,
        help="Minimum market capitalization (in USD).",
    )
    parser.add_argument(
        "--email-to",
        help="Email address to send the detailed report to.",
    )
    parser.add_argument(
        "--email-from",
        help="Sender email address for the report.",
    )
    parser.add_argument(
        "--email-subject",
        default=None,
        help="Custom email subject. Defaults to an auto-generated value.",
    )
    parser.add_argument(
        "--smtp-host",
        help="SMTP server hostname.",
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        default=587,
        help="SMTP server port. Defaults to 587.",
    )
    parser.add_argument(
        "--smtp-username",
        help="SMTP username for authentication (optional).",
    )
    parser.add_argument(
        "--smtp-password",
        help="SMTP password for authentication (optional).",
    )
    parser.add_argument(
        "--smtp-use-ssl",
        action="store_true",
        help="Use SMTP over SSL/TLS (implicit TLS).",
    )
    parser.add_argument(
        "--smtp-use-tls",
        action="store_true",
        help="Upgrade the connection to TLS using STARTTLS.",
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
            format_number(financials.pe_ratio),
            format_number(financials.pb_ratio),
            format_number(financials.dividend_yield),
            format_number(financials.market_cap),
        ]
        print("\t".join(row))


def _send_email_report(
    args: argparse.Namespace,
    criteria: StockFilterCriteria,
    result: ScreeningResult,
) -> None:
    if not args.email_from:
        raise ValueError("--email-from is required when --email-to is specified")
    if not args.smtp_host:
        raise ValueError("--smtp-host is required when --email-to is specified")
    if args.smtp_use_ssl and args.smtp_use_tls:
        raise ValueError("Use either --smtp-use-ssl or --smtp-use-tls, not both")

    subject = args.email_subject or build_email_subject()
    body = build_email_body(criteria, result)
    message = build_email_message(
        sender=args.email_from,
        recipient=args.email_to,
        subject=subject,
        body=body,
    )

    settings = EmailSettings(
        host=args.smtp_host,
        port=args.smtp_port,
        username=args.smtp_username,
        password=args.smtp_password,
        use_tls=args.smtp_use_tls,
        use_ssl=args.smtp_use_ssl,
    )

    send_email(message, settings)
    print(f"\nEmail report sent to {args.email_to}.")


if __name__ == "__main__":  # pragma: no cover - manual usage entrypoint
    raise SystemExit(main())
