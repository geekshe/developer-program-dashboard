"""Developer Program Dashboard."""

############################### Import Modules #################################
import os
import twitter
from klout import *
import time

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

import sqlalchemy

import json

# Import my data model
from model import Environment, API, Call, Request, Agg_Request, Customer, Developer, Application, App_Used
from model import connect_to_db, db

# Import functions from the support file
from server_functions import get_agg_request, get_env_total, calc_call_volume, get_weighted_avg_latency, get_status, get_call_name, create_call_row, calc_ltv, calc_arpu, calc_date_length, calc_conversion, conversion_test, get_app_name, get_paying_customers, calc_retention, calc_average_retention, get_app_type, calc_app_contributions, calc_app_avg_ltv, calc_app_avg_arpu, filter_dict

################################# Web App ######################################

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "lkkljasdienjlkjlkjsadaiuoiqwqynfslkci"

# Raise an error if you use an undefined Jinja2 variable.
app.jinja_env.undefined = StrictUndefined

# configure Twitter API
api = twitter.Api(os.environ.get('TWITTER_CONSUMER_KEY'),
                  os.environ.get('TWITTER_CONSUMER_SECRET'),
                  os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
                  os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))

klout = Klout(os.environ.get('KLOUT_KEY'))

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
    prod_calls = create_call_row(1, '2017-02-08')

    stage_calls = create_call_row(2, '2017-02-08')

    internal_calls = create_call_row(4, '2017-02-08')

    return render_template("env.html", prod_calls=prod_calls, stage_calls=stage_calls, internal_calls=internal_calls)


@app.route('/bubble')
def apps_by_impact():
    """Bubble chart that displays app performance on 4 factors:
        1. conversion (x-axis)
        2. retention (y-axis)
        3. ltv (size)
        4. app type (color)

        Tooltips also include ARPU and LTV
    """

    asf = filter_dict()

    return render_template("bubble.html", asf=asf)


@app.route('/social')
def social():
    """Display social stats."""

    # Fetch klout ID
    klout_id = klout.identity.klout(screenName="geekshe").get('id')

    # fetch klout score
    klout_score = klout.user.score(kloutId=klout_id).get('score')

    # fetch 3 tweets from my account
    my_tweets = api.GetUserTimeline(screen_name='geekshe')

    # Pass tweetss to the social page
    return render_template("social.html", my_tweets=my_tweets, klout_score=klout_score)


@app.route('/map')
def map():
    """Show developer locations world wide."""

    # Render the map
    return render_template("map.html")

# @app.route('/d3')
# def show_apps_customers():
#     """Show relationship of apps to their customers and vice versa."""

#     return render_template("d3.html")


# @app.route('/d3-force-curve')
# def show_apps_curve():
#     """Show relationship of apps to their customers and vice versa."""

#     return render_template("d3-force-curve.html")


# @app.route('/miserables.json')
# def render_d3_relationships():
#     """Show relationship of apps to their customers and vice versa."""

#     json_string = open('miserables.json').read()

#     return json_string


# This is a jinja custom filter
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    pyDate = time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y')  # convert twitter date string into python date/time
    return time.strftime('%Y-%m-%d %H:%M:%S', pyDate)  # return the formatted date.

################################################################################

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.run(port=5000, host='0.0.0.0')
