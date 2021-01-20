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

        # Get Stochastics
        self.data['stoch'], self.data['stoch_signal'] = talib.STOCH(self.data['High'], self.data['Low'],
                                                                    self.data['Close'], fastk_period=14, slowk_period=5)

        return self.data

    def get_stoch_buy_sell(self):
        # This function gives the buy or sell answer for the last stock price related to the Stochastics indicator
        last_stoch_value = self.data.tail(1)['stoch'].values[0]
        last_stoch_signal = self.data.tail(1)['stoch_signal'].values[0]

        if last_stoch_value > last_stoch_signal:
            return 'buy'
        else:
            return 'sell'

    def get_macd_buy_sell(self):
        # This function gives the buy or sell answer for the last stock price related to the MACD indicator
        last_macd_value = self.data.tail(1)['macd'].values[0]
        last_macd_signal_value = self.data.tail(1)['macd_signal'].values[0]

        if last_macd_value > last_macd_signal_value:
            return 'buy'
        else:
            return 'sell'

    def get_ma10_buy_sell(self):
        # This function gives the buy or sell answer for the last stock price related to the MA10 indicator
        last_ma10_value = self.data.tail(1)['ma10'].values[0]
        last_close_price = self.data.tail(1)['Close'].values[0]

        if last_close_price > last_ma10_value:
            return 'buy'
        else:
            return 'sell'

    def plot_chart(self, num_observations):
        # Filter number of observations to plot
        self.data = self.data.iloc[-num_observations:]

        # Create figure and set axes for subplots
        fig = plt.figure()
        fig.set_size_inches((20, 10))
        ax_candle = fig.add_axes((0, 0.48, 1, 0.32))
        ax_macd = fig.add_axes((0, 0.24, 1, 0.2), sharex=ax_candle)
        ax_stoch = fig.add_axes((0, 0, 1, 0.2), sharex=ax_candle)

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
        ax_stoch.plot(self.data.index, self.data["stoch"], label="stoch")
        ax_stoch.plot(self.data.index, self.data["stoch_signal"], label="signal")
        ax_stoch.legend()

        # Plot Stochastics
        ax_macd.plot(self.data.index, self.data["macd"], label="macd")
        ax_macd.bar(self.data.index, self.data["macd_hist"] * 3, label="hist")
        ax_macd.plot(self.data.index, self.data["macd_signal"], label="signal")
        ax_macd.legend()

        # Save the chart as PNG
        fig.savefig(self.ticker + ".png", bbox_inches="tight")

        plt.show()


if __name__ == '__main__':
    test = TA("TSLA")
    test.get_price_history()
    result = test.get_indicators()
    # result.to_excel('test.xlsx')
    # test.plot_chart(180)
    print(test.get_stoch_buy_sell())
