# Stock Screener

A simple command-line stock screener that retrieves fundamental data from Yahoo
Finance and filters securities based on configurable valuation criteria.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

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
