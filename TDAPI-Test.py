# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:51:37 2019

@author: LC
"""

import datetime as dt
from datetime import timedelta

from TDAPI import TDAPI
from Ameritrade_cfg import client_id, redirect_uri, account_id

TDAPI = TDAPI(client_id, redirect_uri, account_id)

TDAPI.Auth.authenticate()
TDAPI.Auth.access_token


### Preferences
preferences = TDAPI.get_preferences(account = account_id)
streamer_sub_keys = TDAPI.get_streamer_subscription_keys(accounts = [account_id])
principals = TDAPI.get_user_principals(fields = ['preferences', 'streamerConnectionInfo'])

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

##### Accounts
accounts = TDAPI.get_accounts(account = account_id, fields = ['orders', 'positions'])
accountss = TDAPI.get_accounts(account = 'all', fields = ['orders', 'positions'])

#### Transactions
trades = TDAPI.get_transactions(account = account_id, transaction_type = 'TRADE')
transactions = TDAPI.get_transactions(account = account_id, transaction_type = 'ALL', start_date = '2019-01-31', end_date = '2019-04-28')

##### Instruments
instruments = TDAPI.search_instruments(symbol = 'SPY', projection = 'symbol-search')
instruments2 = instrument_search_data = TDAPI.search_instruments('MSFT', 'fundamental')
instruments3 = instrument_get_data = TDAPI.get_instruments(cusip = '594918104')

#### Market Hours
market_hours = TDAPI.get_market_hours(market = 'EQUITY')
markets_hours = TDAPI.get_markets_hours()

### Movers
movers_data = TDAPI.get_movers(market = '$DJI', direction = 'up', change = 'value')

##### Quotes
quote = TDAPI.get_quote(instruments = 'AAPL')
quotes = TDAPI.get_quotes(instruments = ['AAPL','GOOG'])

#### Price History
Pricehistory = TDAPI.pricehistoryPeriod(symbol = 'AAPL', periodType = 'day', frequencyType = 'minute', frequency = '1', period = '1', needExtendedHoursData = 'true')
pricehistoryDate = TDAPI.pricehistoryDates(symbol = 'AAPL', periodType = 'day', frequencyType = 'minute', frequency = '1',
                     endDate = dt.datetime.now()-timedelta(weeks=1), startDate = dt.datetime.now()-timedelta(weeks=2), needExtendedHoursData = 'true')

### Options.

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

Option = TDAPI.get_option_chain(option_chain = OptionChain)

#### Watchlist
watchlist = TDAPI.get_watchlist_accounts(account = 'all')
watchlistone = TDAPI.get_watchlist(account = account_id, watchlist_id = '48456994')
TDAPI.delete_watchlist(account = account_id, watchlist_id = '48456994')
            
Watchlist3 =[{"instrument":{"symbol": "KO","assetType": 'EQUITY'}},
             {"instrument":{"symbol": "GOOG","assetType": 'EQUITY'}}]

Watchlist4 =[{"instrument":{"symbol": "AAPL","assetType": 'EQUITY'}},
             {"instrument":{"symbol": "MSFT","assetType": 'EQUITY'}}]
              
TDAPI.create_watchlist(account = account_id, name = 'Prueba23', watchlistItems = Watchlist3)
TDAPI.replace_watchlist(account = account_id, watchlist_id = '1330133653', name_new = 'Repru8', watchlistItems_new = Watchlist4)
TDAPI.update_watchlist(account = account_id, watchlist_id = '1330133653', name_new = 'LLPRU64', watchlistItems_to_add = Watchlist3)

#### Orders
orders = TDAPI.get_orders_path(account = account_id, status = 'QUEUED')
orders2 = TDAPI.get_orders_query(account = account_id, from_entered_time = '2019-10-01', status ='QUEUED')
AAPLAOrder = TDAPI.get_order(account = account_id, order_id = '2358522164')

TDAPI.create_order(account = account_id, symbol = 'MELI', price = '100.00', quantity = '100', instruction = 'BUY', assetType = 'EQUITY', 
                     orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

TDAPI.replace_order(account = account_id, order_Id = '2368925382', symbol = 'MELI', price = '101.00', quantity = '50', instruction = 'BUY', assetType = 'EQUITY', 
                     orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

TDAPI.cancel_order(account = account_id, order_id = '2368925382')

### SavedOrders
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
                                  'instrument':{'symbol':'SPY,
                                                'assetType':'EQUITY'
                                               }
                                 }
                                ]
          }

''' Below is the complete order detail and their option. It can be use to create order custom or replace order custom '''

FullOrder = {
            "session": "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'",
            "duration": "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'",
            "orderType": "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or 'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'",
            "cancelTime": {
                "date": "string",
                "shortFormat": False
            },
            "complexOrderStrategyType": "'NONE' or 'COVERED' or 'VERTICAL' or 'BACK_RATIO' or 'CALENDAR' or 'DIAGONAL' or 'STRADDLE' or 'STRANGLE' or 'COLLAR_SYNTHETIC' or 'BUTTERFLY' or 'CONDOR' or 'IRON_CONDOR' or 'VERTICAL_ROLL' or 'COLLAR_WITH_STOCK' or 'DOUBLE_DIAGONAL' or 'UNBALANCED_BUTTERFLY' or 'UNBALANCED_CONDOR' or 'UNBALANCED_IRON_CONDOR' or 'UNBALANCED_VERTICAL_ROLL' or 'CUSTOM'",
            "quantity": 0,
            "filledQuantity": 0,
            "remainingQuantity": 0,
            "requestedDestination": "'INET' or 'ECN_ARCA' or 'CBOE' or 'AMEX' or 'PHLX' or 'ISE' or 'BOX' or 'NYSE' or 'NASDAQ' or 'BATS' or 'C2' or 'AUTO'",
            "destinationLinkName": "string",
            "releaseTime": "string",
            "stopPrice": 0,
            "stopPriceLinkBasis": "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
            "stopPriceLinkType": "'VALUE' or 'PERCENT' or 'TICK'",
            "stopPriceOffset": 0,
            "stopType": "'STANDARD' or 'BID' or 'ASK' or 'LAST' or 'MARK'",
            "priceLinkBasis": "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
            "priceLinkType": "'VALUE' or 'PERCENT' or 'TICK'",
            "price": 0,
            "taxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'AVERAGE_COST' or 'SPECIFIC_LOT'",
            "orderLegCollection": [
                {
                    "orderLegType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
                    "legId": 0,
                    "instrument": { #"The type <Instrument> has the following subclasses [Option, MutualFund, CashEquivalent, Equity, FixedIncome] descriptions are listed below\""
                                  },
                    "instruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or 'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'",
                    "positionEffect": "'OPENING' or 'CLOSING' or 'AUTOMATIC'",
                    "quantity": 0,
                    "quantityType": "'ALL_SHARES' or 'DOLLARS' or 'SHARES'"
                }
            ],
            "activationPrice": 0,
            "specialInstruction": "'ALL_OR_NONE' or 'DO_NOT_REDUCE' or 'ALL_OR_NONE_DO_NOT_REDUCE'",
            "orderStrategyType": "'SINGLE' or 'OCO' or 'TRIGGER'",
            "orderId": 0,
            "cancelable": False,
            "editable": False,
            "status": "'AWAITING_PARENT_ORDER' or 'AWAITING_CONDITION' or 'AWAITING_MANUAL_REVIEW' or 'ACCEPTED' or 'AWAITING_UR_OUT' or 'PENDING_ACTIVATION' or 'QUEUED' or 'WORKING' or 'REJECTED' or 'PENDING_CANCEL' or 'CANCELED' or 'PENDING_REPLACE' or 'REPLACED' or 'FILLED' or 'EXPIRED'",
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
                          "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
                          "cusip": "string",
                          "symbol": "string",
                          "description": "string",
                          "type": "'VANILLA' or 'BINARY' or 'BARRIER'",
                          "putCall": "'PUT' or 'CALL'",
                          "underlyingSymbol": "string",
                          "optionMultiplier": 0,
                          "optionDeliverables": [
                                                    {
                                                  "symbol": "string",
                                                  "deliverableUnits": 0,
                                                  "currencyType": "'USD' or 'CAD' or 'EUR' or 'JPY'",
                                                  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
                                                    }
                                                ]
                          }
                
                
                
                MutualFund = {
                              "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
                              "cusip": "string",
                              "symbol": "string",
                              "description": "string",
                              "type": "'NOT_APPLICABLE' or 'OPEN_END_NON_TAXABLE' or 'OPEN_END_TAXABLE' or 'NO_LOAD_NON_TAXABLE' or 'NO_LOAD_TAXABLE'"
                             }
                
                
                
                CashEquivalent = {
                                  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
                                  "cusip": "string",
                                  "symbol": "string",
                                  "description": "string",
                                  "type": "'SAVINGS' or 'MONEY_MARKET_FUND'"
                                 }
                
                
                
                Equity = {
                          "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
                          "cusip": "string",
                          "symbol": "string",
                          "description": "string"
                         }
                
                
                
                FixedIncome = {
                                  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
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
                                          "activityType": "'EXECUTION' or 'ORDER_ACTION'",
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
