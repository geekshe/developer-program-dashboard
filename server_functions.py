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


def get_agg_request(sql_filter):
    """Retrieves request objects for a specified environment"""

    sql_filter = sql_filter

    requests = db.session.query(Agg_Request).filter(Agg_Request.env_id == sql_filter).group_by(Agg_Request.aggr_id).all()

    return requests


def get_env_total(sql_filter):

    sql_filter = sql_filter

    success_totals = db.session.query(db.func.sum(Agg_Request.success_count).label('total')).filter(Agg_Request.env_id == sql_filter).group_by(Agg_Request.aggr_id).all()

    env_total = Decimal(0)

    for success_total in success_totals:
        env_total += Decimal(success_total.total)

    return env_total


def calc_call_volume(sql_filter):

    sql_filter = sql_filter

    env_requests = get_agg_request(sql_filter)
    env_total = get_env_total(sql_filter)

    env_call_volumes = {}
    for request in env_requests:
        env_call_volumes[request.call_id] = Decimal(request.success_count) / env_total

    return env_call_volumes


def get_weighted_avg_latency(sql_filter):

    sql_filter = sql_filter

    # Get the latency for each call. Returns a list.
    all_latency = db.session.query(Agg_Request.avg_response_time).filter(Agg_Request.env_id == sql_filter).all()

    # Intitialize the total_latency variable
    total_latency = Decimal(0)

    # Get the volume percent for each call
    # Returns a dictionary
    env_call_volumes = calc_call_volume(sql_filter)

    # Multiply the latency by the volume percent for each call
    # Add those together and divide by the number of calls
    # Return the weighted latency

    weighted_avg_latency = Decimal(0)

    for key in env_call_volumes:
        for latency in all_latency[0]:
            weighted_avg_latency += (env_call_volumes[key] * latency) / Decimal(len(all_latency))

    return weighted_avg_latency

    # avg_latency = total_latency / len(all_latency)

def calc_rating(sql_filter, status_type):

    sql_filter = sql_filter
    status_type = status_type

    return rating


def calc_latency(env):
    pass


def get_status(sql_filter, status_type):

    sql_filter = sql_filter
    status_type = status_type

    avg_latency = get_weighted_avg_latency(sql_filter)

    if avg_latency < 200:
        status = 'green'
        status_icon = 'fa-check-square'
    elif 200 <= avg_latency < 800:
        status = 'yellow'
        status_icon = 'fa-exclamation'
    elif avg_latency >= 800:
        status = 'red'
        status_icon = 'fa-flash'

    return status, status_icon
