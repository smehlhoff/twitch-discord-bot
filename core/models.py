from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bot import load_config

Base = declarative_base()


class Follows(Base):
    __tablename__ = 'follows'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=False)
    channel = Column(String(255), nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


config = load_config()

engine = create_engine('sqlite:///bot.db', echo=config['bot']['debug'])
Base.metadata.create_all(engine)
Base.metadata.bind = engine

Session = sessionmaker(bind=engine)
session = Session()
