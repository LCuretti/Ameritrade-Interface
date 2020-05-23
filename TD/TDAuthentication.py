# -*- coding: utf-8 -*-
"""
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

Created on Sun Oct 13 13:09:41 2019
@author: LC
"""
import os
import sys
import time
import pickle
import getpass
import requests
import webbrowser
from shutil import which
import urllib.parse as up
from datetime import datetime
from datetime import timedelta
from selenium import webdriver


class TDAuthentication(object):
    
    '''
        TD Ameritrade API Class.
        
        Implements OAuth 2.0 Authorization Code Grant workflow, 
        adds token for authenticated calls.
        
        
    '''

    def __init__(self, client_id, redirect_uri, account_id = None, account_cache = True, refresh_cache = True, tduser = None, tdpass = None, single_access = False):
        
        '''
            Initializes the session with default values and any user-provided overrides.
            
            The following arguments MUST be specified at runtime or else initialization
            will fail.
            
            NAME: client_id
            DESC: The Consumer ID assigned to you during the App registration. This can
                  be found at the app registration portal. A must to get the access token
          
            NAME: redirect_uri
            DESC: This is the redirect URL that you specified when created your
                  TD Ameritrade Application. A must in order to get the access token
                  
            NAME: account_id
            DESC: TD Account number. Needed in order to save or retrieve account pass, user and refreshtoken.

            NAME: account_cache
            DESC: If True, User data will be stored.
            
            NAME: refresh_cache
            DESC: If True, RefreshToken will be stored.
            
            NAME: tduser
            DESC: Ameritrade Username(optional)
            
            NAME: tdpass
            DESC: Ameritrade account password(optional)
            
            NAME: single_access
            DESC: True if there is no need to autorefresh the access token. 
                  If after expiration Authentication is call, the complete authentication will be done. 
            
        '''
        
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.account_id = account_id 
        self.account_cache = account_cache
        self.refresh_cache = refresh_cache
        self.single_access = single_access
        self.account_user = tduser
        self.password = tdpass
        self.access_code = None
        self._access_token = None
        self.refresh_token = None
        self.access_expiration = None
        self.refresh_expiration = None
        self.logged_in_state = False

        if os.path.isfile('./{}.pickle'.format(self.account_id)) and not self.account_cache:
            os.remove('./{}.pickle'.format(self.account_id))
        if os.path.isfile('./{}refreshtoken.pickle'.format(self.account_id)) and not self.refresh_cache:
            os.remove('./{}refreshtoken.pickle'.format(self.account_id))

        print("TDAuthentication Initialized at: "+str(datetime.now()))
        
    def __repr__(self):
        '''
            Defines the string representation of our TD Ameritrade Class instance.
        '''
        
        #if never logged in or expired the Log in state is False        
        if self.access_expiration == None:
            self.logged_in_state = False    
        elif self.access_expiration < datetime.now():
            self.logged_in_state = False
        
        # define the string representation
        return '<TDAmeritrade Client (logged_in = {}, client_id = {})>'.format(self.logged_in_state, self.client_id)

    
    def _get_access_code(self):
        '''
            Get access code which is needed for requesting the refresh token.
            
            Need to Authenticate providing User and Password or through the browser.
            
            This authentication is only necessary each 3 month if the refreshtoken is saved (refresh_cache=True)
            User may choose to save the refreshtoken that allows to handle most of the account but Money Transfers for example or
            Save the account data giving full access, and allowing this authentication to be done without any future user interaction.
            The API store the data linked to the account number, so multiple user can use it in the same computer.
            
            The single_access make the API to not store anything, not even in memory. For the cases you are logging in others computer.
            If that the case will be necessary to go through full authentication each 30 min.
            
            The API can obtain User and Password in the followings ways:
                1)They can be pass to the object when creating. If account_cache is true they will be stored and will not be necessary to pass them again.
                2)If account_cache is True the user and password will be load rom the file.
                3)If chromedriver is available and the previous 2 ways did not apply, then user and password will be required in the command line.
                4)If nothing is found from command line, webpage will be prompted for manual authentication.
                5)In the case chrome driver is not available. Command line will provide a link where user can authenticate and grab the code to paste back in the command line. 
                    (Manual way)
                 
        '''
        
        # define the components to buil a URL
        client_code = self.client_id + '@AMER.OAUTHAP'
        
        # build the URL and store it in a new variable
        url = 'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=' + up.quote(self.redirect_uri) + '&client_id=' + up.quote(client_code)
              
        #get windows user name to point chrome driver
        user = getpass.getuser()
        
        # In order to auto-authenticate is necessary to have chromedriver. The standard path is C:/Users/{windows user}/chromedriver
        # define the location of the Chrome Driver
        options = webdriver.ChromeOptions()
          
 
        if sys.platform == 'darwin':
            # MacOS
            if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
                options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            elif os.path.exists("/Applications/Chrome.app/Contents/MacOS/Google Chrome"):
                options.binary_location = "/Applications/Chrome.app/Contents/MacOS/Google Chrome"
        elif 'linux' in sys.platform:
            # Linux
            options.binary_location = which('google-chrome') or which('chrome') or which('chromium')
        else:
            # Windows
            if os.path.exists('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'):
                options.binary_location = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
            elif os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe'):
                options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'


        #options.binary_location = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
        chrome_driver_binary = which('chromedriver') or "C:/Users/{}/chromedriver.exe".format(user) #dowload latest chromedriver and store it in user folder

        #If Chromedriver is available 
        if os.path.isfile(chrome_driver_binary):    
            
            # Fully automated oauth2 authentication (if tdauser and tdapass were inputed into the function, or found as environment variables)
            if self.account_user == None or self.password == None:
                # user and password stored retrive them
                if self.account_cache and os.path.isfile('./{}.pickle'.format(self.account_id)):
                    with open('{}.pickle'.format(self.account_id), 'rb') as f:
                        self.account_user, self.password = pickle.load(f)
                else:
                    # if user or password is not provided 
                    # Request input User and password
                    self.account_user = input('user: ')
                    self.password = getpass.getpass('password: ')  #if you run it in Spyder enviroment password will still be shown on the terminal
        
        
            # if no user nor password prompt browser for authentication
            if not self.account_user or not self.password:
                driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)     
                # go to the URL
                driver.get(url)
                input('after giving access, hit enter to continue')
                access_code = up.unquote(driver.current_url.split('code=')[1])
            else:    
                #set browser to not vissible mode
                options.add_argument("--headless") 
                driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
                # go to the URL
                driver.get(url)
                
                #fill the Authentication forms and click ok
                ubox = driver.find_element_by_id('username')
                pbox = driver.find_element_by_id('password')
                ubox.send_keys(self.account_user)
                pbox.send_keys(self.password)
                driver.find_element_by_id('accept').click()
        
                driver.find_element_by_id('accept').click()
                #wait till get the code that is the url of the forwarded page.
                while 1:
                    try:
                        #grab the part we need, and decode it.
                        access_code = up.unquote(driver.current_url.split('code=')[1])
                        if access_code != '':
                            # store user and password 
                            if not self.single_access and self.account_cache and not os.path.isfile('./{}.pickle'.format(self.account_id)):
                                with open('{}.pickle'.format(self.account_id), 'wb') as f:
                                    pickle.dump([self.account_user, self.password], f)
                            self.account_user == None
                            self.password == None
                            break
                        else:
                            time.sleep(2)
                    except (TypeError, IndexError):
                        pass
       
            #close the browser
            driver.close()

        # if not Chromedriver
        else:
            # aks the user to go to the URL provided, they will be prompted to authenticate themselves.
            print('Please login to your account.')
            webbrowser.open("{}".format(url))
        
            # ask the user to take the final URL after authentication and paste here so we can parse.
            access_code = input('Paste the redirected full URL here: ')
        
        #store acces_code
        self.access_code = access_code

   
    def _get_access_token(self):
        '''
            Request the Refresh and Access token providing the access code, clint_id and redirect_uri.
        '''
              
        self._get_access_code()
        
        # THE AUTHENTICATION ENDPOINT
        #define the endpoint
        url = r"https://api.tdameritrade.com/v1/oauth2/token"
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        access_type = 'offline'
        
        #if Single Access then it will be only request Access token and not Refresh Token
        if self.single_access:
            access_type = None
        
        # define the payload
        payload = {'grant_type': 'authorization_code',
                   'access_type': access_type,
                   'code': self.access_code,
                   'client_id':self.client_id,
                   'redirect_uri':self.redirect_uri}
        
        # post the data to get the token
        authReply = requests.post(url = url, headers = headers, data = payload)
        
        if authReply.status_code != 200:
            self.logged_in_state = False
            raise Exception('Could not authenticate!')
       
        # convert it to dictionary
        decoded_content = authReply.json()
       
        if not self.single_access:
            self.refresh_token = decoded_content['refresh_token']    
            self.refresh_expiration = datetime.now() + timedelta(seconds = 7776000)
            
            # if refresh cache store the refresh token and it expiration
            if self.refresh_cache:
                with open('{}refreshtoken.pickle'.format(self.account_id), 'wb') as f:
                    pickle.dump([self.refresh_token, self.refresh_expiration], f)

        # grab th access_token
        self._access_token = decoded_content['access_token']
        self.access_expiration = datetime.now() + timedelta(seconds = 1800)
        self.logged_in_state = True

        
    def _refresh_access_token(self):
        '''
            refresh the access token providing the refreshtoken. It will run each 30 min.
        '''
        
        resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                             headers={'Content-Type': 'application/x-www-form-urlencoded'},
                             data={'grant_type': 'refresh_token',
                                   'refresh_token': self.refresh_token,
                                   'client_id': self.client_id})
        
        if resp.status_code != 200:
            self.logged_in_state = False
            raise Exception('Could not authenticate!')
        
        decoded_content = resp.json()
        self._access_token = decoded_content['access_token']
        self.access_expiration = datetime.now() + timedelta(seconds = 1800)
        self.logged_in_state = True
       

    def authenticate(self):
        '''
            Verify if the access token is valid and update it if neccesarly.
            We you call it before any API request in order to avoid expiration.
            After go through it ensures that the object token is still valid for requests.
        '''
        
        if self.single_access:
            if self.access_expiration == None:
                self._get_access_token()
            
            elif self.access_expiration - timedelta(seconds = 10) < datetime.now():
                self._get_access_token()    

        else:
            if self.refresh_token == None:
                if self.refresh_cache and os.path.isfile('./{}refreshtoken.pickle'.format(self.account_id)):
                        with open('{}refreshtoken.pickle'.format(self.account_id), 'rb') as f:
                             self.refresh_token, self.refresh_expiration = pickle.load(f)
                        self._refresh_access_token()     
                else:
                    self._get_access_token()

        
            if self.refresh_expiration - timedelta(days = 1) < datetime.now():
                self._get_access_token()

            # if the access token is less than 5 sec to expire or expired, then renew it.
            elif self.access_expiration - timedelta(seconds = 5) < datetime.now():
                self._refresh_access_token()
                
 
    @property
    def access_token(self):
        self.authenticate()
        return self._access_token


