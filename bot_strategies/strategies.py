import numpy as np
import pandas as pd
from typing import Tuple, List

# Tolu Strategy
class Tolu:

    @staticmethod
    def is_bullish_trade(df:pd.DataFrame)->bool:
        r"""
        uses past two session data of market to check if bullish trade condition
        is satisfied. If this condition is satisfied, buying action is to be trigged

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe
            
        returns
        -------------
        returns True, if condition is satisfied for bullish trade, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        condition_1:bool = df['close'].iloc[-1] > df['open'].iloc[-1]
        condition_2:bool = df['high'].iloc[-1] > df['high'].values[-2]
        condition_3:bool = df['low'].iloc[-1] < df['low'].iloc[-2]

        if condition_1 and condition_2 and condition_3: return True

        return False

    @staticmethod
    def is_bearish_trade(df:pd.DataFrame)->bool:
        r"""
        uses past two session data of market to check if bearish trade condition
        is satisfied. If this condition is satisfied, selling action is to be trigged

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe
            
        returns
        -------------
        returns True, if condition is satisfied for bearish trade, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'
            
        condition_1:bool = df['close'].iloc[-1] < df['open'].iloc[-1]
        condition_2:bool = df['high'].iloc[-1] > df['high'].iloc[-2]
        condition_3:bool = df['low'].iloc[-1] < df['low'].iloc[-2]

        if condition_1 and condition_2 and condition_3: return True

        return False


# Engulf Strategy
class Engulf:
    @staticmethod
    def is_bullish_engulf(df:pd.DataFrame)->bool:
        r"""
        checks bullish engulf pattern in market

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe
            
        returns
        -------------
        returns True, if condition is satisfied for bullish engulf, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        condition_1:bool = df['close'].iloc[-1] > df['high'].iloc[-2]
        condition_2:bool = df['open'].iloc[-1] <= df['close'].iloc[-2]
        condition_3:bool = df['close'].iloc[-1] > df['open'].iloc[-1]
        condition_4:bool = df['close'].iloc[-2] < df['open'].iloc[-2]

        if condition_1 and condition_2 and condition_3 and condition_4: return True

        return False

    @staticmethod
    def is_bearish_engulf(df:pd.DataFrame)->bool:
        r"""
        checks bearish engulf pattern in market

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe
            
        returns
        -------------
        returns True, if condition is satisfied for bearish engulf, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'
            
        condition_1:bool = df['close'].iloc[-1] < df['low'].iloc[-2]
        condition_2:bool = df['open'].iloc[-1] >= df['close'].iloc[-2]
        condition_3:bool = df['close'].iloc[-1] < df['open'].iloc[-1]
        condition_4:bool = df['close'].iloc[-2] > df['open'].iloc[-2]

        if condition_1 and condition_2 and condition_3 and condition_4: return True

        return False


#Rjection Strategy
class Rejection:

    @staticmethod
    def is_bullish_rejection(df:pd.DataFrame, iloc_idx:int=-1)->bool:
        r"""
        checks if candle stick is a bullish rejection candle or not

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe
            
        returns
        -------------
        returns True, if condition is satisfied for bullish rejection, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        wick_size:float = df['high'].iloc[iloc_idx] - max(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx])
        tail_size:float = min(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx]) - df['low'].iloc[iloc_idx]
        body_size:float = abs(df['open'].iloc[iloc_idx] - df['close'].iloc[iloc_idx])

        if body_size != 0:
            t2b_ratio:float = tail_size / body_size
            if t2b_ratio >= 2 and wick_size <= 0.25*tail_size: return True
            else:return False

        else:
            if wick_size <= 0.25*tail_size: return True
            else:return False

    @staticmethod
    def is_bearish_rejection(df:pd.DataFrame, iloc_idx:int=-1)->bool:
        r"""
        checks if candle stick is a bearish rejection candle or not

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe
            
        returns
        -------------
        returns True, if condition is satisfied for bearish rejection, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        wick_size:float = df['high'].iloc[iloc_idx] - max(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx])
        tail_size:float = min(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx]) - df['low'].iloc[iloc_idx]
        body_size:float = abs(df['open'].iloc[iloc_idx] - df['close'].iloc[iloc_idx])

        if body_size != 0:
            w2b_ratio:float = wick_size / body_size
            if w2b_ratio >= 1.5 and tail_size <= 0.25*wick_size: return True
            else:return False

        else:
            if tail_size <= 0.25*wick_size: return True
            else:return False


#support resistance strategy
class SupportResistance:

    @staticmethod
    def boundary_trimer(boundaries:List[float], idxs:List[int], threshold:float)->Tuple[List[float], List[int]]:
        r"""
        checks if boundary values are close to each other by some threshold and
        trims them appropriately.

        parameters
        -------------
        boundaries: (List[float]) - list of boundary values

        idxs: (List[int]) - List of corresponding index values for the boundaries 
            
        returns
        -------------
        returns Tuple of two lists, the trimed boundary list and its new index list
        """
        new_boundaries:List[float] = []
        new_idxs:List[int] = []

        for i, b1 in enumerate(boundaries):
            if np.sum([abs(b1 - y) < threshold for y in new_boundaries]) == 0:
                new_boundaries.append(b1)
                new_idxs.append(idxs[i])

        return new_boundaries, new_idxs

    @staticmethod
    def is_support_pivot(df:pd.DataFrame, idx:int)->bool:
        r"""
        checks if index in dataframe is a support pivot

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe

        idx: (int) - index of potential pivot of interest
            
        returns
        -------------
        returns True if index is a support pivot, else returns False
        """
        for i in range(1, idx+1):
            if df['low'].iloc[i] > df['low'].iloc[i-1]: return False

        for i in range(idx+1, len(df)):
            if df['low'].iloc[i] < df['low'].iloc[i-1]: return False

        return True

    @staticmethod
    def is_resistance_pivot(df:pd.DataFrame, idx:int)->bool:
        r"""
        checks if index in dataframe is a resistance pivot

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe

        idx: (int) - index of potential pivot of interest
            
        returns
        -------------
        returns True if index is a resistance pivot, else returns False
        """
        for i in range(1, idx+1):
            if df['high'].iloc[i] < df['high'].iloc[i-1]: return False

        for i in range(idx+1, len(df)):
            if df['high'].iloc[i] > df['high'].iloc[i-1]: return False

        return True

    @staticmethod
    def get_supports(df:pd.DataFrame, n1:int=2, n2:int=2)->Tuple[List[float], List[int]]:
        r"""
        get a list of all support pivots in the stock price dataframe

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe

        n1: (int) - number of candles to consider prior to a potential
        pivot point

        n2: (int) - number of candles to consider after a potential pivot
        point
            
        returns
        -------------
        returns a Tuple of 2 lists, the support values and their corresponding
        index in the dateframe
        """
        supports:List[float] = []
        support_idxs:List[int] = []

        for i in range(n1, len(df)-n2):
            temp_df:pd.DataFrame = df[i-n1:i+n2+1]
            if SupportResistance.is_support_pivot(temp_df, n1):
                supports.append(df['low'].iloc[i])
                support_idxs.append(i)

        space_threshold:float = np.mean(df['high'] - df['low'])
        return SupportResistance.boundary_trimer(supports, support_idxs, space_threshold)

    @staticmethod
    def get_resistances(df:pd.DataFrame, n1:int=2, n2:int=2)->Tuple[List[float], List[int]]:
        r"""
        get a list of all resistance pivots in the stock price dataframe

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe

        n1: (int) - number of candles to consider prior to a potential
        pivot point

        n2: (int) - number of candles to consider after a potential pivot
        point
            
        returns
        -------------
        returns a Tuple of 2 lists, the resistance values and their corresponding
        index in the dateframe
        """
        resistances:List[float] = []
        resistance_idxs:List[int] = []

        for i in range(n1, len(df)-n2):
            temp_df:pd.DataFrame = df[i-n1:i+n2+1]
            if SupportResistance.is_resistance_pivot(temp_df, n1):
                resistances.append(df['high'].iloc[i])
                resistance_idxs.append(i)

        space_threshold:float = np.mean(df['high'] - df['low'])
        return SupportResistance.boundary_trimer(resistances, resistance_idxs, space_threshold)

    @staticmethod
    def is_near_support(df:pd.DataFrame, threshold:float, idx:int=-1):
        r"""
        check if a candle of interest is close to a support level by some
        threshold

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe

        threshold: (float) - threshold value that defines what near a support is

        idx: (int) - index of candle of interest
            
        returns
        -------------
        returns a True if candle is near a support pivot, else returns False
        """
        supports, _ = SupportResistance.get_supports(df)

        if len(supports) == 0:return False

        o:float = df['open'].iloc[idx]
        l:float = df['low'].iloc[idx]
        h:float = df['high'].iloc[idx]
        c:float = df['close'].iloc[idx]

        closest_support:float = min(supports, key=lambda x : abs(x - h))

        c1:bool = h > closest_support and max(o, c) > closest_support
        c2:bool = abs(l - closest_support) <= threshold
        c3:bool = abs(min(o, c) - closest_support) <= threshold
        
        if c1 and (c2 or c3):return True
        return False


    @staticmethod
    def is_near_resistance(df:pd.DataFrame, threshold:float, idx:int=-1):
        r"""
        check if a candle of interest is close to a resistance level by some
        threshold

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe

        threshold: (float) - threshold value that defines what near a resistance is

        idx: (int) - index of candle of interest
            
        returns
        -------------
        returns a True if candle is near a resistance pivot, else returns False
        """
        resistances, _ = SupportResistance.get_resistances(df)

        if len(resistances) == 0:return False

        o:float = df['open'].iloc[idx]
        l:float = df['low'].iloc[idx]
        h:float = df['high'].iloc[idx]
        c:float = df['close'].iloc[idx]

        closest_resistance:float = min(resistances, key=lambda x : abs(x - h))

        c1:bool = l < closest_resistance and min(o, c) < closest_resistance
        c2:bool = abs(h - closest_resistance) <= threshold
        c3:bool = abs(max(o, c) - closest_resistance) <= threshold

        if c1 and (c2 or c3):return True
        return False