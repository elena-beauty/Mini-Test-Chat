import os
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
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

# Constraints
MAX_CLIENTS = 50
MAX_MESSAGES = 500
active_clients = set()  # Track active client connections
message_count = 0  # Track total messages processed

def is_message_acceptable(client_timezone: str, message_type: str) -> bool:
    try:
        client_time = datetime.now(pytz.timezone(client_timezone))
        hour = client_time.hour

        if message_type == "text":
            return 5 <= hour < 24
        elif message_type == "voice":
            return 8 <= hour < 12
        elif message_type == "video":
            return 12 <= hour < 24
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

    if not file_data:
        raise ValueError("File content is missing in file_data")

    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as file:
        file.write(base64.b64decode(file_data))

    return file_path

async def websocket_logic(websocket: WebSocket, db: Session):
    global message_count

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        current_user = get_current_user(token, db)
        user_id = current_user.id

        # Constraint: One client cannot make two connections simultaneously
        if user_id in active_clients:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=400, detail="Client already connected.")

        # Constraint: Maximum of 50 clients allowed
        if len(active_clients) >= MAX_CLIENTS:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=400, detail="Maximum client limit reached.")

        active_clients.add(user_id)
        await websocket.accept()

        has_sent_message = False  # Track if the client has sent at least one message

        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            client_timezone = data.get("timezone")
            content = data.get("message")

            # Constraint: All clients must send at least one message
            has_sent_message = True

            # Constraint: Maximum of 500 messages processed
            if message_count >= MAX_MESSAGES:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                raise HTTPException(status_code=400, detail="Maximum message limit reached.")

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

            message_count += 1

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        # Remove client from active_clients
        active_clients.discard(user_id)

        # Ensure the client sent at least one message
        if not has_sent_message:
            raise HTTPException(status_code=400, detail="Client did not send any messages.")

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
