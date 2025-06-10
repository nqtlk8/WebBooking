from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLALCHEMY_DATABASE_URL sẽ lấy từ settings.DATABASE_URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

# Tạo engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    isolation_level="SERIALIZABLE",
    echo=True
)

# Tạo session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để khai báo model ORM
Base = declarative_base()

# Dependency để inject session vào các route
def get_db():
    db = SessionLocal()
    try:
        logger.info("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()
        logger.info("Database session closed")