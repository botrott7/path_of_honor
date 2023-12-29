from sqlalchemy import Boolean, Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    health = Column(Integer)
    max_hp = Column(Integer)
    gold = Column(Integer)
    fatigue = Column(Boolean)
    hangover = Column(Boolean)
    dysmoral = Column(Boolean)
    password = Column(String)
