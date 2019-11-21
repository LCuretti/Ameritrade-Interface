# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 11:19:59 2019

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
"""

import urllib
import json
#import dateutil.parser
from datetime import datetime
import time
import socket

import pyodbc
import websocket
from threading import Thread

from TDAPI import TDAPI

class TDStreamer():
    '''
         TD Ameritrade API Class.
        
        Performs subscription request to the TD Ameritrade.
 
        id	service              	command        	     parameters	                                       	       fields	                  Response Type
        0	ADMIN	                LOGIN       	     credential, token, version			                                                  response
        1	                        LOGOUT	             None			                                                                      response
        2		                    QOS      	         "qoslevel": "0","1","2","3","4","5"       		                                      response
        3	ACCT_ACTIVITY	        SUBS/UNSUBS     	streamkeys		                                           0,1,2,3                    data
        4	ACTIVES_NASDAQ        	SUBS/ADD/UNSUBS    	"NASDAQ" - "60","300","600","1800","3600","ALL"    	       0,1                        data
        5	ACTIVES_NYSE          	SUBS/ADD/UNSUBS    	"NYSE" - "60","300","600","1800","3600","ALL"      	       0,1                        data
        6	ACTIVES_OTCBB         	SUBS/ADD/UNSUBS    	"OTCBB" - "60","300","600","1800","3600","ALL"     	       0,1                        data
        7	ACTIVES_OPTIONS       	SUBS/ADD/UNSUBS    	"CALLS*","OPTS*","PUTS*","CALLS-DESC*", 	               0,1                        data
                                                        "OPTS-DESC*","PUTS-DESC*"(*options)
                                                        - "60","300","600","1800","3600","ALL"                               
        8	CHART_EQUITY          	SUBS/ADD/UNSUBS    	keys = symbols                                 		       0,1,2,..,8                 data
        9	CHART_FUTURES         	SUBS/ADD/UNSUBS    	keys = future symbol as a product (ie. /ES)                0,1,2,..,6	              data
        10	CHART_OPTIONS          	SUBS/ADD/UNSUBS  	keys = symbols (ie. SPY_111819C300)		                   0,1,2,..,6                 data
        11	QUOTE                	SUBS/ADD/UNSUBS    	keys = symbols                                             0,1,2,…,52                 data
        12	OPTION               	SUBS/ADD/UNSUBS    	keys = symbols (ie. SPY_111819C300)                        0,1,2,..,41                data
        13	LISTED_BOOK          	SUBS/ADD/UNSUBS    	keys = symbols	                                           0,1,2,3                    data
        14	NASDAQ_BOOK          	SUBS/ADD/UNSUBS    	keys = symbols                                             0,1,2,3                    data
        15	OPTIONS_BOOK         	SUBS/ADD/UNSUBS    	keys = symbols (ie. SPY_111819C300)	                       0,1,2,3                    data
        16	LEVELONE_FUTURES       	SUBS/ADD/UNSUBS  	keys = future symbol as a product (ie. /ES)                0,1,2,..,35                data
        17	LEVELONE_FOREX       	SUBS/ADD/UNSUBS    	keys = FOREX symbols (ie.. EUR/USD)                        0,1,2,..,28                data
        18	TIMESALE_EQUITY      	SUBS/ADD/UNSUBS    	keys = symbols                                         	   0,1,2,3,4                  data
        19	TIMESALE_FUTURES	    SUBS/ADD/UNSUBS    	keys = future symbol as a product (ie. /ES)         	   0,1,2,3,4                  data
        20	TIMESALE_OPTIONS     	SUBS/ADD/UNSUBS    	keys = symbols (ie. SPY_111819C300)	                       0,1,2,3,4                  data
        21	NEWS_HEADLINE        	SUBS/ADD/UNSUBS    	keys = symbols                                      	   0,1,2,..,10                data
        22	NEWS_HEADLINELIST    	GET                	keys = symbols                                         	   None                       snapshot
        23	NEWS_STORY           	GET                	story_id (ie. SN20191111010526)                        	   None                       snapshot
        24	CHART_HISTORY_FUTURES	GET                	symbols, frequency: "m1","m5","m10","m30","h1","d1","w1","n1",
                                                        perdiod: "d5","w4","n10","y1","y10", sT, eT		           None                       snapshot
        25	FOREX_BOOK           	SUBS               	Service not available or temporary down.
        26	FUTURES_BOOK         	SUBS               	Service not available or temporary down.		
        27	LEVELONE_FUTURES_OPTIONS SUBS            	Service not available or temporary down.
        28	FUTURES_OPTIONS_BOOK	SUBS            	Not managed
        29	TIMESALE_FOREX       	SUBS               	Not managed
        30	LEVELTWO_FUTURES       	SUBS             	Not managed			
        31	STREAMER_SERVER	                            Not managed

    '''
  
    def __init__(self, client_id, redirect_uri, account_id):
        '''
            Open API object in order to get credentials, url necessary for streaming login
        '''
            
        self.cnxn = None
        self.crsr = None
        self.LoggedIn = False   # To check the status before send subscription request
        self.started = False    # To allow Request iniciate the Login proceses if not started yet
        self.UserLogoff = False # To avoid the Keep alive function Login back when user logged off.
        self.last_message_time = 0
        self.sleep = 2
        
        self.subs = []          # to store subscription in order to resubscribe in the keepalive function
        
        self.notify = []        # Store notify responses (Hearbeats)
        self.response = []      # Store Response of subscription. Success or not
        self.snapshot = []      # Data from the Get requests
        self.subs_data = []     # Data from subscription.
        
        
        '''
            The following part create an object TDAPI in order to get the: "streamerSubscriptionKeys" for ACCT_ACTIVITY method (Account activity subscription),
                                                                           "streamerConnectionInfo" to get the connection URL, and credential for LogIn.
            You may use other than TDAPI api to get those values.
        '''

        self.TDAPI = TDAPI(client_id, redirect_uri, account_id)
        userPrincipalsResponse = self.TDAPI.get_user_principals(fields = ['streamerSubscriptionKeys', 'streamerConnectionInfo'])

        # we need to get the timestamp in order to make our next request, but it needs to be parsed
        epoch = datetime.utcfromtimestamp(0)
        tokenTimeStamp = datetime.strptime(userPrincipalsResponse['streamerInfo']['tokenTimestamp'], "%Y-%m-%dT%H:%M:%S+0000")
        tokenTimeStampAsMs = (tokenTimeStamp - epoch).total_seconds() * 1000
        
        # we need to define our credentials that we will need to make our stream
        self.credentials = {"userid": userPrincipalsResponse['accounts'][0]['accountId'],
                            "token": userPrincipalsResponse['streamerInfo']['token'],
                            "company": userPrincipalsResponse['accounts'][0]['company'],
                            "segment": userPrincipalsResponse['accounts'][0]['segment'],
                            "cddomain": userPrincipalsResponse['accounts'][0]['accountCdDomainId'],
                            "usergroup": userPrincipalsResponse['streamerInfo']['userGroup'],
                            "accesslevel":userPrincipalsResponse['streamerInfo']['accessLevel'],
                            "authorized": "Y",
                            "timestamp": int(tokenTimeStampAsMs),
                            "appid": userPrincipalsResponse['streamerInfo']['appId'],
                            "acl": userPrincipalsResponse['streamerInfo']['acl'] }
        
        self.streamerSubscriptionKey = userPrincipalsResponse['streamerSubscriptionKeys']['keys'][0]['key']
        self.uri = "wss://" + userPrincipalsResponse['streamerInfo']['streamerSocketUrl'] + "/ws"
        
    def __repr__(self):
        '''
            defines the string representation of our TD Ameritrade Class instance.
        '''

        # define the string representation
        
        return 'Stream object connected: {}'.format(self.LoggedIn)




    def is_connected(self):
        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            pass
        return False

    def start_streamer(self):
        self.started = True
        self.UserLogoff = False
        while not self.LoggedIn:
            #connect the SQL database
            self.database_connect()
            #connect websocket
            self.connect()
            #start connection
            self.ws.on_open = self.on_open
            #prepare a thread to have streaming forever while allow to send other commands
            self.ws_thread = Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            #start thread
            self.ws_thread.start()
            time.sleep(self.sleep)
            #self.sleep = int(self.sleep * 5)
        else:
            print("Streamer already started")
    
   
    def database_connect(self):
        
        # define the server and the database, YOU WILL NEED TO CHANGE THIS TO YOUR OWN DATABASE AND SERVER
        server = 'DELL-ULT\SQLEXPRESS' 
        database = 'stock_database'  
        sql_driver = '{ODBC Driver 17 for SQL Server}'

        # define our connection, autocommit MUST BE SET TO TRUE, also we can edit data.
        self.cnxn = pyodbc.connect('DRIVER=' + sql_driver +'; \
                                    SERVER=' + server +'; \
                                    DATABASE=' + database +';\
                                    Trusted_Connection=yes;')

        self.crsr = self.cnxn.cursor()
        
    def database_insert(self, query, data_tuple):   
        
        # execute the query, commit the changes, and close the connection
        self.crsr.execute(query, data_tuple)
        self.cnxn.commit()
        #self.cnxn.close()
        
        #print('Data has been successfully inserted into the database.')

    def connect(self):
        
        #Prepare the websocket and method to be call on each kind of event.
        #uri is stored when init the class.
        websocket.enableTrace(True) #True to see the sending message
        self.ws = websocket.WebSocketApp(self.uri,
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)

    def on_open(self):   
         
        #when connection is open send the logging request
        self.login_request()
        
    def on_error(self, error):
        print('Error: ' + str(error)) 
       
    def on_close(self):
        self.started = False
        self.LoggedIn = False
        print("### closed at: {} local time ###".format(datetime.now()))
        if self.UserLogoff == True: #if user logged off
        #when connection is close, it closes SQL connection as well.   
            self.crsr.close()
            self.cnxn.close()
        else:
            #pass
            self.keep_alive()
            
   
    def keep_alive(self):
        print('keep#########################################')
        internet = self.is_connected()
        while not internet:       
            internet = self.is_connected()
            time.sleep(self.sleep)

        self.start_streamer()
        
        subscriptions = self.subs
        self.subs = []
        for subs in subscriptions:
            self.subs_request(subs)
            
    def on_message(self, message):
        #handle the messages it receives
        
        self.last_message_time = datetime.now()      
        message = json.loads(message,strict=False)
        
        #print(message)  
        if 'notify' in message:
           self.notify.append(message)
           if 'heartbeat' in message['notify'][0]:
               print("Heartbeat at: "+ str(datetime.fromtimestamp(int(message['notify'][0]['heartbeat'])/1000)))  
           else:
               print(message)
           
        elif 'response' in message:
            #the first response is the login answer, if it ok set the LoggedIn to True
            if (message['response'][0]['service'] == 'ADMIN') and (message['response'][0]['content']['code'] == 0):
                self.LoggedIn = True

            self.response.append(message) 
            print(message)
        ### DATA HANDLE AND STORADGE IN SQL PART ###############################################################################################

        elif 'snapshot' in message:
            # snapshot from Get services
            self.snapshot.append(message)
 
        
        elif 'data' in message:
            self.subs_data.append(message)

            ''' This part dumps all services in a single SQL table. All content keeps JSON format and can be query on SQL '''

# =============================================================================
#             for i in range(0,len(message['data'])):
#                 data = message['data'][i]             
#                 insert_query = "INSERT INTO td_service_data2 (service, timestamp, symbol, content) VALUES (?,?,?,?);"
#
#                 for j in range(0, len(data['content'])):
#                     
#                     data_tuple = (data['service'], str(data['timestamp']), data['content'][j]['key'], json.dumps(data['content'][j]))
#                     self.database_insert(insert_query, data_tuple)
# =============================================================================

            ''' The part below segregate data on specifics tables with time adjusted (3600), and whatever left get stored in a single Table '''
            
            for i in range(0,len(message['data'])):
                data = message['data'][i]
                for j in range(0, len(data['content'])):
                
                    
                    if message['data'][i]['service'] == 'ACCT_ACTIVITY':
                        insert_query = "INSERT INTO td_account_activity (service, timestamp, content) VALUES (?,?,?);" 
                        data_tuple = (data['service'], str(data['timestamp']), json.dumps(data['content'][j]))
                        self.database_insert(insert_query, data_tuple)
                    
                    
                    elif message['data'][i]['service'] == 'TIMESALE_EQUITY':
                   
                        insert_query = '''INSERT INTO td_Time_Sales_Equity (DateTime, Ticker, Sequence, Price, Size, LastSequence) VALUES (?,?,?,?,?,?);'''
                        data_tuple = (datetime.fromtimestamp((data['content'][j]['1']/1000)-3600), data['content'][j]['key'], data['content'][j]['seq'], data['content'][j]['2'], data['content'][j]['3'], data['content'][j]['4'])    
                        self.database_insert(insert_query, data_tuple)
               
                    elif message['data'][i]['service'] == 'CHART_EQUITY':
    
                        insert_query = '''INSERT INTO td_price_data_equity (DateTime, Ticker, Sequence, open_price, high, low ,close_price, volume, LastSequence, ChartDay) VALUES (?,?,?,?,?,?,?,?,?,?);'''
                        data_tuple = (datetime.fromtimestamp((data['content'][j]['7']/1000)-3600), data['content'][j]['key'], data['content'][j]['seq'], data['content'][j]['1'], data['content'][j]['2'], data['content'][j]['3'], data['content'][j]['4'], data['content'][j]['5'], data['content'][j]['6'], data['content'][j]['8'])    
                        self.database_insert(insert_query, data_tuple)
                      
                    elif message['data'][i]['service'] == 'NASDAQ_BOOK':
                       
                        insert_query = '''INSERT INTO td_level2_Nasdaq (DateTime, Ticker, [Bid/Ask], Price, Size, Num_Orders, Orders) VALUES (?,?,?,?,?,?,?);'''

                        for k in range(0, len(data['content'][j]['2'])):
                       
                            data_tuple = (datetime.fromtimestamp((data['content'][j]['1']/1000)-3600), data['content'][j]['key'], 'Bid', data['content'][j]['2'][k]['0'], data['content'][j]['2'][k]['1'], data['content'][j]['2'][k]['2'],json.dumps(data['content'][j]['2'][k]['3']))      
                            self.database_insert(insert_query, data_tuple)
                           
                        for k in range(0, len(data['content'][j]['3'])):   
                           
                            data_tuple = (datetime.fromtimestamp((data['content'][j]['1']/1000)-3600), data['content'][j]['key'], 'Ask', data['content'][j]['3'][k]['0'], data['content'][j]['3'][k]['1'], data['content'][j]['3'][k]['2'],json.dumps(data['content'][j]['3'][k]['3']))  
                            self.database_insert(insert_query, data_tuple)
                            
                    else: #Actives, Account Activity, Levelone, Quote, Option   
                        insert_query = "INSERT INTO td_service_data (service, timestamp, symbol, content) VALUES (?,?,?,?);"                       
                        data_tuple = (data['service'], str(data['timestamp']), data['content'][j]['key'], json.dumps(data['content'][j]))
                        self.database_insert(insert_query, data_tuple)


  

    '''****************************************
    ********** Request Methods ****************
    ****************************************'''

    def login_request(self):
        '''
            When WebSocket connection is opened, the first command to the Streamer Server must be a LOGIN command. 
        '''

        login_request = {"requests": [{"service": "ADMIN",
                                       "requestid": "0",  
                                       "command": "LOGIN",
                                       "account": self.credentials['userid'],
                                       "source": self.credentials['appid'],
                                       "parameters": {"credential": urllib.parse.urlencode(self.credentials),
                                                      "token": self.credentials['token'],
                                                      "version": "1.0"}}]}
            
        try:
            self.ws.send(json.dumps(login_request))

        except Exception as e:
            self.started = False
            print(str(e)) 


    def logout_request(self):

        '''
            Logout closes the WebSocket Session and cleans up all subscription for the client session.
            It’s a good practice to logout when closing the client tool.
        '''     

        subs_request = {"requests": [{"service": "ADMIN",
                                       "requestid": "1",
                                       "command": "LOGOUT",
                                       "account": self.credentials['userid'],
                                       "source": self.credentials['appid'],
                                       "parameters": {}}]}
            
        if self.LoggedIn == True:
            self.UserLogoff = True
            self.subs = []      
            self.data_request(subs_request)
        
        else:
            print("Already Logged Out")


    def subs_request(self, subscription):
        #Method for subscription handler
        
        self.subs = self.subs + [subscription]
        
        
        subs_request= {
                        "requests": [
                                    {
                                    "service": subscription[0], 
                                    "requestid": subscription[1], 
                                    "command": subscription[2], 
                                    "account": self.credentials['userid'], 
                                    "source": self.credentials['appid'], 
                                    "parameters": {
                                                    "keys": subscription[3], 
                                                    "fields": subscription[4]
                                                  }
                                    }
                                    ]
                      }
        
        
        
        self.data_request(subs_request)    
    
    def data_request(self, data_request):
        # Method for request handler. Thsi method is teh one that make the actual requests to WebSocket
        
        if self.started == False:
            self.start_streamer()
            
        #print(data_request)           
        self.ws.send(json.dumps(data_request))    


    def QOS_request(self, qoslevel = '2'):

        '''
            Quality of Service provides the different rates of data updates per protocol (binary, websocket etc), or per user based.
            
            0 = Express (500 ms)
            1 = Real-Time (750 ms) ß default value for http binary protocol      
            2 = Fast (1,000 ms)  ßdefault value for websocket and http asynchronous protocol          
            3 = Moderate (1,500 ms)  
            4 = Slow (3,000 ms)          
            5 = Delayed (5,000 ms)
        '''        

        subs_request = {"requests": [{"service": "ADMIN",
                                       "requestid": "2",
                                       "command": "QOS",
                                       "account": self.credentials['userid'],
                                       "source": self.credentials['appid'],
                                       "parameters": {"qoslevel": qoslevel}}]}
            
        self.data_request(subs_request)


    '''***************************************
    ********* GET Requests ******************
    ***************************************'''

    def data_request_news_headlinelist(self, keys = 'SPY'):
        
        '''
          
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
            
            Snapshot fields:
                            1	??
                            2	list amount
                            3	list
                            key	symbol

            EXAMPLES:      
            SessionObject.data_request_news_headlinelist(keys = 'SPY')               
        '''
                
        
        data_request= {
                        "requests": [
                                    {
                                    "service": "NEWS_HEADLINELIST", 
                                    "requestid": "22", 
                                    "command": 'GET', 
                                    "account": self.credentials['userid'], 
                                    "source": self.credentials['appid'], 
                                    "parameters": {
                                                    "keys": keys, 
                                                  }
                                    }
                                    ]
                      }
            
        self.data_request(data_request) 

    def data_request_news_story(self, keys):
        
        '''
             
            NAME: keys
            DESC: StoryID
            TYPE: String
                
            Snapshot fields: 
                            1	??
                            2	timestamp
                            3	story_id
                            4	??
                            5	story_id
                            6	Story
                            7	source
                            keys	story_id

            EXAMPLES:      
            SessionObject.data_request_news_story(keys = 'SN20191111010526')               
        '''
                
        
        data_request= {
                        "requests": [
                                    {
                                    "service": "NEWS_STORY", 
                                    "requestid": "23", 
                                    "command": 'GET', 
                                    "account": self.credentials['userid'], 
                                    "source": self.credentials['appid'], 
                                    "parameters": {
                                                    "keys": keys, 
                                                  }
                                    }
                                    ]
                      }
            
        self.data_request(data_request)   

    def data_request_chart_history_futures(self, symbol = '/ES', frequency = 'm5', period = 'd5', start_time = None, end_time = None):
        
        '''
            Chart history for equities is available via requests to the MDMS services.  Only Futures chart history is available via Streamer Server.
                                            
            NAME: symbol
            DESC: Symbols in upper case and separated by commas
            TYPE: String
            
            NAME: frequency
            DESC: Sample Size of the candle: Fixed frequency choices:
                                                                    m1, m5, m10, m30, h1, d1, w1, n1
                                                                    (m=minute, h=hour, d=day, w=week, n=month)
            TYPE: String
             
            NAME: period
            DESC: Period (not required if START_TIME & END_TIME are sent).
                  The number of periods to show.Flexible time period examples:
                                                                              d5, w4, n10, y1, y10
                                                                              (d=day, w=week, n=month, y=year)
            TYPE: String
            
            NAME: start_Time
            DESC: Start time
            TYPE: String
            
            NAME: end_Time
            DESC: End time
            TYPE: String
                      
            Snapshot fields:
                             Field   Field Name          Type        Field Description
                             0   	key                	String     	Ticker symbol in upper case. 
                             1   	Chart Time         	long       	Milliseconds since Epoch
                             2   	Open Price         	double     	Opening price for the minute
                             3    	High Price        	double     	Highest price for the minute
                             4   	Low Price          	double     	Chart’s lowest price for the minute
                             5   	Close Price        	double     	Closing price for the minute
                             6   	Volume             	doulbe     	Total volume for the minute

                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_chart_history_futures(keys = '/ES', frequecy = 'm5', period = 'd5')              
        '''
        
        
        if end_time != None and start_time != None:
            
            epoch = datetime.utcfromtimestamp(0)
            eD = int((end_time - epoch).total_seconds()*1000)
            sD = int((start_time - epoch).total_seconds()*1000)
        
        else:
            eD = None
            sD = None
        
        data_request= {
                        "requests": [
                                    {
                                    "service": "CHART_HISTORY_FUTURES", 
                                    "requestid": "24", 
                                    "command": 'GET', 
                                    "account": self.credentials['userid'], 
                                    "source": self.credentials['appid'], 
                                    "parameters": {
                                                    "symbol": symbol,
                                                    "frequency": frequency,
                                                    "period": period,
                                                    "END_TIME": eD,
                                                    "START_TIME": sD,

                                                  }
                                    }
                                    ]
                      }
            
        self.data_request(data_request)
        




    '''********************************************
    ********** SUBSCRIPTION REQUESTS **************
    ********************************************'''
    # You may do the subscription request with subs_request but then need to handle the ID asignation in order to add or unsunbscribe or not to 
    # or to avoid requesting different data in same ID. In order to let the streamer handle them use followings methods


    def data_request_account_activity(self, command = "SUBS", fields = '0,1,2,3'):
        '''
            This service is used to request streaming updates for one or more accounts associated with the logged in User ID.  
            Common usage would involve issuing the OrderStatus API request to get all transactions for an account, and subscribing to ACCT_ACTIVITY to get any updates. 
            
            NAME: command
            DESC: chose between "SUBS"= subscribe, "UNSUBS"= unsubscribe
            TYPE: String
            
            NAME: fields
            DESC: select streaming fields.:       
                                          0 = Subscription Key
                                          1 = Account #
                                          2 = Message Type
            TYPE: String

            EXAMPLES:      
            SessionObject.data_request_account_activity(command = "SUBS", fields = '0,1')                       
            
        '''
        
        subs_request = ["ACCT_ACTIVITY", "3", command, self.streamerSubscriptionKey, fields]
                           
        self.subs_request(subs_request)
    
    def data_request_actives_nasdaq(self, command = "SUBS", keys = 'NASDAQ-60', fields = '0,1'):
        
        '''
            Actives shows the day’s top most traded symbols in the four exchanges.  Different duration can be selected.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Shoud be formed as: "Venue"-"Duration"
                  Venue:
                          NASDAQ
                  Duration:
                          ALL= all day
                          3600 = 60 min                           
                          1800 = 30 min                           
                          600 = 10 min                          
                          300 = 5 min                            
                          60 = 1 min
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.:  
                                            0 = Subscription Key
                                            1 = Actives Data
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_actives_nasdaq(command = "SUBS", keys = 'NASDAQ-60', fields = '0,1')               
        '''
        
        subs_request = ["ACTIVES_NASDAQ", "4", command, keys, fields]
                        
        self.subs_request(subs_request)


    def data_request_actives_nyse(self, command = "SUBS", keys = 'NYSE-60', fields = '0,1'):
        
        '''
            Actives shows the day’s top most traded symbols in the four exchanges.  Different duration can be selected.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Shoud be formed as: "Venue"-"Duration"
                  Venue:
                          NYSE

                  Duration:
                          ALL= all day
                          3600 = 60 min                           
                          1800 = 30 min                           
                          600 = 10 min                          
                          300 = 5 min                            
                          60 = 1 min
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.:  
                                            0 = Subscription Key
                                            1 = Actives Data
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_actives_nyse(command = "SUBS", keys = 'NYSE-60', fields = '0,1')               
        '''
         
        subs_request = ["ACTIVES_NYSE", "5", command, keys, fields]
            
        self.subs_request(subs_request) 


    def data_request_actives_otcbb(self, command = "SUBS", keys = 'OTCBB-60', fields = '0,1'):
        
        '''
            Actives shows the day’s top most traded symbols in the four exchanges.  Different duration can be selected.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Shoud be formed as: "Venue"-"Duration"
                  Venue:
                          OTCBB

                  Duration:
                          ALL= all day
                          3600 = 60 min                           
                          1800 = 30 min                           
                          600 = 10 min                          
                          300 = 5 min                            
                          60 = 1 min
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.:  
                                            0 = Subscription Key
                                            1 = Actives Data
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_actives_otcbb(command = "SUBS", keys = 'OTCBB-60', fields = '0,1')               
        '''
        
        subs_request = ["ACTIVES_OTCBB", "6", command, keys, fields]
                   
        self.subs_request(subs_request)   
    
    
    def data_request_actives_options(self, command = "SUBS", keys = 'OPTS-DESC-ALL', fields = '0,1'):
        
        '''
            Actives shows the day’s top most traded symbols in the four exchanges.  Different duration can be selected.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Shoud be formed as: "Venue"-"Duration"
                  Venue:
                          CALLS*
                          OPTS*
                          PUTS*
                          CALLS-DESC*
                          OPTS-DESC*
                          PUTS-DESC*
                          (*options)
                  Duration:
                          ALL= all day
                          3600 = 60 min                           
                          1800 = 30 min                           
                          600 = 10 min                          
                          300 = 5 min                            
                          60 = 1 min
            TYPE: String
                
            NAME: fields
            DESC: select streaming fields.:  
                                            0 = Subscription Key
                                            1 = Actives Data
            TYPE: String                           
            
            EXAMPLES:      
            SessionObject.data_request_actives_options(command = "SUBS", keys = 'OPTS-DESC-ALL', fields = '0,1')               
        '''

        subs_request = ["ACTIVES_OPTIONS", "7", command, keys, fields]      
                   
        self.subs_request(subs_request)    
    

    def data_request_chart_equity(self, command = "SUBS", keys = 'SPY', fields = '0,1,2,3,4,5,6,7,8'):
        
        '''
            Chart provides  streaming one minute OHLCV (Open/High/Low/Close/Volume) for a one minute period .
            The one minute bar falls on the 0 second slot (ie. 9:30:00) and includes data from 0 second to 59 seconds.
            For example, a 9:30 bar includes data from 9:30:00 through 9:30:59.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Subscription Key    String      Ticker symbol in upper case
                                            1       Open Price          double      Opening price for the minute
                                            2       High Price          double      Highest price for the minute
                                            3       Low Price           double      Chart’s lowest price for the minute
                                            4       Close Price         double      Closing price for the minute
                                            5       Volume              double      Total volume for the minute
                                            6       Sequence            long        Identifies the candle minute
                                            7       Chart Time          long        Milliseconds since Epoch
                                            8       Chart Day           int         Not Useful
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_chart_equity(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6,7,8')               
        '''               
        
        subs_request = ["CHART_EQUITY", "8", command, keys, fields]
                    
        self.subs_request(subs_request)  


    def data_request_chart_futures(self, command = "SUBS", keys = '/ES', fields = '0,1,2,3,4,5,6'):
        
        '''
            Chart provides  streaming one minute OHLCV (Open/High/Low/Close/Volume) for a one minute period .
            The one minute bar falls on the 0 second slot (ie. 9:30:00) and includes data from 0 second to 59 seconds.
            For example, a 9:30 bar includes data from 9:30:00 through 9:30:59.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Subscription Key    String      Ticker symbol in upper case
                                            1       ChartTime           long        Milliseconds since Epoch
                                            2       Open Price          double      Opening price for the minute
                                            3       High Price          double      Highest price for the minute
                                            4       Low Price           double      Chart’s lowest price for the minute
                                            5       Close Price         double      Closing price for the minute
                                            6       Volume              double      Total volume for the minute
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_chart_futures(command = "SUBS", keys = '/ES', fields = '0,1,2,3,4,5,6')               
        '''
        
        subs_request = ["CHART_FUTURES", "9", command, keys, fields]
        
        self.subs_request(subs_request)    

    def data_request_chart_options(self, keys, command = "SUBS", fields = '0,1,2,3,4,5,6'):
        
        '''
            Chart provides  streaming one minute OHLCV (Open/High/Low/Close/Volume) for a one minute period .
            The one minute bar falls on the 0 second slot (ie. 9:30:00) and includes data from 0 second to 59 seconds.
            For example, a 9:30 bar includes data from 9:30:00 through 9:30:59.
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Subscription Key    String      Ticker symbol in upper case
                                            1       ChartTime           long        Milliseconds since Epoch
                                            2       Open Price          double      Opening price for the minute
                                            3       High Price          double      Highest price for the minute
                                            4       Low Price           double      Chart’s lowest price for the minute
                                            5       Close Price         double      Closing price for the minute
                                            6       Volume              double      Total volume for the minute
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_chart_options(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6')               
        '''
                       
        subs_request = ["CHART_OPTIONS", "10", command, keys, fields]
        
        self.subs_request(subs_request)  

    def data_request_quote(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52'):
        
        '''
            Listed (NYSE, AMEX, Pacific Quotes and Trades)
            NASDAQ (Quotes and Trades)
            OTCBB (Quotes and Trades)
            Pinks (Quotes only)
            Mutual Fund (No quotes)
            Indices (Trades only)
            Indicators
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Fields	Field Name                       Type	   Field Description
                                            0	      Symbol	                     String	   Ticker symbol in upper case. 
                                            1	      Bid Price	                     float	   Current Best Bid Price
                                            2	      Ask Price	                     float	   Current Best Ask Price
                                            3	      Last Price	                 float	   Price at which the last trade was matched
                                            4	      Bid Size	                     float	   Number of shares for bid
                                            5	      Ask Size	                     float	   Number of shares for ask
                                            6	      Ask ID	                     char	   Exchange with the best ask
                                            7	      Bid ID	                     char	   Exchange with the best bid
                                            8	      Total Volume	                 long	   Aggregated shares traded throughout the day, including pre/post market hours.
                                            9	      Last Size	                     float	   Number of shares traded with last trade
                                            10	     Trade Time	                     int	   Trade time of the last trade
                                            11	     Quote Time	                     int	   Trade time of the last quote
                                            12	     High Price	                     float	   Day’s high trade price
                                            13	     Low Price	                     float	   Day’s low trade price
                                            14	     Bid Tick	                     char	   Indicates Up or Downtick (NASDAQ NMS & Small Cap)
                                            15	     Close Price	                 float	   Previous day’s closing price
                                            16	     Exchange ID	                 char	   Primary "listing" Exchange
                                            17	     Marginable	                     boolean   Stock approved by the Federal Reserve and an investor's broker as being suitable for providing collateral for margin debt.
                                            18	     Shortable	                     boolean   Stock can be sold short.
                                            19	     Island Bid	                     float	   No longer used
                                            20	     Island Ask	                     float	   No longer used
                                            21	     Island Volume	                 Int	   No longer used
                                            22	     Quote Day	                     Int	   Day of the quote
                                            23	     Trade Day	                     Int	   Day of the trade
                                            24	     Volatility	                     float	   Option Risk/Volatility Measurement
                                            25	     Description	                 String	   A company, index or fund name
                                            26	     Last ID	                     char	   Exchange where last trade was executed
                                            27	     Digits	                         int	   Valid decimal points
                                            28	     Open Price	                     float	   Day's Open Price
                                            29	     Net Change	                     float	   Current Last-Prev Close
                                            30	     52  Week High	                 float	   Higest price traded in the past 12 months, or 52 weeks
                                            31	     52 Week Low	                 float	   Lowest price traded in the past 12 months, or 52 weeks
                                            32	     PE Ratio	                     float	
                                            33	     Dividend Amount	             float	   Earnings Per Share
                                            34	     Dividend Yield	                 float	   Dividend Yield
                                            35	     Island Bid Size	             Int	   No longer used
                                            36	     Island Ask Size	             Int	   No longer used
                                            37	     NAV	                         float	   Mutual Fund Net Asset Value
                                            38	     Fund Price	                     float	
                                            39	     Exchange Name	                 String	   Display name of exchange
                                            40	     Dividend Date	                 String	
                                            41	     Regular Market Quote	         boolean	
                                            42	     Regular Market Trade	         boolean	
                                            43	     Regular Market Last Price   	 float	
                                            44	     Regular Market Last Size	     float	
                                            45	     Regular Market Trade Time	     int	
                                            46	     Regular Market Trade Day	     int	
                                            47	     Regular Market Net Change	     float	
                                            48	     Security Status	             String	
                                            49	     Mark	                         double	   Mark Price
                                            50	     Quote Time in Long	             Long	   Last quote time in milliseconds since Epoch
                                            51	     Trade Time in Long	             Long	   Last trade time in milliseconds since Epoch
                                            52	     Regular Market Trade Time in    Long	   Long	Regular market trade time in milliseconds since Epoch
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_chart_quote(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6')               
        '''
        
        subs_request = ["QUOTE", "11", command, keys, fields]
        
        self.subs_request(subs_request)      

    def data_request_option(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,343,35,36,37,38,39,40,41'):
        
        '''
            	
            Level one option quote and trade
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0	    Symbol            	String	Ticker symbol in upper case. 
                                            1	    Description       	String	A company, index or fund name
                                            2	    Bid Price         	float	Current Best Bid Price
                                            3	    Ask Price         	float	Current Best Ask Price
                                            4   	Last Price         	float	Price at which the last trade was matched
                                            5   	High Price         	float	Day’s high trade price
                                            6   	Low Price          	float	Day’s low trade price
                                            7   	Close Price        	float	Previous day’s closing price
                                            8   	Total Volume       	long	Aggregated shares traded throughout the day, including pre/post market hours.
                                            9   	Open Interest      	int	
                                            10  	Volatility         	float	Option Risk/Volatility Measurement
                                            11  	Quote Time         	long	Trade time of the last quote
                                            12  	Trade Time         	long	Trade time of the last trade
                                            13  	Money Intrinsic Value	float	
                                            14  	Quote Day	        Int	Day of the quote
                                            15  	Trade Day          	Int	Day of the trade
                                            16  	Expiration Year    	int	
                                            17  	Multiplier         	float	
                                            18  	Digits             	int	Valid decimal points
                                            19  	Open Price         	float	Day's Open Price
                                            20  	Bid Size           	float	Number of shares for bid
                                            21  	Ask Size           	float	Number of shares for ask
                                            22  	Last Size          	float	Number of shares traded with last trade
                                            23  	Net Change         	float	Current Last-Prev Close
                                            24  	Strike Price       	float	
                                            25  	Contract Type      	char	
                                            26  	Underlying         	String	
                                            27  	Expiration Month	int	
                                            28  	Deliverables       	String	
                                            29  	Time Value         	float	
                                            30  	Expiration Day     	int	
                                            31  	Days to Expiration	int	
                                            32  	Delta              	float	
                                            33  	Gamma              	float	
                                            34  	Theta              	float	
                                            35  	Vega               	float	
                                            36  	Rho                	float	
                                            37  	Security Status    	String	
                                            38  	Theoretical Option Value	float	
                                            39  	Underlying Price	double	
                                            40  	UV Expiration Type	char	
                                            41  	Mark               	double	Mark Price                 
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_option(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6,7,8,9,10')               
        '''

        subs_request = ["OPTION", "12", command, keys, fields]     

        self.subs_request(subs_request)   


    def data_request_listed_book(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol            	String	    Ticker symbol in upper case. 
                                            1       Level2 Time         int         Level2 time in milliseconds since epoch
                                            2       Bid Book            list        List of Bid prices and theirs volumes
                                            3       Ask Book            list        List of Ask prices and theirs volumes
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_listed_book(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3')               
        '''

        subs_request = ["LISTED_BOOK", "13", command, keys, fields]
        
        self.subs_request(subs_request)       

    def data_request_nasdaq_book(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol            	String	    Ticker symbol in upper case. 
                                            1       Level2 Time         int         Level2 time in milliseconds since epoch
                                            2       Bid Book            list        List of Bid prices and theirs volumes
                                            3       Ask Book            list        List of Ask prices and theirs volumes
                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_nasdaq_book(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3')               
        '''

        subs_request = ["NASDAQ_BOOK", "14", command, keys, fields]
                   
        self.subs_request(subs_request)      

    def data_request_options_book(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol            	String	    Ticker symbol in upper case. 
                                            1       Level2 Time         int         Level2 time in milliseconds since epoch
                                            2       Bid Book            list        List of Bid prices and theirs volumes
                                            3       Ask Book            list        List of Ask prices and theirs volumes
                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_options_book(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3')               
        '''
      
        
        subs_request = ["OPTIONS_BOOK", "15", command, keys, fields]
        
        self.subs_request(subs_request)    

    def data_request_levelone_futures(self, command = "SUBS", keys = '/ES', fields = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35'):
        
        '''
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Futures symbol as a product or active symbol (ie. /ES or /ESM4)
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Fields	  Field Name	              Type	    Field Description
                                            0	      Symbol	                  String	Ticker symbol in upper case. 
                                            1	      Bid Price	                  double	Current Best Bid Price
                                            2	      Ask Price	                  double	Current Best Ask Price
                                            3	      Last Price	              double	Price at which the last trade was matched
                                            4	      Bid Size	                  long	    Number of shares for bid
                                            5	      Ask Size	                  long	    Number of shares for ask
                                            6	      Ask ID	                  char	    Exchange with the best ask
                                            7	      Bid ID	                  char	    Exchange with the best bid
                                            8	      Total Volume	              double	Aggregated shares traded throughout the day, including pre/post market hours.
                                            9	      Last Size	                  long	    Number of shares traded with last trade
                                            10	      Quote Time	              long	    Trade time of the last quote in milliseconds since epoch
                                            11	      Trade Time	              long	    Trade time of the last trade in milliseconds since epoch
                                            12	      High Price	              double	Day’s high trade price
                                            13	      Low Price	                  double	Day’s low trade price
                                            14	      Close Price	              double	Previous day’s closing price
                                            15	      Exchange ID	              char	    Primary "listing" Exchange
                                            16	      Description	              String	Description of the product
                                            17	      Last ID	                  char	    Exchange where last trade was executed
                                            18	      Open Price	              double	Day's Open Price
                                            19	      Net Change	              double	Current Last-Prev Close
                                            20	      Future Percent Change	      double	Current percent change
                                            21	      Exhange Name	           	  String    Name of exchange
                                            22	      Security Status	          String	Trading status of the symbol
                                            23	      Open Interest	              int	    The total number of futures ontracts that are not closed or delivered on a particular day
                                            24	      Mark	                      double	Mark-to-Market value is calculated daily using current prices to determine profit/loss
                                            25	      Tick	                      double	Minimum price movement
                                            26	      Tick Amount	              double	Minimum amount that the price of the market can change
                                            27	      Product	                  String	Futures product
                                            28	      Future Price Format	      String	Display in fraction or decimal format.
                                            29	      Future Trading Hours	      String	Trading hours
                                            30	      Future Is Tradable	      boolean	Flag to indicate if this future contract is tradable
                                            31	      Future Multiplier	          double	Point value
                                            32	      Future Is Active	          boolean	Indicates if this contract is active
                                            33	      Future Settlement Price	  double	Closing price
                                            34	      Future Active Symbol	      String	Symbol of the active contract
                                            35	      Future Expiration Date	  long	    Expiration date of this contract
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_chart_levelone_futures(command = "SUBS", keys = '/ES', fields = '0,1,2,3,4,5,6')               
        '''

        subs_request = ["LEVELONE_FUTURES", "16", command, keys, fields]
        
        self.subs_request(subs_request)    

    def data_request_levelone_forex(self, command = "SUBS", keys = 'EUR/USD', fields = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28'):
        
        '''
            	
            Level one option quote and trade
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas (FOREX symbols (ie.. EUR/USD, GBP/USD, EUR/JPY, USD/JPY, GBP/JPY, AUD/USD))
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0   	Symbol	            String	Ticker symbol in upper case. 
                                            1   	Bid Price	        double	Current Best Bid Price
                                            2   	Ask Price          	double	Current Best Ask Price
                                            3   	Last Price         	double	Price at which the last trade was matched
                                            4   	Bid Size           	long	Number of shares for bid
                                            5   	Ask Size           	long	Number of shares for ask
                                            6   	Total Volume       	double	Aggregated shares traded throughout the day, including pre/post market hours.
                                            7   	Last Size          	long	Number of shares traded with last trade
                                            8   	Quote Time	        long	Trade time of the last quote in milliseconds since epoch
                                            9   	Trade Time         	long	Trade time of the last trade in milliseconds since epoch
                                            10  	High Price         	double	Day’s high trade price
                                            11	    Low Price        	double	Day’s low trade price
                                            12  	Close Price        	double	Previous day’s closing price
                                            13  	Exchange ID        	char	Primary "listing" Exchange
                                            14  	Description         String	Description of the product
                                            15  	Open Price         	double	Day's Open Price
                                            16  	Net Change         	double	Current Last-Prev Close
                                            17  	Percent Change     	double	Current percent change
                                            18  	Exchange Name      	String	Name of exchange
                                            19  	Digits             	Int	    Valid decimal points
                                            20  	Security Status    	String	Trading status of the symbol
                                            21  	Tick               	double	Minimum price movement
                                            22  	Tick Amount        	double	Minimum amount that the price of the market can change
                                            23  	Product            	String	Product name
                                            23  	Trading Hours      	String	Trading hours
                                            24  	Is Tradable        	boolean	Flag to indicate if this forex is tradable
                                            25  	Market Maker       	String	
                                            26  	52 Week High       	double	Higest price traded in the past 12 months, or 52 weeks
                                            27  	52 Week Low        	double	Lowest price traded in the past 12 months, or 52 weeks
                                            28  	Mark               	double	Mark-to-Market value is calculated daily using current prices to determine profit/loss

            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_levelone_forex(command = "SUBS", keys = 'EUR/USD', fields = '0,1,2,3,4,5,6,7,8,9,10')               
        '''

        subs_request = ["LEVELONE_FOREX", "17", command, keys, fields]
        
        self.subs_request(subs_request)    


    def data_request_timesale_equity(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol              String      Ticker symbol in upper case. 
                                            1       Trade Time          long        Trade time of the last trade in milliseconds since epoch
                                            2       Last Price          double      Price at which the last trade was matched
                                            3       Last Size           double      Number of shares traded with last trade
                                            4       Las Sequence        long        Number of shares for bid
                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_timesale_equity(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6')               
        '''

        subs_request = ["TIMESALE_EQUITY", "18", command, keys, fields]
        
        self.subs_request(subs_request)         

    def data_request_timesale_futures(self, command = "SUBS", keys = '/ES', fields = '0,1,2,3,4'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol              String      Ticker symbol in upper case. 
                                            1       Trade Time          long        Trade time of the last trade in milliseconds since epoch
                                            2       Last Price          double      Price at which the last trade was matched
                                            3       Last Size           double      Number of shares traded with last trade
                                            4       Las Sequence        long        Number of shares for bid
                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_timesale_futures(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6')               
        '''

        subs_request = ["TIMESALE_FUTURES", "19", command, keys, fields] 
            
        self.subs_request(subs_request)    

    def data_request_timesale_options(self, command = "SUBS", keys = '/ES', fields = '0,1,2,3,4'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol              String      Ticker symbol in upper case. 
                                            1       Trade Time          long        Trade time of the last trade in milliseconds since epoch
                                            2       Last Price          double      Price at which the last trade was matched
                                            3       Last Size           double      Number of shares traded with last trade
                                            4       Las Sequence        long        Number of shares for bid
                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_timesale_options(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6')               
        '''

        subs_request = ["TIMESALE_OPTIONS", "20", command, keys, fields]  
            
        self.subs_request(subs_request) 

    def data_request_news_headline(self, command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6,7,8,9,10'):
        
        '''
            
            
            NAME: command
            DESC: chose between "SUBS": subscribe or replace previous subscription. 
                                "UNSUBS": unsubscribe
                                "ADD": subscribe or ADD to the previos subscription.
            TYPE: String
                                
            NAME: keys
            DESC: Symbols in upper case and separated by commas
            TYPE: String
                
            MAME: fields
            DESC: select streaming fields.: Field   Field Name          Type        Field Description
                                            0       Symbol              String      Ticker symbol in upper case. 
                                            1       Error Code          double      Specifies if there is any error.
                                            2       Story Datetime      long        Headline’s datetime in milliseconds since epoch
                                            3       Headline ID         String      Unique ID for the headline
                                            4       Status              char        
                                            5       Headline            String      News headline
                                            6       Story ID            String
                                            7       Count for Keyword   integer
                                            8       Keyword Array       String
                                            9       Is Hot              boolean
                                            10      Story Source        char
                                            
            TYPE: String                
            
            EXAMPLES:      
            SessionObject.data_request_news_headline(command = "SUBS", keys = 'AAPL', fields = '0,1,2,3,4,5,6,7,8,9,10')               
        '''
        
        subs_request = ["NEWS_HEADLINE", "21", command, keys, fields]
            
        self.subs_request(subs_request)
        
        
        

