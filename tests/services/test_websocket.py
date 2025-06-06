import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.websocket import (
    is_message_acceptable,
    save_file,
    call_openai_api,
    websocket_logic,
)
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime
import pytz
import base64


@pytest.fixture
def mock_db():
    """
    Fixture to create a mocked database session.
    """
    return MagicMock(spec=Session)


@pytest.fixture
def mock_websocket():
    """
    Fixture to create a mocked WebSocket instance.
    """
    websocket = AsyncMock(spec=WebSocket)
    websocket.query_params = {"token": "mock_token"}
    return websocket


def test_is_message_acceptable():
    """
    Test the is_message_acceptable function.
    """
    client_timezone = "UTC"

    # Test for text messages
    assert is_message_acceptable(client_timezone, "text") is True

    # Test for voice messages
    assert is_message_acceptable(client_timezone, "voice") is False

    # Test for video messages
    assert is_message_acceptable(client_timezone, "video") is True

    # Test for unsupported message type
    assert is_message_acceptable(client_timezone, "unsupported") is False

    # Test for invalid timezone
    assert is_message_acceptable("Invalid/Timezone", "text") is False


def test_save_file():
    """
    Test the save_file function.
    """
    file_data = base64.b64encode(b"mock_binary_data").decode("utf-8")
    file_type = "voice"

    file_path = save_file(file_data, file_type)

    assert file_path.endswith(".webm")
    assert file_path.startswith("uploads/")
    with open(file_path, "rb") as file:
        assert file.read() == b"mock_binary_data"

    with pytest.raises(ValueError, match="File content is missing in file_data"):
        save_file("", file_type)


@patch("websocket.client.complete")
def test_call_openai_api_text(mock_complete):
    """
    Test the call_openai_api function for text messages.
    """
    mock_complete.return_value.choices = [MagicMock(message=MagicMock(content="Mock response"))]

    message_type = "text"
    content = "Hello, OpenAI!"
    response = call_openai_api(message_type, content)

    assert response == "Mock response"
    mock_complete.assert_called_once()


@patch("websocket.openai.Audio.transcribe")
def test_call_openai_api_voice(mock_transcribe):
    """
    Test the call_openai_api function for voice messages.
    """
    mock_transcribe.return_value = {"text": "Transcribed text"}

    message_type = "voice"
    content = "mock_audio_file.webm"
    with patch("builtins.open", MagicMock()):
        response = call_openai_api(message_type, content)

    assert response == "Transcribed text"
    mock_transcribe.assert_called_once_with("whisper-1", MagicMock())


def test_call_openai_api_video():
    """
    Test the call_openai_api function for video messages.
    """
    message_type = "video"
    content = "mock_video_file.mp4"
    response = call_openai_api(message_type, content)

    assert response == "Video processing is not supported yet."


def test_call_openai_api_unsupported():
    """
    Test the call_openai_api function for unsupported message types.
    """
    message_type = "unsupported"
    content = "mock_content"
    response = call_openai_api(message_type, content)

    assert response == "Unsupported message type."


@patch("websocket.get_current_user")
@patch("websocket.add_message")
@patch("websocket.call_openai_api")
@patch("websocket.save_file")
@pytest.mark.asyncio
async def test_websocket_logic(
    mock_save_file, mock_call_openai_api, mock_add_message, mock_get_current_user, mock_websocket, mock_db
):
    """
    Test the websocket_logic function.
    """
    mock_get_current_user.return_value = MagicMock(id=1)
    mock_call_openai_api.return_value = "Mock OpenAI response"
    mock_save_file.return_value = "mock_file_path.webm"

    mock_websocket.receive_json.return_value = {
        "type": "voice",
        "timezone": "UTC",
        "message": base64.b64encode(b"mock_binary_data").decode("utf-8"),
    }

    await websocket_logic(mock_websocket, mock_db)

    mock_websocket.accept.assert_called_once()
    mock_websocket.send_json.assert_called_once_with(
        {
            "status": "success",
            "message": "Mock OpenAI response",
        }
    )
    mock_add_message.assert_called()
    mock_call_openai_api.assert_called_once_with("voice", "mock_file_path.webm")
    mock_save_file.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_logic_disconnect(mock_websocket, mock_db):
    """
    Test the websocket_logic function for WebSocket disconnect.
    """
    mock_websocket.receive_json.side_effect = WebSocketDisconnect()

    await websocket_logic(mock_websocket, mock_db)

    mock_websocket.close.assert_called_once()
