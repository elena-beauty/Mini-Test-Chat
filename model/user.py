from sqlalchemy import Column, Integer, String, Date
from database import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    gender = Column(String, nullable=False)
    password = Column(String, nullable=False)