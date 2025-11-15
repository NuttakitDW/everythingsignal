# api/db.py

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
import json
import uuid

DATABASE_URL = "sqlite:///./everythingsignal.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ModelRecord(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, unique=True, index=True)  # external ID
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON list
    artifact_id = Column(String, nullable=True)  # Walrus ID or similar
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    summary_metrics = Column(Text, nullable=True)  # JSON dict


def init_db():
    Base.metadata.create_all(bind=engine)


def create_model_record(
    db,
    *,
    name: Optional[str],
    description: Optional[str],
    tags: Optional[list],
    artifact_id: str,
    summary_metrics: Dict[str, Any],
) -> ModelRecord:
    model_record = ModelRecord(
        model_id=str(uuid.uuid4()),
        name=name,
        description=description,
        tags=json.dumps(tags or []),
        artifact_id=artifact_id,
        summary_metrics=json.dumps(summary_metrics),
    )
    db.add(model_record)
    db.commit()
    db.refresh(model_record)
    return model_record
