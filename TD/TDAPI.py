# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 08:23:24 2019

The MIT License

Copyright (c) 2018 Addison Lynch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: LC
Based on areed1192 / td-ameritrade-python-api
"""

import json
import requests
import urllib.parse
from datetime import datetime

from TDAuthentication import TDAuthentication

class TDAPI():
    '''
        TD Ameritrade API Class.

        Performs request to the TD Ameritrade API. Response in JSON format.

        Method Type                 	Method             	               Type	   Header	                                 Endpoint
        Authentication	                Post Access Token	               POST	   None	                                     /oauth2/token

        User Info and Preferennces	    Get User Principals	               GET	   Bearer <access token>	                 /userprincipals
                                    	Get Streamer Subscription Keys	   GET	   Bearer <access token>	                 /userprincipals/streamersubscriptionkeys
                                        Get Preferences	                   GET	   Bearer <access token>	                 /accounts/{accountId}/preferences
                                        Update Preferences	               PUT	   Bearer <access token> + application/json  /accounts/{accountId}/preferences

        Accounts	                    Get Accounts	                   GET	   Bearer <access token>	                 /accounts
                                    	Get Account	                       GET	   Bearer <access token>	                 /accounts/{accountId}

        Orders	                        Get Order by Query	               GET	   Bearer <access token>	                 /orders
                                    	Get Order by Path	               GET	   Bearer <access token>	                 /accounts/{accountId}/orders
                                        Get Order	                       GET	   Bearer <access token>	                 /accounts/{accountId}/orders/{orderId}
        	                            Cancel Order	                   DELETE  Bearer <access token>	                 /accounts/{accountId}/orders/{orderId}
        	                            Place Order	                       POST	   Bearer <access token> + application/json	 /accounts/{accountId}/orders
        	                            Replace Order	                   PUT	   Bearer <access token> + application/json	 /accounts/{accountId}/orders/{orderId}

        Saved Orders	                Get Saved Orders by Path	       GET	   Bearer <access token>	                 /accounts/{accountId}/savedorders
        	                            Get Saved Order	                   GET	   Bearer <access token>	                 /accounts/{accountId}/savedorders/{savedorderId}
        	                            Cancel Saved Order	               DELETE  Bearer <access token>	                 /accounts/{accountId}/savedorders/{savedorderId}
        	                            Create Saved Order	               POST	   Bearer <access token> + application/json	 /accounts/{accountId}/savedorders
        	                            Replace Saved Order	               PUT	   Bearer <access token> + application/json	 /accounts/{accountId}/savedorders/{savedorderId}

        Transactions History	        Get Transaction	                   GET	   Bearer <access token>	                 /accounts/{accountId}/transactions/
        	                            Get Transactions	               GET	   Bearer <access token>	                 /accounts/{accountId}/transactions/

        Watchlist	                    Get Watchlist for Multiple Accounts	GET	   Bearer <access token>	                 /accounts/watchlists
        	                            Get Watchlist for Single Account   GET	   Bearer <access token>	                 /accounts/{accountId}/watchlists
        	                            Get Watchlist	                   GET	   Bearer <access token>	                 /accounts/{accountId}/watchlists/{watchlistId}
        	                            Delete Watchlist	               DELETE  Bearer <access token>	                 /accounts/{accountId}/watchlists/{watchlistId}
        	                            Create Watchlist	               POST	   Bearer <access token> + application/json	 /accounts/{accountId}/watchlists
        	                            Replace Watchlist	               PUT	   Bearer <access token> + application/json	/accounts/{accountId}/watchlists/{watchlistId}
        	                            Update Watchlist	               PATCH   Bearer <access token> + application/json	/accounts/{accountId}/watchlists/{watchlistId}

        Instruments	                    Search Instruments	               GET	   Bearer <access token>	                /instruments
        	                            Get Instrument	                   GET	   Bearer <access token>	                /instruments/{cusip}

        Market Hours	                Get Hours for Multiple Markets	   GET	   Bearer <access token>	                /marketdata/hours
        	                            Get Hours for a Single Market	   GET	   Bearer <access token>	                /marketdata/{market}/hours

        Movers	                        Get Movers	                       GET	   Bearer <access token>	                /marketdata/{index}/movers

        Option Chains	                Get Option Chain	               GET	   Bearer <access token>	                /marketdata/chains

        Price History	                Get Price History	               GET	   Bearer <access token>	                /marketdata/{symbol}/pricehistory

        Quotes	                        Get Quote	                       GET	   Bearer <access token>	                /marketdata/{symbol}/quotes
        	                            Get Quotes	                       GET	   Bearer <access token>	                /marketdata/quotes

    '''

    def __init__(self, TDCFG):

        '''
            Initialize object with provided account info
            Open Authentication object to have a valid access token for every request.
        '''

        '''
            The following 2 lines create authentication object and run it.
            It will be use in the headers method to send a valid token.
        '''

        self.Auth = TDAuthentication(TDCFG)
        self.Auth.authenticate()
        print("TDAPI Initialized at: "+str(datetime.now()))

    def __repr__(self):
        '''
            defines the string representation of our TD Ameritrade Class instance.
        '''

        # define the string representation
        return '{}'.format(self.Auth)

    def headers(self, mode = None):
        '''
            Returns a dictionary of default HTTP headers for calls to TD Ameritrade API,
            in the headers we defined the Authorization and access toke.
        '''

        '''
            In the following two line we use the Authentication object to get a valid token.
            You may have a different way to get a valid token for the request.
        '''

        # grab the access token
        token = self.Auth.access_token

        # create the headers dictionary
        headers ={'Authorization':f'Bearer {token}'}

        # if mode 'application/json' for request PUT, PATCH and POST
        if mode == 'application/json':
            headers['Content-type'] = 'application/json'

        return headers

    def api_endpoint(self, url):
        '''
            Convert relative endpoint (e.g.,  'quotes') to full API endpoint.
        '''

        # if they pass through a valid url then, just use that.
        if urllib.parse.urlparse(url).scheme in ['http', 'https']:
            return url

        # otherwise build the URL
        return urllib.parse.urljoin('https://api.tdameritrade.com' + '/v1' + "/", url.lstrip('/'))


    def prepare_parameter_list(self, parameter_list = None):

        '''
            This prepares a parameter that is a list for an API request. If
            the list contains more than one item uit will joint the list
            using the "," delimiter. If only one itemis in the list then only
            the first item will be returned.

            NAME: parameter_list
            DESC:  A List of parameter values assigned to an argument.
            TYPE: List

            EXAMPLE:

                SessionObject.handle_list(parameter_list = ['MSFT', 'SQ'])

        '''

        # if more than one item, join.
        if len(parameter_list) > 1:
            parameter_list = ','.join(parameter_list)
        else: # take the first item.
            parameter_list = parameter_list[0]

        return parameter_list

    '''#########################################################
    ############## User Info & Preferences #####################
    #########################################################'''

    def get_preferences(self, account = None):

        '''
            Get's User Preferences for specific account

            Documentation Link: https://developer.tdameritrade.com/user-principal/apis/get/accounts/%7BaccountTd%7D/preferences-0

            NAME: account
            DESC: The account number you wish to receive preference data for.
            TYPE: String

            EXAMPLES:

            SessionObject.get_preferences(account = 'MyAccountNumber')
        '''

        #define the endpoint
        endpoint = '/accounts/{}/preferences'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers()

        # return teh resposnse of the get request.
        return requests.get(url=url, headers=merged_headers, verify = True).json()

    def get_streamer_subscription_keys(self, accounts = None):

        '''
            SubscriptionKey for provided accounts or default accounts.

            Documentation Link: https://developer.tdameritrade.com/user-principal/apis/get/userprincipals/streamersubscriptionkeys-0

            NAME: account
            DESC: A list of account numbers you wish to receive a streamer key for.
            TYPE: List<String>

            EXAMPLES:

            SessionObject.get_streamer_subscription_keys(accounts = ['MyAccountNumber1'])
            SessionObject.get_streamer_subscription_keys(accounts = ['MyAccountNumber1', 'MyAccountNumber2'])

        '''

        # becasue we have a list arguments, prep it for the request.
        accounts = self.prepare_parameter_list(parameter_list = accounts)

        #buid the params dictionary
        data = {'accountIds':accounts}

        # define the endpoint
        endpoint = '/userprincipals/streamersubscriptionkeys'

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the original haders we have stored
        merged_headers = self.headers()

        #return the response of the get request
        return requests.get(url = url, headers=merged_headers, params = data, verify = True).json()

    def get_user_principals(self, fields = None):

        '''
            Returns User Principals details.

            Documentation Link: https://developer.tdameritrade.com/user-principal/apis/get/userprincipals-0

            NAME: fields
            DESC: A comma separated String which allows one specify additional fields to return. Noneof
                  these fields are returned by default. Possible values in this String can be:

                      1. streamerSubscriptionKeys
                      2. streamerConnectionInfo
                      3. preferences
                      4. surrogateIds
            TYPE: List<String>

            EXAMPLES:

            SessionObject.get_user_principals(fields = ['preferences'])
            SessionObject.get_user_principals(fields = ['preferences', 'streamerConnectionInfo'])
        '''

        # because we have a list argumnent, prep it for the request
        fields = self.prepare_parameter_list(parameter_list = fields)

        #build the params dictionary
        data = {'fields':fields}

        # define teh endpoint
        endpoint = '/userprincipals'

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original header we have stored
        merged_headers = self.headers()

        #return the response of the get request.
        return requests.get(url = url, headers=merged_headers, params = data, verify = True).json()

    def update_preferences(self, account = None, dataPayload = None):

        '''
            Update preferences for a specific account. Please note that the directOptionsRouting and
            directEquityRouting values cannot be modified via this operation.

            Documentation Link: https://developers.tdameritrade.com/user-principals/apis/put/accounts/%7BaccountId%7D/preferences-0

            NAME: account
            DESC: The account number you wish to update preferences for.
            TYPE: String

            NAME: dataPayload
            DESC: A dictionary that provides all the keys you wish to update. It must contain the following keys to be build.

                "expressTrading": false,
                "directOptionsRouting": false,
                "directEquityRouting": false,
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

                default:
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

            TYPE: dictionary

            EXAMPLES:

            SessionObject.update_preferences(account = 'MyAccountNumber', dataPayload = Payload)

        '''

        #define teh endpoint
        endpoint = '/accounts/{}/preferences'.format(account)

        #bould the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored
        merged_headers = self.headers(mode = 'application/json')

        # make the request
        response = requests.put(url=url, headers = merged_headers, data = json.dumps(dataPayload), verify = True)

        if response.status_code == 204:
            return "Preferences successfully updated."
        else:
            return response.content

    '''##########################################
    ################ Account ####################
    ##########################################'''

    def get_accounts(self, account = 'all', fields = None):

        '''
            Account balances, positions, and orders for a specific account.
            Account balances, positions, and orders for all linked accounts.

            Serves as the mechanism to make a request to the "Get Accounts" and "Get Account" endpoint.
            If one account is provided a "Get Account" request will be made and if more than one account
            is provided then a "Get Accounts" request will be made.

            Documentation Link: http://developer.tdameritrade.com/account-access/apis

            NAME: account
            DESC: The account number you wish to receive data on. Default values is 'all'
                  which will return all accounts of the user.
            TYPE: String

            NAME: fields
            DESC: Balances displayed by default, additional field can be added here by
                  adding position or orders.
            TYPE = List<String>

            EXAMPLE:

            SessionObject.get_accounts(account = 'all', fields = ['orders'])
            SessionObject.get_accounts(account = 'My AccountNumber', fields = ['orders', 'positions'])

        '''

        # because we have a listarguments prep it for request.
        fields = self.prepare_parameter_list(parameter_list = fields)

        #build a parameter dictionary
        data = {'fields':fields}

        #if all use '/accounts' else pass through the account number.
        if account == 'all':
            endpoint = '/accounts'
        else:
            endpoint = '/accounts/{}'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers()

        #return the response of the get request.
        return requests.get(url = url, headers = merged_headers, params = data, verify = True).json()


    '''#########################################
    ###########Transaction History #############
    #########################################'''

    def get_transactions(self, account = None, transaction_type = None, symbol = None, start_date = None, end_date = None, transaction_id = None):

        '''
            Serves as the mechanism to make a request to the "Get Transactions" and "Get Transaction" Endpoint.
            If one 'transaction_id'is provided a "Get Transaction" request will be made and if it is not provided
            then a "Get Transactions"request will be made.

            Documentation Link: https://developer.tdameritrade.com/transaction-history/apis

            NAME: account
            DESC: The account number you wish to recieve transactions for.
            TYPE: string

            NAME: transaction_type
            DESC: The type of transaction. Only transactions with specified type will be returned. Valid
                  values are the following: ALL, TRADE, BUY_ONLY, SELL_ONLY, CASH_INOR_CASH_OUT, CHECKING,
                                            DIVIDEND, INTEREST, ITHER, ADVISOR_FEES
            TYPE: String

            NAME: symbol
            DESC: The symbol in the specified transaction. Only transactions with the specified
                  symbol will be returned.
            TYPE: string

            NAME: start_date
            DESC: Only transactions after the start date will be returned. Note: the Maximun date range is
                  one year. Valid ISO-8601 formats are: yyyy-MM-dd.
            TYPE: String

            NAME: end_date
            DESC: Only transactions before the End Date will be returned. Mote: the maximun date range is
                  one year. Valid ISO-8601 formats are: yyyy-MM-dd
            TYPE: String

            NAME: transaction_id
            DESC: The transaction ID you wish to search. If this is specified a "Get transaction"request is
                  made. Should only be used if you wish to return one transaction.
            TYPE: String

            EXAMPLES:

            SessionObject.get_transactions(account = 'MyAccountNumber', transaction_type = 'ALL', start_date = '2019-01-31', end_date = '2019-04-28')
            SessionObject.get_transactions(account = 'MyAccountNumber', transaction_type = 'ALL', start_date = '2019-01-31')
            SessionObject.get_transactions(account = 'MyAccountNumber', transaction_type = 'TRADE')
            SessionObject.get_transactions(transaction_id = 'MyTransactionID')

        '''

        #grab the original headers we have sttored.
        merged_headers = self.headers()

        # if transaction_id is not made, it means we need to make a request to the get_transaction endpoint.
        if transaction_id:

            #define the endpoint:
            endpoint = '/accounts/{}/transactions/{}'.format(account, transaction_id)

            #build the url
            url = self.api_endpoint(endpoint)

            # return the response of teh get request
            return requests.get(url = url, headers=merged_headers, verify = True).json()

        # if it isn't then we need to make a request to the get_transactions endpoint.
        else:

            #build the params dictionary
            data = {'type':transaction_type,
                    'symbol':symbol,
                    'startDate':start_date,
                    'endDate':end_date}

            #define the endpoint
            endpoint = '/accounts/{}/transactions'.format(account)

            #build the url
            url = self.api_endpoint(endpoint)

            # return the response of the get request
            return requests.get(url= url, headers = merged_headers, params=data, verify = True).json()

    '''#########################################
    ############### INSTRUMENTS ################
    #########################################'''

    def search_instruments(self, symbol = None, projection = 'symbol-search'):

        '''
            Search or retrive instrument data, including fundamental data.

            Documentation Link: https://developer.tdameritrade.com/instruments/apis/get/instruments

            NAME: symbol
            DESC: The symbol of the financial instrumen you would like toi search.
            TYPE: string

            NAME: projection
            DESC: The type of reques, default is "symbol-search". The type of request include the following:

                    1. symbol-search
                       Retirve instrument data of a specific symbol or cusip

                    2. symbol-regex
                       Retrive instrument data for all symbols matching regex.
                       Example: symbol= XYZ.* will return all symbols beginning with XYZ

                    3. desc-search
                       Retrive instrument data for intruments whose description contains
                       the word supplied. Example: symbol = FakeCompany will returnall
                       instruments with FakeCompany in the description

                    4. desc-regex
                       Search description with full regex support. Exmapl: symbol=XYZ.[A-C]
                       returns all instruments whose descriptios contains a word begining
                       with XYZ followed by a character A through C

                    5. fundamental
                       Returns fundamental data for a single instrument specified by exact symbol.

            TYPE: String

            EAMPLES:

            SessionObject.search_instruments(symbol = 'XYZ', projection = 'symbol-search')
            SessionObject.search_instruments(symbol = 'XYZ', projection = 'symbol-regex')
            SessionObject.search_instruments(symbol = 'FakeCompany', projection = 'desc-search')
            SessionObject.search_instruments(symbol = 'XYZ.[A-C]', projection = 'desc-regex')
            SessionObject.search_instruments(symbol = 'XYZ.[A-C]', projection = 'fundamental')

        '''

        # build the params dictionary
        data = {'symbol':symbol,
                'projection':projection}

        #define the endpoint
        endpoint = '/instruments'

        # build the url
        url = self.api_endpoint(endpoint)

        # grab the original  headers we have stored
        merged_headers = self.headers()

        # return the response of the get request.
        return requests.get(url=url, headers=merged_headers, params=data, verify = True).json()


    def get_instruments(self, cusip = None):

        '''
            Get an instrument by CUSIP (Committe on Uniform Securities Identification PRocedures) code.

            Documentation Link: https://developer.tdameritrade.com/instruments/apis/get/instruments/%7Bcusip%7D

            NAME: cusip
            DESC: The CUSIP code of a given financial instrument.
            TYPE: string

            EXAMPLES:

                SessionObject.get_instruments(cusip = 'SomeCUSIPNumber')
        '''

        #define the endpoint
        endpoint = '/instruments'

        # build the url
        url = self.api_endpoint(endpoint) + "/" + cusip

        #grab the original headers we have stored
        merged_headers = self.headers()

        # return the resposne of the get request.
        return requests.get(url = url, headers=merged_headers, verify = True).json()

    '''#########################################
    #############  Market Hours ################
    #########################################'''

    def get_markets_hours(self, markets = "all", date = datetime.now()):

        '''
        Retrieve market hours for specified markets

        Serves as the mechanism to make a request to the "Get Hours for multiple Markets for today or future date"

            Documentation Link: https://developer.tdameritrade.com/market-hours/apis


            EXAMPLES:

            SessionObject.get_market_hours(markets = ['EQUITY', 'OPTION'], date = '2019-11-18')
        '''
         # build the params dictionary
        if markets == 'all':
            markets = ['EQUITY', 'OPTION', 'FUTURE', 'BOND','FOREX']

        markets = self.prepare_parameter_list(markets)

        data = {'markets': markets,
                'date': date}

        # define the endpoint
        endpoint = '/marketdata/hours'

        # build the url
        url = self.api_endpoint(endpoint)

        #grab the originsal headers we have stored.
        merged_headers = self.headers()

        # return the response of the get request.
        return requests.get(url = url, headers = merged_headers, params = data, verify = True).json()


    def get_market_hours(self, market = None, date = datetime.now()):

        '''
            Serves as the mechanism to make a request to the
            "Get Hours for simple Markets for today or future date" endpoint."

            Documentation Link: https://developer.tdameritrade.com/market-hours/apis

            NAME: markets
            DESC: The markets for which you're requesting market hours, comma-separated.
                  Valid markets are EQUITY, OPTION, FUTURE, BOND, or FOREX.
            TYPE: List<Strings>


            EXAMPLES:

            SessionObject.get_market_hours(market = 'EQUITY')
        '''

        data = {'date': date}


        # define the endpoint
        endpoint = '/marketdata/{}/hours'.format(market)

        # build the url
        url = self.api_endpoint(endpoint)

        #grab the originsal headers we have stored.
        merged_headers = self.headers()

        # return the response of the get request.
        return requests.get(url = url, headers = merged_headers, params = data, verify = True).json()

    '''#####################################
    ############## Movers ##################
    ####################################'''


    def get_movers(self, market = None, direction = None, change = None):

        '''
            Top 10 (up or down) movers by value or percent for a particular index.

            Documentation Link: https://developer.tdameritrade.com/movers/apis/get/marketdata

            NAME: market
            DESC: The index symbol to get movers for. Can be $DJI, $COMPX, or $SPX.X.
            TYPE: String

            NAME: direction
            DESC: To return movers with the specified directions of up or down. Valid values
                 are "up" or "down"
            TYPE: String

            NAME: change
            DESC: Toreturn movers with the specified change types of percent or value. Valid
                  values are "percent" or "value".
            TYPE: String

            EXAMPLES:

            SessionObjec.get_movers(market = $DJI', direction = 'up', change = 'Value')
            SessionObjec.get_movers(market = $COMPX', direction = 'down', change = 'percent')

        '''

        # build the params dictionary
        data = {'direction': direction,
                'change':change}

        # define teh endpoint
        endpoint = '/marketdata/{}/movers'.format(market)

        # build the url
        url = self.api_endpoint(endpoint)

        # grab the original headers we have stored.
        merged_headers = self.headers()

        #return the response of the request.
        return requests.get(url=url, headers=merged_headers, params=data, verify = True).json()

    '''#############################################
    ################# Quotes #######################
    #############################################'''

    def get_quotes(self, instruments = None):

        '''
            Serves as the mechanism to make a request to Get Quotes Endpoint.

            Documentation Link: https://developer.tdameritrade.com/quotes/apis

            NAME: instruments
            DESC: A List of differen financial intruments.
            TYPE: List

            EXAMPLE:

                SessionObject.get_quotes(intruments = ['MSFT'])
                SessionObject.get_quotes(instruments = ['MSFT', 'SQ'])

        '''

        # becasue we have a list argument, prep it for the request.
        instruments = self.prepare_parameter_list(parameter_list = instruments)

        # buikld the params dictionary
        data = {'symbol':instruments}

        #define the endpoint
        endpoint = '/marketdata/quotes'

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the original headers we have stored.
        merged_headers = self.headers()

        #return the response of the get request.
        return requests.get(url = url, headers=merged_headers, params=data, verify = True).json()

    def get_quote(self, instruments = None):

        '''

            Serves as the mechanism to make a request to Get Quote.

            Documentation Link: https://developer.tdameritrade.com/quotes/apis

            NAME: instruments
            DESC: A List of differen financial intruments.
            TYPE: String

            EXAMPLE:

                SessionObject.get_quotes(intruments = 'MSFT')

        '''

        #define the endpoint
        endpoint = '/marketdata/{}/quotes'.format(instruments)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the original headers we have stored.
        merged_headers = self.headers()

        #return the response of the get request.
        return requests.get(url = url, headers=merged_headers, verify = True).json()


    '''###########################################
    ########### Price History ####################
    ###########################################'''


    def pricehistoryPeriod(self, symbol = None, periodType = None, frequencyType = None, frequency = None, period = None,
                           needExtendedHoursData = None):

        '''
            Get price history for a symbol defining Period. Its provide data up to the last closed day.

            NAME: symbol
            DESC:
            TYPE: String

            NAME: periodType
            DESC: The type of period to show. Valid values are day, month, year, or ytd (year to date). Default is day.
            TYPE: String

            NAME: frequencyType
            DESC: The type of frequency with which a new candle is formed.
                  Valid frequencyTypes by periodType (defaults marked with an asterisk):
                                                                                        day: minute*
                                                                                        month: daily, weekly*
                                                                                        year: daily, weekly, monthly*
                                                                                        ytd: daily, weekly*
            TYPE: String

            NAME: frequency
            DESC: The number of the frequencyType to be included in each candle.
                  Valid frequencies by frequencyType (defaults marked with an asterisk):
                                                                                        minute: 1*, 5, 10, 15, 30
                                                                                        daily: 1*
                                                                                        weekly: 1*
                                                                                        monthly: 1*
            TYPE: String

            NAME: period
            DESC: The number of periods to show.
                  Example: For a 2 day / 1 min chart, the values would be:
                                                                            period: 2
                                                                            periodType: day
                                                                            frequency: 1
                                                                            frequencyType: min

                  Valid periods by periodType (defaults marked with an asterisk):
                                                                            day: 1, 2, 3, 4, 5, 10*
                                                                            month: 1*, 2, 3, 6
                                                                            year: 1*, 2, 3, 5, 10, 15, 20
                                                                            ytd: 1*
            TYPE: String

            NAME: needExtendedHoursData
            DESC: true to return extended hours data, false for regular market hours only. Default is true
            TYPE: String
        '''

        #define the payload
        data = {
                'periodType':periodType,
                'frequencyType':frequencyType,
                'frequency':frequency,
                'period':period,
                'needExtendedHoursData':needExtendedHoursData
                }

        # define the endpoint
        endpoint = 'marketdata/{}/pricehistory'.format(symbol)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers()

        #make the request
        return requests.get(url = url, headers = merged_headers, params = data, verify = True).json()


    def pricehistoryDates(self, symbol = None, periodType = None, frequencyType = None, frequency = None,
                          endDate = datetime.now(), startDate = datetime.now(), needExtendedHoursData = 'true'):

        '''
            Get price history for a symbol defining date Interval. It provides data till the last second.

            NAME: symbol
            DESC:
            TYPE: String

            NAME: periodType
            DESC: The type of period to show. Valid values are day, month, year, or ytd (year to date). Default is day.
            TYPE: String

            NAME: frequencyType
            DESC: The type of frequency with which a new candle is formed.
                  Valid frequencyTypes by periodType (defaults marked with an asterisk):
                                                                                        day: minute*
                                                                                        month: daily, weekly*
                                                                                        year: daily, weekly, monthly*
                                                                                        ytd: daily, weekly*
            TYPE: String

            NAME: frequency
            DESC: The number of the frequencyType to be included in each candle.
                  Valid frequencies by frequencyType (defaults marked with an asterisk):
                                                                                        minute: 1*, 5, 10, 15, 30
                                                                                        daily: 1*
                                                                                        weekly: 1*
                                                                                        monthly: 1*
            TYPE: String

            NAME: endDate
            DESC: End date as milliseconds since epoch. If startDate and endDate are provided, period should not be provided. Default is previous trading day.
            Type: DateTime

            NAME: startDate
            DESC: Start date as milliseconds since epoch. If startDate and endDate are provided, period should not be provided.
            Type: DateTime

            NAME: needExtendedHoursData
            DESC: true to return extended hours data, false for regular market hours only. Default is true
            TYPE: String
        '''
        epoch = datetime.utcfromtimestamp(0)
        eD = int((endDate - epoch).total_seconds()*1000)
        sD = int((startDate - epoch).total_seconds()*1000)

        #define the payload
        data = {
                'periodType':periodType,
                'frequencyType':frequencyType,
                'frequency':frequency,
                'endDate':eD,
                'startDate':sD,
                'needExtendedHoursData':needExtendedHoursData
                }

        # define the endpoint
        endpoint = 'marketdata/{}/pricehistory'.format(symbol)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers()

        #make the request
        return requests.get(url = url, headers = merged_headers, params = data, verify = True).json()

    '''###########################################
    ########## Option Chain ######################
    ###########################################'''

    def get_option_chain(self, option_chain = None):

        # symbol = None, contractType = None, StrikeCount = None, IncludeQuotes = None, Strategy = None,
        #                         interval = None, Strike = None, range = None, fromDate = None, toDate = None, volatility = None,
        #                         underlyingPrice = None, interestRate = None, daysToExpiration = None, expMonth = None, optionType = None

        '''
            Get optionchain for a optionable Symbol.

            Documentation Link: https://developer.tdameritrade.com/option-chains/apis/get/marketdata/chains

            NAME: option_chain
            DESC: Represents a single OptionChainObject.
            Type: TDAmeritrade.OptionChainObject

            EXAMPLE:

                OptionChain_1 = {
                                "symbol": "",
                                "contractType": ['CALL', 'PUT', 'ALL'],
                                "strikeCount": '',
                                "includeQuotes":['TRUE','FALSE'],
                                "strategy": ['SINGLE', 'ANALYTICAL', 'COVERED', 'VERTICAL', 'CALENDAR', 'STRANGLE', 'STRADDLE', 'BUTTERFLY', 'CONDOR', 'DIAGONAL', 'COLLAR', 'ROLL'],
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

                SessionObject.get_option_chain( option_chain = option_chain_1)
        '''
        # take JSON representation of the string
        data = option_chain

        #define the endpoint
        endpoint = '/marketdata/chains'

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers()

        #return the response of the get request.
        return requests.get(url = url, headers = merged_headers, params = data, verify = True).json()

    '''################################################
    #################### WatchList ####################
    ################################################'''

    def create_watchlist(self, account = None, name = None, watchlistItems = None):

        '''
            Create watchlist for specific account. This methos dows not verify that the symbol or asses type are valid.

            Documentation Link: https://developer.tdameritrade.com/watchlist/apis/post/accounts/%7BaccountId%7D/watchlist-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: name
            DESC: The name you want to give your wathclist.
            TYPE: String

            NAME: watchlistItems
            DESC: A list of watchlistitems object.
            TYPE: List<WatchListItems>



                Full WatchListItem = {
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

            EXAMPLES:

            WatchlistItem =[{"instrument":{"symbol": "BLUE",
                                           "assetType": 'EQUITY'},
                            {"instrument":{"symbol": "AAPL",
                                           "assetType": 'EQUITY'}
                            }]

            FullWatchListItem = [
                                {
                                "quantity": 100,
                                "averagePrice": 100,
                                "commission": 10,
                                "purchasedDate": "2020-03-12",
                                "instrument": {
                                                "symbol": "AAPL",
                                                "assetType": 'EQUITY'
                                              }
                                 }
                                 ]


            SessionObject.create_watchlist(account = 'MyAccountNumber', name = 'MyWatchListName', watchlistItems = WatchlistItem)

        '''

        #define the payload
        payload = {"name": name, "watchlistItems": watchlistItems}

        # define the endpoint
        endpoint = '/accounts/{}/watchlists'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.post(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)

        if response.status_code == 201:
            return "Watchlist {} was successfully created.".format(name)
        else:
            return response.content

    def get_watchlist_accounts(self, account = 'all'):

        '''
            Serves as the mechanism to make a request to the "Get Watchlist for single accoun"and
            "Get Watchlist for Multiple Accounts"Endpoint. If one accountis provided a
            "Get Watchlist for single account"request will be made and if 'all' is provided then a
            "Get Watchlist for multipleAccounts"request will be made.

            Documentation Link: https://developer.tdameritrade.com/watchlist/apis

            NAME: account
            DESC: The account number you wish to pull watchlists from. Default value is 'all'
            TYPE: String

            EXAMPLES:

            SessionObject.get_watchlist_accounts(account = 'all')
            SessionObject.get_watchlist_accounts(account = 'MyAccount1')

        '''

        #define the endpoint
        if account == 'all':
            endpoint = '/accounts/watchlists'
        else:
            endpoint = '/accounts/{}/watchlists'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the original headers we have stored.
        merged_headers = self.headers()

        #Make the request
        return requests.get(url = url, headers = merged_headers, verify = True).json()

    def get_watchlist(self, account = None, watchlist_id = None):

        '''
            Returns a specific watchlist for a specific account.

            Documentation Link: https://developer.tdameritrade.com/watchlist/apis/get/accounts/%7BaccountId%7D/watchlists/%7BwatchlistId%7D-0

            NAME: account
            DESC: The account number you wish to pull watchlists from
            TYPE: String

            NAME: watchlist_id
            DESC: The ID of the watchlist you wish to return.
            TYPE: String

            EXAMPLES:

            SessionObject.get_watchlist(account = 'MyAccount1', watchlist_id = 'MyWatchlistId')

        '''

        # define the endpoint
        endpoint = '/accounts/{}/watchlists/{}'.format(account, watchlist_id)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers()

        #make a request
        return requests.get(url = url, headers = merged_headers, verify = True).json()

    def delete_watchlist(self, account = None, watchlist_id = None):

        '''

            Deletes a specific watchlist for a specific account.

            Documentation Link: https://developer.tdameritrade.com/watchlist/apis/delete/accounts/%7BaccountId%7D/watchlist/%7BwatchlistId&7D-0

            NAME: account
            DESC: The account number you wish to delete the watchlist from.
            TYPE: String

            NAME: watchlist_id
            DESC: The ID of the watchlist you wish to delete.
            TYPE: String

            EXAMPLES:

            SessionObject.delete_watchlist(account = 'MyAccount1', watchlist_id = 'MyWatchlistId')

        '''

        #define the endpoint
        endpoint = '/accounts/{}/watchlists/{}'.format(account, watchlist_id)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the original headers we have stored.
        merged_headers = self.headers()

        #make teh request
        response = requests.delete(url = url, headers = merged_headers, verify = True)

        if response.status_code == 204:
            return "Watchlist {} was successfully deleted.".format(watchlist_id)
        else:
            return response.content



    def update_watchlist(self, account = None, watchlist_id = None, name_new = None, watchlistItems_to_add = None):

        '''

            Partially update watchlist for a sppecific account: change watchlis name, add the beggining/emd of a
            watchlist, update or delete items in a watchlist. This method does not verify that the symbol or asset
            type are valid.

            Documentation Link: https://developer.tdameritrade.com/watchlist/apis/patch/accounts/%7BaccountId%7D/watchlist/%7BwatchlistId%7D-0

            NAME: account
            DESC: The account number that containsteh watchlist you wich to update.
            TYPE: STring

            NAME: watchlist_id
            DESC: The ID of the watchlistyou wish to update
            TYPE: String

            NAME: watchlistItems
            DESC: A List of the original watchlist items you wish to update and their modified keys.
            TYPE: List<WatchListItems>

            EXAMPLES:

            Session.Object.update_watchlist(account = 'MyAccountNumber',
                                            watchlist_id = 'WatchListID',
                                            watchlistItems = [WatchListItem1, WatchListItem2])

        '''

        # define the payload
        payload = {"name": name_new, "watchlistItems": watchlistItems_to_add}

        #define the endpoint
        endpoint = '/accounts/{}/watchlists/{}'.format(account, watchlist_id)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make a request
        response = requests.patch(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)

        if response.status_code == 204:
            return "Watchlist {} was successfully updated.".format(watchlist_id)
        else:
            return response.content

    def replace_watchlist(self, account = None, watchlist_id = None, name_new = None, watchlistItems_new = None):

        '''

            Replace watchlist for a specific account. This method does not verify that teh symbol or asset type are valid.

            Documentation Link: https://developer.tdameritrade.com/watchlist/apis/put/accounts/%7BaccountId%7D/watchlists/%7BwatchlistId%7D-0

            NAME: account
            DESC: The account number that contains teh watchlist you wish to replace.
            TYPE: String

            NAME: watchlist_id
            DESC: The ID of the watchlist you wish to replace.
            TYPE: String

            NAME: name_new
            DESC: The name of teh new watchlist.
            TYPE: String

            NAME: watchlistItems_new
            DESC: The new watchlistitems you wish to add to teh watchlist.
            TYPE: List<WatchListItems>

            EXAMPLES:

            Session.Object.replace_watchlist(account = 'MyAccountNumber',
                                             watchlist_id = 'WatchListID',
                                             name_new = 'MyNewName',
                                             watchlistItems_new = [WatchListItem1, WatchListItem2])

        '''

        # define the payload
        payload = {"name": name_new, "watchlistItems": watchlistItems_new}

        # define the endpoint
        endpoint = '/accounts/{}/watchlists/{}'.format(account, watchlist_id)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab teh original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.put(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)
        if response.status_code == 204:
            return "Watchlist {} was successfully repleaced.".format(watchlist_id)
        else:
            return response.content

    '''#################################################
    #################### Orders ########################
    #################################################'''

    def get_orders_path(self, account = None, max_results = None, from_entered_time = None, to_entered_time = None, status = None):

        '''
            Returns the savedorders for a specific account.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/get/accounts/%7BaccountId%7D/orders-0

            NAME: account
            DESC: The account number that you want to query for orders.
            TYPE: String

            NAME: max_results
            DESC: The maximum nymber of orders to receive.
            TYPE: integer

            NAME: from_entered_time
            DESC: Specifies that no orders entered before this time should be returned. Valid ISO-8601 formats are :
                      yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz Date must be within 60 days from today's date. 'toEnteredTime' must also be set.
            TYPE: string

            NAME: to_entered_time
            DESC: Specifies that no orders entered after this time should be returned.Valid ISO-8601 formats are :
                      yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz. 'fromEnteredTime' must also be set.
            TYPE: String

            NAME: status
            DESC: Specifies that only orders of this status should be returned. Possible values are:

                    1. AWAITING_PARENT_ORDER
                    2. AWAITING_CONDITION
                    3. AWAITING_MANUAL_REVIEW
                    4. ACCEPTED
                    5. AWAITING_UR_NOT
                    6. PENDING_ACTIVATION
                    7. QUEUED
                    8. WORKING
                    9. REJECTED
                    10. PENDING_CANCEL
                    11. CANCELED
                    12. PENDING_REPLACE
                    13. REPLACED
                    14. FILLED
                    15. EXPIRED

            EXAMPLES:

            SessionObject.get_orders_path(account = 'MyAccountID', max_result = 6, from_entered_time = '2019-10-01', to_entered_tme = '2019-10-10)
            SessionObject.get_orders_path(account = 'MyAccountID', max_result = 6, status = 'EXPIRED')
            SessionObject.get_orders_path(account = 'MyAccountID', status ='REJECTED')
            SessionObject.get_orders_path(account = 'MyAccountID')

        '''

        # define the payload
        data = {"maxResults": max_results, "fromEnteredTime": from_entered_time, "toEnteredTime": to_entered_time, "status": status}

        #define the endpoint
        endpoint = '/accounts/{}/orders'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        return requests.get(url=url, headers = merged_headers, params = data, verify = True).json()


    def get_orders_query(self, account = None, max_results = None, from_entered_time = None, to_entered_time = None, status = None):

        '''
            All orders for a specific account or, if account ID isn't specified, orders will be returned for all linked accounts

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/get/orders-0

            NAME: account
            DESC: The account number that you want to query for orders.
            TYPE: String

            NAME: max_results
            DESC: The maximum nymber of orders to receive.
            TYPE: integer

            NAME: from_entered_time
            DESC: Specifies that no orders entered before this time should be returned.Valid ISO-8601 formats are :
                    yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:sszDate must be within 60 days from today's date. 'toEnteredTime' must also be set.
            TYPE: string

            NAME: to_entered_time
            DESC: Specifies that no orders entered after this time should be returned.Valid ISO-8601 formats are :
                    yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz. 'fromEnteredTime' must also be set.
            TYPE: String

            NAME: status
            DESC: Specifies that only orders of this status should be returned. Possible values are:

                    1. AWAITING_PARENT_ORDER
                    2. AWAITING_CONDITION
                    3. AWAITING_MANUAL_REVIEW
                    4. ACCEPTED
                    5. AWAITING_UR_NOT
                    6. PENDING_ACTIVATION
                    7. QUEUED
                    8. WORKING
                    9. REJECTED
                    10. PENDING_CANCEL
                    11. CANCELED
                    12. PENDING_REPLACE
                    13. REPLACED
                    14. FILLED
                    15. EXPIRED

            EXAMPLES:

            SessionObject.get_orders_query(account = 'MyAccountID', max_result = 6, from_entered_time = '2019-10-01', to_entered_tme = '2019-10-10)
            SessionObject.get_orders_query(account = 'MyAccountID', max_result = 6, status = 'EXPIRED')
            SessionObject.get_orders_query(account = 'MyAccountID', status ='REJECTED')
            SessionObject.get_orders_query(account = 'MyAccountID')

        '''
        # define the payload
        data = {"accountId":account,
                "maxResults": max_results,
                "fromEnteredTime": from_entered_time,
                "toEnteredTime": to_entered_time,
                "status": status}

        # define teh endpoint
        endpoint = '/orders'

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        return requests.get(url=url, headers = merged_headers, params = data, verify = True).json()


    def get_order(self, account = None, order_id = None):

        '''
            Get a specific order for a specific account.

            Documentation Link: https://developers.tdameritrade.com/account-access/apis/get/orders-a

            NAME: account
            DESC: The accountnumber that you want to queary the order for.
            TYPE: String

            NAME: order_id
            DESC: The order id.
            TYPE: String

            EXA<PLES:

            Session.Object.get_order(account = 'MyAccountID', order_id_ 'MyOrderID')

        '''

        #define the endpoint
        endpoint = '/accounts/{}/orders/{}'.format(account, order_id)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        return requests.get(url=url, headers = merged_headers, verify = True).json()

    def cancel_order(self, account = None, order_id = None):

        '''
            Cancel specific order for a specific account.

            Documentation Link: https://developers.tdameritrade.com/account-access/apis/delete/accounts/%7BaccountId%7D/orders/%7BporderID%7D-0

            NAME: account
            DESC: The accountnumber that you want to queary the order for.
            TYPE: String

            NAME: order_id
            DESC: The order id.
            TYPE: String

            EXAMPLES:

            Session.Object.cancel_order(account = 'MyAccountID', order_id_ 'MyOrderID')

        '''

        #define the endpoint
        endpoint = '/accounts/{}/orders/{}'.format(account, order_id)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        response = requests.delete(url=url, headers = merged_headers, verify = True)

        if response.status_code == 200:
            return "Order {} was successfully CANCELED.".format(order_id)
        else:
            return response.content


    def create_order(self, account = None, symbol = None, price = None, quantity = '0', instruction = None, assetType = None,
                     orderType = 'MARKET', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE'):

        '''
            Create order for specific account. This method does not verify that the symbol or assets type are valid.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/post/accounts/%7BaccountId%7D/orders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: symbol
            DESC: Symbol to operate with.
            TYPE: String

            NAME: price
            DESC: price level for the order. If orderType is Market leave it in None
            TYPE: String

            NAME: quantity
            DESC: amount of shares to operate
            TYPE: String

            NAME: intruction
            DESC: "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or
                   'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'"
            TYPE: String

            NAME: assetType
            DESC: "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            TYPE: String

            NAME: orderType
            DESC: "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or
                   'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'"
            TYPE: String

            NAME: session
            DESC: "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'"
            TYPE: String

            NAME: duration
            DESC: "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'"
            TYPE: String

            NAME: orderStrategyType
            DESC: "'SINGLE' or 'OCO' or 'TRIGGER'"
            TYPE: String


            EXAMPLES:

            SessionObject.create_order(account = 'MyaccountNumber' symbol = 'MELI', price = '100.00', quantity = '100', instruction = 'BUY',
                                       assetType = 'EQUITY', orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

        '''

        #define the payload
        payload = {'orderType':orderType,
                   'session':session,
                   'price': price,
                   'duration':duration,
                   'orderStrategyType':orderStrategyType,
                   'orderLegCollection':[
                                         {'instruction':instruction,
                                          'quantity':quantity,
                                          'instrument':{'symbol':symbol,
                                                        'assetType':assetType
                                                       }
                                         }
                                        ]
                  }

        # define the endpoint
        endpoint = '/accounts/{}/orders'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.post(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)

        if response.status_code == 201:
            return "New {} order was successfully created.".format(symbol)
        else:
            return response.content


    def replace_order(self, account = None, order_Id = None, symbol = None, price = None, quantity = 0, instruction = None, assetType = None,
                     orderType = 'MARKET', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE'):

        '''
            Replace an existing order for an account. The existing order will be replaced by the new order. Once replaced,
            the old order will be canceled and a new order will be created.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/put/accounts/%7BaccountId%7D/orders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: order_Id
            DESC: Order to be replaced
            TYPE: String

            NAME: symbol
            DESC: Symbol to operate with.
            TYPE: String

            NAME: price
            DESC: price level for the order. If orderType is Market leave it in None
            TYPE: String

            NAME: quantity
            DESC: amount of shares to operate
            TYPE: String

            NAME: intruction
            DESC: "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or
                   'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'"
            TYPE: String

            NAME: assetType
            DESC: "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            TYPE: String

            NAME: orderType
            DESC: "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or
                   'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'"
            TYPE: String

            NAME: session
            DESC: "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'"
            TYPE: String

            NAME: duration
            DESC: "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'"
            TYPE: String

            NAME: orderStrategyType
            DESC: "'SINGLE' or 'OCO' or 'TRIGGER'"
            TYPE: String


            EXAMPLES:

            SessionObject.replace_order(account = 'MyAccountNumber', order_Id = 'MyOrderID', symbol = 'MELI', price = '101.00', quantity = '50', instruction = 'BUY',
                                        assetType = 'EQUITY', orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

        '''

        #define the payload
        payload = {'orderType':orderType,
                   'session':session,
                   'price': price,
                   'duration':duration,
                   'orderStrategyType':orderStrategyType,
                   'orderLegCollection':[
                                         {'instruction':instruction,
                                          'quantity':quantity,
                                          'instrument':{'symbol':symbol,
                                                        'assetType':assetType
                                                       }
                                         }
                                        ]
                  }

        # define the endpoint
        endpoint = '/accounts/{}/orders/{}'.format(account,order_Id)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.put(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)

        if response.status_code == 201:
            return "Order {} was successfully replaced.".format(order_Id)
        else:
            return response.content

    '''#################################################
    ################Saved Orders ######################
    #################################################'''
    #If you have Advance Features Eneabled fot Thinkorswim, API will not be able to handle them.

    def get_savedorders_path(self, account = None, max_results = None, from_entered_time = None, to_entered_time = None, status = None):

        '''
            Returns the savedorders for a specific account.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/get/accounts/%7BaccountId%7D/orders-0

            NAME: account
            DESC: The account number that you want to query for orders.
            TYPE: String

            NAME: max_results
            DESC: The maximum nymber of orders to receive.
            TYPE: integer

            NAME: from_entered_time
            DESC: Specifies that no orders entered before this time should be returned. Valid ISO-8601 formats are:
                  yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz. 'to_entered_time'
                  must alse be set.
            TYPE: string

            NAME: to_entered_time
            DESC: Specifies that no orders entered after this time should be returned. Valid ISO-8601 formats are:
                  yyyy-MM-dd and yyyy-MM-dd'T'HH:mm:ssz. 'from_entered_time' must alse be set.
            TYPE: String

            NAME: status
            DESC: Specifies that only orders of this status should be returned. Possible values are:

                    1. AWAITING_PARENT_ORDER
                    2. AWAITING_CONDITION
                    3. AWAITING_MANUAL_REVIEW
                    4. ACCEPTED
                    5. AWAITING_UR_NOT
                    6. PENDING_ACTIVATION
                    7. QUEUED
                    8. WORKING
                    9. REJECTED
                    10. PENDING_CANCEL
                    11. CANCELED
                    12. PENDING_REPLACE
                    13. REPLACED
                    14. FILLED
                    15. EXPIRED

            EXAMPLES:

            SessionObject.get_savedorders_path(account = 'MyAccountID', max_result = 6, from_entered_time = '2019-10-01', to_entered_tme = '2019-10-10)
            SessionObject.get_savedorders_path(account = 'MyAccountID', max_result = 6, status = 'EXPIRED')
            SessionObject.get_savedorders_path(account = 'MyAccountID', status ='REJECTED')
            SessionObject.get_savedorders_path(account = 'MyAccountID')

        '''

        # define the payload
        data = {"maxResults": max_results, "fromEnteredTime": from_entered_time, "toEnteredTime": to_entered_time, "status": status}

        #define the endpoint
        endpoint = '/accounts/{}/savedorders'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        return requests.get(url=url, headers = merged_headers, params = data, verify = True).json()

    def get_savedorder(self, account = None, savedorder_id = None):

        '''
            All orders for a specific account or, if account ID isn't specified, orders will be returned for all linked accounts

            Documentation Link: https://developers.tdameritrade.com/account-access/apis/get/orders-a

            NAME: account
            DESC: The accountnumber that you want to queary the order for.
            TYPE: String

            NAME: order_id
            DESC: The savedorder id.
            TYPE: integer

            EXAMPLES:

            Session.Object.get_savedorder(account = 'MyAccountID', order_id_ 'MysavedOrderID')

        '''

        #define the endpoint
        endpoint = '/accounts/{}/savedorders/{}'.format(account, savedorder_id)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        return requests.get(url=url, headers = merged_headers, verify = True).json()

    def cancel_savedorder(self, account = None, savedorder_id = None):

        '''
            Cancel specific order for a specific account.

            Documentation Link: https://developers.tdameritrade.com/account-access/apis/delete/accounts/%7BaccountId%7D/orders/%7BporderID%7D-0

            NAME: account
            DESC: The accountnumber that you want to queary the order for.
            TYPE: String

            NAME: order_id
            DESC: The savedorder id.
            TYPE: integer

            EXA<PLES:

            Session.Object.cancel_savedorder(account = 'MyAccountID', order_id_ 'MysavedOrderID')

        '''

        #define the endpoint
        endpoint = '/accounts/{}/savedorders/{}'.format(account, savedorder_id)

        #build the url
        url = self.api_endpoint(endpoint)

        # grab the originbal headers we have stored.
        merged_headers =self.headers()

        #make the request
        response = requests.delete(url=url, headers = merged_headers, verify = True)

        if response.status_code == 200:
            return "SavedOrder {} was successfully CANCELED.".format(savedorder_id)
        else:
            return response.content


    def create_savedorder(self, account = None, symbol = None, price = None, quantity = 0, instruction = None, assetType = None,
                     orderType = 'MARKET', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE'):

        '''
            Create order for specific account. This method does not verify that the symbol or assets type are valid.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/post/accounts/%7BaccountId%7D/savedorders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: symbol
            DESC: Symbol to operate with.
            TYPE: String

            NAME: price
            DESC: price level for the order. If orderType is Market leave it in None
            TYPE: String

            NAME: quantity
            DESC: amount of shares to operate
            TYPE: String

            NAME: intruction
            DESC: "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or
                   'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'"
            TYPE: String

            NAME: assetType
            DESC: "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            TYPE: String

            NAME: orderType
            DESC: "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or
                   'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'"
            TYPE: String

            NAME: session
            DESC: "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'"
            TYPE: String

            NAME: duration
            DESC: "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'"
            TYPE: String

            NAME: orderStrategyType
            DESC: "'SINGLE' or 'OCO' or 'TRIGGER'"
            TYPE: String


            EXAMPLES:

            SessionObject.create_savedorder(account = 'MyaccountNumber' symbol = 'MELI', price = '100.00', quantity = '100', instruction = 'BUY',
                                            assetType = 'EQUITY', orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

        '''

        #define the payload
        payload = {'orderType':orderType,
                   'session':session,
                   'price': price,
                   'duration':duration,
                   'orderStrategyType':orderStrategyType,
                   'orderLegCollection':[
                                         {'instruction':instruction,
                                          'quantity':quantity,
                                          'instrument':{'symbol':symbol,
                                                        'assetType':assetType
                                                       }
                                         }
                                        ]
                  }

        # define the endpoint
        endpoint = '/accounts/{}/savedorders'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.post(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)

        if response.status_code == 201:
            return "SavedOrder {} was successfully created.".format(symbol)
        else:
            return response.content

    def replace_savedorder(self, account = None, savedorder_Id = None, symbol = None, price = None, quantity = 0, instruction = None, assetType = None,
                     orderType = 'MARKET', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE'):

        '''
            Replace an existing savedorder for an account. The existing savedorder will be replaced by the new savedorder. Once replaced,
            the old order will be canceled and a new order will be created.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/put/accounts/%7BaccountId%7D/savedorders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: order_Id
            DESC: Order to be replaced
            TYPE: String

            NAME: symbol
            DESC: Symbol to operate with.
            TYPE: String

            NAME: price
            DESC: price level for the order. If orderType is Market leave it in None
            TYPE: String

            NAME: quantity
            DESC: amount of shares to operate
            TYPE: String

            NAME: intruction
            DESC: "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or
                   'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'"
            TYPE: String

            NAME: assetType
            DESC: "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
            TYPE: String

            NAME: orderType
            DESC: "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or
                   'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'"
            TYPE: String

            NAME: session
            DESC: "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'"
            TYPE: String

            NAME: duration
            DESC: "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'"
            TYPE: String

            NAME: orderStrategyType
            DESC: "'SINGLE' or 'OCO' or 'TRIGGER'"
            TYPE: String


            EXAMPLES:

            SessionObject.replace_savedorder(account = 'MyAccountNumber', order_Id = 'MyOrderID', symbol = 'MELI', price = '101.00', quantity = '50', instruction = 'BUY',
                                        assetType = 'EQUITY', orderType = 'LIMIT', session = 'NORMAL', duration = 'DAY', orderStrategyType = 'SINGLE')

        '''

        #define the payload
        payload = {'orderType':orderType,
                   'session':session,
                   'price': price,
                   'duration':duration,
                   'orderStrategyType':orderStrategyType,
                   'orderLegCollection':[
                                         {'instruction':instruction,
                                          'quantity':quantity,
                                          'instrument':{'symbol':symbol,
                                                        'assetType':assetType
                                                       }
                                         }
                                        ]
                  }

        # define the endpoint
        endpoint = '/accounts/{}/savedorders/{}'.format(account,savedorder_Id)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.put(url = url, headers = merged_headers, data = json.dumps(payload), verify = True)

        if response.status_code == 201:
            return "SavedOrder {} was successfully replaced.".format(savedorder_Id)
        else:
            return response.content

        '''#####################################################
        ################# Custom Orders ########################
        ####################################################'''

    def create_custom_order(self, account = None, order = None):

        '''
            Create order for specific account. This method does not verify that the symbol or assets type are valid.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/post/accounts/%7BaccountId%7D/orders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: order
            DESC: order payload externally prepared.
            TYPE: json type order

            EXAMPLE:
                SessionObject.create_custom_order(account = 'MyaccountNumber', order = order_1)
        '''

        # define the endpoint
        endpoint = '/accounts/{}/orders'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.post(url = url, headers = merged_headers, data = json.dumps(order), verify = True)

        if response.status_code == 201:
            return "New costumed order was successfully created."
        else:
            return response.content

    def replace_custom_order(self, account = None, order_Id = None, order = None):

        '''
            Create order for specific account. This method does not verify that the symbol or assets type are valid.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/post/accounts/%7BaccountId%7D/orders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: order_Id
            DESC: Order to be replaced
            TYPE: String

            NAME: order
            DESC: order payload externally prepared.
            TYPE: json type order

            EXAMPLE:

                SessionObject.replace_custom_order(account = 'MyaccountNumber', order_Id = None, order = order_1)
        '''


        # define the endpoint
        endpoint = '/accounts/{}/orders/{}'.format(account,order_Id)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.put(url = url, headers = merged_headers, data = json.dumps(order), verify = True)

        if response.status_code == 201:
            return "Order {} was successfully replaced.".format(order_Id)
        else:
            return response.content

    def create_custom_savedorder(self, account = None, savedorder = None):

        '''
            Create order for specific account. This method does not verify that the symbol or assets type are valid.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/post/accounts/%7BaccountId%7D/orders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: order
            DESC: order payload externally prepared.
            TYPE: json type order

            EXAMPLE:
                SessionObject.create_custom_savedorder(account = 'MyaccountNumber', order = order_1)
        '''

        # define the endpoint
        endpoint = '/accounts/{}/savedorders'.format(account)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.post(url = url, headers = merged_headers, data = json.dumps(savedorder), verify = True)

        if response.status_code == 201:
            return "New costumed savedorder was successfully created."
        else:
            return response.content

    def replace_custom_savedorder(self, account = None, savedorder_Id = None, order = None):

        '''
            Create order for specific account. This method does not verify that the symbol or assets type are valid.

            Documentation Link: https://developer.tdameritrade.com/account-access/apis/post/accounts/%7BaccountId%7D/orders/%7BorderId%7D-0

            NAME: account
            DESC: The account number you wish to create the watchlist for.
            TYPE: String

            NAME: savedorder_Id
            DESC: Order to be replaced
            TYPE: String

            NAME: order
            DESC: order payload externally prepared.
            TYPE: json type order

            EXAMPLE:
                SessionObject.replace_custom_savedorder(account = 'MyaccountNumber', order_Id = None, order = order_1)
        '''


        # define the endpoint
        endpoint = '/accounts/{}/savedorders/{}'.format(account,savedorder_Id)

        #build the url
        url = self.api_endpoint(endpoint)

        #grab the original headers we have stored.
        merged_headers = self.headers(mode = 'application/json')

        #make the request
        response = requests.put(url = url, headers = merged_headers, data = json.dumps(order), verify = True)

        if response.status_code == 201:
            return "Savedorder {} was successfully replaced.".format(savedorder_Id)
        else:
            return response.content