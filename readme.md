# 📊 Multi-Asset Portfolio Analyzer

`portfolio_analyzer.py` is a simple quantitative finance tool that helps you analyze how a portfolio of multiple assets performs over time. It computes portfolio returns, volatility, Sharpe ratio, asset correlations, and compares the portfolio to a benchmark like SPY.

This project builds directly on the *daily-return-analyser* and extends it to multi-asset portfolio analytics.

---

## 🚀 Features

- Download historical price data for multiple tickers  
- Compute daily returns for each asset  
- Apply user-defined portfolio weights  
- Calculate:  
  - **Annualized portfolio return**  
  - **Annualized volatility (risk)**  
  - **Sharpe ratio (risk-adjusted return)**  
- Generate a **correlation heatmap** for diversification analysis  
- Plot **portfolio vs benchmark** cumulative returns  

---

## 🧠 Concepts Used

### **Portfolio Weights**
The fraction of the total investment allocated to each asset.  
Example: `40 30 30` → 40% AAPL, 30% MSFT, 30% GOOG.

### **Daily Returns**
Percent change in price from one day to the next.

### **Portfolio Return**
Weighted sum of individual asset returns.

### **Annualized Return**
Compounded yearly growth based on average daily returns.

### **Annualized Volatility**
Measures how much the portfolio fluctuates.

### **Sharpe Ratio**
How much excess return (above risk-free rate) you earn per unit of risk.

### **Correlation Matrix**
Shows how assets move relative to each other (for diversification).

---

## 📦 Installation

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install requirements:

    pip install -r requirements.txt


---

## ▶️ How to Run

    python portfolio_analyzer.py

You will be prompted to enter:

- Tickers (e.g., `AAPL MSFT GOOG`)  
- Start date  
- End date  
- Portfolio weights  
- Benchmark ticker (optional)  
- Annual risk-free rate  

Example:

    Enter asset tickers: AAPL MSFT GOOG
    Enter START date: 2017-01-01
    Enter END date: 2024-01-01
    Enter 3 portfolio weights: 40 30 30
    Enter benchmark ticker: SPY
    Enter annual risk-free rate: 5

---

## 📈 Outputs

1. **Portfolio Metrics**
   - Annualized Return  
   - Annualized Volatility  
   - Sharpe Ratio  

2. **Correlation Heatmap**  
   Shows how strongly each pair of assets moves together.

3. **Portfolio vs Benchmark Chart**  
   Visualizes long-term portfolio performance compared to SPY.

---

## 📁 File Structure

    project2_portfolio_analyzer/
    ├── portfolio_analyzer.py
    ├── requirements.txt
    └── README.md

---

## ✅ Summary

This script gives you a complete understanding of how a multi-asset portfolio performs over a given time period. It is a foundational quant project that prepares you for more advanced topics like:

- Efficient frontiers  
- Risk parity portfolios  
- Factor models  
- Backtesting engines  
