# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###
from __future__ import absolute_import

from .api.electricity_user_list import ElectricityUserList
from .api.electricity_balance_userId import ElectricityBalanceUserid
from .api.electricity_dailys_userId import ElectricityDailysUserid
from .api.electricity_latest_month_userId import ElectricityLatestMonthUserid
from .api.electricity_this_year_userId import ElectricityThisYearUserid


routes = [
    dict(resource=ElectricityUserList, urls=['/electricity/user_list'], endpoint='electricity_user_list'),
    dict(resource=ElectricityBalanceUserid, urls=['/electricity/balance/<userId>'], endpoint='electricity_balance_userId'),
    dict(resource=ElectricityDailysUserid, urls=['/electricity/dailys/<userId>'], endpoint='electricity_dailys_userId'),
    dict(resource=ElectricityLatestMonthUserid, urls=['/electricity/latest_month/<userId>'], endpoint='electricity_latest_month_userId'),
    dict(resource=ElectricityThisYearUserid, urls=['/electricity/this_year/<userId>'], endpoint='electricity_this_year_userId'),
]