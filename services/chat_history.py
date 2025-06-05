from sqlalchemy.orm import Session
from model.chat_history import ChatHistory

def add_message(db: Session, user_id: int, message_type: str, content: str, is_bot: bool = False):
    """
    Add a new chat message to the database.
    """
    new_message = ChatHistory(
        user_id=user_id,
        message_type=message_type,
        content=content,
        is_bot=is_bot
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_messages(db: Session, user_id: int, limit: int, offset: int):
    """
    Retrieve chat messages from the database.
    If user_id is provided, filter messages by user_id.
    """

    return (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )