import ccxt
import os 
import re
import time
import schedule
import datetime
import pandas as pd
from pushbullet import Pushbullet #to comunicate with ethernal log
import numpy as np
from stockstats import StockDataFrame as Sdf

h12_pairs=[]


# configure exchange for datafeed (orders in other file)
exchange = ccxt.binance({
  'timeout': 10000,
  'enableRateLimit': True
})
#define comunication interface api
pb = Pushbullet("")
ONLY_CHANGE_POSITION_COMUNICATIONS=False
def init_pairs_12h():
    h12_pairs.append({'pair':'BTC/USDT','sentinel': 1,'slopeshortparam':9,'slopelongparam':21,'baseema':130,'tfema':200})
    h12_pairs.append({'pair':'BNB/BTC','sentinel': 1,'slopeshortparam':9,'slopelongparam':21,'baseema':130,'tfema':200})
    pass


def get_historical_data(coin_pair, timeframe):
    """Get Historical data (ohlcv) from a coin_pair
    """
    # optional: exchange.fetch_ohlcv(coin_pair, '1h', since)
    data = exchange.fetch_ohlcv(coin_pair, timeframe)
    # update timestamp to human readable timestamp
    data = [[exchange.iso8601(candle[0])] + candle[1:] for candle in data]
    header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = pd.DataFrame(data, columns=header)
    return df
def create_stock(historical_data):
    stock  = Sdf.retype(historical_data)
    return stock
def ema(values, period):
    values = np.array(values)
    df_test = pd.DataFrame(data = values)
    return df_test.ewm( span=period).mean()
def return_ema_vector(stock,emalength):
    return stock['close_'+emalength+'_ema']
def return_change_vector(ema_vector):
    change_vector=[]
    for i in range(1,len(ema_vector)-1):
        change_vector.append(ema_vector[i]-ema_vector[i-1])
    return change_vector
def return_slp_vector(ema_vector):
    change_vector=return_change_vector(ema_vector)
    slp_vector=[]
    for change in change_vector:
        slp_vector.append(change/ema_vector[len(ema_vector)-1])
    return slp_vector
def crossunder(ema1,ema2):
    if (ema1[0]>ema1[1])and (ema2[0]<ema2[1]):
        return True
    return False
def check_entry(sentinel,price_200_ema,emaSlopeF_last,emaSlopeS_last,emaSlopeF_previus,emaSlopeS_previus,price):

    ConditionEntryLong = (emaSlopeF_last>emaSlopeS_last) and not (sentinel<0) and (price>price_200_ema)
    ConditionEntryShort= (emaSlopeF_last<emaSlopeS_last) and not (sentinel>0) and (price<price_200_ema)
    ConditionExitL=crossunder([emaSlopeF_previus,emaSlopeS_previus],[emaSlopeF_last,emaSlopeS_last]) and sentinel==1
    ConditionExitS=crossunder([emaSlopeS_previus,emaSlopeF_previus],[emaSlopeS_last,emaSlopeF_last]) and sentinel==-1

    if (ConditionExitL  and sentinel!=0) :
        sentinel=0
        return -1

    if (ConditionExitS  and sentinel!=0) :
        sentinel=0
        return 1 

    if(ConditionEntryLong and sentinel==0):
        sentinel=1
        return 1

    if(ConditionEntryShort and sentinel==0):
        sentinel -1
        return -1

    return 0  
def check_pair(pair,sentinel,slopeshortparam,slopelongparam,baseema,tfema):
    data=create_stock(get_historical_data(pair,'12h'))
    slp=return_slp_vector(return_ema_vector(data,str(baseema)))
    emaSlopeF_last=ema(slp,slopeshortparam)
    emaSlopeS_last=ema(slp,slopelongparam)
    emaSlopeF_prev=emaSlopeF_last[0][len(emaSlopeF_last[0])-2]
    emaSlopeS_prev=emaSlopeS_last[0][len(emaSlopeS_last[0])-2]
    emaSlopeF_last=emaSlopeF_last[0][len(emaSlopeF_last[0])-1]
    emaSlopeS_last=emaSlopeS_last[0][len(emaSlopeS_last[0])-1]
    tranding_ema=return_ema_vector(data,str(tfema))
    tranding_ema=tranding_ema[len(tranding_ema)-1]
    old_position=sentinel
    act_price=data['close'][len(data)-1]
    result=check_entry(sentinel,tranding_ema,emaSlopeF_last,emaSlopeS_last,emaSlopeF_prev,emaSlopeS_prev,act_price)

    if(ONLY_CHANGE_POSITION_COMUNICATIONS==False):
        push = pb.push_note(pair+" "+__name__, "Result: "+str(result)+" New positon: "+str(sentinel)+ " Old position: "+str(old_position))
    else:
        if(result!=0):
            push = pb.push_note(pair+" "+__name__, "Result: "+str(result)+" New positon: "+str(sentinel)+ " Old position: "+str(old_position))
def check_trandfollower_12h():
    for pair in h12_pairs:
        check_pair(pair['pair'],pair['sentinel'],pair['slopeshortparam'],pair['slopelongparam'],pair['baseema'],pair['tfema'])
    pass
def main():
    init_pairs_12h()
    exchange.load_markets()
    a= datetime.datetime.now()
    push = pb.push_note(__name__, "STARTING") 
    check_trandfollower_12h()
    while (a.minute!=0 and a.second!=0 and a.microsecond!=0):
        pass
    push = pb.push_note(__name__, "STARTED")
    check_trandfollower_12h()
    schedule.every(1).hour.do(check_trandfollower_12h)

    while True:
        schedule.run_pending()
        time.sleep(1)

main()






