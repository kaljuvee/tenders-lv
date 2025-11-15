"""Database models and connection for Latvia procurement tenders."""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database connection
DATABASE_URL = os.getenv('DB_URL', 'postgresql://indurent_db_user:mORTX4lmewn7ZJsMiU7Ox7Qb8gnxPRgf@dpg-d40gneur433s738clpeg-a.frankfurt-postgres.render.com/indurent_db')

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProcurementNotice(Base):
    """Procurement notice model matching tenders_lv schema."""
    __tablename__ = 'procurement_notices'
    __table_args__ = {'schema': 'tenders_lv'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(String(255))
    country_code = Column(String(2), default='LV')
    name = Column(Text)
    description = Column(Text)
    notice_type = Column(String(100))
    procedure_type = Column(String(100))
    main_nature_type = Column(String(100))
    cpv_type = Column(String(50))
    estimated_value = Column(String(50))
    currency = Column(String(10))
    organization_name = Column(Text)
    organization_city = Column(String(255))
    organization_identifier = Column(String(255))
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    contact_telephone = Column(String(50))
    public_opening_date = Column(DateTime)
    deadline_receipt_tenders_date = Column(DateTime)
    documents_url = Column(Text)
    submission_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DataSyncLog(Base):
    """Data synchronization log."""
    __tablename__ = 'data_sync_log'
    __table_args__ = {'schema': 'tenders_lv'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20))
    records_processed = Column(Integer, default=0)
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
