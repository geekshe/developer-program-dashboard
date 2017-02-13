"""Utility file to seed data from Mashery CSV data dump"""

from sqlalchemy import func
from model import Environment, API, Call, Agg_Request, Request

from datetime import datetime

from model import connect_to_db, db
from server import app

import csv

def read_data_file():
    """Read data from CSV and return it for addition to various tables"""

    f = open('mashery_sm.csv')
    csv_f = csv.reader(f)

    return list(csv_f)


def load_env(data):
    """Load API values. In this case, they don't come from the CSV file, but
       are the same for each row in that file."""

    # Hard-code data as it never changes
    row1 = Environment(
        env_id = 1,
        env_name = 'Production',
        env_base_url = 'https://api.constantcontact.com/v2')

    row2 = Environment(
        env_id = 2,
        env_name = 'Staging',
        env_base_url = 'https://api.constantcontact.com/staging')

    row3 = Environment(
        env_id = 3,
        env_name = 'Partner',
        env_base_url = 'https://api.constantcontact.com/L1')

    row4 = Environment(
        env_id = 4,
        env_name = 'Internal',
        env_base_url = 'https://api.constantcontact.com/D1')

        # We need to add to the session or it won't ever be stored
    db.session.add_all([row1, row2, row3, row4])

        # Once we're done, we should commit our work
    db.session.commit()


def load_api(data):
    """Load values relating to the API as a whole."""

    # [[TODO: Merge identical lines into the DB]]
    # [[TODO: Skip header row]]

    # Read data from csv file and insert rows
    # header_row = next(data)  // Syntax to skip header not working on list
    for row in data[1:]:

        api_name = 'Constant Contact API'
        if "Production" in row[2]:
            env_id = 1
        elif "Stage" in row[2]:
            env_id = 2
        elif "L1" in row[2]:
            env_id = 3
        elif "D1" in row[2]:
            env_id = 4
        else:
            env_id = 1

        if 'v2' in row[0]:
            version = 'v2'
        else:
            version = 'v1'

        api = API(api_name=api_name,
                  env_id=env_id,
                  version=version)

        # We need to add to the session or it won't ever be stored
        db.session.add(api)

    # Once we're done, we should commit our work
    db.session.commit()


def load_call(data):
    """Load values for an individual API call"""

    # Read data from csv file and insert rows
    header_row = next(data)

    for row in data:
        if "list" in row[0]:
            call_code_prefix = 'lists'
            endpoint = '/lists'
            method = 'GET'
        elif "email" in row[0]:
            call_code_prefix = 'email'
            endpoint = '/emailmarketing'
            method = 'GET'
        elif "contact" in row[0]:
            call_code_prefix = 'contacts'
            endpoint = '/contacts'
            method = 'GET'
        elif "eventspot" in row[0]:
            call_code_prefix = 'events'
            endpoint = '/eventspot'
            method = 'GET'
        elif "info" in row[0]:
            call_code_prefix = 'account'
            endpoint = '/account/info'
            method = 'GET'
        elif "verified" in row[0]:
            call_code_prefix = 'email_ver'
            endpoint = '/account/verifiedemailaddresses'
            method = 'GET'
        else:
            call_code_prefix = 'other'
            endpoint = None
            method = None

        if "Production" in row[2]:
            call_code_suffix = 'prod'
        elif "Stage" in row[2]:
            call_code_suffix = 'stage'
        elif "L1" in row[2]:
            call_code_suffix = 'l1'
        elif "D1" in row[2]:
            call_code_suffix = 'd1'
        else:
            call_code_suffix = 'other'

        call_code = "{}: {}".format(call_code_prefix, call_code_suffix)
        call_name = row[1]
        api_id = 1

        call = Call(call_code=call_code,
                  call_name=call_name,
                  api_id=api_id,
                  endpoint=endpoint,
                  method = method)

        # We need to add to the session or it won't ever be stored
        db.session.add(call)

    # Once we're done, we should commit our work
    db.session.commit()

# def load_agg_request(data):
#     """Load aggregate values for different calls and environments"""

#     # Read data from csv file and insert rows
#     # header_row = next(data)
#     for row in data:
#         call_code = row.get_call_code()
#         success_count = row[5]
#         block_count = row[6]
#         other_count = row[7]
#         total_responses = row[8]
#         avg_response_time = row[4]


#         agg_request = Agg_Request(call_code=call_code,
#                   success_count=success_count,
#                   block_count=block_count,
#                   other_count=other_count,
#                   total_responses=total_responses,
#                   avg_response_time=avg_response_time)

#         # We need to add to the session or it won't ever be stored
#         db.session.add(call)

#     # Once we're done, we should commit our work
#     db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    data = read_data_file()
    load_env(data)
    load_api(data)
    load_call(data)
    # load_agg_request(data)
    # load_requests()
