"""Developer Program Dashboard."""

############################### Import Modules #################################
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

import sqlalchemy

from decimal import Decimal

import json

# Import my data model
from model import Environment, API, Call, Request, Agg_Request, Customer, Developer, Application, App_Used
from model import connect_to_db, db

from server_functions import get_agg_request, get_env_total, calc_call_volume, get_weighted_avg_latency

################################# Web App ######################################

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "lkkljasdienynfslkci"

# Raise an error if you use an undefined Jinja2 variable.
app.jinja_env.undefined = StrictUndefined

############################### Flask Routes ###################################

# env_id 1 = production
# env_id 2 = staging
# env_id 3 = partner
# env_id 4 = internal


@app.route('/')
def index():
    """Home page."""

    sql_filter = 1

    avg_latency = get_weighted_avg_latency(sql_filter)

    # Compare avg_latency to a range of values.
    # Based on place in range, choose green/yellow/red icon.

    if avg_latency < 200:
        overall_status = 'green'
        overall_status_icon = 'fa-check-square'
    elif 200 <= avg_latency < 800:
        overall_status = 'yellow'
        overall_status_icon = 'fa-exclamation'
    elif avg_latency >= 800:
        overall_status = 'red'
        overall_status_icon = 'fa-flash'

    # Pass icon to template.
    return render_template("homepage.html", overall_rating=overall_rating, overall_status=overall_status, overall_status_icon=overall_status_icon, performance_rating=performance_rating, performance_status=performance_status, performance_status_icon=performance_status_icon, outreach_rating=outreach_rating, outreach_status=outreach_status, outreach_status_icon=outreach_status_icon)


@app.route('/env')
def calls_by_env():
    """Chart of API calls by environment."""

    # Retrieve request objects for calls in the production environment

    prod_requests = get_request('%prod%')
    prod_total = get_env_total('%prod%')

    stage_requests = get_request('%l1%')
    stage_total = get_env_total('%l1%')

    internal_requests = get_request('%d1%')
    internal_total = get_env_total('%d1%')

    return render_template("env.html", prod_requests=prod_requests, prod_total=prod_total, stage_requests=stage_requests, stage_total=stage_total, internal_requests=internal_requests, internal_total=internal_total)

# @app.route('/prod.json')
# def env_info():
#     """Chart of API calls by environment."""

#     # Retrieve request objects for calls in the production environment

#     prod_requests = get_request('%prod%')

#     return jsonify(prod_requests)

@app.route('/type')
def calls_by_type():
    """Chart of API calls by developer type."""

    sql_filter = '%prod%'

    requests = db.session.query(Request).filter(Request.call_code.like(sql_filter)).group_by(Request.aggr_id).all()

    success_totals = db.session.query(db.func.sum(Request.success_count).label('total')).filter(Request.call_code.like(sql_filter)).group_by(Request.aggr_id).all()

    env_total = 0

    for success_total in success_totals:
        env_total += success_total.total

    return render_template("env.html", requests=requests, env_total=env_total)


@app.route('/d3')
def show_apps_customers():
    """Show relationship of apps to their customers and vice versa."""

    return render_template("d3.html")


@app.route('/d3-force-curve')
def show_apps_curve():
    """Show relationship of apps to their customers and vice versa."""

    return render_template("d3-force-curve.html")


@app.route('/miserables.json')
def render_d3_relationships():
    """Show relationship of apps to their customers and vice versa."""

    json_string = open('miserables.json').read()

    return json_string


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
