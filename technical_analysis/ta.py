import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

import talib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

        # self.data['Short Date'] = pd.DatetimeIndex(self.data.index).day.astype(str) + '-' + pd.DatetimeIndex(
        #     self.data.index).month.astype(str)

        return self.data

    def get_indicators(self):
        # Get MACD
        self.data['macd'], self.data['macd_signal'], self.data['macd_hist'], = talib.MACD(self.data['Close'])

        # Get MA for 10 trading days
        self.data['ma10'] = talib.MA(self.data['Close'], timeperiod=10)

        # Get MA for 50 trading days
        self.data['ma50'] = talib.MA(self.data['Close'], timeperiod=50)

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

    def plot_chart(self, num_months, fig_dir=None, show_fig=False):
        # Filter number of observations to plot based on how amount of months
        start_date = (self.today - relativedelta(months=num_months)).strftime('%d/%m/%Y')
        self.data = self.data.loc[start_date:]

        # Use dark background for chart
        plt.style.use('dark_background')

        # Create figure and set axes for subplots
        fig = plt.figure(figsize=(16, 10), dpi=100)
        ax_candle = fig.add_axes((0, 0.49, 1, 0.50))
        ax_macd = fig.add_axes((0, 0.26, 1, 0.20), sharex=ax_candle)
        ax_stoch = fig.add_axes((0, 0.03, 1, 0.20), sharex=ax_candle)

        # Format x-axis ticks as dates
        ax_candle.xaxis_date()

        # Last indicators
        last_vol = self.data['Volume'][-1]
        last_close = self.data['Close'][-1]
        last_close_date = self.data.index[-1].strftime('%d/%m/%Y')
        last_stoch = self.data['stoch'][-1]
        last_stoch_signal = self.data['stoch_signal'][-1]
        last_macd = self.data['macd'][-1]
        last_macd_signal = self.data['macd_signal'][-1]
        last_ma10 = self.data['ma10'][-1]
        last_ma50 = self.data['ma50'][-1]

        # Get nested list of date, open, high, low and close prices
        ohlc = []
        for date, row in self.data.iterrows():
            openp, highp, lowp, closep = row[:4]
            ohlc.append([date2num(date), openp, highp, lowp, closep])

        # Plot candlestick chart
        ax_candle.plot(self.data.index, self.data['ma10'], label=f"MA-10 ({round(last_ma10, 2)})",
                       color='cyan')
        ax_candle.plot(self.data.index, self.data['ma50'], label=f"MA-50 ({round(last_ma50, 2)})",
                       color='violet', alpha=0.5)
        candlestick_ohlc(ax_candle, ohlc, colorup="g", colordown="r", width=0.8)

        # Define volume division number so that the volume bars are shown in good proportion with the candle bar and MAs
        # digits_last_close = len(str(int(last_close)))
        # digits_last_vol = len(str(int(last_vol)))
        # vol_div = 10**(digits_last_vol-digits_last_close+1)

        # Show volume on price chart
        # ax_candle.bar(self.data.index, self.data["Volume"] / vol_div,
        #               label=f"Volume ({round(last_vol / 1000000)} Million)", color='#256ad9', alpha=0.3)

        ax_candle.yaxis.set_label_position("right")
        ax_candle.yaxis.tick_right()

        # Vertical line representing last close date
        ax_candle.axvline(x=self.data.index[-1], color='white', linestyle='-.', linewidth=0.7, alpha=0.5,
                          label=f"Last Close ({round(last_close, 2)})")

        # Create specific grid
        ax_candle.grid(True, which='major', color='grey', linestyle=':')

        # Include extra features to candle plot
        handles, labels = ax_candle.get_legend_handles_labels()
        handles.append(
            mpatches.Patch(color='none', label=f"Last Close Date: {last_close_date}"))
        handles.append(
            mpatches.Patch(color='none', label=f"Last Volume: {round(last_vol/1000000, 2)} Million"))
        ax_candle.legend(handles=handles, loc=2)

        # Format all x axis accordingly
        ax_candle.set_xticks(self.data.index, minor=True)

        # Plot Stochastics
        ax_stoch.plot(self.data.index, self.data["stoch"], label=f"stoch ({round(last_stoch, 2)})",
                      color='green')
        ax_stoch.plot(self.data.index, self.data["stoch_signal"],
                      label=f"signal ({round(last_stoch_signal, 2)})", color='red')

        # ax_stoch.plot(self.data.index, [80] * len(self.data.index), color='grey', linestyle='--', linewidth=1,
        #               alpha=0.7)
        # ax_stoch.plot(self.data.index, [20] * len(self.data.index), color='grey', linestyle='--', linewidth=1,
        #               alpha=0.7)
        ax_stoch.axhspan(20, 80, alpha=0.5, color='#2F2050')

        # Create specific grid
        ax_stoch.grid(True, which='major', color='grey', linestyle='-', alpha=0.5)

        ax_stoch.yaxis.set_label_position("right")
        ax_stoch.yaxis.tick_right()
        ax_stoch.legend(loc=2)

        # Plot MACD
        ax_macd.plot(self.data.index, self.data["macd"], label=f"macd  ({round(last_macd, 2)})",
                     color='green')
        ax_macd.plot(self.data.index, self.data["macd_signal"],
                     label=f"signal ({round(last_macd_signal, 2)})", color='red')

        colors = ['red' if (x < 0) else 'green' for x in self.data['macd_hist']]
        ax_macd.bar(self.data.index, self.data["macd_hist"] * 3, color=colors, alpha=0.3)

        ax_macd.yaxis.set_label_position("right")
        ax_macd.yaxis.tick_right()
        ax_macd.legend(loc=2)

        # Save the chart as PNG
        if fig_dir is not None and show_fig is True:
            fig_path = os.path.join(fig_dir, self.ticker + ".png")
            fig.savefig(fig_path, bbox_inches="tight")
            os.startfile(fig_path)


if __name__ == '__main__':
    test = TA("TSLA")
    test.get_price_history()
    result = test.get_indicators()
    # result.to_excel('test.xlsx')
    test.plot_chart(num_months=4, fig_dir=r'D:\PythonProjects\technical_analysis\technical_analysis\tests', show_fig=True)
    # print(test.get_stoch_buy_sell())
