# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:51:37 2019

@author: Luis
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

