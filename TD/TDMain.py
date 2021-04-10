# -*- coding: utf-8 -*-
"""
Created on Tue May 19 12:57:24 2020

@author: LC
"""

from datetime import datetime, timedelta
import json
import xmltodict

from Ameritrade_cfg_obj import TDConfig
from TDAPI import TDAPI
from TDStream import TDStreamerClient
from TDPortfolio import Portfolio


TDCFG = TDConfig()

TDAPI = TDAPI(TDCFG)

Porfo = Portfolio(TDAPI, account_id = TDCFG.account_id, method='LIFO')

TDS = TDStreamerClient(TDAPI)

TDS.connect()

TDS.QOS_request(qoslevel = '0')
indicators = '$DJI, $TICK'
equities = 'SPY, AAPL, MELI, GOOG, AMZN, NFLX, TSLA, NVDA, SLB, C, FB, MSFT, KO, DIS, ADBE, QQQ, TWTR, KO'
futures = '/ES, /CL'

keys = equities +str(', ')+ indicators

TDS.data_request_account_activity()

TDS.data_request_chart_equity(keys = keys)
TDS.data_request_timesale_equity(keys = keys)
TDS.data_request_nasdaq_book(keys = keys)
TDS.data_request_quote(keys = keys)

TDS.data_request_chart_futures(keys = futures)
TDS.data_request_levelone_futures(keys = futures)
TDS.data_request_timesale_futures(keys = futures)

TDS.data_request_actives_nasdaq()
TDS.data_request_actives_nyse()
TDS.data_request_actives_otcbb()
TDS.data_request_actives_options()

###############################################################################################

instrument_fundamentals = TDAPI.search_instruments(equities, 'fundamental')
today = datetime.today()-timedelta(hours=2)
today = today.strftime('%Y-%m-%d')
json.dump( instrument_fundamentals, open( "./StreamData/Fundamentals_{}.json".format(today), 'w' ) )

###################################################################################################

optionsChains = []
equitiesList = equities.split(", ")
for equity in equitiesList:

    OptionChain = {
                    "symbol": equity,
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

    options = TDAPI.get_option_chain(option_chain = OptionChain)
    optionsChains.append(options)

json.dump(optionsChains, open( "./StreamData/Options_Chains_{}.json".format(today), 'w' ) )

#################################################################################################

account_act = TDS.data['account_activity']
chart_equity = TDS.data['chart_equity']
time_sales = TDS.data['time_sales_equity']
level2_nasdaq = TDS.data['level_2_nasdaq']
subs_act = TDS.data['subscription_data']

notify = TDS.response_types['notify']
response = TDS.response_types['response']
snapshot = TDS.response_types['snapshot']

######################################################

subs = TDS.current_subscriptions


# TDS.logout_request()


###############################################


accountActivity = []
acc_prt = 0


def acc_activity_check(reponse_type=None):
    global acc_prt
    global accountActivity
    #while True:

    acc_len = len(account_act)
    if acc_prt < acc_len:
        new = acc_len - acc_prt
        newActivities = account_act[-new:]

        for activity in newActivities:

            lastAcct = json.loads(activity[2])

            if lastAcct['2'] != 'SUBSCRIBED' and lastAcct['2'] != 'ERROR':
                last = xmltodict.parse(lastAcct['3'])[str(lastAcct['2']+"Message")]
                accountActivity.append(last)
                print(last)
                print ("*********************************")
            else:
                print(lastAcct['2'])
                print ("*********************************")
        print ("*********************************")
        #print (account_act[-new:])

        acc_prt = acc_len


TDS.bind_to(acc_activity_check)



