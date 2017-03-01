import sqlalchemy
from sqlalchemy import func

from decimal import Decimal

import json

from model import Environment, API, Call, Request, Agg_Request, Customer, Developer, Application, App_Used
from model import connect_to_db, db

from datetime import datetime, timedelta

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
    """Given a environment filter and a type of status calculation to do, calculate the status, compare it to a range, and return the status attributes."""

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

    call_data = []

    for call in env_calls:
        this_call = {}
        this_call['call_id'] = call.call_id
        # TODO: If call_id has already been used, use the same call name, and add the success count
        this_call['call_name'] = get_call_name(call.call_id)
        this_call['percent_volume'] = round(call.success_count / env_total, 2)
        this_call['call_latency'] = call.avg_response_time
        this_call['date'] = call.date
        call_data.append(this_call)

    return call_data


def calc_arpu():
    """Calculate the revenue for a paying customer. In this case, with our anonymized data, this is just the customer.revenue value.

    Return this data as a list of dictionaries, one per paying customer."""

    # Retrieve all subscribing customers
    all_customers = db.session.query(Customer).filter(Customer.sub_status == 'paid').all()

    all_customer_data = []

    # Iterate through each customer and grab certain attributes
    for customer in all_customers:
        this_cust = {}
        this_cust['cust_id'] = customer.customer_id
        this_cust['revenue'] = customer.revenue

        all_customer_data.append(this_cust)

    return all_customer_data

def calc_ltv():
    """If a customer has a paid subscription, determine what their monthly revenue is, how long they've had the paid subscription, and multiply the two values to get LTV (life time value).

    Return this data as a list of dictionaries, one per paying customer."""

    # Retrieve all subscribing customers
    all_customers = db.session.query(Customer).filter(Customer.sub_status == 'paid').all()

    all_customer_data = []

    for customer in all_customers:
        this_cust = {}
        this_cust['cust_id'] = customer.customer_id
        this_cust['revenue'] = customer.revenue
        this_cust['sub_months'] = calc_date_length(customer.sub_start, customer.sub_end)
        this_cust['ltv'] = this_cust['revenue'] * this_cust['sub_months']

        all_customer_data.append(this_cust)

    return all_customer_data

def calc_conversion():
    """For paying customers (whether or not their subscription is currently active), determine if their subscription started within 30 days of their using an app. If so, that counts as an app-driven conversion and can be attributed to that app."""

    conversion_within_days = 30
    # Retrieve all subscribing customers
    all_customers = db.session.query(Customer).filter(Customer.sub_status == 'paid').all()

    # Initialize an empty list to hold app_id's and the number of customers they converted
    all_app_conversions = {}
    counter = 0

    # Iterate through each paying customer.
    for customer in all_customers:
        # Find their subscription start date.
        cust_id = customer.customer_id
        sub_start = customer.sub_start
        # Retrieve any apps they have used, and the start time for each app
        all_cust_apps = db.session.query(App_Used).filter(App_Used.customer_id == cust_id).all()
        # Loop through each app a customer uses
        for app in all_cust_apps:
            this_app = {}
            app_id = app.app_id
            app_id_str = str(app.app_id)
            use_start = app.use_start

            # Determine if any sub start date is within 30 days of the app start date
            if sub_start < use_start + timedelta(days=conversion_within_days):
                # If so, check to see if that app is in the list already
                if app_id in all_app_conversions:
                    this_app['counter'] = this_app.get('counter', 0) + 1
                    # print 'I am in the list already'
                # Increment the conversion counter for any other app they
                # used within the 30 days.
                all_app_conversions[app_id_str] = this_app
                # Clear the this_app container

    # Return a list of apps and their counter values
    # That counter value determines the x axis of the bubble
    return all_app_conversions

def calc_retention():
    # Iterate through each paying customer.
    # Find their subscription duration.
    # Retrieve any apps they have used.
    # Retention = customers with apps remain paying customers longer
    # Retention per app = customers with certain apps remain paying
    #   customers even longer than the app average
    # That counter value determines the y axis of the bubble?
    # Non-app retention with be a constant in this case
    pass

def calc_date_length(start_date, end_date):
    """Given a date range, calculate the number of days between them. Divide by 30 to get the number of months (with no remainder)."""

    # If a subscription is still active, it has no end_date. In that case,
    # set the end_date equal to today's date for our calculations.
    if end_date is None:
        end_date = datetime.today()

    elapsed_time = end_date - start_date

    # Convert the datetime object to a Decimal containing the number of days
    elapsed_time_days = Decimal(elapsed_time.days)

    # Subscriptions are billed once per 30 day period, so we can throw away
    # the remainder and just look at the number of months
    num_of_months = elapsed_time_days // Decimal(30)

    return num_of_months


def get_app_data(env_filter, date):
    # In progress
    env_filter = env_filter
    date = date

    apps = db.session.query(Agg_Request).filter(Agg_Request.env_id == env_filter).group_by(Agg_Request.aggr_id).all()
