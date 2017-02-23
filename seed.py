"""Utility file to seed data from Mashery CSV data dump"""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from model import Environment, API, Call, Agg_Request, Request, Customer, Developer, Application, App_Used

from datetime import datetime

from model import connect_to_db, db
from server import app

from decimal import Decimal

import csv

import json


def read_json_file():
    """Read JSON file for use in creating tables."""

    json_string = open('full_schema.json').read()

    return json.loads(json_string)


def read_csv_file():
    """Read data from CSV and return it for addition to various tables"""

    # Uncomment to open test file
    f = open('mashery_sm.csv')

    # Uncomment to open full file
    # f = open('mashery.csv')

    # Uncomment to open full schema file
    # f = open('full_schema.csv')

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


def load_customer(data):
    """Create customer table"""

    for row in data[1:]:
        customer = row['customer']

        username = customer['username']
        first_name = customer['first_name']
        last_name = customer['last_name']
        email = customer['email']
        city = customer['city']
        state = customer['state']
        country = customer['country']
        sub_status = customer['sub_status']
        sub_level = customer['sub_level']

        str_revenue = customer['revenue']
        if str_revenue is not None:
            revenue = Decimal(str_revenue.strip('$'))
        else:
            revenue = None

        sub_start = customer['sub_start']
        sub_end = customer['sub_end']

        cust = Customer(username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        city=city,
                        state=state,
                        country=country,
                        sub_status=sub_status,
                        sub_level=sub_level,
                        revenue=revenue,
                        sub_start=sub_start,
                        sub_end=sub_end)

        try:
            db.session.add(cust)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()


def load_developer(data):
    """Create developer table"""

    for row in data[1:]:
        developer = row['developer']

        username = developer['username']
        first_name = developer['first_name']
        last_name = developer['last_name']
        email = developer['email']
        company = developer['company']
        city = developer['city']
        state = developer['state']
        country = developer['country']
        dev_type = developer['dev_type']

        dev = Developer(username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        company=company,
                        city=city,
                        state=state,
                        country=country,
                        dev_type=dev_type)

        try:
            db.session.add(dev)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()


def load_application(data):
    """Create application table"""

    for row in data[1:]:
        application = row['app']

        app_name = application['app_name']
        app_type = application['app_type']
        dev_id = application['dev_id']
        application_id = application['application_id']

        app = Application(app_name=app_name,
                          app_type=app_type,
                          dev_id=dev_id,
                          application_id=application_id)

        try:
            db.session.add(app)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()


def load_app_used(data):
    """Create association table for customers and the apps they use"""

    for row in data[1:]:
        customer = row['customer']

        for num in range(1, 4):
            app_node = 'app_{}'.format(num)
            app = customer[app_node]

            if app['app_id']:
                customer_id = customer['customer_id']
                app_id = app['app_id']
                use_start = app['use_start']
                use_end = app['use_end']

                app_used = App_Used(customer_id=customer_id,
                                    app_id=app_id,
                                    use_start=use_start,
                                    use_end=use_end)

                try:
                    db.session.add(app_used)
                    db.session.commit()

                except IntegrityError:
                    db.session.rollback()


def load_env(data):
    """Load API values. In this case, they don't come from the CSV file, but
       are the same for each row in that file."""

    # Hard-code data as it never changes
    row1 = Environment(
        env_id=1,
        env_name='Production',
        env_base_url='https://api.constantcontact.com/v2')

    row2 = Environment(
        env_id=2,
        env_name='Staging',
        env_base_url='https://api.constantcontact.com/staging')

    row3 = Environment(
        env_id=3,
        env_name='Partner',
        env_base_url='https://api.constantcontact.com/L1')

    row4 = Environment(
        env_id=4,
        env_name='Internal',
        env_base_url='https://api.constantcontact.com/D1')

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
        api_name='Ecommerce API',
        env_id=1,
        version='2.2')

    row2 = API(
        api_name='Ecommerce API',
        env_id=2,
        version='2.2')

    row3 = API(
        api_name='Ecommerce API',
        env_id=3,
        version='2.2')

    row4 = API(
        api_name='Ecommerce API',
        env_id=4,
        version='2.3')

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
        call = row['call']

        call_name = call['call_name']
        env_id = call['env_id']
        key_type = call['key_type']
        latency = call['latency']
        success = call['success']
        fail = call['fail']
        date = call['date']

        call = Call(call_name=call_name,
                    env_id=env_id,
                    key_type=key_type,
                    latency=latency,
                    success=success,
                    fail=fail,
                    date=date)

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
    # data = read_csv_file()
    data = read_json_file()
    # create_call_code(data)
    load_customer(data)
    load_developer(data)
    load_application(data)
    load_app_used(data)
    load_env(data)
    load_api(data)
    load_call(data)
    # load_agg_request(data)
    # load_requests()
