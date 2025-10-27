# Stock Screener

A simple command-line stock screener that retrieves fundamental data from Yahoo
Finance and filters securities based on configurable valuation criteria.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To work on the project as an installable package in development mode, install it
directly from the repository root:

```bash
pip install -e .
```

This exposes the package (`stock_screener`) and a `stock-screener` console
script for local testing without repeatedly adjusting `PYTHONPATH`.

## Usage

Run the screener with default tickers:

```bash
python -m stock_screener.cli --max-pe 25 --max-pb 5 --min-dividend-yield 1.5
```

Specify custom tickers directly:

```bash
python -m stock_screener.cli --tickers AAPL MSFT KO --max-pe 20
```

You can also store tickers in a newline-delimited file:

```bash
python -m stock_screener.cli --ticker-file path/to/tickers.txt --max-pe 15 --min-market-cap 1e11
```

All ratios use trailing values provided by Yahoo Finance. Dividend yield is
expressed as a percentage.

## Using the data layer directly

The data package can be used standalone if you want to embed the screener's
data retrieval in another application or script. The example below shows how to
instantiate the default Yahoo Finance datasource with optional in-memory caching
and fetch fundamental metrics for a list of tickers:

```python
from stock_screener.data import DataRepository, InMemoryCache, YahooFinanceDataSource

repo = DataRepository(YahooFinanceDataSource(), cache=InMemoryCache())

for ticker in ("AAPL", "MSFT", "GOOGL"):
    result = repo.fetch(ticker)
    if result.financials is None:
        print(f"{ticker}: error fetching data -> {result.error}")
        continue

    financials = result.financials
    print(
        f"{financials.ticker}: PE={financials.pe_ratio} "
        f"PB={financials.pb_ratio} Dividend Yield={financials.dividend_yield} "
        f"Market Cap={financials.market_cap}"
    )
```

### Running the standalone example script

You can try the ready-made script that ships with the project:

```bash
python examples/fetch_financials.py
```

By default, the script queries a handful of large-cap technology tickers. Supply
custom tickers to override that list, and disable caching if you want to force
fresh lookups for each run:

```bash
python examples/fetch_financials.py TSLA NVDA --no-cache
```

This is a convenient way to experiment with the pluggable data layer without
invoking the CLI workflow.
