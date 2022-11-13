import pandas as pd

# Tolu Strategy
class ToluStrategy:

    @staticmethod
    def is_bullish_trade(df:pd.DataFrame)->bool:
        r"""
        uses past two session data of market to check if bullish trade condition
        is satisfied. If this condition is satisfied, buying action is to be trigged

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe, dataframe must have
        only 2 rows
            
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
        df: (pandas.core.frame.DataFrame) - input dataframe, dataframe must have
        only 2 rows
            
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
        df: (pandas.core.frame.DataFrame) - input dataframe, dataframe must have
        only 2 rows
            
        returns
        -------------
        returns True, if condition is satisfied for bullish engulf, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        condition_1:bool = df['close'].iloc[-1] > df['high'].iloc[-2]
        condition_2:bool = df['open'].iloc[-1] <= df['close'].iloc[-2]
        condition_3:bool = df['close'].iloc[-1] > df['open'].iloc[-1]

        if condition_1 and condition_2 and condition_3: return True

        return False

    @staticmethod
    def is_bearish_engulf(df:pd.DataFrame)->bool:
        r"""
        checks bearish engulf pattern in market

        parameters
        -------------
        df: (pandas.core.frame.DataFrame) - input dataframe, dataframe must have
        only 2 rows
            
        returns
        -------------
        returns True, if condition is satisfied for bearish engulf, else False
        """
        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'
            
        condition_1:bool = df['close'].iloc[-1] < df['low'].iloc[-2]
        condition_2:bool = df['open'].iloc[-1] >= df['close'].iloc[-2]
        condition_3:bool = df['close'].iloc[-1] < df['open'].iloc[-1]

        if condition_1 and condition_2 and condition_3: return True

        return False


#Rjection Strategy
class Rejection:

    @staticmethod
    def is_bullish_rejection(df:pd.DataFrame, iloc_idx:int=-1)->bool:

        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        wick_size:float = df['high'].iloc[iloc_idx] - max(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx])
        tail_size:float = min(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx]) - df['low'].iloc[iloc_idx]
        body_size:float = abs(df['open'].iloc[iloc_idx] - df['close'].iloc[iloc_idx])

        if body_size != 0:
            t2b_ratio:float = tail_size / body_size
            if t2b_ratio > 2 and wick_size <= 0.2*tail_size: return True
            else:return False

        else:
            if wick_size <= 0.2*tail_size: return True
            else:return False


    
    @staticmethod
    def is_bearish_rejection(df:pd.DataFrame, iloc_idx:int=-1)->bool:

        assert isinstance(df, pd.DataFrame), \
            f'expects input to be {pd.DataFrame}, got {type(df)} isntead'

        wick_size:float = df['high'].iloc[iloc_idx] - max(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx])
        tail_size:float = min(df['open'].iloc[iloc_idx], df['close'].iloc[iloc_idx]) - df['low'].iloc[iloc_idx]
        body_size:float = abs(df['open'].iloc[iloc_idx] - df['close'].iloc[iloc_idx])

        if body_size != 0:
            w2b_ratio:float = wick_size / body_size
            if w2b_ratio > 2 and tail_size <= 0.2*wick_size: return True
            else:return False

        else:
            if tail_size <= 0.2*wick_size: return True
            else:return False