from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv
from fastapi import Depends
from typing import Annotated

# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-an-engine

load_dotenv()

database_url = os.getenv("DATABASE_URL")

# a SQLModel engine (underneath it's actually a SQLAlchemy engine) is what holds the connections to the database.
engine = create_engine(database_url, echo=True)


# this creates the database and starts all models from SQLModel 
# (we must import the models inside main.py (or here) for python to register them)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

""" a Session is what stores the objects in memory and keeps track of any changes needed in the data, then it uses the engine 
to communicate with the database. we will create a FastAPI dependency with yield that will provide a new Session for each request. This is what ensures that we use a single session per request. """
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]