from logging import exception
import ccxt
class FtxProcessor:
    def __init__(self, ApiKey=None, ApiSecret=None,SubAccount=None):
        self.ApiKey=ApiKey
        self.ApiSecret=ApiSecret
        if(ApiKey!=None and ApiSecret!=None):
            if(SubAccount!=None):
                self.cctxConnector=ccxt.ftx({
                    'headers':
                    {
                        'FTX-SUBACCOUNT' : SubAccount,
                    },
                    'apiKey': ApiKey,
                    'secret': ApiSecret,
                    'enableRateLimit': True,
                    })
            else:
                self.cctxConnector=ccxt.ftx({
                    'apiKey': ApiKey,
                    'secret': ApiSecret,
                    'enableRateLimit': True,
                    })
        else:
            self.cctxConnector=ccxt.ftx({
                        'enableRateLimit': True,
            })
        self.cctxConnector.load_markets()

    def getMarkets(self):
        return self.cctxConnector.symbols
        
    def getBalance(self, ticker):
        balance=self.cctxConnector.fetch_balance()[ticker]['free']
        print(balance)
        return balance


    def getActualPrice(self,ticker):
       return float(self.cctxConnector.fetchTicker(ticker)['last'])

    def buyDerivate(self,ticker,size,percent):
        print("DERIVATE MARKET BUY")
        usdbalance=self.getBalance("USD")
        print(usdbalance)
        if(usdbalance==0):
            t=ticker
            inverseticker=t.split("-")[0]
            inverseoinbalance=self.getBalance(inverseticker)*self.getActualPrice(ticker)
            usdbalance=inverseoinbalance
        
        if(percent>0):
            usdbalance=usdbalance*size
        print(self.cctxConnector.createMarketBuyOrder(ticker,usdbalance/self.getActualPrice(ticker)))

    def sellDerivate(self,ticker,size,percent):
        print("DERIVATE MARKET BUY")
        usdbalance=self.getBalance("USD")
        print(usdbalance)
        if(usdbalance==0):
            t=ticker
            inverseticker=t.split("-")[0]
            inverseoinbalance=self.getBalance(inverseticker)*self.getActualPrice(ticker)
            usdbalance=inverseoinbalance
        
        if(percent>0):
            usdbalance=usdbalance*size
        print(self.cctxConnector.createMarketSellOrder(ticker,size))
        return ""

    def MarketBuy(self,ticker, size,percent=0,isDerivate=0):
        if(isDerivate):
            return self.buyDerivate(ticker,size,percent)
        basecoin=ticker.split("/")
        
        if(percent>0):
            basecoin_balance=self.getBalance(basecoin[1])
            size=basecoin_balance*size

        print(self.cctxConnector.createMarketBuyOrder(ticker,size/self.getActualPrice(ticker)))
        return ""
        


    def MarketSell(self,ticker, size,percent=0,isDerivate=0):
        if isDerivate:
            return self.sellDerivate(ticker,size,percent)
        basecoin=ticker.split("/")
        if(percent>0):
            basecoin_balance=self.getBalance(basecoin[0])
            size=basecoin_balance*size
        print(self.cctxConnector.createMarketSellOrder(ticker,size))  
        return ""

    def getFuturePosition(self,ticker):
        x= self.cctxConnector.private_get_positions()['result']
        for json in x:
            if json['future']==ticker:
                return float(json['netSize'])
        return 0

    def ClosePosition(self,ticker):
        size=self.getFuturePosition(ticker)
        x=""
        print(ticker,size)
        if(size>=0):
            x=self.cctxConnector.createMarketSellOrder(ticker,size,params={'reduce-only': True})
        else:
           x= self.cctxConnector.createMarketBuyOrder(ticker,size*-1,params={'reduce-only': True})
        print(x)
        return x
        