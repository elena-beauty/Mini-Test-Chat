from fastapi import FastAPI, WebSocket, Depends, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

from services.user import create_user, get_user_by_id, get_all_users
from services.websocket import websocket_logic

from database import get_db
from sqlalchemy.orm import Session
from services.chat_history import add_message, get_messages
from services.user import signup_user, login_user, get_current_user
from pydantic import BaseModel

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

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_logic(websocket, db)


@app.post("/users/")
def add_user(name: str, email: str, gender: str, db: Session = Depends(get_db)):
    """
    API endpoint to create a new user.
    """
    return create_user(db, name, email, gender)

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    API endpoint to get a user by ID.
    """
    return get_user_by_id(db, user_id)

@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    """
    API endpoint to list all users.
    """
    return get_all_users(db)


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    gender: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/signup/")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    API endpoint for user signup.
    """
    return signup_user(db, request)

@app.post("/login/")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    API endpoint for user login.
    """
    return login_user(db, request)

@app.post("/messages/")
def create_message(user_id: int, message_type: str, content: str, db: Session = Depends(get_db)):
    return add_message(db, user_id, message_type, content)

@app.get("/messages/")
def retrieve_messages(
    request: Request, 
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    API endpoint to retrieve chat messages with pagination.
    """
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(token, db=db)

    messages = get_messages(db, user_id=current_user.id, limit=limit, offset=offset)
    messages_json = jsonable_encoder(messages)
    return {"messages": messages_json, "limit": limit, "offset": offset}

@app.get("/me")
def get_current_user_info(
    request: Request, db: Session = Depends(get_db)
):
    """
    API endpoint to get the current user's information.
    """
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]
    current_user = get_current_user(token, db=db)
    return {"user_id": current_user.id, "name": current_user.name, "email": current_user.email}
