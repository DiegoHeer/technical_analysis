import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

import talib
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.pylab import date2num


class TA:
    def __init__(self, ticker):
        self.ticker = ticker

        # Get today's date as UTC timestamp
        self.today = datetime.strptime(datetime.today().strftime("%d/%m/%Y %z") + " +0000", "%d/%m/%Y %z")
        self.today_timestamp = int(self.today.timestamp())

        # Get date from 1 year ago as UTC timestamp
        self.one_year_ago = self.today - relativedelta(years=1)
        self.one_year_ago_timestamp = int(self.one_year_ago.timestamp())

        # Parameters for usage
        self.data = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_price_history(self):
        # Put stock price data in dataframe
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{self.ticker}?period1=" \
              f"{self.one_year_ago_timestamp}&period2={self.today_timestamp}&interval=1d&events=history"
        self.data = pd.read_csv(url)

        # Convert date to timestamp and make index
        self.data.index = self.data["Date"].apply(lambda x: pd.Timestamp(x))
        self.data.drop("Date", axis=1, inplace=True)

        return self.data

    def get_indicators(self):
        # Get MACD
        self.data['macd'], self.data['macd_signal'], self.data['macd_hist'], = talib.MACD(self.data['Close'])

        # Get MA for 10 trading days
        self.data['ma10'] = talib.MA(self.data['Close'], timeperiod=10)

        # # Get Stochastics
        # self.data['stoch'] = talib.STOCH(self.data['Close'])

        return self.data

    def plot_chart(self, num_observations):
        # Filter number of observations to plot
        self.data = self.data.iloc[-num_observations:]

        # Create figure and set axes for subplots
        fig = plt.figure()
        fig.set_size_inches((20, 16))
        ax_candle = fig.add_axes((0, 0.72, 1, 0.32))
        ax_macd = fig.add_axes((0, 0.48, 1, 0.2), sharex=ax_candle)
        ax_vol = fig.add_axes((0, 0, 1, 0.2), sharex=ax_candle)

        # Format x-axis ticks as dates
        ax_candle.xaxis_date()

        # Get nested list of date, open, high, low and close prices
        ohlc = []
        for date, row in self.data.iterrows():
            openp, highp, lowp, closep = row[:4]
            ohlc.append([date2num(date), openp, highp, lowp, closep])

        # Plot candlestick chart
        ax_candle.plot(self.data.index, self.data['ma10'], label="MA10")
        candlestick_ohlc(ax_candle, ohlc, colorup="g", colordown="r", width=0.8)
        ax_candle.legend()

        # Plot MACD
        ax_macd.plot(self.data.index, self.data["macd"], label="macd")
        ax_macd.bar(self.data.index, self.data["macd_hist"] * 3, label="hist")
        ax_macd.plot(self.data.index, self.data["macd_signal"], label="signal")
        ax_macd.legend()

        # Show volume in millions
        ax_vol.bar(self.data.index, self.data["Volume"] / 1000000)
        ax_vol.set_ylabel("(Million)")

        # Save the chart as PNG
        fig.savefig(self.ticker + ".png", bbox_inches="tight")

        plt.show()


if __name__ == '__main__':
    test = TA("AAPL")
    test.get_price_history()
    test.get_indicators()
    test.plot_chart(180)
