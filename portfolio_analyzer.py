#!/usr/bin/env python3

"""
Multi-Asset Portfolio Analyzer

Features:
- Ask user for tickers, weights, start/end dates, risk-free rate.
- Download adjusted close prices.
- Compute daily returns for each asset.
- Compute portfolio daily returns from weights.
- Calculate annualized return, annualized volatility, and Sharpe ratio.
- Plot:
  1. Correlation heatmap of asset returns.
  2. Portfolio vs benchmark cumulative returns.
"""

import sys
import datetime as dt
from typing import List

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns


def parse_tickers(raw: str) -> List[str]:
    """
    Convert a space- or comma-separated string of tickers into a clean list.
    Example: "AAPL MSFT,GOOG" -> ["AAPL", "MSFT", "GOOG"]
    """
    if not raw.strip():
        raise ValueError("You must enter at least one ticker.")
    # Replace commas with spaces, split, and uppercase
    tokens = raw.replace(",", " ").split()
    return [t.upper() for t in tokens]


def parse_weights(raw: str, n: int) -> np.ndarray:
    """
    Parse weights like "0.4 0.3 0.3" or "40 30 30" into a normalized vector of length n.

    - If weights sum to ~1, we assume they are fractions.
    - If weights sum to ~100, we assume they are percentages.
    """
    parts = raw.replace(",", " ").split()
    if len(parts) != n:
        raise ValueError(f"You provided {len(parts)} weights but {n} tickers.")

    w = np.array([float(p) for p in parts], dtype=float)
    s = w.sum()

    if s <= 0:
        raise ValueError("Weights must sum to a positive number.")

    # Detect percentage style
    if abs(s - 1.0) < 1e-6:
        # Already fractions
        return w
    elif abs(s - 100.0) < 1e-3:
        # Looks like percentages
        return w / 100.0
    else:
        # Just normalize
        return w / s


def annualize_return(daily_returns: pd.Series) -> float:
    """
    Annualized return from daily returns.
    Assumes ~252 trading days per year.
    """
    mean_daily = daily_returns.mean()
    return (1 + mean_daily) ** 252 - 1


def annualize_volatility(daily_returns: pd.Series) -> float:
    """
    Annualized volatility from daily returns.
    Assumes ~252 trading days per year.
    """
    return daily_returns.std() * np.sqrt(252)


def compute_sharpe_ratio(
    daily_returns: pd.Series,
    risk_free_rate_annual: float = 0.0,
) -> float:
    """
    Compute annual Sharpe ratio given portfolio daily returns and annual risk-free rate.

    risk_free_rate_annual is in decimal (e.g., 0.05 for 5%).
    """
    # Convert annual risk-free to daily (simple approximation)
    rf_daily = (1 + risk_free_rate_annual) ** (1 / 252) - 1
    excess_daily = daily_returns - rf_daily

    mean_excess_daily = excess_daily.mean()
    vol_daily = excess_daily.std()

    if vol_daily == 0:
        return np.nan

    sharpe_daily = mean_excess_daily / vol_daily
    # Scale to annual
    return sharpe_daily * np.sqrt(252)


def download_price_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """
    Download Adjusted Close prices for the given tickers and date range using yfinance.
    Returns a DataFrame with Date index and one column per ticker.
    """
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )

    # yfinance returns a multi-index columns when multiple tickers are used.
    # We only care about the 'Adj Close' level.
    if isinstance(data.columns, pd.MultiIndex):
        adj_close = data["Adj Close"].copy()
    else:
        # Single ticker case: rename to have a consistent DataFrame
        adj_close = data.to_frame(name=tickers[0])

    adj_close = adj_close.dropna(how="all")
    return adj_close


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute simple daily returns from price levels.
    """
    returns = prices.pct_change().dropna(how="all")
    return returns


def build_portfolio_returns(
    asset_returns: pd.DataFrame,
    weights: np.ndarray,
) -> pd.Series:
    """
    Given a T x N returns DataFrame and an N-length weight vector,
    compute the portfolio daily returns: r_p(t) = sum_i w_i * r_i(t).
    """
    # Align shapes: columns correspond to assets, weights is a vector
    return (asset_returns * weights).sum(axis=1)


def plot_correlation_heatmap(asset_returns: pd.DataFrame, tickers: List[str]) -> None:
    """
    Plot correlation heatmap between asset returns.
    """
    corr = asset_returns.corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        xticklabels=tickers,
        yticklabels=tickers,
    )
    plt.title("Asset Return Correlation Matrix")
    plt.tight_layout()
    plt.show()


def plot_portfolio_vs_benchmark(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series | None,
    start_value: float = 1_000.0,
) -> None:
    """
    Plot cumulative return curve for the portfolio vs optional benchmark.

    start_value is the initial investment amount (e.g., $1,000).
    """
    portfolio_cum = (1 + portfolio_returns).cumprod() * start_value

    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_cum.index, portfolio_cum.values, label="Portfolio")

    if benchmark_returns is not None:
        benchmark_cum = (1 + benchmark_returns).cumprod() * start_value
        plt.plot(benchmark_cum.index, benchmark_cum.values, label="Benchmark", linestyle="--")

    plt.title("Cumulative Returns: Portfolio vs Benchmark")
    plt.xlabel("Date")
    plt.ylabel(f"Portfolio value (starting at {start_value:,.0f})")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def main():
    print("=== Multi-Asset Portfolio Analyzer ===")

    # 1. Get user inputs
    raw_tickers = input("Enter asset tickers (space- or comma-separated): ").strip()
    tickers = parse_tickers(raw_tickers)
    n_assets = len(tickers)

    start = input("Enter START date (YYYY-MM-DD): ").strip()
    end = input("Enter END date (YYYY-MM-DD): ").strip()

    raw_weights = input(
        f"Enter {n_assets} portfolio weights "
        "(fractions that sum to 1 or percentages that sum to 100): "
    ).strip()
    weights = parse_weights(raw_weights, n_assets)

    benchmark = input(
        "Enter benchmark ticker (e.g., SPY), or press ENTER to skip: "
    ).strip()
    benchmark_ticker = benchmark.upper() if benchmark else None

    rf_str = input(
        "Enter annual risk-free rate in % (e.g., 5 for 5%, default 0): "
    ).strip()
    risk_free_rate_annual = float(rf_str) / 100.0 if rf_str else 0.0

    print("\nDownloading price data...")
    prices = download_price_data(tickers, start, end)

    if prices.empty:
        print("No price data downloaded. Check tickers and dates.")
        sys.exit(1)

    print(f"Downloaded price data for: {list(prices.columns)}")
    asset_returns = compute_daily_returns(prices)

    # Ensure tickers are in the same order as in the DataFrame
    tickers = list(prices.columns)
    n_assets = len(tickers)


    # Align weights with actual data columns (in case some tickers failed)
    actual_tickers = list(prices.columns)
    if len(actual_tickers) != len(tickers):
        print(
            "Warning: Some tickers may not have data. "
            "Weights will be re-normalized over available assets."
        )
        # Simple approach: assume the same order of successful tickers
        weights = weights[: len(actual_tickers)]
        weights = weights / weights.sum()
        tickers = actual_tickers

    portfolio_returns = build_portfolio_returns(asset_returns, weights)

    # 2. Compute metrics
    ann_ret = annualize_return(portfolio_returns)
    ann_vol = annualize_volatility(portfolio_returns)
    sharpe = compute_sharpe_ratio(portfolio_returns, risk_free_rate_annual)

    print("\n=== Portfolio Metrics ===")
    print(f"Tickers: {tickers}")
    print(f"Weights: {np.round(weights, 4)}")
    print(f"Annualized Return:     {ann_ret * 100:.2f}%")
    print(f"Annualized Volatility: {ann_vol * 100:.2f}%")
    print(f"Sharpe Ratio:          {sharpe:.2f}")

    # 3. Correlation heatmap
    print("\nGenerating correlation heatmap...")
    plot_correlation_heatmap(asset_returns, tickers)

    # 4. Portfolio vs benchmark plot
    benchmark_returns = None
    if benchmark_ticker:
        print(f"Downloading benchmark data for {benchmark_ticker}...")
        bench_prices = download_price_data([benchmark_ticker], start, end)
        if not bench_prices.empty:
            bench_ret = compute_daily_returns(bench_prices)
            # Take first (and only) column
            benchmark_returns = bench_ret.iloc[:, 0]
        else:
            print("Could not download benchmark data; skipping benchmark plot.")

    print("Plotting portfolio vs benchmark...")
    plot_portfolio_vs_benchmark(portfolio_returns, benchmark_returns)


if __name__ == "__main__":
    main()
