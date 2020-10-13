
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Sequence, Integer, String

from dotenv import load_dotenv
load_dotenv()


DB_URI = os.getenv('PG_PAWPAW_DB')
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'))
    name = Column(String(100))
    email = Column(String(100), primary_key=True)

    def __repr__(self):
        return f"{self.id}; {self.name}"

class Token(Base):
    __tablename__ = 'tokens'
    user_id = Column(Integer, primary_key=True)
    key = Column(String(250))

Base.metadata.create_all(engine)
