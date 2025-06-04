from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_bot = Column(String, default='False')