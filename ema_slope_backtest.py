import ccxt
import os 
import re
import time
from numpy.core.numeric import cross
import schedule
import datetime
import pandas as pd
import numpy as np
from stockstats import StockDataFrame as Sdf

h12_pairs=[]


# configure exchange for datafeed (orders in other file)
exchange = ccxt.binance({
  'timeout': 10000,
  'enableRateLimit': True
})

def get_historical_data(coin_pair, timeframe):
    # optional: 
    data=exchange.fetch_ohlcv(coin_pair, timeframe)
    #data = exchange.fetch_ohlcv(coin_pair, timeframe)
    # update timestamp to human readable timestamp
    data = [[exchange.iso8601(candle[0])] + candle[1:] for candle in data]
    header = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(data, columns=header)
    return df

def calculate_SMA(ser, len):
    sma = ser.rolling(window=len).mean()
    return sma

def calculate_EMA(ser,days):
    return ser.ewm(span=days,min_periods=0,adjust=False,ignore_na=False).mean()

def calculate_SLP(ser):
    slp= (ser.diff(periods=1)/ser)*100
    return slp

def backtest_strategy(data,position):
    result=0
    filter_ema=calculate_EMA(data,200)
    TrandFilter=filter_ema.close.iloc[-1]<data.close.iloc[-1]       #true se ema 200 < close
    base_ema=calculate_EMA(data,130)
    slp=calculate_SLP(base_ema)

    slopeFast=calculate_EMA(slp,9)
    slopeSlow=calculate_EMA(slp,21)
    

    EntryLong=(slopeFast.close.iloc[-1]>slopeSlow.close.iloc[-1]) and TrandFilter
    ExitLong=(slopeSlow.close.iloc[-1]>slopeFast.close.iloc[-1]) and (slopeSlow.close.iloc[-2]<slopeFast.close.iloc[-2])

    EntryShort=(slopeFast.close.iloc[-1]<slopeSlow.close.iloc[-1]) and (not TrandFilter)
    ExitShort=(slopeSlow.close.iloc[-1]<slopeFast.close.iloc[-1]) and (slopeSlow.close.iloc[-2]>slopeFast.close.iloc[-2])

    if(EntryLong) and position==0:
        result=1
    if(ExitLong) and position>0:
        result=-1
    if(EntryShort)and position==0:
        result=-1
    if(ExitShort) and position<0:
        result=1

    if result!=0:
        f=open("LOG.csv",'a+')
        #DATA:PRICE:OLD:RES:NEW:SHORT:LONG
        string=""+data.timestamp.iloc[-1]+";"+str(data.close.iloc[-1])+";"+str(position)+";"+str(result)+";"+str(position+result)+";"+str(slopeFast.close.iloc[-1])+";"+str(slopeSlow.close.iloc[-1])
        f.write(string+'\n')
    return position,result,position+result

data=get_historical_data('BTC/USDT','12h')
actual_position=0
for i in range(120,len(data)-1):
    prev_pos,result,actual_position=backtest_strategy(data[:i],actual_position)
    print("DATE",data.timestamp.iloc[i],"PRICE",data.close.iloc[i],"PREV",str(prev_pos),"RESULT",str(result),"ACTPOS",str(actual_position))




