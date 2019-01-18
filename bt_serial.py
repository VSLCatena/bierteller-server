#!/usr/bin/python
# -*- coding: utf-8 -*-
# bierteller serial class
#
# ---------------


# Standard library imports.
import serial


#Related third party imports.

#Local application/library specific imports.
from bt_general import *


# ---------------



class Bierteller_serial(object):

    def __init__(self):
        self.con=None
        self.buffer=None
        self.bufferTimestamp=None
        self.decodeTimestamp=None
        self.tapvalues=None
        
        self.create() 

        

     
        
    #
    # Creating serial instance
    #
    # input:
    # output: serial object
    #
    def create(self):
        if self.con==None:
            try:
                con = serial.Serial(None, 19200, timeout=1)  # initialized serial connection
                con.port = '/dev/ttyS0'
                timestamp('[serial_create]-> Serial initialized. Port is still closed')
                self.con=con
            except Exception as e:
                timestamp('[serial_create]-> Error while initializing serial: \n' + str(e))
                del self.con
                self.con=None
        else:
            timestamp('[serial_create]-> Error. Serial object already exist')

    #
    # Destroy serial instance
    #
    # input: object
    # output:
    #
    def destroy(self):
        try:         
            del self.con
            time.sleep(1)
            timestamp('[serial_close]-> Force closed. Serial object needs to be manually created with "create"-method.')
            self.con = None
        except Exception as e:
            timestamp('[serial_destroy]-> Error while destroying object serial: \n' + str(e))


    #
    # Opening serial port
    # ....
    # input:
    # output: open port of object
    #
    def open(self):
        try:
            self.con.open()
            timestamp('[open]-> Port opened.')
        except Exception as e:
            timestamp('[open]-> Error while opening serial port: \n' + str(e))


    #
    # closing serial port
    #
    # input: force
    # output: close port or delete object
    #
    def close(self, force=False):
        try:
            self.con.close()
            if force == True:
                self.destroy()
            else:
                timestamp('[close]-> Port has been closed. Reopen with "open"-method.')
        except Exception as e:
            timestamp('[close]-> Error while closing serial port: \n' + str(e))

    #
    # closing serial port
    #
    # input: force
    # output: close port or delete object
    #
    def check_port(self,tryopen=False):
        if(self.con.is_open==False):
            timestamp('[check_port]-> Port is closed')
            if tryopen==True:
                try:
                    timestamp('[check_port]-> Trying to open port..')
                    self.open() 
                    return True
                except Exception as e:
                    return False
        else:
            timestamp('[check_port]-> Port is already open')
            return True

    #
    # checking serial buffer
    #
    # input:
    # output:
    #
    def check_buffer(self,tryread=False):
        buffersize = 0
        max_retries = 8
        i = 0
        if(self.check_port(True)):
            self.con.reset_input_buffer()
            timestamp('[check_buffer]-> Flushing and checking buffer... ')            
            while (buffersize < 51) and (i < max_retries):  # correction for empty buffer or \r\n
                i += 1
                try:
                    buffersize = self.con.in_waiting
                except Exception as e:
                    timestamp('[check_buffer]-> Error: '+str(e))
                    break
                time.sleep(2)
                timestamp('[check_buffer]-> Status buffer: i:{}/{}, size:{}'.format(i,max_retries,buffersize))

            if (i >= max_retries) and (buffersize < 50):
                timestamp('[check_buffer]-> Error. Nothing found in buffer. Status:({},size:{}). Shutting down port.'.format(i,buffersize))
                self.close()
            else:
                if tryread==True:
                    self.read()
                else:
                    timestamp('[check_buffer]-> Success. Status:({},size:{}). Warning: It is recommended to immediately read the buffer, by using "True" as argument.'.format(i,buffersize))
                    self.close()

    #
    # Opening serial port
    #
    # input:
    # output: buffer
    #

    def read(self):
        linesize = 0
        max_retries = 6
        i = 0
        try:
            timestamp('[read]-> Reading buffer')
            while (linesize <= 4) and (i < max_retries):
                self.buffer = self.con.readline()
                self.bufferTimestamp = timestamp(type='short')
                linesize=len(self.buffer)
                if (linesize <= 4):
                    time.sleep(2)
                if (linesize >= 4):
                    break
            self.close()
            if (linesize <4):
                timestamp('[read]-> Too many empty lines in buffer. Shutting down port. \n')
                raise Exception
        except Exception as e:
            timestamp('[read]-> Error while reading serial port: \n' + str(e))
    
    
    #
    # decoding serial data
    #
    # input: buffer
    # output:
    #
    def decode(self,delete_buffer=True):
        timestamp('[decode]-> Decoding data')
        try:
            b_trim = self.buffer[15:31]
            b_bytelist = [b_trim[i:i + 1] for i in range(len(b_trim))]  # create [list of bytes]
            b_intlist = [ord(x) for x in b_bytelist]  # translate [list of bytes] to [list of integers]
            self.tapvalues = [b_intlist[x] + b_intlist[x + 1] * 256 for x in range(0, 16, 2)]  # [first integer + second integer *256], etc
            self.decodeTimestamp=timestamp()
            timestamp('[decode]-> Success.')
            del self.buffer
            self.buffer=None
        except Exception as e:
            timestamp('[decode]->  Error while decoding: \n' + str(e))
