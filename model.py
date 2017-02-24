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
    __table_args__ = (db.UniqueConstraint('api_name', 'env_id', 'version', name='_api_env_version'),)

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

    call_id = db.Column(db.Integer, primary_key=True)
    call_name = db.Column(db.String(128))
    env_id = db.Column(db.Integer,
                       db.ForeignKey("environment.env_id"),
                       nullable=False)
    api_id = db.Column(db.Integer,
                       db.ForeignKey("api.api_id"),
                       nullable=False)
    key_type = db.Column(db.String(128))
    endpoint = db.Column(db.String(128))
    method = db.Column(db.String(10))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Call call_id={} call_name={} api_id={} endpoint={}, method={}>".format(
                                                                       self.call_id,
                                                                       self.call_name,
                                                                       self.api_id,
                                                                       self.endpoint,
                                                                       self.method)


class Customer(db.Model):
    """Customer properties."""

    __tablename__ = "customer"

    customer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    state = db.Column(db.String(128), nullable=True)
    country = db.Column(db.String(128), nullable=False)
    sub_status = db.Column(db.String(128), nullable=False)
    sub_level = db.Column(db.String(128), nullable=True)
    revenue = db.Column(db.Numeric, nullable=True)
    sub_start = db.Column(db.DateTime, nullable=True)
    sub_end = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Customer customer_id={} username={} sub_status={} sub_level={} sub_start={} sub_end={}>".format(
                                                                       self.customer_id,
                                                                       self.username,
                                                                       self.sub_status,
                                                                       self.sub_level,
                                                                       self.sub_start,
                                                                       self.sub_end)


class Developer(db.Model):
    """Developer properties."""

    __tablename__ = "developer"

    dev_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    state = db.Column(db.String(128), nullable=True)
    country = db.Column(db.String(128), nullable=False)
    dev_type = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Developer dev_id={} username={} company={} dev_type={}>".format(
                                                                       self.dev_id,
                                                                       self.username,
                                                                       self.company,
                                                                       self.dev_type)


class Application(db.Model):
    """Application properties."""

    __tablename__ = "application"

    app_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    app_name = db.Column(db.String(128), nullable=False)
    app_type = db.Column(db.String(128), nullable=False)
    dev_id = db.Column(db.Integer,
                        db.ForeignKey("developer.dev_id"),
                        nullable=False)
    application_id = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Application app_id={} app_name={} app_type={}>".format(
                                                                       self.app_id,
                                                                       self.app_name,
                                                                       self.app_type)

    developer = db.relationship("Developer",
                           backref=db.backref("application",
                           order_by=dev_id))


class Request(db.Model):
    """The container for an individual API request to the server."""

    __tablename__ = "request"

    request_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    call_id = db.Column(db.Integer,
                        db.ForeignKey("call.call_id"),
                        nullable=False)
    app_id = db.Column(db.Integer,
                        db.ForeignKey("application.app_id"),
                        nullable=False)
    response_code = db.Column(db.String(128), nullable=False)
    response_time = db.Column(db.Numeric, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Request request_id={} call_id={} response_code={} response_time={} date={}>".format(
                                                                       self.request_id,
                                                                       self.call_id,
                                                                       self.response_code,
                                                                       self.response_time,
                                                                       self.date)

    call = db.relationship("Call",
                           backref=db.backref("request",
                           order_by=call_id))

    application = db.relationship("Application",
                           backref=db.backref("request",
                           order_by=app_id))


class App_Used(db.Model):
    """Application/customer relationships."""

    __tablename__ = "app_used"

    use_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    app_id = db.Column(db.Integer,
                        db.ForeignKey("application.app_id"),
                        nullable=False)
    customer_id = db.Column(db.Integer,
                        db.ForeignKey("customer.customer_id"),
                        nullable=False)
    use_start = db.Column(db.DateTime, nullable=False)
    use_end = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<App_Used use_id={} app_id={} customer_id={}>".format(
                                                                       self.use_id,
                                                                       self.app_id,
                                                                       self.customer_id)

    application = db.relationship("Application",
                           backref=db.backref("app_used",
                           order_by=app_id))

    customer = db.relationship("Customer",
                           backref=db.backref("app_used",
                           order_by=customer_id))

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
