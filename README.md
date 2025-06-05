# Real-Time Chat Application

This project is a real-time chat application that supports text, voice, and video communication. It is designed to provide seamless interaction between users with features like:
- Text messaging
- Voice calls
- Video calls
- API documentation for integration

## Architecture

The application is built using the following technologies:
- **Backend**: FastAPI for API development and WebSocket support.
- **Frontend**: HTML, CSS for the user interface.
- **Database**: PostgreSQL for storing user data and chat history.
- **Real-Time Communication**: WebRTC for voice and video calls, and WebSocket for text messaging.
- **Containerization**: Docker for consistent development and deployment environments.

### Component Interaction
1. **Frontend** communicates with the backend via REST APIs and WebSocket for real-time updates.
2. **Backend** handles API requests, WebSocket connections, and integrates WebRTC for voice/video communication.
3. **Database** stores user profiles, chat history, and call logs.

## Setup Instructions

Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/realtime-chat-app.git
   cd realtime-chat-app 

2. **Run in local**:
    ``` 
    pip3 install -r requirements.txt

    uvicorn main:app --reload

    kill -9 $(lsof -ti :8000)
