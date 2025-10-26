"""Utilities for building and sending stock screening reports."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
import smtplib
from typing import Sequence

from .criteria import StockFilterCriteria
from .data import FetchResult
from .formatting import format_number
from .models import StockFinancials
from .screener import ScreeningResult


@dataclass(frozen=True)
class EmailSettings:
    """Configuration used to connect to an SMTP server."""

    host: str
    port: int
    username: str | None = None
    password: str | None = None
    use_tls: bool = True
    use_ssl: bool = False

    def __post_init__(self) -> None:
        if self.use_tls and self.use_ssl:
            raise ValueError("use_tls and use_ssl cannot both be enabled")


def build_email_subject(now: datetime | None = None) -> str:
    """Create a descriptive email subject line."""

    timestamp = (now or datetime.now()).strftime("%Y-%m-%d")
    return f"Stock screening report - {timestamp}"


def build_email_body(criteria: StockFilterCriteria, result: ScreeningResult) -> str:
    """Generate the plain-text body for an email report."""

    lines: list[str] = []

    lines.append("Stock screening summary")
    lines.append("=" * len(lines[-1]))
    lines.append("")

    lines.append("Screening criteria:")
    for description in criteria.describe():
        lines.append(f"  • {description}")
    lines.append("")

    total_reviewed = len(result.matches) + len(result.non_matches) + len(result.errors)
    lines.append(f"Tickers reviewed: {total_reviewed}")
    lines.append(f"Recommended trades: {len(result.matches)}")
    lines.append(f"Do-not-trade candidates: {len(result.non_matches)}")
    lines.append(f"Tickers with data issues: {len(result.errors)}")
    lines.append("")

    lines.extend(_format_financials_section("Recommended trades", result.matches))
    lines.append("")
    lines.extend(_format_rejections_section(criteria, result.non_matches))
    lines.append("")
    lines.extend(_format_errors_section(result.errors))

    return "\n".join(lines).strip() + "\n"


def build_email_message(
    *,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> EmailMessage:
    """Construct an ``EmailMessage`` ready for sending."""

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    return message


def send_email(message: EmailMessage, settings: EmailSettings) -> None:
    """Send ``message`` using the provided SMTP ``settings``."""

    if settings.use_ssl:
        smtp_cls = smtplib.SMTP_SSL
    else:
        smtp_cls = smtplib.SMTP

    with smtp_cls(settings.host, settings.port) as server:
        if settings.use_tls and not settings.use_ssl:
            server.starttls()
        if settings.username:
            server.login(settings.username, settings.password or "")
        server.send_message(message)


def _format_financials_section(
    title: str,
    financials: Sequence[StockFinancials],
) -> list[str]:
    if not financials:
        return [f"{title}: none"]

    lines = [title + ":"]
    table_lines = _render_financials_table(financials)
    lines.extend(f"  {line}" for line in table_lines)
    return lines


def _render_financials_table(financials: Sequence[StockFinancials]) -> list[str]:
    headers = ("Ticker", "P/E", "P/B", "Dividend Yield (%)", "Market Cap (USD)")
    rows: list[Sequence[str]] = [headers]

    for item in financials:
        rows.append(
            (
                item.ticker,
                format_number(item.pe_ratio),
                format_number(item.pb_ratio),
                format_number(item.dividend_yield),
                format_number(item.market_cap),
            )
        )

    column_widths = [max(len(row[idx]) for row in rows) for idx in range(len(headers))]

    def _join(row: Sequence[str]) -> str:
        return " | ".join(cell.ljust(column_widths[idx]) for idx, cell in enumerate(row))

    separator = "-+-".join("-" * width for width in column_widths)
    lines = [_join(rows[0]), separator]
    lines.extend(_join(row) for row in rows[1:])
    return lines


def _format_rejections_section(
    criteria: StockFilterCriteria,
    financials: Sequence[StockFinancials],
) -> list[str]:
    if not financials:
        return ["Do-not-trade candidates: none"]

    lines = ["Do-not-trade candidates:"]
    for item in financials:
        dividend = format_number(item.dividend_yield)
        dividend_display = dividend if dividend == "-" else f"{dividend}%"
        market_cap = format_number(item.market_cap)
        market_cap_display = market_cap if market_cap == "-" else f"{market_cap} USD"
        metrics = (
            f"P/E={format_number(item.pe_ratio)}",
            f"P/B={format_number(item.pb_ratio)}",
            f"Dividend Yield={dividend_display}",
            f"Market Cap={market_cap_display}",
        )
        lines.append(f"  - {item.ticker} ({', '.join(metrics)})")
        for reason in criteria.rejection_reasons(item):
            lines.append(f"      • {reason}")
    return lines


def _format_errors_section(results: Sequence[FetchResult]) -> list[str]:
    if not results:
        return ["Tickers with data issues: none"]

    lines = ["Tickers with data issues:"]
    for result in results:
        error_detail = result.error or "Unknown error"
        lines.append(f"  - {result.ticker}: {error_detail}")
    return lines
