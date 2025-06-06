from fastapi import FastAPI, WebSocket, Depends, Query, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from pydantic import BaseModel

from services.user import create_user, get_user_by_id, get_all_users, signup_user, login_user, get_current_user
from services.websocket import websocket_logic
from services.chat_history import add_message, get_messages
from database import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/style", StaticFiles(directory="style"), name="style")

class UserRequest(BaseModel):
    name: str
    email: str
    gender: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    gender: str

class LoginRequest(BaseModel):
    email: str
    password: str

class MessageRequest(BaseModel):
    user_id: int
    message_type: str
    content: str

class MessageResponse(BaseModel):
    id: int
    user_id: int
    type: str
    content: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    gender: str

@app.get("/", response_model=dict)
def root() -> dict[str, str]:
    """
    Root endpoint to check API status.
    """
    return {"message": "Hello"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time communication.
    """
    await websocket_logic(websocket, db)

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    API endpoint to get a user by ID.
    """
    return get_user_by_id(db, user_id)

@app.get("/users/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """
    API endpoint to list all users.
    """
    return get_all_users(db)

@app.post("/signup/", response_model=UserResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    API endpoint for user signup.
    """
    return signup_user(db, request)

@app.post("/login/", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    API endpoint for user login.
    """
    return login_user(db, request)

@app.post("/messages/", response_model=MessageResponse)
def create_message(request: MessageRequest, db: Session = Depends(get_db)):
    """
    API endpoint to create a new message.
    """
    return add_message(db, request.user_id, request.message_type, request.content)

@app.get("/messages/", response_model=dict)
def retrieve_messages(
    request: Request, 
    limit: int = Query(10, ge=1, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
):
    """
    API endpoint to retrieve chat messages with pagination.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(token, db=db)

    messages = get_messages(db, user_id=current_user.id, limit=limit, offset=offset)
    messages_json = jsonable_encoder(messages)
    return {"messages": messages_json, "limit": limit, "offset": offset}

@app.get("/me", response_model=dict)
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """
    API endpoint to get the current user's information.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(token, db=db)
    return {"user_id": current_user.id, "name": current_user.name, "email": current_user.email}
