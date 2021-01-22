import pytest
from application import create_app


@pytest.fixture
def app():

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": "sqlite:///:memory:",
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()
