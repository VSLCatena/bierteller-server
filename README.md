# bierteller-server
 Flowguard has mounted a volume counter at the side of our beer cooling. This device, the FGFM8B‏, can be accessed using a serial connection. A Raspberry Pi can be used to access this data and upload it to anything. From there you can do everything with this data.  
 
 The data has been recoded twice due to enormous programming errors and low fault tolerance. The latest version 2.4c, splits the essential modules and is written for Python 3.x.
 
## Instructions
 
* Clone repo
* Install requirements
  * sudo apt-get install screen (optional)
  * sudo apt-get purge python (not needed)
  * sudo apt-get install python3-setuptools python3-dev
  * sudo easy_install3 pip (for third party python modules)
  * sudo pip install pyserial (essential serial connection)
    * https://pythonhosted.org/pyserial/
  * sudo pip install mysqlclient (optional for mysql)
  * sudo pip install google-api-python-client oauth2client google-auth google-auth-oauthlib google-auth-httplib2 (optional for gsheets)
* Fill in settings.cfg (example of default)

    [databases]

    write_mysql=false

    write_csv=true

    write_gsheets=false

    read=csv

    [mysqldb]

    host=

    port=0

    username=

    password=

    database=

    [general]

    amount_tap=4

    [debug]

    #NONE, DEBUG,INFO,WARNING,ERROR,CRITICAL

    console = WARNING

    log= INFO

    [gsheets]

    spreadsheet_id=

    range_name=

* If you are using gsheets, get credentials for the API.
* Open screen session as root (recommended) as "screen -dmS bier ./bierteller.sh"
  * Bierteller.sh just cd to directory and execute python as below.
* Go to directory and execute "python3 -i bierteller.py" (-i will not quit Python when error has occured)
* Profit!



## Changelog:

  * 3.0: Rewrite bt_gsheets.py due to changes in google api
  * 2.5: Hourly upload added
  * 2.4c: Add buffer=None right after del buffer in function bt_serial/decode() 
  * 2.4b: Removed quit() after Exception has occured
  * 2.4: Rewritten code to Python3 and split modules.
  * 2.3: Remove validation
  * 2.2: ?
  * 2.1: Fix hostname errors 
  * 2.0: Rewritten code, made functions, error exceptions, integer, english, timestamps, new way to find correction factor, rewritten decode (error was in previous)
  * 1.2: Better correction for minute check, read buffersize
  * 1.1: Read 4056 buffer, updated serial connection
  * 1.0: ? Got new PIC chip for Flowguard device. 
  * 0.X: Initial version [Open serial, open csv-file, write "a" to Flowguard device, read output (27bytes), decode with binascii.b2a_hex and store data to file] 
