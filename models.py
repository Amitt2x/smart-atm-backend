from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    card_number = Column(String, unique=True, index=True)
    pin_hash = Column(String)
    balance = Column(Float, default=0.0)
    is_locked = Column(Boolean, default=False)


from sqlalchemy import DateTime
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String)
    type = Column(String)  # deposit / withdraw
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)