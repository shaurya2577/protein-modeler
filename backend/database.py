from sqlalchemy import create_engine, Column, String, Float, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import json

from config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class DiseaseDB(Base):
    __tablename__ = "diseases"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    burden_score = Column(Float, nullable=True)
    sources = Column(JSON, nullable=True)


class ProteinDB(Base):
    __tablename__ = "proteins"
    
    id = Column(String, primary_key=True, index=True)
    uniprot_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=True)
    name = Column(String, nullable=True)
    family = Column(String, nullable=True)
    pathways = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)


class AssociationDB(Base):
    __tablename__ = "associations"
    
    id = Column(String, primary_key=True, index=True)
    disease_id = Column(String, ForeignKey("diseases.id"), nullable=False, index=True)
    protein_id = Column(String, ForeignKey("proteins.id"), nullable=False, index=True)
    association_strength = Column(Float, nullable=True)
    evidence_text = Column(Text, nullable=True)
    citations = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)
    maturity = Column(String, nullable=True)
    last_updated = Column(String, nullable=True)


class TherapyDB(Base):
    __tablename__ = "therapies"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_protein_id = Column(String, ForeignKey("proteins.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    drugbank_id = Column(String, nullable=True)
    chembl_id = Column(String, nullable=True)
    indications = Column(JSON, nullable=True)
    sources = Column(JSON, nullable=True)


class ClinicalTrialDB(Base):
    __tablename__ = "trials"
    
    id = Column(String, primary_key=True, index=True)
    nct_id = Column(String, nullable=False, unique=True, index=True)
    phase = Column(String, nullable=True)
    status = Column(String, nullable=True)
    condition = Column(String, nullable=True)
    target_protein_id = Column(String, ForeignKey("proteins.id"), nullable=True, index=True)
    start_date = Column(String, nullable=True)
    link = Column(String, nullable=True)
    sources = Column(JSON, nullable=True)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clear_db():
    """Clear all tables"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

