"""Utility file to seed data from Mashery CSV data dump"""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from model import Environment, API, Call, Agg_Request, Request

from datetime import datetime

from model import connect_to_db, db
from server import app

import csv

def read_data_file():
    """Read data from CSV and return it for addition to various tables"""

    # Uncomment to open test file
    f = open('mashery_sm.csv')

    # Uncomment to open full file
    # f = open('mashery.csv')

    csv_f = csv.reader(f)

    return list(csv_f)

def create_call_code(row):

    if "list" in row[0]:
        call_code_prefix = 'lists'
    elif "emailmarketing" in row[0]:
        call_code_prefix = 'email'
    elif "contact" in row[0]:
        call_code_prefix = 'contacts'
    elif "eventspot" in row[0]:
        call_code_prefix = 'events'
    elif "info" in row[0]:
        call_code_prefix = 'account'
    elif "verified" in row[0]:
        call_code_prefix = 'verif'
    elif "library" in row[0]:
        call_code_prefix = 'libr'
    elif "partner" in row[0]:
        call_code_prefix = 'part'
    else:
        call_code_prefix = row[0]

    if "Production" in row[2]:
        call_code_suffix = 'prod'
    elif "Stage" in row[2]:
        call_code_suffix = 'stage'
    elif "L1" in row[2]:
        call_code_suffix = 'l1'
    elif "D1" in row[2]:
        call_code_suffix = 'd1'
    else:
        call_code_suffix = row[2]

    call_code = "{} ({})".format(call_code_prefix, call_code_suffix)
    return call_code

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

        try:
        # We need to add to the session or it won't ever be stored
        db.session.add_all([row1, row2, row3, row4])

        # Once we're done, we should commit our work
        db.session.commit()

        except IntegrityError:
            db.session.rollback()


def load_api(data):
    """Load values relating to the API as a whole."""

    # [[TODO: Don't issue api_id unless successful add]]

    row1 = API(
        api_name = 'Ecommerce API',
        env_id = 1,
        version = '2.2')

    row2 = API(
        api_name = 'Ecommerce API',
        env_id = 2,
        version = '2.2')

    row3 = API(
        api_name = 'Ecommerce API',
        env_id = 3,
        version = '2.2')

    row4 = API(
        api_name = 'Ecommerce API',
        env_id = 4,
        version = '2.3')

        try:
            db.session.add_all([row1, row2, row3, row4])
            db.session.commit()

        except IntegrityError:
            db.session.rollback()


def load_call(data):
    """Load values for an individual API call"""

    # Read data from csv file and insert rows
    # But skip the header row: data[0]
    for row in data[1:]:

        call_code = create_call_code(row)
        call_name = row[1]
        api_id = 1

        if "list" in row[0]:
            endpoint = '/lists'
            method = 'GET'
        elif "emailmarketing" in row[0]:
            endpoint = '/emailmarketing'
            method = 'GET'
        elif "contact" in row[0]:
            endpoint = '/contacts'
            method = 'GET'
        elif "eventspot" in row[0]:
            endpoint = '/eventspot'
            method = 'GET'
        elif "info" in row[0]:
            endpoint = '/account/info'
            method = 'GET'
        elif "verified" in row[0]:
            endpoint = '/account/verifiedemailaddresses'
            method = 'GET'
        elif "library" in row[0]:
            endpoint = '/libraries'
            method = 'GET'
        elif "partner" in row[0]:
            endpoint = '/partners'
            method = 'GET'
        else:
            endpoint = None
            method = None

        call = Call(call_code=call_code,
                  call_name=call_name,
                  api_id=api_id,
                  endpoint=endpoint,
                  method = method)

        # We need to add to the session or it won't ever be stored
        db.session.add(call)

    # Once we're done, we should commit our work
    db.session.commit()

def load_agg_request(data):
    """Load aggregate values for different calls and environments"""

    # Read data from csv file and insert rows
    for row in data[1:]:
        call_code = call_code = create_call_code(row)
        success_count = row[5]
        block_count = row[6]
        other_count = row[7]
        total_responses = row[8]
        avg_response_time = row[4]

        agg_request = Agg_Request(call_code=call_code,
                  success_count=success_count,
                  block_count=block_count,
                  other_count=other_count,
                  total_responses=total_responses,
                  avg_response_time=avg_response_time)

        # We need to add to the session or it won't ever be stored
        db.session.add(agg_request)

    # Once we're done, we should commit our work
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    data = read_data_file()
    # create_call_code(data)
    load_env(data)
    load_api(data)
    load_call(data)
    load_agg_request(data)
    # load_requests()
