# API FOR DATABASE CONNECTION
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = "sqlite:///./tasks.db"
db_engine = create_engine(url=DB_URL, connect_args={
    "check_same_thread": False
})
db_session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
Base = declarative_base()
