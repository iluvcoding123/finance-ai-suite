# test_yf.py
import yfinance as yf

ticker = "AAPL"

tkr = yf.Ticker(ticker)
hist = tkr.history(period="5d")

if not hist.empty:
    print(f"Latest close for {ticker}: {hist['Close'].iloc[-1]}")
else:
    print(f"Failed to fetch data for {ticker}")