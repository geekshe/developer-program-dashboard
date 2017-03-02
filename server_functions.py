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

    # Retrieve all subscribing customers. Returns list of customer objects
    all_customers = get_paying_customers()

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

    # Retrieve all subscribing customers. Returns list of customer objects
    all_customers = get_paying_customers()

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

    # Retrieve all subscribing customers. Returns list of customer objects
    all_customers = get_paying_customers()

    # Initialize an empty list to hold app_id's and the number of customers they converted
    all_app_conv_count = {}

    # Iterate through each paying customer.
    for customer in all_customers:
        # Find their subscription start date.
        cust_id = customer.customer_id
        sub_start = customer.sub_start

        # Retrieve any apps they have used, and the start time for each app.
        # Returns list of App_Use objects (up to three)
        all_cust_apps = db.session.query(App_Used).filter(App_Used.customer_id == cust_id).all()

        # Loop through each app a customer uses
        for app in all_cust_apps:
            app_id = app.app_id
            app_id_str = str(app.app_id)  # Stringify app_id for use as a key
            use_start = app.use_start

            # Determine if any sub start date is within 30 days of the app start date
            conv_test_pass = conversion_test(sub_start, use_start)

            if conv_test_pass:
                # If so, check to see if that app_id number is a key in the list already
                if app_id_str in all_app_conv_count:
                    # Assign a name to outer dictionary to avoid confusion
                    app_id_dict = all_app_conv_count[app_id_str]
                    # Retrieve the counter value and add one to it
                    app_id_dict['counter'] = app_id_dict.get('counter', 0) + 1
                else:
                    # If not in the main dictioary, add it with the inital counter value of 1
                    all_app_conv_count[app_id_str] = {'counter': 1, 'app_name': get_app_name(app_id)}

    # Return the dictionary of apps and their counter values
    # That counter value determines the x axis of the bubble chart
    return all_app_conv_count


def conversion_test(sub_start, use_start, num_days=30):
    """Give the paid subscription start date and """

    sub_start = sub_start
    use_start = use_start
    num_days = num_days
    conversion = False

    if sub_start < use_start + timedelta(days=num_days):
        conversion = True
    return conversion


def get_app_name(app_id):
    "Given the app_id value, retrieve the app_name for that app."

    app_id = app_id
    app_obj = db.session.query(Application.app_name).filter(Application.app_id == app_id).one()

    return app_obj.app_name

def get_paying_customers():
    """Query the DB for all customers whose subscription status is 'paid'"""

    paying_customers = db.session.query(Customer).filter(Customer.sub_status == 'paid').all()

    return paying_customers

def calc_retention():
    """Calculate retention (how many months of subscription) for paying customers who use apps"""

    # Retrieve all subscribing customers. Returns list of customer objects
    all_customers = get_paying_customers()

    # Initialize an empty list to hold app_id's and the subscription
    # length of their customers
    all_app_retention = {}

    # Iterate through each paying customer.
    for customer in all_customers:
        cust_id = customer.customer_id
        # Find their subscription duration.
        sub_length = calc_date_length(customer.sub_start, customer.sub_end)

        # Retrieve any apps they have used.
        # Returns list of App_Use objects (up to three)
        all_cust_apps = db.session.query(App_Used).filter(App_Used.customer_id == cust_id).all()

        # Loop through each app a customer uses
        for app in all_cust_apps:
            app_id = app.app_id
            app_id_str = str(app.app_id)  # Stringify app_id for use as a key

            if app_id_str in all_app_retention:
                all_app_retention[app_id_str].append({'cust_id': cust_id, 'retention_months': sub_length})
            else:
                all_app_retention[app_id_str] = [{'cust_id': cust_id, 'retention_months': sub_length}]

    return all_app_retention


def calc_average_retention():
    """Given apps and the retention values for their customers, calculate the average for that app"""

    all_apps = calc_retention()

    avg_retention = {}

    for app_id_str in all_apps:
        cust_values = all_apps[app_id_str]
        app_retention_total = 0
        for value in cust_values:
            app_retention_total += value['retention_months']
        app_avg_retention = app_retention_total / len(cust_values)
        avg_retention[app_id_str] = {'app_avg_retention': round(app_avg_retention, 0)}

    # Retention = customers with apps remain paying customers longer
    # Retention per app = customers with certain apps remain paying
    #   customers even longer than the app average
    # That counter value determines the y axis of the bubble
    # Non-app retention will be a constant in this case
    return avg_retention

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


# def get_app_data(env_filter, date):
#     # In progress
#     env_filter = env_filter
#     date = date

#     apps = db.session.query(Agg_Request).filter(Agg_Request.env_id == env_filter).group_by(Agg_Request.aggr_id).all()

def get_app_type(app_id):
    """Given an app_id, retrieve the app_type for that app """

    app_id = app_id

    app_obj = db.session.query(Application.app_type).filter(Application.app_id == app_id).one()

    return app_obj.app_type

def calc_app_contributions():
    pass