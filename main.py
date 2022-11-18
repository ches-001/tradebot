############################################################################################
# Author: Chibueze Henry (Ches)                                                            #
# Email: henrychibueze774@gmail.com                                                        #
# Github: ches-001                                                                         #
# Phone no: +2349057900367                                                                 #
############################################################################################

import time, sys, argparse
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Union, Optional, List, Dict
from bot_strategies import Tolu, Engulf, Rejection, SupportResistance
from utils import *

# bot details
BOT_DETAILS:Dict[str, str] = {
    'BOT_NAME' : "Peinjo",
    'VERSION' : '0.0.1',
}

# chain all buy strategies into one to form a composite
# buy strategy
def composite_strategy_buy(df:pd.DataFrame)->bool:
    return Tolu.is_bullish_trade(df) or \
            Engulf.is_bullish_engulf(df) or \
            Rejection.is_bullish_rejection(df)

# chain all sell strategies into one to form a composite
# sell strategy
def composite_strategy_sell(df:pd.DataFrame)->bool:
    return Tolu.is_bearish_trade(df) or \
            Engulf.is_bearish_engulf(df) or\
            Rejection.is_bearish_rejection(df)


# class for accessing all strategies. 
class Strategy:

    @staticmethod
    def tolu()->dict:
        return {'buy':Tolu.is_bullish_trade, 'sell':Tolu.is_bearish_trade}

    @staticmethod
    def engulf()->dict:
        return {'buy':Engulf.is_bullish_engulf, 'sell':Engulf.is_bearish_engulf}

    @staticmethod
    def rejection()->dict:
        return {'buy':Rejection.is_bullish_rejection, 'sell':Rejection.is_bearish_rejection}

    @staticmethod
    def composite()->dict:
        return {'buy':composite_strategy_buy, 'sell':composite_strategy_sell}


#available times
AVAIALBLE_TIMEFRAMES:dict = {
    'M1':(mt5.TIMEFRAME_M1, 1),
    'M2':(mt5.TIMEFRAME_M2, 2),
    'M3':(mt5.TIMEFRAME_M3, 3),
    'M4':(mt5.TIMEFRAME_M4, 4),
    'M5':(mt5.TIMEFRAME_M5, 5),
    'M10':(mt5.TIMEFRAME_M10, 10),
    'M12':(mt5.TIMEFRAME_M12, 12),
    'M15':(mt5.TIMEFRAME_M15, 15),
}


# this function returns true (p x 100)% of the times, and verifys
# that the index is at the support (100 - (p-100))% of the times
def at_support(df:pd.DataFrame, p:float=0.5, **kwargs)->bool:
    if np.random.random() < p:
        return SupportResistance.is_near_support(df, **kwargs)
    return True

# this function returns true (p x 100)% of the times, and verifys
# that the index is at the reistance (100 - (p-100))% of the times
def at_resistance(df:pd.DataFrame, p:float=0.5, **kwargs)->bool:
    if np.random.random() < p:
        return SupportResistance.is_near_resistance(df, **kwargs)
    return True


if __name__ == "__main__":
    APP_NAME:str = f"{BOT_DETAILS['BOT_NAME']} - (A MetaTrader 5 Trade Bot)"
    VERSION:str = BOT_DETAILS['VERSION']

    # CLI Parsed parameters
    parser = argparse.ArgumentParser(description=f'{APP_NAME}. Version - ({VERSION})')

    #login arguments
    parser.add_argument('login', type=int, metavar='login', help='Login ID')
    parser.add_argument('password', type=str, metavar='password', help='Password')
    parser.add_argument('server', type=str, metavar='server', help='Broker Server')

    #trade arguments
    parser.add_argument('--symbol', type=str, default='EURUSD', metavar='', help='Trade symbol')
    parser.add_argument('--volume', type=float,default=1.0, metavar='', help='Volume to trade')
    parser.add_argument('--deviation', type=int, default=0, metavar='', help='Maximum acceptable deviation from the requested price')
    parser.add_argument('--unit_pip', type=float, default=1e-5, metavar='', help='Value of 1 pip for symbol')
    parser.add_argument('--use_atr', type=int, choices=[0, 1], default=0, metavar='', help='Use Average True Return (ATR) to compute stop loss, trail and take profit. Note that when set to True, the unit_pip value will be set to the most recent ATR value')
    parser.add_argument('--default_sl', type=float, default=4.0, metavar='', help='Default stop loss value (in pip)')
    parser.add_argument('--max_sl_dist', type=float, default=4.0, metavar='', help='Maximum distance between current price and stop loss (in pip)')
    parser.add_argument('--sl_trail', type=float, default=0.0, metavar='', help='Stop loss trail value (in pip)')
    parser.add_argument('--default_tp', type=float, default=8.0, metavar='', help='Take profit value (in pip)')
    parser.add_argument('--strategy', type=str, default='tolu', metavar='', help='Strategy to use: Options(tolu, engulf, rejection, composite)')
    parser.add_argument('--timeframe', type=str, default='M1', choices=list(AVAIALBLE_TIMEFRAMES.keys()), metavar='', help='Trade timeframe, \visit the help \menu for options')
    parser.add_argument('--sr_likelihood', type=float, default=0.8, metavar='', help='likelihood score for support / resistance indicator utilisation.\
        When set to 1 or close to 1, the bot will only pick the relevant signals only at supports and resistances, and the opposite when set to 0')
    parser.add_argument('--sr_threshold', type=float, default=3.0, metavar='', help='Threshold distance (in pips) between candle stick that triggered a signal\
        and the corresponding support / resistance line the signal was picked')
    parser.add_argument('--period', type=int, default=15, metavar='', help='period of past timestamps to use for compute current statistical states')

    args = parser.parse_args()


    # initialise the MetaTrader 5 app
    init_env:bool = mt5.initialize(login=args.login, password=args.password, server=args.server)
    if not init_env:
        print('failed to initialise metatrader5')
        mt5.shutdown()
        sys.exit()

    # check if symbol is valid
    if not is_valid_symbol(args.symbol):
        print(f'{args.symbol} is an invalid symbol')
        sys.exit()

    # check if strategy is valid
    if not hasattr(Strategy, args.strategy):
        print(f'{args.strategy} is an invalid strategy, go to the help menu for available options')
        sys.exit()

    # initial console comments
    print(APP_NAME, '\n')
    print(f"Version:                {BOT_DETAILS['VERSION']}")
    print(f'Trade Symbol:           {args.symbol}')
    print(f'Trade Volume:           {args.volume}')
    print(f'Trade Deviation:        {args.deviation}')
    print(f'Trade Unit PIP:         {args.unit_pip}')
    print(f'Use ATR:                {bool(args.use_atr)}')
    print(f'Trade Default SL:       {args.default_sl}')
    print(f'Trade max SL distance:  {args.max_sl_dist}')
    print(f'Trail SL Value:         {args.sl_trail}')
    print(f'Trade TP:               {args.default_tp}')
    print(f'Strategy:               {args.strategy}')
    print(f'Timeframe:              {args.timeframe}')
    print(f'SR likelihood           {args.sr_likelihood}')
    print(f'SR contact treshold     {args.sr_threshold}')
    print(f'Period:                 {args.period}')
    print(f'Bot Session start time: {datetime.now()}', '\n')

    # Parameters
    ####################################################################################################################################################
    SYMBOL:str = args.symbol                                            # symbol                                                                       #
    VOLUME:float = args.volume                                          # volume to trade                                                              #
    DEVIATION:int = args.deviation                                      # allowable deviation for trade                                                #
    UNIT_PIP:Optional[float] = args.unit_pip                            # unit pip value                                                               #
    DEFAULT_SL:Optional[float] = args.default_sl                        # stop loss points                                                             #
    MAX_DIST_SL:float = args.max_sl_dist                                # maximun distance between price and stop loss                                 #
    TRAIL_AMOUNT:float = args.sl_trail                                  # icrement / decrement value for stop loss                                     #
    DEFAULT_TP:Optional[float] = args.default_tp                        # take profit points                                                           #
    STRATEGY:str = args.strategy                                        # strategy                                                                     #
    USE_ATR:bool = bool(args.use_atr)                                   # option for using atr instead of unit pip value                               #
    TIMEFRAME:str = args.timeframe                                      # trade timeframe                                                              #     
    SR_LIKELIHOOD:float = args.sr_likelihood                            # probability score that controls how support resistance indicators are used   #
    SR_THRESHOLD:float = args.sr_threshold * UNIT_PIP                   # minimum distance between signal candle and support / resistance line         #
    PERIOD:int = args.period                                            # period of past timestamps to use for compute current statistical states      #
    ####################################################################################################################################################

    #utility variables for the event loop
    start_time:Optional[datetime] = None
    timezone_diff:timedelta = timedelta(hours=2)
    lagtime:timedelta = timedelta(minutes=AVAIALBLE_TIMEFRAMES[TIMEFRAME][1]*PERIOD)
    position_ids:List[int] = []
    session_profit:float = 0.0
    atr_value:Optional[float] = None

    while True:
        
        # trails stop loss for each ticket
        if position_ids:
            for id in position_ids:
                trailed_order:Union[int, mt5.OrderSendResult] = trail_sl(
                    position_id=id, 
                    default_sl_points=DEFAULT_SL * (atr_value if USE_ATR else UNIT_PIP), 
                    max_dist_sl=MAX_DIST_SL * (atr_value if USE_ATR else UNIT_PIP), 
                    trail_amount=TRAIL_AMOUNT * (atr_value if USE_ATR else UNIT_PIP))

                if isinstance(trailed_order, int):
                    profit:float = check_profit(trailed_order)
                    session_profit += profit
                    print(f'\nOrder at position_id {trailed_order} is closed')
                    print(f'Deal Profit value:---------------------  {profit}')
                    print(f'Total session Profit value:------------  {session_profit}\n')
                    position_ids.remove(trailed_order)

        # delay (secs)
        time.sleep(0.06)

        # set datetime to now
        now:datetime = datetime.now() + timezone_diff

        # error handle for if Index error (IndexError) is thrown. The index
        # error is thrown when the "lagtime" variable that specifies the 
        # time difference is incorrectly set, or when the market is closed.
        try:
            # get last 2 sessions + current session and convert to dataframe
            rates:np.array = mt5.copy_rates_range(SYMBOL, AVAIALBLE_TIMEFRAMES[TIMEFRAME][0], (now - lagtime), now)
            rates_df:pd.DataFrame = pd.DataFrame(rates)

            # if no time is set (bot just started), set to latest time in rates_df
            if not start_time:
                start_time = format_uts(rates_df['time'].values[-1], dt_obj=True)

            # get current time from rates_df dataframe
            current_time:datetime = format_uts(rates_df['time'].values[-1], dt_obj=True)
        
        except IndexError:
            print('Market is currently closed, or timezone difference is incorrect.')
            mt5.shutdown()
            break

        # check if new session has started by the current time, and initialise trade
        if start_time != current_time:
            
            #input dateframe for strategies
            input_df:pd.DataFrame = rates_df.iloc[:-1, :]

            #compute latest ATR past candle sticks prior to current one
            if USE_ATR: atr_value = compute_latest_atr(input_df)

            # Tolu strategy works with the signal being picked up in real-time, rather
            # than awaiting a 3rd candle stick to form
            if STRATEGY == 'tolu': input_df:pd.DataFrame = rates_df.iloc[:, :]
            else: start_time = current_time

            # check if condition for buying is satisfied and trade
            # then append the position id to the positions_id
            # list
            if getattr(Strategy, STRATEGY)()['buy'](input_df) and \
                at_support(input_df, p=SR_LIKELIHOOD, threshold=SR_THRESHOLD):
                order = make_trade(
                    symbol = SYMBOL, 
                    buy = True, 
                    position_id = None, 
                    volume = VOLUME, 
                    sl_points = DEFAULT_SL * (atr_value if USE_ATR else UNIT_PIP),
                    tp_points = DEFAULT_TP * (atr_value if USE_ATR else UNIT_PIP),
                    deviation = DEVIATION)
                
                print(order.comment)
                if USE_ATR: print(f'current ATR: {round(atr_value, 4)}')
                if order.order != 0:
                    log_open_order(order, buy=True)
                    position_ids.append(order.order)

                if STRATEGY == 'tolu': start_time = current_time


            # likewise, check if condition for selling is satisfied and
            # trade then append the position id to the positions_id
            # list
            elif getattr(Strategy, STRATEGY)()['sell'](input_df) and \
                at_resistance(input_df, p=SR_LIKELIHOOD, threshold=SR_THRESHOLD):
                order = make_trade(
                    symbol = SYMBOL, 
                    buy = False, 
                    position_id = None, 
                    volume = VOLUME, 
                    sl_points = DEFAULT_SL * (atr_value if USE_ATR else UNIT_PIP),
                    tp_points = DEFAULT_TP * (atr_value if USE_ATR else UNIT_PIP),
                    deviation = DEVIATION)
                
                print(order.comment)
                if USE_ATR: print(f'current ATR: {round(atr_value, 4)}')
                if order.order != 0:
                    log_open_order(order, buy=False)
                    position_ids.append(order.order)

                if STRATEGY == 'tolu': start_time = current_time