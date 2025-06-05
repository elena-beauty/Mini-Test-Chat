import os
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from services.chat_history import add_message
from services.user import get_current_user

from datetime import datetime
import pytz
import random
import base64
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model = os.getenv("AZURE_OPENAI_MODEL", "openai/gpt-4.1-mini")
token = os.getenv("AZURE_OPENAI_API_KEY")

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def is_message_acceptable(client_timezone: str, message_type: str) -> bool:
    try:
        client_time = datetime.now(pytz.timezone(client_timezone))
        hour = client_time.hour

        if message_type == "text":
            return 5 <= hour < 24
        elif message_type == "voice":
            return 8 <= hour < 12
        elif message_type == "video":
            return 2 <= hour < 24
        else:
            return False
    except Exception as e:
        print(f"Error processing timezone or message type: {e}")
        return False

def save_file(file_data: str, file_type: str) -> str:
    """
    Save a base64-encoded file to the server and return the file path.
    """
    file_extension = "webm" if file_type == "voice" else "mp4"
    file_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as file:
        file.write(base64.b64decode(file_data.split(",")[1]))

    return file_path

async def websocket_logic(websocket: WebSocket, db: Session):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        current_user = get_current_user(token, db)
        user_id = current_user.id

        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            client_timezone = data.get("timezone")
            content = data.get("message")

            if message_type in ["voice", "video"]:
                file_path = save_file(content, message_type)
                content = file_path

            add_message(db, user_id, message_type, content)
            openai_response = call_openai_api(message_type, content)

            if is_message_acceptable(client_timezone, message_type):
                response = {
                    "status": "success",
                    "message": openai_response,
                }
            else:
                response = {
                    "status": "unsuccessful",
                    "message": "Message rejected due to time restrictions",
                }

            add_message(db, user_id, "text", openai_response, True)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        print("Client disconnected")


def call_openai_api(message_type: str, content: str) -> str:
    """
    Call OpenAI API with the given message type and content.
    """
    try:
        if message_type == "text":
            response = client.complete(
                messages=[
                    SystemMessage("You are a helpful assistant."),
                    UserMessage(content),
                ],
                temperature=1.0,
                top_p=1.0,
                model=model
            )
            return response.choices[0].message.content

        elif message_type == "voice":
            with open(content, "rb") as audio_file:
                response = openai.Audio.transcribe("whisper-1", audio_file)
            return response['text']

        elif message_type == "video":
            return "Video processing is not supported yet."

        else:
            return "Unsupported message type."

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error processing your request."
