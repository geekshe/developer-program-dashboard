"""Models and database functions for Dev Program Dashboard project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions


class Environment(db.Model):
    """Environment (production/staging) an API operates in."""

    __tablename__ = "environment"

    env_id = db.Column(db.Integer, primary_key=True)
    env_name = db.Column(db.String(64), nullable=False, unique=True)
    env_base_url = db.Column(db.String(128), nullable=False, unique=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Environment env_id={} env_name={} env_base_url={}>".format(self.env_name,
                                                                       self.env_name,
                                                                       self.env_base_url)


class API(db.Model):
    """API provided by a company."""

    __tablename__ = "api"

    api_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    api_name = db.Column(db.String(64), nullable=False)
    env_id = db.Column(db.Integer,
                       db.ForeignKey("environment.env_id"),
                       nullable=False)
    version = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<API api_id={} api_name={} env_id={} version={}>".format(
                                                                       self.api_id,
                                                                       self.api_name,
                                                                       self.env_id,
                                                                       self.version)

    # Define relationship to call
    call = db.relationship("Call",
                           backref=db.backref("api",
                           order_by=api_id))
    environment = db.relationship("Environment",
                           backref=db.backref("api",
                           order_by=env_id))


class Call(db.Model):
    """A call from a company's API."""

    __tablename__ = "call"

    call_code = db.Column(db.String(128), primary_key=True)
    call_name = db.Column(db.String(128))
    api_id = db.Column(db.Integer,
                       db.ForeignKey("api.api_id"),
                       nullable=False)
    endpoint = db.Column(db.String(128))
    method = db.Column(db.String(10))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Call call_code={} call_name={} api_id={} endpoint={}, method={}>".format(
                                                                       self.call_code,
                                                                       self.call_name,
                                                                       self.api_id,
                                                                       self.endpoint,
                                                                       self.method)


class Agg_Request(db.Model):
    """The the aggregated stats for each call."""

    __tablename__ = "agg_request"

    aggr_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    call_code = db.Column(db.String(128),
                        db.ForeignKey("call.call_code"),
                        nullable=False)
    success_count = db.Column(db.Integer, nullable=False)
    block_count = db.Column(db.Integer, nullable=False)
    other_count = db.Column(db.Integer, nullable=False)
    total_responses = db.Column(db.Integer, nullable=False)
    avg_response_time = db.Column(db.Numeric, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Agg_Request aggr_id={} call_code={} success_count={} block_count={} other_count={} total_responses={} avg_response_time={}>".format(
                                                                       self.aggr_id,
                                                                       self.call_code,
                                                                       self.success_count,
                                                                       self.block_count,
                                                                       self.other_count,
                                                                       self.total_responses,
                                                                       self.avg_response_time)

    call = db.relationship("Call",
                           backref=db.backref("agg_request",
                           order_by=call_code))


class Request(db.Model):
    """The container for an individual API request to the server."""

    __tablename__ = "request"

    request_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    call_code = db.Column(db.String(128),
                        db.ForeignKey("call.call_code"),
                        nullable=False)
    response_code = db.Column(db.String(128), nullable=False)
    response_time = db.Column(db.Numeric, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Request request_id={} call_code={} response_code={} response_time={}>".format(
                                                                       self.request_id,
                                                                       self.call_code,
                                                                       self.response_code,
                                                                       self.response_time)

    call = db.relationship("Call",
                           backref=db.backref("request",
                           order_by=call_code))


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database

    # Uncomment to connect to test DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_dashboard'

    # Uncomment to connect to production DB
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dashboard'

    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
