"""Utility file to seed data from Mashery CSV data dump"""

from sqlalchemy import func
from model import Environment, API, Call, Agg_Request, Request

from datetime import datetime

from model import connect_to_db, db
from server import app

def read_data_file():
    """Read data from CSV and return it for addition to various tables"""

    import csv
    f = open('mashery_sm.csv')
    csv_f = csv.reader(f)

    return list(csv_f)


def load_env(data):
    """Load API values. In this case, they don't come from the CSV file, but
       are the same for each row in that file."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate api lines
    Environment.query.delete()

    # Read u.user file and insert data
    for row in data:

        if data[2] == "AppConnect Production":
            env_name = 'Production'
            env_base_url = 'https://api.constantcontact.com/v2'
        else:
            env_name = 'Sandbox'
            env_base_url = 'https://api.constantcontact.com/sandbox'

        environment = Environment(env_name=env_name,
                  env_base_url=env_base_url)

        # We need to add to the session or it won't ever be stored
        db.session.add(environment)

    # Once we're done, we should commit our work
    db.session.commit()


def load_api(data):
    """Load API values. In this case, they don't come from the CSV file, but
       are the same for each row in that file."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate api lines
    API.query.delete()

    # Read u.user file and insert data
    for row in data:

        api_name = 'Constant Contact API'
        if data[2] == "AppConnect Production":
            q = Environment.query.filter_by(env_name='Production').one()
            env_id = q[0]
        else:
            q = Environment.query.filter_by(env_name='Sandbox').one()
            env_id = q[0]
        if 'v2' in data[0]:
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


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    data = read_data_file()
    load_env(data)
    # load_api(data)
    # load_call(data)
    # load_agg_requests(data)
    # load_requests()
