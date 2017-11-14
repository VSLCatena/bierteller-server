#!/usr/bin/env python

#HEADER
import serial
import binascii
import time
import datetime
import os
from decimal import *
getcontext().prec = 1

import csv
import MySQLdb

# Import setting from settings.cfg
#[mysqldb]
#host=3
#port=4

import ConfigParser
config = ConfigParser.SafeConfigParser()
config.read('settings.cfg')
db_host = config.get('mysqldb', 'host')
db_port = config.getint('mysqldb', 'port')
db_user = config.get('mysqldb', 'username')
db_pw = config.get('mysqldb', 'password')
db_db = config.get('mysqldb', 'database')

####BODY
print "Verbinden met SQL + CSV"
#initeer database
db = MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_pw,db=db_db)
cursor = db.cursor()
retrieve = "SELECT tap1, tap2, tap3, tap4, dtap1, dtap2, dtap3, dtap4 FROM log ORDER BY tijd DESC LIMIT 1"
#	tijd 	  			 	tap1 	tap2 	tap3 	tap4  dtap1 dtap2 dtap3 dtap4
#	2016-04-16 03:33:54 	1345.2 	876.1 	1829.6 	38.3 	


#initieer serieel	
ser = serial.Serial('/dev/ttyS0', 19200, timeout=2)
#ser.close()

#Interval
interval = 0 
reset_nobeer = 60 #Na laatste afname, per uur uploaden ipv per minuut
start = 0 #negeer de eerste keer boven de 3.5



#def bierteller():
# while True:
	# bierteller()
	# time.sleep(60)
while True:
	
	#SQL-database previous value
	cursor.execute(retrieve)
	result = cursor.fetchone()
	tap1vorig = round(result[0],1)
	tap2vorig = round(result[1],1)
	tap3vorig = round(result[2],1)
	tap4vorig = round(result[3],1)
	totaalvorig = round(result[5],1)
	dtap1vorig = round(result[4],1)
	dtap2vorig = round(result[5],1)
	dtap3vorig = round(result[6],1)
	dtap4vorig = round(result[7],1)
	print "Vorige waarden (SQL): 1-4, d1-d4"	
	print tap1vorig, tap2vorig, tap3vorig, tap4vorig, dtap1vorig, dtap2vorig, dtap3vorig, dtap4vorig,"\n"
	
	
	#initeer csv
	local = csv.writer(open("database.csv", "ab"))
	
	#seriele data
	time.sleep(5)	
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	
	ser_cor=-1
	while (ser_cor <0):
		ser_raw = ser.read(size=4056) #laad de hele buffer in
		time.sleep(2) #het kost tijd
		ser_cor=ser_raw.find("\r\nAT+SCASTB:22") #zoek deze terugkerende tekst op.
		print ser_cor
	#if cor = -1: ser.reset_input_buffer() Wait(1)
	ser_split =[ser_raw[52*i+ser_cor+i:(i+1)*52+ser_cor] for i in xrange(len(ser_raw)//51)] #split de seriele data vanaf de eerste 'tekst' en split dat door 52
	ser_short= [ser_split[i][17:25] for i in xrange(len(ser_split))]
	#haal hier de bier
	ser_1_split=[ser_short[0][i:(i+1)] for i in xrange(len(ser_short[0]))]
	int_1_split=[ord(x) for x in ser_1_split]
	bierdata=[int_1_split[x]+int_1_split[x+1]*256 for x in xrange(0,8,2)]
	#
	# data in low,hi 17-25
	#'\r\nAT+SCASTB:22\rt0-\x02\xb6\x03@\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n'
	#0-51

	tap1 = round(bierdata[0],1)/10
	tap2 = round(bierdata[1],1)/10
	tap3 = round(bierdata[2],1)/10
	tap4 = round(bierdata[3],1)/10

	#mutaties
	sub = tap1 + tap2 + tap3
	totaal = tap1 + tap2 + tap3 + tap4
	
	dtap1 = tap1 - tap1vorig
	dtap2 = tap2 - tap2vorig
	dtap3 = tap3 - tap3vorig
	dtap4 = tap4 - tap4vorig
	dtotaal = dtap1 + dtap2 + dtap3 + dtap4
	
	#print in terminal
	print "Huidige absolute waarden (Serial):"
	print "\n", st
	print "Tap 1: ",tap1,"L","\n","Tap 2: ", tap2,"L","\n","Tap 3: ", tap3,"L","\n","Tap 4: ", tap4,"L","\n","Soos-totaal: ", sub,"L","\n", "Totaal:", totaal, "L","\n"	
	print "Deltawaarden:"
	print "dtap 1: ",dtap1,"L","\n","dtap 2: ",dtap2,"L","\n","dtap 3: ",dtap3,"L","\n","dtap 4: ",dtap4,"L","\n",
	
	#the checks
	
	#geen bier getapt in afgelopen minuut
	if (dtotaal == 0 and interval < reset_nobeer and start !=0): 
		interval +=1
		print "geen verandering, %d/%d" % (interval, reset_nobeer)
	
	#normaal werkend  (1x per minuut)
		#SQL
	if (dtotaal > 0 and dtotaal <3.5) or (interval==reset_nobeer) or (start == 0): 
		cursor.execute( "INSERT INTO log VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (st, tap1, tap2, tap3, tap4, sub, totaal, dtap1, dtap2, dtap3, dtap4) )
		db.commit()
		#VERANDER STRINGS NAAR NUMBERS!!!!!
		
		#CSV
		local.writerow([st, tap1, tap2, tap3, tap4, sub, totaal, dtap1, dtap2, dtap3, dtap4, dtotaal])
		#local.close()
		
		print "upload + interval=0"
		interval = 0
		
	#fout in bierteller (geef foutmelding door)		
	if (dtotaal < 0): 
		db.rollback()
		print "geen upload. Fout <0"
		
	#fout in bierteller (geef foutmelding door)	
	if (dtotaal  > 3.5) and (start !=0): 
		db.rollback()
		print "geen upload. Fout >3.5"
	
	start = 1 #first round 
	#ser.close()
	print "\n", "---"
	time.sleep(60)
	
cursor.close()
db.close()


#example '\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n\r\nAT+SCASTB:22\rt04\x02\xbf\x03E\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0
