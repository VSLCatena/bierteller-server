#!/usr/bin/env python
#
#Version 2.0
#
#Rewritten code, made functions, error exceptions, integer, english, timestamps, new way to find correction factor, rewritten decode (error was in previous)
#
#HEADER/Import
import serial
import binascii
import time
import datetime
import os
from decimal import *
getcontext().prec = 1
import csv
import MySQLdb
import ConfigParser
import re

#HEADER/Config
config = ConfigParser.SafeConfigParser()
config.read('settings.cfg')
db_host = config.get('mysqldb', 'host')
db_port = config.getint('mysqldb', 'port')
db_user = config.get('mysqldb', 'username')
db_pw = config.get('mysqldb', 'password')
db_db = config.get('mysqldb', 'database')

start = 0 #I have not been started. 
interval = 0 # current interval no.
time_sleep = 5 #seconds; amount of sleep after check of serial port
time_check = 60 #Seconds; Interval of serial port check
reset_nobeer = 30 #after [reset_nobeer] tries of [interval] each which takes [time_check] seconds, upload 



####BODY
### ALL VALUES ARE IN INTEGER 123 = 12.3 

def timestamp(string=""):
 ts=time.time()
 if (string !=""):
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')
  data = st+" "+str(string)
  print data
 if (string==""):
  st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
  data = st
 return	data
 

def database_read():
 timestamp("Connecting with SQL-server")
 try: 
  db = MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_pw,db=db_db)
  cursor = db.cursor()
  retrieve = "SELECT tap1, tap2, tap3, tap4, dtap1, dtap2, dtap3, dtap4 FROM log ORDER BY tijd DESC LIMIT 1" 
  # latest data plz
  #	tijd 	  			 	tap1 	tap2 	tap3 	tap4  dtap1 dtap2 dtap3 dtap4
  #	2016-04-16 03:33:54 	13452 	8761 	18296 	383 0 0 0 0 	
  cursor.execute(retrieve)
  result = cursor.fetchone()
  cursor.close()
  tap1vorig = result[0]
  tap2vorig = result[1]
  tap3vorig = result[2]
  tap4vorig = result[3]
  totaalvorig = result[5]
  dtap1vorig = result[4]
  dtap2vorig = result[5]
  dtap3vorig = result[6]
  dtap4vorig = result[7]
  info = "{}({}) {}({}) {}({}) {}({})".format(tap1vorig,dtap1vorig,tap2vorig,dtap2vorig,tap3vorig,dtap3vorig,tap4vorig,dtap4vorig)
  timestamp("Connected. Previous values from SQL: "+info)	
  
 except Exception as e:
  print("Error:"+str(e)) 
 return tap1vorig, tap2vorig, tap3vorig, tap4vorig, dtap1vorig, dtap2vorig, dtap3vorig, dtap4vorig
 
def database_write(rollback=0):
 try:
  db = MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_pw,db=db_db)
  cursor = db.cursor()
  if (rollback ==1):
   cursor.close()
   db.rollback()
  if (rollback ==0):
   cursor.execute( "INSERT INTO log VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",  (timestamp(), tap1, tap2, tap3, tap4, sub, totaal, dtap1, dtap2, dtap3, dtap4) )
   db.commit()
   cursor.close()
   db.close()
   timestamp("Written to SQL-database")
 except Exception as e:
  timestamp(str(e))

 
def csv_write():
 try:
  local = csv.writer(open("database.csv", "ab"))
  local.writerow([timestamp(), tap1, tap2, tap3, tap4, sub, totaal, dtap1, dtap2, dtap3, dtap4, dtotaal])
  timestamp("Written to CSV-file")
 except Exception as e:
  timestamp("Error while writing to CSV: \n"+str(e))
  
	
def serial_read():
#serial data
 global time_sleep	
 ser_cor=-1 #position of header. Correction factor
 ser_cor_t=0 #amount of times through the check-loop
 timestamp("Reading serial...")
 try:
  while (ser_cor <0) and (ser_cor_t<6): #search correction factor until found (ser_cor! <1) or amount of times =6
   buffersize=ser.inWaiting() #length of buffer 
   ser_raw = ser.read(size=buffersize) #load complete buffer 
   time.sleep(time_sleep) #sleep
  
   #ser_cor=ser_raw.find("\r\nAT+SCASTB:22") #search this text. Result = location. (-1)=nothing (>-1)=location
   ser_cor_list=[m.start() for m in re.finditer('\r\nAT\+SCASTB:22', ser_raw)] #the + has to be escaped
   try:
    ser_cor=ser_cor_list[0] #first occurence of HEADER-text
   except:
    ser_cor=-1 #if not found, try again.
   
   ser_cor_t += 1 #try again
   print "pos({}) try:({}) size:{}".format(ser_cor, ser_cor_t,buffersize)
 except Exception as e:
  timestamp("Error while reading: \n"+str(e))
 print("")
 return ser_raw,ser_cor_list,ser_cor_t
		
		
def serial_decode(ser_raw,ser_cor_list):
 timestamp("Decoding data")
 #
 # data in low,hi 17-25
 #'\r\nAT+SCASTB:22\rt0-\x02\xb6\x03@\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n'
 #0-51
 ser_all_split=[]
 int_all_split=[]
 bierdata=[]
 
 ser_split =[ser_raw[ser_cor_list[i]:ser_cor_list[i]+50] for i in xrange(len(ser_cor_list))] #split serial data at each HEADER-text
 ser_len = len(ser_split) #amount of substrings of "\r\nAT ... \r\n"
 ser_short= [ser_split[i][17:25] for i in xrange(ser_len)] #trim junk
 
 for j in xrange(ser_len): #for each HEADER-text
  ser_all_split.append([ser_short[j][i:(i+1)] for i in xrange(len(ser_short[j]))]) #create [list of bytes]
  int_all_split.append([ord(x) for x in ser_all_split[j]]) #translate [list of bytes] to [list of integers] 
  bierdata.append([int_all_split[j][x]+int_all_split[j][x+1]*256 for x in xrange(0,8,2)]) # [first integer + second integer *256], etc
 
 return bierdata[0] #only interested in latest data

def prepare(bierdata):
 tap1 = bierdata[0]
 tap2 = bierdata[1]
 tap3 = bierdata[2]
 tap4 = bierdata[3]

 #mutations
 sub = tap1 + tap2 + tap3
 totaal = tap1 + tap2 + tap3 + tap4


 #difference
 dtap1 = tap1 - tap1vorig
 dtap2 = tap2 - tap2vorig
 dtap3 = tap3 - tap3vorig
 dtap4 = tap4 - tap4vorig
 dtotaal = dtap1 + dtap2 + dtap3 + dtap4
 

 #print in terminal
 timestamp("Preparing data\nCurrent absolute values (Serial):")
 print("Tap 1: {:.1f} L\nTap 2: {:.1f} L\nTap 3: {:.1f} L\nTap 4: {:.1f} L\nSoos-total: {:.1f} L\nTotal: {:.1f} L\n ".format(
 float(tap1)/10,
 float(tap2)/10,
 float(tap3)/10,
 float(tap4)/10,
 float(sub)/10,
 float(totaal)/10))	
 print "Delta values:"
 print("dtap 1: {:.1f} L\ndtap 2: {:.1f} L\ndtap 3: {:.1f} L\ndtap 4: {:.1f} L\n".format(
 float(dtap1)/10,
 float(dtap2)/10,
 float(dtap3)/10,
 float(dtap4)/10))
 
 return tap1,tap2,tap3,tap4,sub,totaal,dtap1,dtap2,dtap3,dtap4,dtotaal
 
def check(tap1,tap2,tap3,tap4,sub,totaal,dtap1,dtap2,dtap3,dtap4,dtotaal): 
 global interval
 global reset_nobeer
 global start
  
 if (dtotaal == 0 and interval < reset_nobeer and start !=0): #no beer has been consumed
  interval +=1
  timestamp("No change, {}/{}".format(interval, reset_nobeer))

 #
 #NORMAL USE
 #
 if (dtotaal > 0 and dtotaal <35) or (interval==reset_nobeer) or (start == 0): #beer has been consumed OR obligatory upload needed OR this is first run
  database_write()
  csv_write()
  timestamp("upload + interval=0")
  interval = 0

#			
#ERROR
#
 if (dtotaal < 0): 
  database_write(rollback=1)
  timestamp("Rollback / No upload. Error value <0") #negative value has been reported
			
 if (dtotaal  > 35) and (start !=0): 
  database_write(rollback=1)
  timestamp("Rollback / No upload. Error value >35") #too high value has been reported
		
 start = 1 #first round has just been started

 
 
 
######MAIN####			

try:
 ser = serial.Serial('/dev/ttyS0', 19200, timeout=2) #initialized serial connection
 timestamp("Serial connected")
except Exception as e:
 timestamp("Error while connecting to serial: \n"+str(e)) 
 quit()
while True: #just continue running
 tap1vorig, tap2vorig, tap3vorig, tap4vorig, dtap1vorig, dtap2vorig, dtap3vorig, dtap4vorig = database_read() #read all SQL-data
 ser_raw,ser_cor_list,ser_cor_t=serial_read() #Read all serial data
 if (ser_cor_t !=6 and len(ser_cor_list)!=0): #Correction factor has to be found or else we'll wait 
  bierdata = serial_decode(ser_raw,ser_cor_list) #Plz decode the serial data to values
  tap1,tap2,tap3,tap4,sub,totaal,dtap1,dtap2,dtap3,dtap4,dtotaal = prepare(bierdata) #plz prepare the data with previous data
  check(tap1,tap2,tap3,tap4,sub,totaal,dtap1,dtap2,dtap3,dtap4,dtotaal) #check if values are "correct".

 waittime=(time_check-(ser_cor_t*time_sleep)) #Amount of time to wait between each check  
 print("--"+str(waittime)+"sec sleep --\n") #how long are you going to sleep.
 time.sleep(waittime)


# '\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0
