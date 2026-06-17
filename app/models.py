import secrets
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from .database import Base


class Org(Base):
    __tablename__ = "orgs"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    event = Column(String, nullable=False)
    properties = Column(JSON, default=dict)
    user = Column(String)
    project = Column(String)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
