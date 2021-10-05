from ExchangeAdaptor import ExchangeAdaptor
class ExchangeConnector:
    
    
    def __init__(self,pair,isderivate):
        self.pair=pair
        self.isderivate=isderivate
        if "USD" in self.pair and "BTC" in self.pair:           #if pair is btc
            self.exchanges=[
            {
                'exchange':"FTX",   
                'api':"",
                'secret':"",
                'subaccount':"coperturabtc"

            }]
        if "USD" in self.pair and "ETH" in self.pair:           #if pair is eth
            self.exchanges=[
            {
                'exchange':"FTX",   
                'api':"",
                'secret':"",
                'subaccount':"coperturaeth"

            }]
        if self.pair=="BNB/BTC" :                               #if pair is bnb
            self.exchanges=[
            {
                'exchange':"FTX",   
                'api':"",
                'secret':"",
                'subaccount':""

            }]

    def setpair(self,exchange):
        pair=self.pair
        if(exchange=="FTX"):
            if(self.pair=="BTC/USDT" and self.isderivate==1):
                pair="BTC-PERP"
            if(self.pair=="ETH/USDT" and self.isderivate==1):
                pair="ETHPERP"
            if("USDT" in pair):
                a,b=self.pair.split("/")
                pair=a+"/"+"USD"
        return pair
    def ClosePosition(self,size=1):
        for exchange in self.exchanges:
            eA=ExchangeAdaptor(exchange['exchange'],self.setpair(exchange['exchange']),self.isderivate,size,-1,exchange['api'],exchange['secret'],exchange['subaccount'])
            eA.processOrder()

    def buy(self,size=1):
        for exchange in self.exchanges:
            eA=ExchangeAdaptor(exchange['exchange'],self.setpair(exchange['exchange']),self.isderivate,size,int(0),exchange['api'],exchange['secret'],exchange['subaccount'])
            print(eA.processOrder())
    
    def sell(self,size=1):
        for exchange in self.exchanges:
            eA=ExchangeAdaptor(exchange['exchange'],self.setpair(exchange['exchange']),self.isderivate,size,1,exchange['api'],exchange['secret'],exchange['subaccount'])
            print(eA.processOrder())