import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define your portfolio
portfolio = {
    '379810.KS': 0.3,  # KODEX 미국나스닥100TR
    '379800.KS': 0.3,  # KODEX 미국S&P500TR
    '251350.KS': 0.3,  # KODEX 선진국MSCI World
    '453810.KS': 0.1,  # KODEX 인도 nifty50
}

# Download historical data for each stock in the portfolio
data = yf.download(list(portfolio.keys()), start="2021-05-01", end="2024-07-01")['Adj Close']

# Calculate daily returns
daily_returns = data.pct_change()

# Calculate portfolio returns
weights = np.array(list(portfolio.values()))
portfolio_returns = daily_returns.dot(weights)

# Calculate cumulative returns
cumulative_returns = (1 + portfolio_returns).cumprod() - 1

# Plot the portfolio performance
plt.figure(figsize=(10, 6))
plt.plot(cumulative_returns, label='Portfolio')
plt.title('Portfolio Cumulative Returns')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.legend()
plt.show()

# Display portfolio performance metrics
total_return = cumulative_returns.iloc[-1]
annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1  # Assuming 252 trading days in a year
annualized_volatility = portfolio_returns.std() * np.sqrt(252)

print(f'Total Return: {total_return:.2%}')
print(f'Annualized Return: {annualized_return:.2%}')
print(f'Annualized Volatility: {annualized_volatility:.2%}')