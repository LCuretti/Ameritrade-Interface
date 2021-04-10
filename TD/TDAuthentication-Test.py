# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 09:31:45 2019

@author: LC
"""

from TDAuthentication import TDAuthentication #Authentication API
from Ameritrade_cfg_obj import TDConfig

TDCFG = TDConfig()



TEST = TDAuthentication(TDCFG)

TEST.access_token

TEST.authenticate()
TEST
TEST._access_token

TEST._get_access_token()