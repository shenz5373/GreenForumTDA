1: account_stock_list.txt
[{"account_number":"111111111","stock_list":["METX","AMD"]},{"account_number":"222222222","stock_list":[]}]

2:lastMETXrec.txt
{'Version': '2.00', 'BuyOrderId': 3587066880, 'BuyOrderSendTime': 0, 'SellOrderId': 3587066881, 'SellOrderSendTime': 0, 'TradeQty': 1, 'HighestExecPrice': 3.0, 'LowestExecPrice': 0.5, 'PriceStep': 0.01, 'ProfitStep': 0.05, 'SmallPriceOpti': 0, 'OptiState': -1, 'MainContract': 'STOCK', 'LastBuyPrice': 0.97, 'AlarmHighPrice': 2.5, 'AlarmLowPrice': 1.1}

3:lastAMDrec.txt
{'Version': '2.00', 'BuyOrderId': 3587066882, 'BuyOrderSendTime': 0, 'SellOrderId': 3587066883, 'SellOrderSendTime': 0, 'TradeQty': 1, 'HighestExecPrice': 120.0, 'LowestExecPrice': 60.0, 'PriceStep': 0.01, 'ProfitStep': 30, 'SmallPriceOpti': 0, 'OptiState': -1, 'MainContract': 'STOCK', 'LastBuyPrice': 70.0, 'AlarmHighPrice': 80.0, 'AlarmLowPrice': 70.0}


install step:
1 based on "Ubuntu 20.04.2 LTS"
2 install google chrome
3 install Chrome WebDriver        https://splinter.readthedocs.io/en/latest/drivers/chrome.html
4 edit "chromedriver_path" in config.py      chromedriver_path = r"/home/shenz1973/bin/chromedriver"