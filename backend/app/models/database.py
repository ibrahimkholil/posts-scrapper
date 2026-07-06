from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRole(enum.Enum):
    admin = "admin"
    editor = "editor"


class JobStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.editor)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    wp_connections = relationship("WPConnection", back_populates="creator")


class WPConnection(Base):
    __tablename__ = "wp_connections"
    
    id = Column(String, primary_key=True, index=True)
    site_name = Column(String, nullable=False)
    site_url = Column(String, nullable=False)
    wp_username = Column(String, nullable=False)
    wp_app_password_encrypted = Column(Text, nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("User", back_populates="wp_connections")
    jobs = relationship("ImportJob", back_populates="wp_connection")


class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(String, primary_key=True, index=True)
    source_url = Column(String, unique=True, index=True, nullable=False)
    target_wp_connection_id = Column(String, ForeignKey("wp_connections.id"))
    status = Column(Enum(JobStatus), default=JobStatus.pending)
    wp_post_id = Column(Integer, nullable=True)
    wp_draft_url = Column(String, nullable=True)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    wp_connection = relationship("WPConnection", back_populates="jobs")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
