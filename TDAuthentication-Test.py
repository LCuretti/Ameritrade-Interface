# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 09:31:45 2019

@author: LC
"""

from TDAuthentication import TDAuthentication #Authentication API

from Ameritrade_cfg import client_id, redirect_uri, account_id  #Account information stored. You can check on Ameritrade_cfg_emptyexample

TEST = TDAuthentication(client_id, redirect_uri, account_id)
TEST.authenticate()
TEST
TEST.access_token