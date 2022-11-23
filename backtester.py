import sys
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from backtesting import Backtest, Strategy
from bot_strategies import Engulf, Rejection, Tolu
from utils.utilities import compute_latest_atr
from datetime import datetime
from typing import Optional
from main import at_resistance, at_support

#Base Strategy Class
class BaseStrategyCase(Strategy):
    unit_pip:Optional[float] = None
    sr_threshold:float = 0.1
    default_sl_points:float = 1.5
    default_tp_point:float = 4.5
    sr_probability:float = 0.0
    offset:int = 15

    def init(self):
        super().init()

    def next(self):
        super().next()

        #current price
        #current_price:float = self.data.Close[-1]

        #update stop loss for all trades
        # for trade in self.trades:
        #     if trade.is_long:
        #         trade.sl = max(trade.sl or -np.inf, current_price - (self.unit_pip * self.default_sl_points))
        #     else:
        #         trade.sl = min(trade.sl or np.inf, current_price + (self.unit_pip * self.default_sl_points))


# backtest Tolu Strategy
class ToluStrategyCase(BaseStrategyCase):

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            self.unit_pip = compute_latest_atr(df.iloc[(-self.offset - 1):-1, :])
            sr_threshold = self.unit_pip * self.sr_threshold

            if Tolu.is_bullish_trade(df.iloc[(-self.offset - 1):-1, :]) and \
                at_support(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price + (self.unit_pip * self.default_tp_point)
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl, tp=tp)

            elif Tolu.is_bearish_trade(df.iloc[(-self.offset - 1):-1, :]) and \
                at_resistance(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price - (self.unit_pip * self.default_tp_point)
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl, tp=tp)


# backtest engulf strategy
class EngulfStrategyCase(BaseStrategyCase):

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            self.unit_pip = compute_latest_atr(df.iloc[(-self.offset - 1):-1, :])
            sr_threshold = self.unit_pip * self.sr_threshold

            if Engulf.is_bullish_engulf(df.iloc[(-self.offset - 1):-1, :]) and \
                at_support(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price + (self.unit_pip * self.default_tp_point)
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl, tp=tp)

            elif Engulf.is_bearish_engulf(df.iloc[(-self.offset - 1):-1, :]) and \
                at_resistance(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price - (self.unit_pip * self.default_tp_point)
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl, tp=tp)


# Backtest Asian Rejection
class RejectionStrategyCase(BaseStrategyCase):

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            self.unit_pip = compute_latest_atr(df.iloc[(-self.offset - 1):-1, :])
            sr_threshold = self.unit_pip * self.sr_threshold

            if Rejection.is_bullish_rejection(df.iloc[(-self.offset - 1):-1, :]) and \
                at_support(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price + (self.unit_pip * self.default_tp_point)
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl, tp=tp)

            elif Engulf.is_bearish_engulf(df.iloc[(-self.offset - 1):-1, :]) and \
                at_resistance(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price - (self.unit_pip * self.default_tp_point)
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl, tp=tp)


# Composite Strategy Case
# Backtest Asian Rejection
class CompositeStrategyCase(BaseStrategyCase):

    offset = 12

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            self.unit_pip = compute_latest_atr(df.iloc[(-self.offset - 1):-1, :])
            sr_threshold = self.unit_pip * self.sr_threshold

            if (
                Rejection.is_bullish_rejection(df.iloc[(-self.offset - 1):-1, :]) or
                Engulf.is_bullish_engulf(df.iloc[(-self.offset - 1):-1, :]) or
                Tolu.is_bullish_trade(df.iloc[(-self.offset - 1):-1, :])) and \
                at_support(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price + (self.unit_pip * self.default_tp_point)
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl, tp=tp)

            elif (
                Rejection.is_bearish_rejection(df.iloc[(-self.offset - 1):-1, :]) or
                Engulf.is_bearish_engulf(df.iloc[(-self.offset - 1):-1, :]) or
                Tolu.is_bearish_trade(df.iloc[(-self.offset - 1):-1, :])) and \
                at_resistance(df.iloc[(-self.offset - 1):-1, :], p=self.sr_probability, threshold=sr_threshold):
                tp:float = current_price - (self.unit_pip * self.default_tp_point)
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl, tp=tp)


# main
if __name__ == '__main__':
    init_env:bool = mt5.initialize(login=51024038, password='uyQ8b3yr', server='ICMarketsSC-Demo')

    if not init_env:
        print('failed to initialise metatrader5')
        mt5.shutdown()
        sys.exit()

    #start time
    start_time:datetime = datetime(2022, 11, 14)

    # fetch and compile data
    rates:np.ndarray = mt5.copy_rates_from('US30', mt5.TIMEFRAME_M1, start_time, 180_000)
    rates_df:pd.DataFrame = pd.DataFrame(rates)
    rates_df['time'] = [datetime.fromtimestamp(uts) for uts in rates_df['time']]
    rates_df.index = rates_df['time']
    rates_df = rates_df[['open', 'low', 'high', 'close']]
    rates_df = rates_df.rename(columns={'close':'Close', 'open':'Open', 'low':'Low', 'high':'High'})

    # backtest cases
    tolu_backtester:Backtest = Backtest(rates_df, ToluStrategyCase, cash=100_000, commission=0)
    engulf_backtester:Backtest = Backtest(rates_df, EngulfStrategyCase, cash=100_000, commission=0)
    rejection_backtester:Backtest = Backtest(rates_df, RejectionStrategyCase, cash=100_000, commission=0)
    composite_backtester:Backtest = Backtest(rates_df, CompositeStrategyCase, cash=100_000, commission=0)


    print(tolu_backtester.run(), '\n\n')
    print(engulf_backtester.run(), '\n\n')
    print(rejection_backtester.run(), '\n\n')
    print(composite_backtester.run(), '\n\n')