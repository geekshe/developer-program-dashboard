"""Developer Program Dashboard."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import Environment, API, Call, Agg_Request, Request, connect_to_db, db

import sqlalchemy
from sqlalchemy import func

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

################################################################################


@app.route('/')
def index():
    """Home page."""

    sql_filter = '%prod%'

    avg_latency = db.session.query(db.func.avg(Agg_Request.avg_response_time).label('avg_latency')).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    return render_template("homepage.html", avg_latency=avg_latency)


@app.route('/env')
def calls_by_env():
    """Chart of API calls by environment."""

    sql_filter = '%prod%'

    agg_requests = db.session.query(Agg_Request).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    success_totals = db.session.query(db.func.sum(Agg_Request.success_count).label('total')).filter(Agg_Request.call_code.like(sql_filter)).group_by(Agg_Request.aggr_id).all()

    env_total = 0

    for success_total in success_totals:
        env_total += success_total.total

    return render_template("calls.html", agg_requests=agg_requests, env_total=env_total)

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
