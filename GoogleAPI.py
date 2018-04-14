
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

class google:
    def __init__(self, auth="r"):
        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
        scopes={"r" : 'https://www.googleapis.com/auth/spreadsheets.readonly',
                "rw" : 'https://www.googleapis.com/auth/spreadsheets'}
        self.SCOPES = scopes[auth]
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self.APPLICATION_NAME = 'GoogleAPI_Caerulea'
        self.credentials=None
        self.batch_update_values_request_body = {
            # How the input data should be interpreted.
            'value_input_option': 'RAW',  # TODO: Update placeholder value.

            # The new values to apply to the spreadsheet.
            'data': [],  # TODO: Update placeholder value.

            # TODO: Add desired entries to the request body.
        }

    def get_credentials(self):
        """Gets valid user credentials from storage.(Log in to google)

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-UserCredentials.json')
        store = Storage(credential_path)

        self.credentials = store.get()
        if not self.credentials or self.credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                self.credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                self.credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return self.credentials

    def getData(self, spreadsheetId, rangeName):
        """Shows basic usage of the Sheets API.

        Creates a Sheets API service object and prints the names and majors of
        students in a sample spreadsheet:
        https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
        """
        http = self.credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return None
        else:
            return values

    def setSheetId(self, spreadSheetId):
        self.spreadsheet_id = spreadSheetId  # TODO: Update placeholder value.

    def addData(self, range, input):
        #input should be 2-dim array
        # The ID of the spreadsheet to update
        #
        # # The A1 notation of the values to update.
        # range_ = range  # TODO: Update placeholder value.
        #
        # # How the input data should be interpreted.
        # value_input_option = 'RAW'  # TODO: Update placeholder value.
        #
        # value_range_body = {'values':input}
        # request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
        # response = request.execute()

        self.batch_update_values_request_body['data'].append(
        {
        'range' : range,
        'values' : input
        }
        )


    def updateData(self):
        service = discovery.build('sheets', 'v4', credentials=self.credentials)
        request = service.spreadsheets().values().batchUpdate\
            (spreadsheetId=self.spreadsheet_id, \
            body=self.batch_update_values_request_body)
        response = request.execute()

        # TODO: Change code below to process the `response` dict:
        # print(response)
        self.batch_update_values_request_body = {
            # How the input data should be interpreted.
            'value_input_option': 'RAW',  # TODO: Update placeholder value.

            # The new values to apply to the spreadsheet.
            'data': [],  # TODO: Update placeholder value.

            # TODO: Add desired entries to the request body.
        }

if __name__ == '__main__':
    googleconn=google(auth="rw")
    googleconn.get_credentials()
    spreadsheetId = '1eleX5jJmBgKzJkjz4d7TWHO_Y0eHR-Zbq8ywwJlBxJk'
    rangeName = 'A1:B5'
    res=googleconn.getData(spreadsheetId, rangeName)
    googleconn.writeData(spreadsheetId, "A7:B8", [["p", "q"], ["r", "s"]])
    print(res)
