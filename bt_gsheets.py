#!/usr/bin/python
# -*- coding: utf-8 -*-
# bierteller gsheets functions
#
# ---------------


# Standard library imports.
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

#Related third party imports.

#Local application/library specific imports.
from bt_general import *

# ---------------

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# ---------------
     
        
def gsheets_basic(data,action,cfg):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    if(action=="write"):gsheets_write(data,cfg,service)
    if(action=="read"):gsheets_read(cfg)

def gsheets_read(cfg):
    # Call the Sheets API
    result = service.spreadsheets().values().get(spreadsheetId=cfg['spreadsheet_id'],range=cfg['range_name']).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s' % (row))
            
            
            
def gsheets_write(data,cfg,service):
    body = {
    "majorDimension": "ROWS",
    "values": [data]
    }

    result=service.spreadsheets().values().append(
        spreadsheetId=cfg['spreadsheet_id'],
        range=cfg['range_name'],
        body=body,
        valueInputOption="USER_ENTERED"
        ).execute()

