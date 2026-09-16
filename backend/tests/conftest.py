import pytest
from app import create_app
from core.database import db
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()