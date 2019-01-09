from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of spreadsheet.
SPREADSHEET_ID = '1FjM6QL8n3cn3ziIR4Su_CyzgGRtvghu7S1DFybbFDPE'
RANGE_NAME = 'A2:E'

def main(data):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    write(data,service)

def read():
    # Call the Sheets API
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s' % (row))
def write(data,service):

 list = data
 resource = {
  "majorDimension": "ROWS",
  "values": list
 }

 service.spreadsheets().values().append(
  spreadsheetId=SPREADSHEET_ID,
  range=RANGE_NAME,
  body=resource,
  valueInputOption="USER_ENTERED"
 ).execute()


if __name__ == '__main__':
    main(data)
