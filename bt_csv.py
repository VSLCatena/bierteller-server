#!/usr/bin/python
# -*- coding: utf-8 -*-
# bierteller csv functions
#
# ---------------


# Standard library imports.
import csv
#Related third party imports.

#Local application/library specific imports.
from bt_general import *



# ---------------

def csv_simplify_dict(d):
    #'timestamp','tap1','tap2','tap3','tap4','dtap1','dtap2','dtap3','dtap4'
    csv_dict=OrderedDict(list(d['tap'].items())+list(d['dtap'].items()))
    return csv_dict


def csv_write(d, fieldnames=['timestamp','tap1','tap2','tap3','tap4','dtap1','dtap2','dtap3','dtap4']):
    try:
        with open('database.csv', 'a',newline='') as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames,delimiter=',',quotechar='\'', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(d)
        timestamp('[csv_write]-> Written to CSV-file') 
    except Exception as e:
        timestamp('Error while writing to CSV: \n' + str(e))

def csv_read(fieldnames=['timestamp','tap1','tap2','tap3','tap4','dtap1','dtap2','dtap3','dtap4']):
    try:
        with open('database.csv', 'r',newline='') as csvfile:
            reader = csv.DictReader(csvfile,fieldnames=fieldnames,delimiter=',',quotechar='\'', quoting=csv.QUOTE_NONNUMERIC)
            timestamp('[csv_read]-> Reading last row')
            for row in reader:
                continue
        try:
            row =  {k:int(row[k]) if isinstance(row[k],float) else row[k] for k in row.keys()}  #conversion of float to int
            timestamp('[csv_read]-> Success.')
            return row #last row
        except Exception as e:
            timestamp('[csv_read]-> Error in reader Object: \n' + str(e))
            return False
    except Exception as e:
        timestamp('[csv_read]-> Error reading rows: \n' + str(e))
