from database import SessionLocal
from models.user import User
from api.auth import get_password_hash
import logging
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_default_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@gmail.com").first()
        
        if existing_admin:
            logger.info("Default admin already exists!")
            return
        
        # Create new admin
        admin = User(
            name="Admin",
            email="admin@gmail.com",
            hashed_password=get_password_hash("123456"),
            date_of_birth=date(1990, 1, 1),  # Default date
            phone_number="0000000000",  # Default phone
            type="admin"
        )
        
        # Add to database
        db.add(admin)
        db.commit()
        logger.info("Default admin created successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating default admin: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_default_admin() 