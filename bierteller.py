#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Version 2.10
#
#  fixed empty csv file initialization
#

# ---------------

# Standard library imports.
import os
import configparser
from collections import OrderedDict
from decimal import *
#Related third party imports.
#import MySQLdb
#Local application/library specific imports.
from bt_general import *
from bt_serial import *
from bt_csv import *
from bt_sql import *
from bt_gsheets import *

# ---------------




#
# HEADER/Configparser
#
#parsing contents of configparser. Alternative to the commented lines below
config = configparser.ConfigParser(allow_no_value=True)
config.read('./settings.cfg')
settings = {} 
for s in config.sections():
    settings[s]={}
    for k,v in config.items(s):
        if v.isdigit():
            v=int(v)
        if isinstance(v, str):
            if v.lower()=="false":
                v=False
            elif v.lower()=="true":
                v=True
            elif v=="":
                v=None
        settings[s][k]=v
#s:dict(tuple(int(u) if u.isdigit()  else u for u in t) for t in config.items(s)) for s in config.sections()} #includes int conversion but no None/Boolean
#{s:dict(config.items(s)) for s in config.sections()} only strings 

#
# HEADER/Dictionary
#
bierteller = {
    'tap':{},
    'tapvorig' : {},
    'dtap' : {},
    'dtapvorig' : {},
}
# initialize tapnames
for i in range(1, settings['general']['amount_tap'] + 1):
    key1 = 'tap' + str(i)
    key2 = 'tapvorig' + str(i)
    key3 = 'dtap' + str(i)
    key4 = 'dtapvorig' + str(i)
    bierteller['tap'][key1] = 0 
    bierteller['tapvorig'][key2] = 0
    bierteller['dtap'][key3] = 0
    bierteller['dtapvorig'][key4] = 0

# sort dictionary nested dictionary
for k,v in bierteller.items():
    if(k=="tap" or k=="tapvorig"):
        bierteller[k] = OrderedDict([('timestamp',0)]+sorted(v.items()))
    else:
        bierteller[k] = OrderedDict(sorted(v.items()))

#
# HEADER / Global vars
#
getcontext().prec = 16  # precision of Decimal lib to 1
is_started = False  # I have not been started.
interval=0


#
# BODY   
#
#(ALL VALUES ARE IN INTEGER 123 = 12.3 )
#
s=Bierteller_serial() #create instance of bt_serial, with closed port.
start_time=timestamp()
try:
    while(True):
        timestamp('Program started at {} ({})'.format(start_time,interval))
        if settings['databases']['read']=='gsheets':
            old=gsheets_read()
        if settings['databases']['read']=='csv':
            old=csv_read()
        if settings['databases']['read']=='mysql':
            old=sql_read()
        for k in range(0, settings['general']['amount_tap']):
            if old==False:
                bierteller['tapvorig']['tapvorig' + str(k + 1)] =0
                bierteller['dtapvorig']['dtapvorig' + str(k + 1)] =0
            else:
                bierteller['tapvorig']['tapvorig' + str(k + 1)] = old['tap'+str(k+1)] 
                bierteller['dtapvorig']['dtapvorig' + str(k + 1)] = old['dtap'+str(k+1)] 
        print_values(d=bierteller,version='csv')      
        #get new values
        s.check_buffer(True) #open port, flush/check buffer and immediatly read it.
        if(s.buffer!=None): 
            if(s.decode()): #decode binary data
                for k in range(0, settings['general']['amount_tap']):
                    bierteller['tap']['tap' + str(k + 1)] = s.tapvalues[k]        
                    bierteller['tap']['timestamp']=s.bufferTimestamp
                    bierteller['dtap']['dtap' + str(k + 1)] = bierteller['tap']['tap' + str(k + 1)] - bierteller['tapvorig']['tapvorig' + str(k + 1)]
                    
                #write values to csv
                if(is_consume(bierteller) or is_started==False or is_hour()==True):
                    simple_dict=csv_simplify_dict(bierteller)
                    if(settings['databases']['write_csv']): csv_write(simple_dict)
                    try:
                        if(settings['databases']['write_gsheets']): gsheets_basic(data=list(simple_dict.values()),action='write',cfg=settings['gsheets'])
                    except Exception as e:
                        timestamp('Error. Ignoring it and retry later')
                        print(e)
                print_values(d=bierteller,version='serial')
        is_started = True
        interval+=1
        timestamp('Going to sleep until next minute')
        sleeper(60)


except Exception as e:
    print(e)
 
 



# '\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0
