"""Test the setup of my Flask SQLAlchemy Package"""
import pytest
import application


def test_init_scoped_session_called_once():
    """1. test that init_scoped_session is only called once in app setup and usage."""

    class Recorder(object):
        called = 0

    def recorder_decorator(func):
        def wrapper():
            Recorder.called += 1
            return func()

        return wrapper

    application.db.init_scoped_session = recorder_decorator(
        application.db.init_scoped_session
    )
    app = application.create_app(
        {
            "TESTING": True,
            "DATABASE": "sqlite:///:memory:",
        }
    )
    # create app should have called the function once
    assert Recorder.called == 1
    client = app.test_client()
    client.post("/", data={"username": "kelly", "password": "kelly"})
    client.get("/")
    # neither request should have called init_scoped_session
    assert Recorder.called == 1


def test_session_access(app):
    # this function lives in a module outside of the init file where db was created
    # and it uses the scoped_session session object provided by the db
    application.api.create_user(username="kelly", password="kelly")
    assert (
        application.database.User.query.filter_by(username="kelly").first() is not None
    )


def test_init_scoped_session_remove_called_after_request2():
    """#2. test that scoped_session.remove() is called when the web request ends."""

    class Recorder(object):
        count = 0

    def recorder_decorator(func):
        def wrapper(*args, **kwargs):
            Recorder.count += 1
            return func(*args, **kwargs)

        return wrapper

    application.db.remove_session = recorder_decorator(application.db.remove_session)
    app = application.create_app(
        {
            "TESTING": True,
            "DATABASE": "sqlite:///:memory:",
        }
    )
    ctx = app.test_request_context()
    ctx.push()
    ctx.pop()
    # create app should have called the the teardown functions once
    assert Recorder.count == 1
    app.test_client().get("/")
    # the request should have called the the teardown functions another time
    assert Recorder.count == 2


def test_db_session_same_in_same_request(app):
    """Test that within a single request db.session/Session() returns the same
    session object each time it's called"""
    with app.test_request_context():
        session1 = application.db.session()
        session2 = application.db.session()
    assert session1 == session2


def test_db_session_different_in_different_request(app):
    """Ensure that db.session/Session() returns a two different session for two
    requests."""
    with app.test_request_context():
        session1 = application.db.session()
    with app.test_request_context():
        session2 = application.db.session()
    assert session1 != session2


@pytest.mark.xfail
def test_show_problem_with_implicit_method_access_comparison(app):
    """the assertion assert session1 != session3 in the following code
    will fail because instead of comparing the inidividual session objects
    (<sqlalchemy.orm.session.Session object at ...>) which is different for
    each request we're comparing the scoped_session object itself
    (<sqlalchemy.orm.scoping.scoped_session object at ...>)
    which remains the same throughout requests."""
    with app.test_request_context():
        session1 = application.db.session
        session2 = application.db.session
    with app.test_request_context():
        session3 = application.db.session
    assert session1 == session2
    assert session1 != session3
