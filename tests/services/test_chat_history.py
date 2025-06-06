import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from services.chat_history import add_message, get_messages
from model.chat_history import ChatHistory

@pytest.fixture
def mock_db():
    """
    Fixture to create a mocked database session.
    """
    return MagicMock(spec=Session)

def test_add_message(mock_db):
    """
    Test the add_message function.
    """
    mock_message = MagicMock(spec=ChatHistory)
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    user_id = 1
    message_type = "text"
    content = "Hello, world!"
    is_bot = False

    result = add_message(mock_db, user_id, message_type, content, is_bot)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(result)
    assert result.user_id == user_id
    assert result.message_type == message_type
    assert result.content == content
    assert result.is_bot == is_bot

def test_get_messages(mock_db):
    """
    Test the get_messages function.
    """
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [
        ChatHistory(user_id=1, message_type="text", content="Hello", is_bot=False),
        ChatHistory(user_id=1, message_type="text", content="Hi", is_bot=False),
    ]

    user_id = 1
    limit = 10
    offset = 0

    result = get_messages(mock_db, user_id, limit, offset)

    mock_db.query.assert_called_once_with(ChatHistory)
    mock_query.filter.assert_called_once_with(ChatHistory.user_id == user_id)
    mock_query.order_by.assert_called_once()
    mock_query.offset.assert_called_once_with(offset)
    mock_query.limit.assert_called_once_with(limit)
    assert len(result) == 2
    assert result[0].content == "Hello"
    assert result[1].content == "Hi"
