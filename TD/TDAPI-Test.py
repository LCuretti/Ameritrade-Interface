# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:51:37 2019

@author: LC
"""

import pandas as pd
from datetime import datetime, timedelta


from Ameritrade_cfg_obj import TDConfig
from TDAPI import TDAPI


TDCFG = TDConfig()
TDAPI = TDAPI(TDCFG)

TDAPI.Auth.authenticate()
TDAPI.Auth.access_token


account_id = TDCFG.account_id

'''#################### Preferences '''
preferences = TDAPI.get_preferences(account = account_id)
streamer_sub_keys = TDAPI.get_streamer_subscription_keys(accounts = [account_id])
principals = TDAPI.get_user_principals(fields = ['preferences', 'streamerConnectionInfo','streamerSubscriptionKeys'])

#DataFrame Data
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

flatened = flatten_json(principals)
principal_df = pd.io.json.json_normalize(flatened).T




#### Preferences payload options:
Payload = {
           "expressTrading": False,
           "directOptionsRouting": False,
           "directEquityRouting": False,
           "defaultEquityOrderLegInstruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'NONE'",
           "defaultEquityOrderType": "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or 'NONE'",
           "defaultEquityOrderPriceLinkType": "'VALUE' or 'PERCENT' or 'NONE'",
           "defaultEquityOrderDuration": "'DAY' or 'GOOD_TILL_CANCEL' or 'NONE'",
           "defaultEquityOrderMarketSession": "'AM' or 'PM' or 'NORMAL' or 'SEAMLESS' or 'NONE'",
           "defaultEquityQuantity": 0,
           "mutualFundTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
           "optionTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
           "equityTaxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'MINIMUM_TAX' or 'AVERAGE_COST' or 'NONE'",
           "defaultAdvancedToolLaunch": "'TA' or 'N' or 'Y' or 'TOS' or 'NONE' or 'CC2'",
           "authTokenTimeout": "'FIFTY_FIVE_MINUTES' or 'TWO_HOURS' or 'FOUR_HOURS' or 'EIGHT_HOURS'"
           }

#### Preferences payload default:
Payload = {
           "expressTrading": False,
           "directOptionsRouting": False,
           "directEquityRouting": False,
           "defaultEquityOrderLegInstruction": 'NONE',
           "defaultEquityOrderType": 'MARKET',
           "defaultEquityOrderPriceLinkType": 'NONE',
           "defaultEquityOrderDuration": 'DAY',
           "defaultEquityOrderMarketSession": 'NORMAL',
           "defaultEquityQuantity": 0,
           "mutualFundTaxLotMethod": 'FIFO',
           "optionTaxLotMethod": 'FIFO',
           "equityTaxLotMethod": 'FIFO',
           "defaultAdvancedToolLaunch": 'NONE',
           "authTokenTimeout": 'FIFTY_FIVE_MINUTES'
          }

TDAPI.update_preferences(account = account_id, dataPayload = Payload)

'''################################# Accounts '''
accounts = TDAPI.get_accounts(account = account_id, fields = ['orders', 'positions'])
accountss = TDAPI.get_accounts(account = 'all', fields = ['orders', 'positions'])

#DataFrame Data
flatened = flatten_json(accounts)
accounts_df = pd.io.json.json_normalize(flatened).T

'''################################# Transactions'''
#### All trades last year
trades = TDAPI.get_transactions(account = account_id, transaction_type = 'TRADE')

#### All transaction specific dates
transactions = TDAPI.get_transactions(account = account_id, transaction_type = 'ALL', start_date = '2019-01-31', end_date = '2019-04-28')

#DataFrame Data
trades_df = pd.io.json.json_normalize(trades).T
transactions_df = pd.io.json.json_normalize(transactions).T

'''################################# Instruments'''
instruments = TDAPI.search_instruments(symbol = 'SPY', projection = 'symbol-search')
instrument_search_data = TDAPI.search_instruments('MSFT', 'fundamental')
instrument_get_data = TDAPI.get_instruments(cusip = '594918104')

#DataFrame Data
search_df = pd.DataFrame(instruments)
fundamentals_df = pd.io.json.json_normalize(instrument_search_data).T
cusip_df = pd.DataFrame(instrument_get_data).T

'''####################################### Market Hours'''
market_hours = TDAPI.get_market_hours(market = 'EQUITY', date = '2019-12-09')
markets_hours = TDAPI.get_markets_hours(markets = 'all', date = '2019-12-09')

#DataFrame Data

flatened = flatten_json(markets_hours)

market_df = pd.io.json.json_normalize(market_hours).T
markets_df = pd.io.json.json_normalize(flatened).T

'''######################################## Movers'''
movers_data = TDAPI.get_movers(market = '$DJI', direction = 'up', change = 'value')

'''######################################## Quotes'''
quote = TDAPI.get_quote(instruments = 'AAPL')
quotes = TDAPI.get_quotes(instruments = ['AAPL','GOOG'])


#DataFrame Data
quotes_df = pd.DataFrame.from_dict(quotes).T

for col in ('tradeTimeInLong', 'quoteTimeInLong', 'regularMarketTradeTimeInLong'):
    quotes_df[col] = pd.to_datetime(quotes_df[col]/1000*10**9)-timedelta(hours=5)

quotes_df = quotes_df.T



'''######################################### Price History'''
Pricehistory = TDAPI.pricehistoryPeriod(symbol = 'AAPL', periodType = 'day', frequencyType = 'minute', frequency = '1', period = '1', needExtendedHoursData = 'true')
pricehistoryDate = TDAPI.pricehistoryDates(symbol = 'AAPL', periodType = 'day', frequencyType = 'minute', frequency = '1',
                     endDate = datetime.now()-timedelta(weeks=1), startDate = datetime.now()-timedelta(weeks=2), needExtendedHoursData = 'true')

#DataFrame Data
Candles = pd.DataFrame(Pricehistory['candles'])
Candles.set_index(pd.DatetimeIndex(Candles['datetime']/1000*10**9)-timedelta(hours=5), inplace=True)
Candles.drop("datetime", axis=1, inplace= True)


CandlesDate = pd.DataFrame(pricehistoryDate['candles'])
CandlesDate.set_index(pd.DatetimeIndex(CandlesDate['datetime']/1000*10**9)-timedelta(hours=5), inplace=True)
CandlesDate.drop("datetime", axis=1, inplace= True)


'''###################################### Options.'''

OptionChain = {
                "symbol": "",
                "contractType": ['CALL', 'PUT', 'ALL'],
                "strikeCount": '',
                "includeQuotes":['TRUE','FALSE'],
                "strategy": ['SINGLE', 'ANALYTICAL', 'COVERED', 'VERTICAL', 'CALENDAR', 'STRANGLE', 'STRADDLE', 'BUTTERFLY'],
                "interval": '',
                "strike": "",
                "range": ['ITM', 'NTM', 'OTM', 'SAK','SBK','SNK','ALL'],
                "fromDate": "yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz",
                "toDate": "yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz",
                "volatility": "",
                "underlyingPrice": "",
                "interestRate": "",
                "daysToExpiration": "",
                "expMonth":['ALL','JAN','FEB','MAR', 'APR','MAY','JUN', 'JUL','AUG','SEP', 'OCT', 'NOV', 'DEC'],
                "optionType": ['S', 'NS', 'ALL']
              }

OptionChain = {
                "symbol": "AAPL",
                "contractType": 'ALL',
                "strikeCount": 1,
                "includeQuotes":'FALSE',
                "strategy": 'SINGLE',
                "interval": None,
                "strike": None,
                "range": 'ALL',
                "fromDate": None,
                "toDate": None,
                "volatility": None,
                "underlyingPrice": None,
                "interestRate": None,
                "daysToExpiration": None,
                "expMonth":'ALL',
                "optionType":'ALL'
              }

option = TDAPI.get_option_chain(option_chain = OptionChain)


#DataFrame Data

ret = []
for date in option['callExpDateMap']:
    for strike in option['callExpDateMap'][date]:
        ret.extend(option['callExpDateMap'][date][strike])
for date in option['putExpDateMap']:
    for strike in option['putExpDateMap'][date]:
        ret.extend(option['putExpDateMap'][date][strike])

df = pd.DataFrame(ret)
for col in ('tradeTimeInLong', 'quoteTimeInLong', 'expirationDate', 'lastTradingDay'):
    df[col] = pd.to_datetime(df[col], unit='ms')





'''############################ Watchlist '''
watchlist = TDAPI.get_watchlist_accounts(account = 'all')
watchlistone = TDAPI.get_watchlist(account = account_id, watchlist_id = '635544934')
TDAPI.delete_watchlist(account = account_id, watchlist_id = '48456994')


FullWatchListItem = {
                                    "name": "string",
                                    "watchlistItems": [
                                                        {
                                                        "quantity": 0,
                                                        "averagePrice": 0,
                                                        "commission": 0,
                                                        "purchasedDate": "DateParam\"",
                                                        "instrument": {
                                                                        "symbol": "string",
                                                                        "assetType": "'EQUITY' or 'OPTION' or 'MUTUAL_FUND' or 'FIXED_INCOME' or 'INDEX'"
                                                                      }
                                                         }
                                                      ]
                                     }

'''Not sure why anyone would chosse "quantity, "averagePrice", "commission" or purchaseDate'''

Watchlist3 =[{"instrument":{"symbol": "KO","assetType": 'EQUITY'}},
             {"instrument":{"symbol": "GOOG","assetType": 'EQUITY'}}]

Watchlist4 =[{"instrument":{"symbol": "AAPL","assetType": 'EQUITY'}},
             {"instrument":{"symbol": "MSFT","assetType": 'EQUITY'}}]

TDAPI.create_watchlist(account = account_id, name = 'Prueba23', watchlistItems = Watchlist3)
TDAPI.replace_watchlist(account = account_id, watchlist_id = '1330133653', name_new = 'Repru8', watchlistItems_new = Watchlist4)
TDAPI.update_watchlist(account = account_id, watchlist_id = '1330133653', name_new = 'LLPRU64', watchlistItems_to_add = Watchlist3)

'''################################ Orders '''

orders = TDAPI.get_orders_path(account = account_id, status = 'QUEUED')
orders2 = TDAPI.get_orders_query(account = account_id, from_entered_time = '2019-10-01', status ='QUEUED')
AAPLAOrder = TDAPI.get_order(account = account_id, order_id = '2358522164')

TDAPI.create_order(account = account_id, symbol = 'MELI', price = '100.00', quantity = '100', instruction = 'BUY', assetType = 'EQUITY',
                     orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

TDAPI.replace_order(account = account_id, order_Id = '2368925382', symbol = 'MELI', price = '101.00', quantity = '50', instruction = 'BUY', assetType = 'EQUITY',
                     orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

TDAPI.cancel_order(account = account_id, order_id = '2368925382')

'''########################### SavedOrders '''
savedorders = TDAPI.get_savedorders_path(account = account_id, status = 'QUEUED')



'''############################### Custom Order ####################################'''

BaseOrder = {'orderType':'LIMIT',
           'session':'NORMAL',
           'price': 0,
           'duration':'DAY',
           'orderStrategyType':'SINGLE',
           'orderLegCollection':[
                                 {'instruction':'BUY',
                                  'quantity':100,
                                  'instrument':{'symbol':'SPY',
                                                'assetType':'EQUITY'
                                               }
                                 }
                                ]
          }

''' Below is the complete order detail and their option. It can be use to create order custom or replace order custom '''

FullOrder = {
            "session": "'NORMAL','AM','PM','SEAMLESS'",
            "duration": "'DAY','GOOD_TILL_CANCEL','FILL_OR_KILL'",
            "orderType": "'MARKET','LIMIT','STOP','STOP_LIMIT','TRAILING_STOP','MARKET_ON_CLOSE','EXERCISE','TRAILING_STOP_LIMIT','NET_DEBIT','NET_CREDIT','NET_ZERO'",
            "cancelTime": {
                "date": "string",
                "shortFormat": False
            },
            "complexOrderStrategyType": "'NONE','COVERED','VERTICAL','BACK_RATIO','CALENDAR','DIAGONAL','STRADDLE','STRANGLE','COLLAR_SYNTHETIC','BUTTERFLY','CONDOR','IRON_CONDOR','VERTICAL_ROLL','COLLAR_WITH_STOCK','DOUBLE_DIAGONAL','UNBALANCED_BUTTERFLY','UNBALANCED_CONDOR','UNBALANCED_IRON_CONDOR','UNBALANCED_VERTICAL_ROLL','CUSTOM'",
            "quantity": 0,
            "filledQuantity": 0,
            "remainingQuantity": 0,
            "requestedDestination": "'INET','ECN_ARCA','CBOE','AMEX','PHLX','ISE','BOX','NYSE','NASDAQ','BATS','C2','AUTO'",
            "destinationLinkName": "string",
            "releaseTime": "string",
            "stopPrice": 0,
            "stopPriceLinkBasis": "'MANUAL','BASE','TRIGGER','LAST','BID','ASK','ASK_BID','MARK','AVERAGE'",
            "stopPriceLinkType": "'VALUE','PERCENT','TICK'",
            "stopPriceOffset": 0,
            "stopType": "'STANDARD','BID','ASK','LAST','MARK'",
            "priceLinkBasis": "'MANUAL','BASE','TRIGGER','LAST','BID','ASK','ASK_BID','MARK','AVERAGE'",
            "priceLinkType": "'VALUE','PERCENT','TICK'",
            "price": 0,
            "taxLotMethod": "'FIFO','LIFO','HIGH_COST','LOW_COST','AVERAGE_COST','SPECIFIC_LOT'",
            "orderLegCollection": [
                {
                    "orderLegType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'",
                    "legId": 0,
                    "instrument": { #"The type <Instrument> has the following subclasses [Option, MutualFund, CashEquivalent, Equity, FixedIncome] descriptions are listed below\""
                                  },
                    "instruction": "'BUY','SELL','BUY_TO_COVER','SELL_SHORT','BUY_TO_OPEN','BUY_TO_CLOSE','SELL_TO_OPEN','SELL_TO_CLOSE','EXCHANGE'",
                    "positionEffect": "'OPENING','CLOSING','AUTOMATIC'",
                    "quantity": 0,
                    "quantityType": "'ALL_SHARES','DOLLARS','SHARES'"
                }
            ],
            "activationPrice": 0,
            "specialInstruction": "'ALL_OR_NONE','DO_NOT_REDUCE','ALL_OR_NONE_DO_NOT_REDUCE'",
            "orderStrategyType": "'SINGLE','OCO','TRIGGER'",
            "orderId": 0,
            "cancelable": False,
            "editable": False,
            "status": "'AWAITING_PARENT_ORDER','AWAITING_CONDITION','AWAITING_MANUAL_REVIEW','ACCEPTED','AWAITING_UR_OUT','PENDING_ACTIVATION','QUEUED','WORKING','REJECTED','PENDING_CANCEL','CANCELED','PENDING_REPLACE','REPLACED','FILLED','EXPIRED'",
            "enteredTime": "string",
            "closeTime": "string",
            "tag": "string",
            "accountId": 0,
            "orderActivityCollection": {#"\"The type <OrderActivity> has the following subclasses [Execution] descriptions are listed below\""
                                       },
            "replacingOrderCollection": [
                                            {}
                                        ],
            "childOrderStrategies": [
                                            {}
                                    ],
            "statusDescription": "string"
        }

##The class <Instrument> has the following subclasses:
##JSON for each are listed below:
instrument = {
                Option = {
                          "assetType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'",
                          "cusip": "string",
                          "symbol": "string",
                          "description": "string",
                          "type": "'VANILLA','BINARY','BARRIER'",
                          "putCall": "'PUT','CALL'",
                          "underlyingSymbol": "string",
                          "optionMultiplier": 0,
                          "optionDeliverables": [
                                                    {
                                                  "symbol": "string",
                                                  "deliverableUnits": 0,
                                                  "currencyType": "'USD','CAD','EUR','JPY'",
                                                  "assetType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'"
                                                    }
                                                ]
                          }



                MutualFund = {
                              "assetType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'",
                              "cusip": "string",
                              "symbol": "string",
                              "description": "string",
                              "type": "'NOT_APPLICABLE','OPEN_END_NON_TAXABLE','OPEN_END_TAXABLE','NO_LOAD_NON_TAXABLE','NO_LOAD_TAXABLE'"
                             }



                CashEquivalent = {
                                  "assetType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'",
                                  "cusip": "string",
                                  "symbol": "string",
                                  "description": "string",
                                  "type": "'SAVINGS','MONEY_MARKET_FUND'"
                                 }



                Equity = {
                          "assetType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'",
                          "cusip": "string",
                          "symbol": "string",
                          "description": "string"
                         }



                FixedIncome = {
                                  "assetType": "'EQUITY','OPTION','INDEX','MUTUAL_FUND','CASH_EQUIVALENT','FIXED_INCOME','CURRENCY'",
                                  "cusip": "string",
                                  "symbol": "string",
                                  "description": "string",
                                  "maturityDate": "string",
                                  "variableRate": 0,
                                  "factor": 0
                               }
            }

##The class <OrderActivity> has the following subclasses:
##JSON for each are listed below:
orderActivityCollection = {
                            Execution = {
                                          "activityType": "'EXECUTION','ORDER_ACTION'",
                                          "executionType": "'FILL'",
                                          "quantity": 0,
                                          "orderRemainingQuantity": 0,
                                          "executionLegs": [
                                                            {
                                                              "legId": 0,
                                                              "quantity": 0,
                                                              "mismarkedQuantity": 0,
                                                              "price": 0,
                                                              "time": "string"
                                                            }
                                                            ]
                                        }
                        }



CustomedOrder = {
            "session": 'NORMAL',
            "duration": 'DAY',
            "orderType": 'LIMIT',
            "complexOrderStrategyType": 'NONE',
            "requestedDestination": 'AUTO',
            "price": 101,
            "taxLotMethod": 'LIFO',
            "orderLegCollection": [
                {
                    "instrument": {"assetType": 'EQUITY',
                                   "symbol": "MELI",
                                  },
                    "instruction": 'BUY',
                    "quantity": 50,
                }
            ],
            "orderStrategyType": 'SINGLE'
        }

TDAPI.create_custom_order(account = account_id, order = CustomedOrder)
TDAPI.replace_custom_order(account = account_id, order_Id = '2369502052', order = CustomedOrder)
