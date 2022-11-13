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
from typing import Union, Optional, List
from bot_strategies import ToluStrategy
from utils import *

if __name__ == "__main__":
    APP_NAME = 'MetaTrader 5 Trade Bot'

    # CLI Parsed parameters
    parser = argparse.ArgumentParser(description=APP_NAME)

    #login arguments
    parser.add_argument('login', type=int, metavar='login', help='Login ID')
    parser.add_argument('password', type=str, metavar='password', help='Password')
    parser.add_argument('server', type=str, metavar='server', help='Broker Server')

    #trade arguments
    parser.add_argument('--symbol', type=str, default='EURUSD', metavar='', help='Trade symbol')
    parser.add_argument('--volume', type=float,default=10.0, metavar='', help='Volume to trade')
    parser.add_argument('--deviation', type=int, default=0, metavar='', help='Maximum acceptable deviation from the requested price')
    parser.add_argument('--unit_pip', type=float, default=1e-5, metavar='', help='Value of 1 pip for symbol')
    parser.add_argument('--default_sl', type=float, default=4.0, metavar='', help='Default stop loss value (in pip)')
    parser.add_argument('--max_sl_dist', type=float, default=4.0, metavar='', help='Maximum distance between current price and stop loss (in pip)')
    parser.add_argument('--sl_trail', type=float, default=4.0, metavar='', help='Stop loss trail value (in pip)')
    args = parser.parse_args()


    #initialise the MetaTrader 5 app
    init_env:bool = mt5.initialize(login=args.login, password=args.password, server=args.server)
    if not init_env:
        print('failed to initialise metatrader5')
        mt5.shutdown()
        sys.exit()

    #check if symbol is valid
    if not is_valid_symbol(args.symbol):
        print(f'{args.symbol} is an invalid symbol')
        sys.exit()

    #initial console comments
    print(APP_NAME, '\n')
    print(f'Trade Symbol:           {args.symbol}')
    print(f'Trade Volume:           {args.volume}')
    print(f'Trade Deviation:        {args.deviation}')
    print(f'Trade Unit PIP:         {args.unit_pip}')
    print(f'Trade Default SL:       {args.default_sl}')
    print(f'Trade max SL distance:  {args.max_sl_dist}')
    print(f'Trail SL Value:         {args.sl_trail}')
    print(f'Bot Session start time: {datetime.now()}', '\n')

    # Parameters
    ########################################################################################################################
    SYMBOL:str = args.symbol                                            #symbol                                            #
    VOLUME:float = args.volume                                          #volume to trade                                   #
    DEVIATION:int = args.deviation                                      #allowable deviation for trade                     #
    DEFAULT_SL_POINTS:Optional[float] = args.default_sl * args.unit_pip #stop loss points                                  #
    MAX_DIST_SL:float = args.max_sl_dist * args.unit_pip                #maximun distance between price and stop loss      #
    TRAIL_AMOUNT:float = args.sl_trail * args.unit_pip                  #icrement / decrement value for stop loss          #
    DEFAULT_TP_POINTS:Optional[float] = None                            #take profit points                                #
    ########################################################################################################################

    #utility variables for the event loop
    start_time:Optional[datetime] = None
    timezone_diff:timedelta = timedelta(hours=2)
    lagtime:timedelta = timedelta(minutes=3)
    position_ids:List[int] = []
    session_profit:float = 0

    while True:
        
        # trails stop loss for each ticket
        if position_ids:
            for id in position_ids:
                trailed_order:Union[int, mt5.OrderSendResult] = trail_sl(
                    position_id=id, 
                    default_sl_points=DEFAULT_SL_POINTS, 
                    max_dist_sl=MAX_DIST_SL, 
                    trail_amount=TRAIL_AMOUNT)

                if isinstance(trailed_order, int):
                    profit:float = check_profit(trailed_order)
                    session_profit += profit
                    print(f'\nOrder at position_id {trailed_order} is closed')
                    print(f'Deal Profit value:---------------------  {profit}')
                    print(f'Total session Profit value:------------  {session_profit}\n')
                    position_ids.remove(trailed_order)

        # delay (secs)
        time.sleep(0.1)

        # set datetime to now
        now:datetime = datetime.now() + timezone_diff

        # error handle for if Index error (IndexError) is thrown. The index
        # error is thrown when the "lagtime" variable that specifies the 
        # time difference is incorrectly set, or when the market is closed.
        try:
            # get last 2 sessions + current session and convert to dataframe
            rates:np.array = mt5.copy_rates_range(SYMBOL, mt5.TIMEFRAME_M1, (now - lagtime), now)
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

            # check if condition for buying is satisfied and trade
            # then append the position id to the positions_id
            # list
            if ToluStrategy.is_bullish_trade(rates_df):
                order = make_trade(
                    symbol = SYMBOL, 
                    buy = True, 
                    position_id = None, 
                    volume = VOLUME, 
                    sl_points = DEFAULT_SL_POINTS,
                    tp_points = DEFAULT_TP_POINTS,
                    deviation = DEVIATION)
                    
                print(order.comment)
                if order.order != 0:
                    log_open_order(order, buy=True)
                    position_ids.append(order.order)

                start_time = current_time

            # likewise, check if condition for selling is satisfied and
            # trade then append the position id to the positions_id
            # list
            elif ToluStrategy.is_bearish_trade(rates_df):
                order = make_trade(
                    symbol = SYMBOL, 
                    buy = False, 
                    position_id = None, 
                    volume = VOLUME, 
                    sl_points = DEFAULT_SL_POINTS, 
                    tp_points = DEFAULT_TP_POINTS,
                    deviation = DEVIATION)
                
                print(order.comment)
                if order.order != 0:
                    log_open_order(order, buy=False)
                    position_ids.append(order.order)

                start_time = current_time