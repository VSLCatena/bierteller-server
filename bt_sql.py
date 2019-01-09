#bierteller sql functions
def database_read():
 timestamp("Connecting with SQL-server")
 data=[]
 info_format_list=[]
 try: 
  db = MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_pw,db=db_db)
  cursor = db.cursor()
  retrieve = "SELECT "+', '.join(bierteller['tap'])+", "+ ', '.join(bierteller['dtap'])+" FROM log ORDER BY tijd DESC LIMIT 1" 
  # latest data plz
  #	tijd 	  			 	tap1 	tap2 	tap3 	tap4  dtap1 dtap2 dtap3 dtap4
  #	2016-04-16 03:33:54 	13452 	8761 	18296 	383 0 0 0 0 	
  cursor.execute(retrieve)
  result = cursor.fetchone()
  cursor.close()
  for i in range (0,2*amount_tap): 
   data.append(result[i])
  for i in range (0,amount_tap):
   bierteller['tapvorig']['tap'+str(i+1)+'vorig']=data[i] #previous values in dict
   bierteller['dtapvorig']['dtap'+str(i+1)+'vorig']=data[i+4] #previous values dtap in dict
   info_format_list.append("{d["+str(i)+"]}({d["+str(i+4)+"]})")
  info_format = " ".join(info_format_list)
  info = info_format.format(d=data)
  timestamp("Connected. Previous values from SQL: "+info)
  return True
 except MySQLdb.OperationalError as e: #Error while connecting to host.
  timestamp("Error: "+str(e[1]))
  return False 

 
def database_write(rollback=0):
 try:
  db = MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_pw,db=db_db)
  cursor = db.cursor()
  if (rollback ==1):
   cursor.close()
   db.rollback()
   
  if (rollback ==0):
   cursor.execute("INSERT INTO log (tijd, "+', '.join(bierteller['tap'])+', '+', '.join(bierteller['dtap'])+") VALUES ("+'%s, '*2*(amount_tap) + "%s)",(
   [timestamp()]+bierteller['tap'].values()+bierteller['dtap'].values()) )
   db.commit()
   cursor.close()
   db.close()
   timestamp("Written to SQL-database")
 except MySQLdb.OperationalError as e: #Error while connecting to host.
  timestamp("Error: "+str(e[1]))