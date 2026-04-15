from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# SQLite database file path
SQLALCHEMY_DATABASE_URL = "sqlite:///./leads.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company = Column(String)
    email = Column(String, unique=True, nullable=True, index=True)
    phone = Column(String, unique=True, nullable=True)
    website = Column(String, nullable=True)
    niche = Column(String, default="Law Firm")
    city = Column(String, nullable=True)
    map_link = Column(String, nullable=True)
    twitter = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    instagram = Column(String, nullable=True)
    source = Column(String, default="Maps") # Maps, Twitter, Reddit
    lead_intent = Column(String, default="Medium") # High, Medium, Low
    status = Column(String, default="New") # New, Contacted, Interested, Closed
    ai_score = Column(Integer, default=0) # 0-100 based on "Opportunity"
    pitch = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database Initialized: leads.db created successfully.")
