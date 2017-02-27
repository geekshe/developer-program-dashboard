import sqlalchemy
from sqlalchemy import func

from decimal import Decimal

import json

from model import Environment, API, Call, Request, Agg_Request, Customer, Developer, Application, App_Used
from model import connect_to_db, db

############################## Helper Functions ################################

# env_id 1 = production
# env_id 2 = staging
# env_id 3 = partner
# env_id 4 = internal


def get_agg_request(env_filter):
    """Retrieves request objects for a specified environment"""

    env_filter = env_filter

    requests = db.session.query(Agg_Request).filter(Agg_Request.env_id == env_filter).group_by(Agg_Request.aggr_id).all()

    return requests


def get_env_total(env_filter):

    env_filter = env_filter

    success_totals = db.session.query(db.func.sum(Agg_Request.success_count).label('total')).filter(Agg_Request.env_id == env_filter).group_by(Agg_Request.aggr_id).all()

    env_total = Decimal(0)

    for success_total in success_totals:
        env_total += Decimal(success_total.total)

    return env_total


def calc_call_volume(env_filter):

    env_filter = env_filter

    env_requests = get_agg_request(env_filter)
    env_total = get_env_total(env_filter)

    env_call_volumes = {}
    for request in env_requests:
        env_call_volumes[request.call_id] = Decimal(request.success_count) / env_total

    return env_call_volumes


def get_weighted_avg_latency(env_filter):

    env_filter = env_filter

    # Get the latency for each call. Returns a list.
    all_latency = db.session.query(Agg_Request.avg_response_time).filter(Agg_Request.env_id == env_filter).all()

    # Intitialize the total_latency variable
    total_latency = Decimal(0)

    # Get the volume percent for each call
    # Returns a dictionary
    env_call_volumes = calc_call_volume(env_filter)

    # Multiply the latency by the volume percent for each call
    # Add those together and divide by the number of calls
    # Return the weighted latency

    weighted_avg_latency = Decimal(0)

    for key in env_call_volumes:
        for latency in all_latency[0]:
            weighted_avg_latency += (env_call_volumes[key] * latency) / Decimal(len(all_latency))

    return weighted_avg_latency

    # avg_latency = total_latency / len(all_latency)


def calc_rating(env_filter, status_type):

    env_filter = env_filter
    status_type = status_type

    return rating


def calc_latency(env):
    pass


def get_status(env_filter, status_type):

    env_filter = env_filter
    status_type = status_type

    status_rating = {}

    status_rating['avg_latency'] = get_weighted_avg_latency(env_filter)

    # Compare avg_latency to a range of values.
    # Based on place in range, choose green/yellow/red icon.
    if status_rating['avg_latency'] < 200:
        status_rating['status_color'] = 'green'
        status_rating['rating'] = 9
        status_rating['status_icon'] = 'fa-check-square'
    elif 200 <= status_rating['avg_latency'] < 800:
        status_rating['status_color'] = 'yellow'
        status_rating['rating'] = 5
        status_rating['status_icon'] = 'fa-exclamation'
    elif status_rating['avg_latency'] >= 800:
        status_rating['status_color'] = 'red'
        status_rating['rating'] = 2
        status_rating['status_icon'] = 'fa-flash'

    return status_rating


def get_call_name(call_id):
    """Given a single call_id (which comes from the agg_request table) retrieve
        that call object (from the call table) and return the call_name.

        Retrieving the whole object allows more flexibility in what can be returned."""

    this_call_id = call_id
    this_call_name = db.session.query(Call).filter(Call.call_id == this_call_id).first()

    return this_call_name.call_name


def create_call_row(env_filter):

    env_filter = env_filter

    env_total = get_env_total(env_filter)

    # Object containing individual agg_requests
    env_calls = get_agg_request(env_filter)

    call_rows = []

    for obj in env_calls:
        row = {}
        row['call_id'] = obj.call_id
        # TODO: If call_id has already been used, use the same call name, and add the success count
        row['call_name'] = get_call_name(obj.call_id)
        row['percent_volume'] = round(obj.success_count / env_total, 2)
        row['call_latency'] = obj.avg_response_time
        row['date'] = obj.date
        call_rows.append(row)

    return call_rows
