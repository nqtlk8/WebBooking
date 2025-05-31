from sqlalchemy import Column, Integer, String, Date
from database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    phone_number = Column(String, nullable=True)
    type = Column(String, nullable=True)  # e.g., 'user', 'admin' 