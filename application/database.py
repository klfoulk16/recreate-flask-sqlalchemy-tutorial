from sqlalchemy import Column, Integer, String
from application import db


class User(db.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String, unique=True)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
