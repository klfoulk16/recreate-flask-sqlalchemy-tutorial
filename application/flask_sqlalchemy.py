import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import flask


class Flask_SQLAlchemy:
    def __init__(self):
        """Create instance of class to be used when defining tables"""
        # tell SQLAlchemy how you'll define tables and models
        self.Base = declarative_base()

    def init_app(self, app):
        """Set up SQLAlchemy to work with Flask Application"""
        # connect database
        self.engine = sqlalchemy.create_engine(app.config["DATABASE"])
        # create session factory
        self.sessionmaker = sqlalchemy.orm.sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        # set up scoped_session registry
        # #add ability to access scoped session registry (implicitly)
        self.session = self.init_scoped_session()
        # add ability to query against the tables in database
        self.Base.query = self.session.query_property()
        # make sure db is initialize and up to date
        self.Base.metadata.create_all(bind=self.engine)
        # tells app to call scoped_session.remove() after each request ends
        app.teardown_request(self.remove_session)

    def init_scoped_session(self):
        "Create empty scoped session registry upon app startup"
        return sqlalchemy.orm.scoped_session(
            self.sessionmaker, scopefunc=flask._app_ctx_stack.__ident_func__
        )

    def remove_session(self, error=None):
        """Removes the current Session object associated with
        the request"""
        self.session.remove()
        # this is necessary for teardown functions
        if error:
            # Log the error
            print("logging error", str(error))
