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

from server_functions import get_agg_request, get_env_total, calc_call_volume, get_weighted_avg_latency, get_status, get_call_name, create_call_row

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

    # Get dictionay of status attributes by passing in the env_id and the
    # status type: overall, performance, or outreach
    overall_status = get_status(1, 'overall')
    performance_status = get_status(2, 'performance')
    outreach_status = get_status(4, 'outreach')

    # Pass dictionary containing status color, rating, and icon to template.
    return render_template("homepage.html", overall_status=overall_status, performance_status=performance_status, outreach_status=outreach_status)


@app.route('/env')
def calls_by_env():
    """Chart of API calls by environment."""

    # Retrieve request objects for calls in each environment
    prod_calls = create_call_row(1)

    stage_calls = create_call_row(2)

    internal_calls = create_call_row(4)

    return render_template("env.html", prod_calls=prod_calls, stage_calls=stage_calls, internal_calls=internal_calls)


@app.route('/type')
def calls_by_type():
    """Chart of API calls by developer type."""

    env_filter = '%prod%'

    requests = db.session.query(Request).filter(Request.call_code.like(env_filter)).group_by(Request.aggr_id).all()

    success_totals = db.session.query(db.func.sum(Request.success_count).label('total')).filter(Request.call_code.like(env_filter)).group_by(Request.aggr_id).all()

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
