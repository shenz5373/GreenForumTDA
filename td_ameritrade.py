from tda_trade_file import read_trade_paras_from_file, append_trade_record, save_trade_paras_to_file, \
    get_account_stock_from_file
from td_ameritrade_api import place_order, get_access_token, account_available, get_order, cancel_order, \
    refresh_token, get_working_orders, get_queued_orders, trading_hours
import time
from datetime import datetime

REFRESH_TIME = 1800
EXCEPTION_LIMITS = 3
exception_count = 0


def generate_buy_order(account_number, stock_symbol):
    m_buy_order_id = place_order(
        account_num=account_number,
        access_token=access_token,
        symbol=stock_symbol,
        asset_type="EQUITY",
        instruction="Buy",
        price=tradeParas['LastBuyPrice'] - tradeParas['PriceStep'],
        quantity=tradeParas['TradeQty']
    )
    return m_buy_order_id


def generate_sell_order(account_number, stock_symbol):
    m_sell_order_id = place_order(
        account_num=account_number,
        access_token=access_token,
        symbol=stock_symbol,
        asset_type="EQUITY",
        instruction="Sell",
        price=tradeParas['LastBuyPrice'] + tradeParas['ProfitStep'],
        quantity=tradeParas['TradeQty']
    )
    return m_sell_order_id


access_token = get_access_token()
last_refresh_time = datetime.now()

asl = get_account_stock_from_file()
for account in asl:
    account_available(account_num=account['account_number'], access_token=access_token)
    for stock in account['stock_list']:
        tradeParas = read_trade_paras_from_file(stock)
        print("Buy  ", tradeParas['TradeQty'], " ", stock, " @",
              "{:.2f}".format(tradeParas['LastBuyPrice'] - tradeParas['PriceStep']), "  and  Sell ",
              tradeParas['TradeQty'], " ", stock, " @",
              "{:.2f}".format(tradeParas['LastBuyPrice'] + tradeParas['ProfitStep']))
        if input('Do you confirm the initial orders?') != 'y':
            exit(1)
print(
    "Program are running, during trading hours(7 am until 8 pm US EASTERN | Monday through Friday) you can monitor the orders on the TD Ameritrade website->Trade->Order Status")
first_time_enter_trading_hours = True
while True:
    try:
        time.sleep(0.4)
        if (datetime.now() - last_refresh_time).seconds > REFRESH_TIME - 120:
            access_token = refresh_token()
            last_refresh_time = datetime.now()

        if trading_hours():
            print('trading hours process')
            for account in asl:
                queued_orders = get_queued_orders(account_num=account['account_number'], access_token=access_token)
                for stock in account['stock_list']:
                    tradeParas = read_trade_paras_from_file(stock)
                    if tradeParas['BuyOrderId'] == 0 and tradeParas['SellOrderId'] == 0:
                        tradeParas['BuyOrderId'] = generate_buy_order(account_number=account['account_number'],
                                                                      stock_symbol=stock)
                        tradeParas['SellOrderId'] = generate_sell_order(account_number=account['account_number'],
                                                                        stock_symbol=stock)
                        save_trade_paras_to_file(stock, tradeParas)
                    else:
                        buy_order_found = False
                        sell_order_found = False
                        for order in queued_orders:
                            if order['orderId'] == tradeParas['BuyOrderId']:
                                buy_order_found = True
                            elif order['orderId'] == tradeParas['SellOrderId']:
                                sell_order_found = True
                        if not (buy_order_found and sell_order_found):
                            print("deal with orders")
                            buy_order = get_order(account_num=account['account_number'], access_token=access_token,
                                                  order_id=tradeParas['BuyOrderId'])
                            sell_order = get_order(account_num=account['account_number'], access_token=access_token,
                                                   order_id=tradeParas['SellOrderId'])

                            if (int(buy_order['filledQuantity']) == tradeParas['TradeQty']) and (
                                    int(sell_order['filledQuantity']) == tradeParas['TradeQty']):
                                append_trade_record(stock, "Buy " + str(
                                    buy_order['filledQuantity']) + stock + " @Price:" + str(buy_order['price'])
                                                    + " and Sell " + str(
                                    sell_order['filledQuantity']) + stock + " @Price:" + str(sell_order['price']))
                                tradeParas['BuyOrderId'] = generate_buy_order(account_number=account['account_number'],
                                                                              stock_symbol=stock)
                                tradeParas['SellOrderId'] = generate_sell_order(
                                    account_number=account['account_number'],
                                    stock_symbol=stock)
                                save_trade_paras_to_file(stock, tradeParas)

                            elif int(buy_order['filledQuantity']) == tradeParas['TradeQty']:
                                append_trade_record(stock,
                                                    "Buy " + str(
                                                        buy_order['filledQuantity']) + stock + " @Price:" + str(
                                                        buy_order['price']))
                                cancel_order(account_num=account['account_number'], access_token=access_token,
                                             order_id=tradeParas['SellOrderId'])
                                tradeParas['LastBuyPrice'] = tradeParas['LastBuyPrice'] - tradeParas['PriceStep']
                                tradeParas['BuyOrderId'] = generate_buy_order(account_number=account['account_number'],
                                                                              stock_symbol=stock)
                                tradeParas['SellOrderId'] = generate_sell_order(
                                    account_number=account['account_number'],
                                    stock_symbol=stock)
                                save_trade_paras_to_file(stock, tradeParas)

                            elif int(sell_order['filledQuantity']) == tradeParas['TradeQty']:
                                append_trade_record(stock,
                                                    "Sell " + str(
                                                        sell_order['filledQuantity']) + stock + " @Price:" + str(
                                                        sell_order['price']))
                                cancel_order(account_num=account['account_number'], access_token=access_token,
                                             order_id=tradeParas['BuyOrderId'])
                                tradeParas['LastBuyPrice'] = tradeParas['LastBuyPrice'] + tradeParas['PriceStep']
                                tradeParas['BuyOrderId'] = generate_buy_order(account_number=account['account_number'],
                                                                              stock_symbol=stock)
                                tradeParas['SellOrderId'] = generate_sell_order(
                                    account_number=account['account_number'],
                                    stock_symbol=stock)
                                save_trade_paras_to_file(stock, tradeParas)

                            elif first_time_enter_trading_hours and (
                                    buy_order['status'] == 'CANCELED' or buy_order['status'] == 'EXPIRED') and (
                                    sell_order['status'] == 'CANCELED' or sell_order['status'] == 'EXPIRED'):
                                tradeParas['BuyOrderId'] = generate_buy_order(account_number=account['account_number'],
                                                                              stock_symbol=stock)
                                tradeParas['SellOrderId'] = generate_sell_order(
                                    account_number=account['account_number'],
                                    stock_symbol=stock)
                                save_trade_paras_to_file(stock, tradeParas)
                                print("Enter trading hours.", stock, " old orders are canceled, new orders placed")
                            else:
                                print(stock, " buy sell orders can not be found in Queued orders and be processed")
                        # else:
                        #    print(stock, " buy sell order found in Queued orders!")
            first_time_enter_trading_hours = False
        else:
            first_time_enter_trading_hours = True

    except:
        exception_count = exception_count + 1
        if exception_count > EXCEPTION_LIMITS:
            print("Too many exceptions exceed the EXCEPTION_LIMIT:", EXCEPTION_LIMITS)
            exit(100)
        else:
            print("Exception happened ", exception_count, " times")
            time.sleep(10)
            pass
