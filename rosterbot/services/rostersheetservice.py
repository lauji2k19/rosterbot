from __future__ import print_function
import asyncio
import pickle
import os.path
import json
import os
import operator
import socket
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from rosterbot.utils.generalhelpers import GeneralHelpers
from rosterbot.models import singleunit
from rosterbot.utils.ranks import Rank
from rosterbot.constants import ROSTER_SPREADSHEET_ID

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

ROSTER_SPREADSHEET_GID = '0'

class RosterSheetService:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('sheettoken.pickle'):
            with open('sheettoken.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('sheettoken.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()

    def safe_get(self, list, i):
        try:
            return list[i]
        except IndexError:
            return ''

    def read_roster(self, division):
        result = self.sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range=f"{division}!A2:F").execute()
        values = result.get('values', [])
        units = []
        row = 2
        for value in values:
            if (value[0] != ''):
                unit = singleunit.SingleUnit(value[0], value[1], value[2], self.safe_get(value, 3), self.safe_get(value, 4), self.safe_get(value, 5), row)
                units.append(unit)
                row += 1
        units.sort(reverse=True, key=operator.attrgetter('rank.value'))
        return units

    def read_roster_backup(self):
        result = self.sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range="Roster (Backup)!A2:F").execute()
        values = result.get('values', [])
        units = []
        row = 2
        for value in values:
            if (value[0] != ''):
                unit = singleunit.SingleUnit(value[0], value[1], value[2], value[3], value[4], value[5], row)
                units.append(unit)
                row += 1
        units.sort(reverse=True, key=operator.attrgetter('rank.value'))
        return units

    def push_to_roster(self, division, unit):
        units = self.read_roster(division)

        for each_unit in units:
            if unit.name.split()[-1] in each_unit.name:
                return f"Push to roster failed. There is already a unit with digits {unit.name.split()[-1]}. You will have to change your digits."

        next_row = len(units)+2
        range_string = f"{division}!$A{str(next_row)}"
        nameRequest = [[unit.name, unit.steam_id, unit.user_id, unit.activity_check, unit.loa, unit.long_loa]]
        body = {
            "majorDimension": "ROWS",
            "values": nameRequest
        }
        response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()
        return f"{unit.name} was pushed to the roster."

    def trigger_discord_update(self, division):
        body = {
            "majorDimension": "ROWS",
            "values": [["UPDATED"]]
        }
        response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=f"{division}!Z2", valueInputOption="USER_ENTERED", body=body).execute()
        return response

    def sort_roster_spreadsheet(self, division):
        units = self.read_roster(division)

        range_string = f"{division}!A2:{len(units)+1}"
        nameRequest = []
        for unit in units:
            nameRequest.append([unit.name, unit.steam_id, unit.user_id, unit.activity_check, unit.loa, unit.long_loa])
        body = {
            "majorDimension": "ROWS",
            "values": nameRequest
        }
        response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()

        self.trigger_discord_update(division)
        return units
    
    def find_in_roster(self, division, digits):
        units = self.read_roster(division)
        for unit in units:
            if digits in unit.name:
                return unit
        return None

    def find_in_roster_user_id(self, division, user_id):
        units = self.read_roster(division)
        for unit in units:
            if str(user_id) == unit.user_id:
                return unit
        return None
    
    def find_units_in_roster(self, division, user_ids):
        if isinstance(user_ids, list):
            str_user_ids = [str(id) for id in user_ids]
            all_units = self.read_roster(division)
            desired_units = []
            for unit in all_units:
                if unit.user_id in str_user_ids:
                    desired_units.append(unit)
            return desired_units
        else:
            unit = self.find_in_roster_user_id(division, user_ids)
            if unit is not None:
                return [unit]
            return []

    def get_check_active(self, division):
        result = self.sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range=f"{division}!Y1").execute()
        values = result.get('values', [])
        return values[0][0]

    def set_check_active(self, division, check_active):
        body = {
            "majorDimension": "ROWS",
            "values": [[check_active]]
        }
        response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=f"{division}!Y1", valueInputOption="USER_ENTERED", body=body).execute()
        return check_active

    def list_loa(self, division):
        units = self.read_roster(division)
        results = []
        for unit in units:
            if unit.loa == "TRUE" or unit.long_loa == "TRUE":
                results.append(unit)
        return results

    def manual_loa_status(self, division, user_id, is_loa):
        units = self.read_roster(division)
        for i in range(len(units)):
            if str(user_id) == units[i].user_id:
                range_string = f"{division}!E{str(i+2)}"
                body = GeneralHelpers.generate_request_body(is_loa)
                response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()
                if is_loa:
                    return f"<@{user_id}> is now on LOA."
                else:
                    return f"<@{user_id}> is no longer on LOA."
        return "Unit could not be found."

    def get_loa_form_prefilled_url(self, unit_name, user_id):
        result = self.sheet.values().get(spreadsheetId=ROSTER_SPREADSHEET_ID,
                                    range="LOA Request Fields!A1").execute()
        prefill_url = result.get('values', [])[0][0]
        unit_name = unit_name.replace(" ", "+")
        prefill_url = prefill_url.replace("nameFieldValue", unit_name)
        prefill_url = prefill_url.replace("userIDFieldValue", str(user_id))
        return prefill_url

    def set_activity_check(self, division, user_id, completed_check):
        units = self.read_roster(division)
        for i in range(len(units)):
            if str(user_id) == units[i].user_id:
                range_string = f"{division}!D{str(i+2)}"
                body = GeneralHelpers.generate_request_body(completed_check)
                response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()
                if completed_check:
                    return f"<@{units[i].user_id}> has completed the activity check."
                else:
                    return units[i].name + "'s activity check status has been set to FALSE."
        return "Unit could not be found."

    def set_unit_name(self, division, digits, new_name, user_id):
        units = self.read_roster(division)
        desired_unit = None
        for unit in units:
            if new_name.split()[-1] in unit.name and str(user_id) != unit.user_id:
                return f"Set name failed. There is already a unit with digits {new_name.split()[-1]}. Try a new set of digits."
            elif str(user_id) == unit.user_id:
                desired_unit = unit
        if (desired_unit != None):
            range_string = f"{division}!A{desired_unit.row_number}"
            body = GeneralHelpers.generate_request_body(new_name)
            response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()
            return f"{unit.name}'s new name is now {new_name}."
        return "Unit could not be found."

    def set_unit_steamid(self, division, digits, steam_id):
        unit = self.find_in_roster(division, digits)
        if (unit != None):
            range_string = f"B{unit.row_number}"
            body = GeneralHelpers.generate_request_body(steam_id)
            response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()
            return f"{unit.name}'s SteamID is now {steam_id}."
        return "Unit could not be found."
    
    def set_tasking_points(self, division, digits, points):
        unit = self.find_in_roster(division, digits)
        if (unit != None):
            range_string = f"F{unit.row_number}"
            body = GeneralHelpers.generate_request_body(points)
            response = self.sheet.values().update(spreadsheetId=ROSTER_SPREADSHEET_ID, range=range_string, valueInputOption="USER_ENTERED", body=body).execute()
            return f"{unit.name} now has {points} point(s)."
        return "Unit could not be found."
    
    def remove_from_roster(self, division, user_ids):
        units = self.find_units_in_roster(division, user_ids)
        if len(units) > 0:
            spreadsheet_data = []
            for i in range(len(units)):
                units[i].row_number -= i
                spreadsheet_data.append({
                    "deleteDimension": {
                        "range": {
                            "sheetId": self.get_division_gid(division),
                            "dimension": "ROWS",
                            "startIndex": units[i].row_number-1,
                            "endIndex": units[i].row_number
                        }
                    }
                })
            body = {"requests": spreadsheet_data}
            response = self.sheet.batchUpdate(spreadsheetId=ROSTER_SPREADSHEET_ID, body=body).execute()
            return units
        return "No units found."
    
    def get_division_gid(self, division):
        spreadsheet = self.sheet.get(spreadsheetId=ROSTER_SPREADSHEET_ID).execute()
        for sheet in spreadsheet["sheets"]:
            if division.upper() == sheet["properties"]["title"].upper():
                return sheet["properties"]["sheetId"]
        return None

    def add_division_sheet(self, division):
        body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": division.upper()
                        }
                    }
                }
            ]
        }
        response = self.sheet.batchUpdate(spreadsheetId=ROSTER_SPREADSHEET_ID, body=body).execute()
        self.set_check_active(division, False)
        return response

def main():
    obj = RosterSheetService()
    names = [["09", "4912", "", "STEAMID"], ["08", "4916", "", "STEAMID"]]
    body = {
        "majorDimension": "ROWS",
        "values": names
    }
    test = obj.push_to_roster(body)
    print(test)

def read_roster_test():
    obj = RosterSheetService()
    division = "BALLISTA"
    units = obj.read_roster(division)
    for unit in units:
        print(f"{unit.name}: {unit.steam_id}, {unit.user_id}")

def find_unit_test(digits):
    obj = RosterSheetService()
    unit = obj.find_in_roster(digits)
    print(unit.name)
    print(unit.row_number)

def list_loa_test():
    obj = RosterSheetService()
    loa_units = obj.list_loa()
    for unit in loa_units:
        print(unit.name)

def test_stuff(digits):
    obj = RosterSheetService()
    division = "BALLISTA"
    units = obj.read_roster(division)

    for unit in units:
        if digits in unit.name:
            print("Do stuff.")
            return "Done."
    
    return "Could not find the unit."

def manual_loa_test():
    obj = RosterSheetService()
    print(obj.manual_loa_status("bobby", True))

def remove_unit_test(digits):
    obj = RosterSheetService()
    print(obj.remove_from_roster(digits))

def set_unit_name_test(digits, new_name):
    obj = RosterSheetService()
    print(obj.set_unit_name(digits, new_name))

def sort_roster_spreadsheet_test():
    obj = RosterSheetService()
    division = "BALLISTA"
    sorted_roster = obj.sort_roster_spreadsheet(division)
    for unit in sorted_roster:
        print(unit.name)

def set_unit_steamid_test():
    obj = RosterSheetService()
    print(obj.set_unit_steamid("Tubular", "SteamID123"))

def update_backup_roster_test():
    obj = RosterSheetService()
    obj.update_backup_roster()

def read_roster_backup_test():
    obj = RosterSheetService()
    units = obj.read_roster_backup()
    for unit in units:
        print(unit.name)

def find_in_roster_user_id_test():
    obj = RosterSheetService()
    unit = obj.find_in_roster_user_id(214894631949828097)
    print(unit.name)

def set_check_active_test():
    obj = RosterSheetService()
    obj.set_check_active(True)
    print(obj.get_check_active())

if __name__ == '__main__':
    #main()
    #read_roster_test()
    #find_unit_test("Melzer")
    #set_unit_name_test("9863", "Test")
    #list_loa_test()
    #manual_loa_test()
    #remove_unit_test("Melzer")
    #sort_roster_spreadsheet_test()
    #set_unit_steamid_test()
    #update_backup_roster_test()
    #read_roster_backup_test()
    #find_in_roster_user_id_test()
    #set_check_active_test()
    print()