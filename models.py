from sqlalchemy import Column, String, JSON, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Use Supabase URL or local fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# If on Vercel and no DB URL is provided, we might still want to use memory or error out.
# However, for true persistence on Vercel, DATABASE_URL must be a real PG URL.
if "postgres" in DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    # Fallback to SQLite for local dev
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="Pending") # Pending, Processing, Completed, Failed
    input_type = Column(String) # text, url, pdf
    input_data = Column(Text)
    results = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
