import sys
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from backtesting import Backtest, Strategy
from bot_strategies import Engulf, Rejection, Tolu, SupportResistance
from utils.utilities import compute_latest_atr
from datetime import datetime

#Base Strategy Class
class BaseStrategyCase(Strategy):
    unit_pip:float = 0.01
    default_sl_points:float = 5
    sr_treshold:float = 0.2

    def init(self):
        super().init()

    def next(self):
        super().next()


# backtest Tolu Strategy
class ToluStrategyCase(BaseStrategyCase):

    offset = 12

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        #update stop loss for all trades
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl or -np.inf, current_price - (self.unit_pip * self.default_sl_points))
            else:
                trade.sl = min(trade.sl or np.inf, current_price + (self.unit_pip * self.default_sl_points))

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            if Tolu.is_bullish_trade(df) and SupportResistance.is_near_support(df, self.sr_treshold):
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl)

            elif Tolu.is_bearish_trade(df) and SupportResistance.is_near_resistance(df, self.sr_treshold):
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl)


# backtest engulf strategy
class EngulfStrategyCase(BaseStrategyCase):

    offset = 12

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        #update stop loss for all trades
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl or -np.inf, current_price - (self.unit_pip * self.default_sl_points))
            else:
                trade.sl = min(trade.sl or np.inf, current_price + (self.unit_pip * self.default_sl_points))

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            if Engulf.is_bullish_engulf(df) and SupportResistance.is_near_support(df, self.sr_treshold):
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl)

            elif Engulf.is_bearish_engulf(df) and SupportResistance.is_near_resistance(df, self.sr_treshold):
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl)


# Backtest Asian Rejection
class RejectionStrategyCase(BaseStrategyCase):

    offset = 12

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        #update stop loss for all trades
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl or -np.inf, current_price - (self.unit_pip * self.default_sl_points))
            else:
                trade.sl = min(trade.sl or np.inf, current_price + (self.unit_pip * self.default_sl_points))

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            if Rejection.is_bullish_rejection(df) and SupportResistance.is_near_support(df, self.sr_treshold):
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl)

            elif Engulf.is_bearish_engulf(df) and SupportResistance.is_near_resistance(df, self.sr_treshold):
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl)


# Composite Strategy Case
# Backtest Asian Rejection
class CompositeStrategyCase(BaseStrategyCase):

    offset = 12

    def next(self):
        super().next()

        #current price
        current_price:float = self.data.Close[-1]

        #update stop loss for all trades
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl or -np.inf, current_price - (self.unit_pip * self.default_sl_points))
            else:
                trade.sl = min(trade.sl or np.inf, current_price + (self.unit_pip * self.default_sl_points))

        df = pd.DataFrame()
        df['close'] = self.data.Close[-self.offset:]
        df['open'] = self.data.Open[-self.offset:]
        df['high'] = self.data.High[-self.offset:]
        df['low'] = self.data.Low[-self.offset:]

        if len(df) >= self.offset:
            if (
                Rejection.is_bullish_rejection(df) or
                Engulf.is_bullish_engulf(df) or
                Tolu.is_bullish_trade(df)) and SupportResistance.is_near_support(df, self.sr_treshold):
                sl:float = current_price - (self.unit_pip * self.default_sl_points)
                self.buy(sl=sl)

            elif (
                Rejection.is_bearish_rejection(df) or
                Engulf.is_bearish_engulf(df) or
                Tolu.is_bearish_trade(df)) and SupportResistance.is_near_resistance(df, self.sr_treshold):
                sl:float = current_price + (self.unit_pip * self.default_sl_points)
                self.sell(sl=sl)


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
    rates:np.ndarray = mt5.copy_rates_from('XAUUSD', mt5.TIMEFRAME_M1, start_time, 1000)
    rates_df:pd.DataFrame = pd.DataFrame(rates)
    rates_df['time'] = [datetime.fromtimestamp(uts) for uts in rates_df['time']]
    rates_df.index = rates_df['time']
    rates_df = rates_df[['open', 'low', 'high', 'close']]
    rates_df = rates_df.rename(columns={'close':'Close', 'open':'Open', 'low':'Low', 'high':'High'})

    # backtest cases
    tolu_backtester:Backtest = Backtest(rates_df, ToluStrategyCase, cash=20_000, commission=0)
    engulf_backtester:Backtest = Backtest(rates_df, EngulfStrategyCase, cash=20_000, commission=0)
    rejection_backtester:Backtest = Backtest(rates_df, RejectionStrategyCase, cash=20_000, commission=0)
    composite_backtester:Backtest = Backtest(rates_df, CompositeStrategyCase, cash=20_000, commission=0)


    print(tolu_backtester.run(), '\n\n')
    print(engulf_backtester.run(), '\n\n')
    print(rejection_backtester.run(), '\n\n')
    print(composite_backtester.run(), '\n\n')