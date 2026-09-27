from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config

Base = declarative_base()


class ScrapeTarget(Base):
    __tablename__ = "scrape_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    css_selector = Column(String(512), nullable=True)
    use_selenium = Column(Integer, default=0)  # 0/1 boolean flag for SQLite simplicity
    created_at = Column(DateTime, default=datetime.utcnow)


class ScrapedItem(Base):
    __tablename__ = "scraped_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer, nullable=False, index=True)
    title = Column(String(1024), nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(2048), nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)


engine = create_engine(Config.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(bind=engine)
