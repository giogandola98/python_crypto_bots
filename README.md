# python_crypto_bots

### **REQUIREMENTS**
- python3 installed and in path
- pip3 installed and in path
- pushbullet installed on pc or phone (free versione) and API token 
- pip3 install -r requirements.txt

### **SETUP PRODUCTION**
1. get pushbullet api token from pushbulet website (in settings)
2. insert in variable named PUSHTOKEN in ema_slope_multicoin.py
3. change PRODUCTION to true if you want auto exchange orders in ema_slope_multicoin.py
4. setup exchanges keys into file ExcahngeConnector.py and some logic stuffs if needed (only ftx supported )
5. setup coin pairs and paramethers in init_h12_pairs() function in ema_slope_multicoin.py
6. run with python3 ema_slope_munticoin.py inside folder

### **BACKTEST**
1.run ema_slope_backtest.py
2.open generate log.csv and check data

3.format is **data:price:oldposition:operationresult:newposition:short slope:long slope**
 
