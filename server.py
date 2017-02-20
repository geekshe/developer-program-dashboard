"""Developer Program Dashboard."""

############################### Import Modules #################################
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

import sqlalchemy

from decimal import Decimal

import json

# Import my data model
from model import Environment, API, Call, Agg_Request, Request, connect_to_db, db

################################# Web App ######################################

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "lkkljasdienynfslkci"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

############################## Helper Functions ################################

def get_agg_request(sql_filter):

    # Retrieves agg_request objects for a specified environment
    agg_requests = db.session.query(Agg_Request).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    return agg_requests

def get_env_total(sql_filter):

    success_totals = db.session.query(db.func.sum(Agg_Request.success_count).label('total')).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    env_total = 0

    for success_total in success_totals:
        env_total += success_total.total

    return env_total


############################### Flask Routes ###################################

@app.route('/')
def index():
    """Home page."""

    sql_filter = '%prod%'

    all_latency = db.session.query(Agg_Request.avg_response_time).filter(Agg_Request.call_code.like(sql_filter)).all()

    total_latency = Decimal(0)

    for latency in all_latency:
        total_latency += latency[0]

    avg_latency = total_latency / len(all_latency)

    if avg_latency < 200:
        overall_status = 'green'
        status_icon = 'fa-check-square'
    elif 200 <= avg_latency < 800:
        overall_status = 'yellow'
        status_icon = 'fa-exclamation'
    elif avg_latency >= 800:
        overall_status = 'red'
        status_icon = 'fa-flash'

    # Compare avg_latency to a range of values. 
    # Based on place in range, choose green/yellow/red icon. 
    # Pass icon to template.

    return render_template("homepage.html", avg_latency=avg_latency, overall_status=overall_status, status_icon=status_icon)


@app.route('/env')
def calls_by_env():
    """Chart of API calls by environment."""

    # Retrieve agg_request objects for calls in the production environment

    prod_agg_requests = get_agg_request('%prod%')
    prod_total = get_env_total('%prod%')

    stage_agg_requests = get_agg_request('%l1%')
    stage_total = get_env_total('%l1%')

    internal_agg_requests = get_agg_request('%d1%')
    internal_total = get_env_total('%d1%')

    return render_template("calls.html", prod_agg_requests=prod_agg_requests, prod_total=prod_total, stage_agg_requests=stage_agg_requests, stage_total=stage_total, internal_agg_requests=internal_agg_requests, internal_total=internal_total)

@app.route('/prod.json')
def env_info():
    """Chart of API calls by environment."""

    # Retrieve agg_request objects for calls in the production environment

    prod_agg_requests = get_agg_request('%prod%')

    return jsonify(prod_agg_requests)

@app.route('/type')
def calls_by_type():
    """Chart of API calls by developer type."""

    sql_filter = '%prod%'

    agg_requests = db.session.query(Agg_Request).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    success_totals = db.session.query(db.func.sum(Agg_Request.success_count).label('total')).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    env_total = 0

    for success_total in success_totals:
        env_total += success_total.total

    return render_template("calls.html", agg_requests=agg_requests, env_total=env_total)

@app.route('/d3')
def show_apps_customers():
    """Show relationship of apps to their customers and vice versa."""

    return render_template("d3.html")

@app.route('/d3-force')
def show_apps():
    """Show relationship of apps to their customers and vice versa."""


    return render_template("d3-force.html", jsonify(graph.json))


################################################################################

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(port=5000, host='0.0.0.0')
