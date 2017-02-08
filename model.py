"""Models and database functions for Dev Program Dashboard project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions


class API(db.Model):
    """API provided by a company."""

    __tablename__ = "api"

    api_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    api_name = db.Column(db.String(64), nullable=False)
    env_base_url = db.Column(db.String(128),
                       db.ForeignKey("env.env_base_url"),
                       nullable=False)
    version = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<API api_id={} api_name={} env_base_url={} version={}>".format(
                                                                       self.api_id,
                                                                       self.api_name,
                                                                       self.env_base_url,
                                                                       self.version)

    # Define relationship to call
    call = db.relationship("Call",
                           backref=db.backref("api",
                           order_by=api_id))
    env = db.relationship("Environment",
                           backref=db.backref("api",
                           order_by=env_base_url))
    # request = db.relationship("Request",
    #                        backref=db.backref("api",
    #                        order_by=env_base_url))


class Environment(db.Model):
    """Environment (production/staging) a n API operates in."""

    __tablename__ = "environment"

    env_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    env_name = db.Column(db.String(64), nullable=False)
    env_base_url = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Environment env_id={} env_name={} env_base_url={}>".format(self.env_id,
                                                                       self.env_name,
                                                                       self.env_base_url)


class Call(db.Model):
    """A call from a company's API."""

    __tablename__ = "call"

    call_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    call_name = db.Column(db.String(64), nullable=False)
    api_id = db.Column(db.Integer,
                       db.ForeignKey("api.api_id"),
                       nullable=False)
    endpoint = db.Column(db.String(128), nullable=False)
    method = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<API call_id={} call_name={} api_id={} endpoint={}, method={}>".format(
                                                                       self.call_id,
                                                                       self.call_name,
                                                                       self.api_id,
                                                                       self.endpoint
                                                                       self.method)


class Request(db.Model):
    """The container for an individual API request to the server."""

    __tablename__ = "request"

    request_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    call_id = db.Column(db.Integer,
                       db.ForeignKey("call.call_id"),
                       nullable=False)
    response_code = db.Column(db.String(128), nullable=False)
    response_time = db.Column(db.DateTime(fsp=6), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<API api_id={} api_name={} base_url={} version={}>".format(self.api_id,
                                                                       self.email,
                                                                       self.base_url,
                                                                       self.version)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dashboard'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
