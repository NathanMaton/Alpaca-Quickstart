"""
More of an analytical tool and plotting script than part of a trading bot, this is a helper
file.
"""

import yfinance as yf
import pandas as pd
import ta
import matplotlib.pyplot as plt

# Crypto assets to track
assets = ["BTC-USD", "SOL-USD", "ETH-USD", "DOGE-USD"]

# Plotting
fig, axes = plt.subplots(nrows=len(assets), ncols=1, figsize=(12, 10), sharex=True)
fig.suptitle('RSI for Multiple Crypto Assets Over the Last Year', fontsize=16)

# RSI Calculation and Plotting
for i, asset in enumerate(assets):
    # Fetch data
    data = yf.Ticker(asset).history(period="1y")
    
    # Calculate RSI
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=7).rsi()

    # Identify oversold/overbought signals
    data['Oversold'] = data['RSI'] < 30
    data['Overbought'] = data['RSI'] > 70

    # Plotting
    axes[i].plot(data.index.to_numpy(), data['RSI'].to_numpy(), color='blue', label='RSI')
    axes[i].set_ylabel(f'{asset} RSI')

    # Oversold Signals (green dots)
    axes[i].scatter(data.loc[data['Oversold']].index.to_numpy(), 
                    data.loc[data['Oversold']]['RSI'].to_numpy(), 
                    marker='o', color='green', label='Oversold')

    # Overbought Signals (orange dots)
    axes[i].scatter(data.loc[data['Overbought']].index.to_numpy(), 
                    data.loc[data['Overbought']]['RSI'].to_numpy(), 
                    marker='o', color='orange', label='Overbought')

    # Add horizontal lines for RSI thresholds
    axes[i].axhline(y=20, color='green', linestyle='--', linewidth=0.5)
    axes[i].axhline(y=80, color='orange', linestyle='--', linewidth=0.5)

    axes[i].grid(axis='y')
    axes[i].legend()

# Format x-axis dates
import matplotlib.dates as mdates
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.xticks(rotation=45)
plt.xlabel('Date', fontsize=12)
plt.tight_layout()
plt.subplots_adjust(top=0.92)  # Adjust for title overlap
plt.show()
