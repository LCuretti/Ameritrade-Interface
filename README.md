# Ameritrade Python Interface
Handles Authentication, WebSocket streaming subscriptions and API requests

TDAuthentication.py:

    Keeps a valid token access to be use by TDAPI(endpoint requests).
    
    It can be run without any preview setup as it handle different authentication methods.
    
    Full Automated where account info will be stored for future authentication 
    or Full Manual where you have to authenticate each 30 min.
  
TDAPI.py [Based on areed1192](https://github.com/areed1192/td-ameritrade-python-api):

    Handle all API requests. GET, POST,PUT, PATCH.
  
    In order to send a valid request it keep authenticating throuh TDAtuthentication Class.
  
    Find below the table with all possible requests.
   
 
TDAPI-Test.py:

    Has multiple endpoints check for the TDAPI file.
  
    Added customed create orders.
  
TDStream.py:

    Handle all subscription for WebSocket streaming. SUBS, UNSUBS, ADD, LOGIN, LOGOUT, QOS.
  
    In order to request the credentials it uses TDAPI Class.
  
    Find below subscription table.
    
    New feature: Keep alive method that subscribes back all subscription when connection comes alive again.
 
TDStreamer-test-py:

    Has multiple subscription method to test TDStream.

TDAPI requests table:

![Screenshot](TDAPITable.png)

TDStream subscription table:

![Screenshot](TDStreamerTable.png)

TO DO: 

    Add DataFrame interface to convert from JSON output.
    Add parameter verification.
              
    Add a trigger from streamer, and ping connection to keep alive the streamer.
