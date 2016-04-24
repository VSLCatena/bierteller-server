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
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
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
	#a = ser.open()
	ser.flushInput() #reset_input_buffer()
	ser.flushOutput() #reset_output_buffer()
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		#write 'a' to buffer
	x = ser.write("a")
		#sleep for delay		
	time.sleep(.3)	
		#It gets a 27byte back. (00000110 x 27 )
	
	#serdata = ser.read(size=27)
	#splitserdata =[serdata[8*i:8*(i+1)] for i in xrange(len(serdata)//8)]
	
	a = ser.read(size=1)
	b = ser.read(size=1)
	c = ser.read(size=1)
	d = ser.read(size=1)
	e = ser.read(size=1)
	f = ser.read(size=1)
	g = ser.read(size=1)
	h = ser.read(size=1)
	i = ser.read(size=1)
	j = ser.read(size=1)
	k = ser.read(size=1)
	l = ser.read(size=1)
	rest = ser.read(size=15)
	ser.flush()
	
	# teller1h = binascii.b2a_hex(splitserdata[0])
	# teller1m = binascii.b2a_hex(splitserdata[1])
	# teller1l = binascii.b2a_hex(splitserdata[2])
	# teller2h = binascii.b2a_hex(splitserdata[3])
	# teller2m = binascii.b2a_hex(splitserdata[4])
	# teller2l = binascii.b2a_hex(splitserdata[5])
	# teller3h = binascii.b2a_hex(splitserdata[6])
	# teller3m = binascii.b2a_hex(splitserdata[7])
	# teller3l = binascii.b2a_hex(splitserdata[8])
	# teller4h = binascii.b2a_hex(splitserdata[9])
	# teller4m = binascii.b2a_hex(splitserdata[10])
	# teller4l = binascii.b2a_hex(splitserdata[11])
	#12-26 not used
	ser.flush()
	
	teller1h = binascii.b2a_hex(a)
	teller1m = binascii.b2a_hex(b)
	teller1l = binascii.b2a_hex(c)
	teller2h = binascii.b2a_hex(d)
	teller2m = binascii.b2a_hex(e)
	teller2l = binascii.b2a_hex(f)
	teller3h = binascii.b2a_hex(g)
	teller3m = binascii.b2a_hex(h)
	teller3l = binascii.b2a_hex(i)
	teller4h = binascii.b2a_hex(j)
	teller4m = binascii.b2a_hex(k)
	teller4l = binascii.b2a_hex(l)
	tap1u = int(teller1h, 16) + (int(teller1m, 16)*256) + (int(teller1l, 16)*256*256)
	tap1 = round(tap1u,1)/10
	tap2u = int(teller2h, 16) + (int(teller2m, 16)*256) + (int(teller2l, 16)*256*256)
	tap2 = round(tap2u,1)/10
	tap3u = int(teller3h, 16) + (int(teller3m, 16)*256) + (int(teller3l, 16)*256*256)
	tap3 = round(tap3u,1)/10
	tap4u = int(teller4h, 16) + (int(teller4m, 16)*256) + (int(teller4l, 16)*256*256)
	tap4 = round(tap4u,1)/10

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
	print a, "\n", st
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
