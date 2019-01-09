#!/usr/bin/python
# -*- coding: utf-8 -*-
# bierteller general functions
#
# ---------------


# Standard library imports.
import time
import datetime
from collections import OrderedDict
#Related third party imports.
from decimal import *
#Local application/library specific imports.

# ---------------




def timestamp(string='',level=None, epoch=False):
    """ 
    NUMBER Level	When it’s used
    0 DEBUG	Detailed information, typically of interest only when diagnosing problems.
    1 INFO	Confirmation that things are working as expected.
    2 WARNING	An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
    3 ERROR	Due to a more serious problem, the software has not been able to perform some function.
    4 CRITICAL A serious error, indicating that the program itself may be unable to continue running.
    """
    ts = time.time()
    if epoch==True:
        st = str(ts)
    else:
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')
    if string != '':
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')
        data = st + ' ' + str(string)
        print(data)
    if string == '':
        data = st
    return data

    
def sleeper(timer):
    sleeping=timer-(time.time()%timer)
    time.sleep(sleeping)
    
    
def print_values(d,version):
    timestamp('[print_values]-> Displaying ' +str(version)+ ' values')
    if version=='serial':
        for k,v in d['tap'].items():
            if k=='timestamp': continue
            print('{:s}: {:f}L  ({:+f})'.format(k, Decimal(v) / Decimal(10),Decimal(d['dtap']['d'+k])/Decimal(10)))
    elif version in ['csv','gsheets','mysql']:
        for k,v in d['tapvorig'].items():
            if k=='timestamp': continue
            print('{:s}: {:f}L  ({:+f})'.format(k, Decimal(v) / Decimal(10),Decimal(d['dtapvorig']['d'+k])/Decimal(10)))    

            
            
def is_consume(d=None):
    sum=0
    for k,v in d['dtap'].items():
        sum+=v
    if (sum == 0):
        return False
    else:
        return True