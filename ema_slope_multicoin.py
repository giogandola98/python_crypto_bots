import ccxt
import os 
import re
import time
from numpy.core.numeric import cross
import pushbullet
import schedule
import datetime
import pandas as pd
import numpy as np
from ExchangeConnector import ExchangeConnector
from pushbullet import Pushbullet #to comunicate with ethernal log


h12_pairs=[]
PRODUCTION=False
pb = Pushbullet("o.tnrSSAKjGKqaOs3qLm59x9jLFjkHYRUd")
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
def send_exchange_order(pair,isderivate,sentinel,old_sentinel,result):
    EC=ExchangeConnector(pair,isderivate)
    if(result!=0)and(sentinel!=0)and(old_sentinel==0):   #caso di apertura posizione
        if(result > 0):
            EC.buy()
        else:
            if isderivate:                              #apre short solo il caso sia un derivato per evitare il margin trading (si puo cabiare)
                EC.sell()
        print(pair," OPENING ",result)

    if(result!=0)and(sentinel==0)and(old_sentinel!=0):  #caso chiusura posizione
        if(isderivate>0):
            EC.ClosePosition()
        else:
            if(result>0):
                EC.buy()
            else:
                EC.sell()
        print(pair," CLOSING ",result)
def do_strategy(data,position,base_len=130,fast_len=9,slow_len=21,tf_len=200):
    result=0
    filter_ema=calculate_EMA(data,tf_len)
    TrandFilter=filter_ema.close.iloc[-1]<data.close.iloc[-1]       #true se ema 200 < close
    base_ema=calculate_EMA(data,base_len)
    slp=calculate_SLP(base_ema)

    slopeFast=calculate_EMA(slp,fast_len)
    slopeSlow=calculate_EMA(slp,slow_len)
    

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
def run_12h_wrapper(pair,position,base_len,fast_len,slow_len,tf_len,isderivate):
    data=get_historical_data(pair,'12h')
    old,res,pos=do_strategy(data,position,base_len,fast_len,slow_len,tf_len)

    
    string="OLD POSITION: "+str(old)+" RESULT: "+str(res)+" NEW POSITION: "+str(pos)
    pb.push_note(pair,string)
    print(pair,string)
    if (res!=0):
        if(PRODUCTION):
            send_exchange_order(pair,isderivate,pos,old,res)

    return pos

def init_h12_pairs():
    h12_pairs.append({'pair':'BTC/USDT', 'position': 1, "base_ema":130, "fast":9, "slow" : 21, "tf_ema":200,"isderivate":1})
def run_12h_slope():
    for pair in h12_pairs:
        pair['position']=run_12h_wrapper(pair['pair'],pair['position'],pair['base_ema'],pair['fast'],pair['slow'],pair['tf_ema'],pair['isderivate'])
        

def main():
    init_h12_pairs()
    exchange.load_markets()
    pb.push_note("BOT TW", "STARTING") 
    print("STARTING AT",datetime.datetime.now())
    push = pb.push_note(__name__, "STARTED at "+str(datetime.datetime.now()))
    run_12h_slope()
    schedule.every(1).hour.do(run_12h_slope)
    while datetime.datetime.now.minute!=0:
        time.sleep(1)
        pass
    while True:
        schedule.run_pending()
        time.sleep(1)

main()
