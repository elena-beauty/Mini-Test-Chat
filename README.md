# Real-Time Chat Application

This project is a real-time chat application that supports text, voice, and video communication. It is designed to provide seamless interaction between users with features like:
- Text messaging
- Voice calls
- Video calls
- API documentation for integration

## Features

### Time Zone-Based Message Acceptance
The server processes client messages based on their time zones and the type of communication:
- **Text chat**: Accepted between 5 AM and midnight.
- **Voice chat**: Accepted between 8 AM and 12 PM.
- **Video chat**: Accepted between 8 PM and midnight.
Messages outside these time windows are rejected, and the client is notified of the unsuccessful status.

### Message Processing & Replies
- **Text chat**: The server replies with one text message, with a randomized response time between 0-1 seconds.
- **Voice chat**: The server replies with one text message and one voice message, with a randomized response time between 1-2 seconds.
- **Video chat**: The server replies with one text message, one voice message, and one image message, with a randomized response time between 2-3 seconds.
- **GPT-4o-mini Integration**: Text replies are generated using GPT-4o-mini, with customizable prompts.

### Client Disconnection Handling
- If a client disconnects before receiving reply messages, those messages are marked as unsuccessful.

### Chat History Retrieval
- Messages are saved to a database.
- An API is provided to retrieve messages with pagination, suitable for common chat screens like LINE, WhatsApp, or Telegram.

## Constraints
- A maximum of **50 clients** can communicate with the server simultaneously.
- A maximum of **500 messages** can be processed by the server at any time.
- Clients cannot establish multiple simultaneous connections.
- All clients must send at least one message to the server.


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
