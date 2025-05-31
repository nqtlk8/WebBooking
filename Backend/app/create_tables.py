from database import engine, Base
from models.user import User
from models.booking import Booking
from models.seat import Seat
from models.bookingdetail import BookingDetail
from models.ticket_type import TicketType
from sqlalchemy import text
from core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    print("Checking database tables...")
    print(f"Database URL: {settings.DATABASE_URL}")  # In ra URL kết nối
    try:
        # Kiểm tra kết nối
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection successful!")

        # Tạo các bảng nếu chưa có (SQLAlchemy tự kiểm tra)
        logger.info("Creating all tables (if not exist)...")
        Base.metadata.create_all(bind=engine)
        logger.info("Table creation completed!")

    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

if __name__ == "__main__":
    create_tables() 