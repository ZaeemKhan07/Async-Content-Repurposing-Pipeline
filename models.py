from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PENDING")  # PENDING, SUMMARIZING, GENERATING_SOCIALS, COMPLETED, FAILED
    original_text = Column(Text)
    summary = Column(Text, nullable=True)
    twitter_thread = Column(JSON, nullable=True)
    linkedin_post = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
