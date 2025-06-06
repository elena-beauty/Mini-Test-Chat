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



---

## Sequence Diagram
### Client Connection
1. User opens the chat interface ([`static/chat.html`]
2. WebSocket connection is established via [`services/websocket.py`]
3. User authentication is verified using [`services/user.py`]

### Message Handling
1. Client sends a message via WebSocket.
2. Message is processed by [`services/websocket.py`]
3. Message is stored in the database using [`services/chat_history.py`]
4. Message is broadcasted to other connected clients.

### Client Disconnection
1. Client disconnects from WebSocket.
2. [`services/websocket.py`]
3. Disconnection is logged for monitoring purposes.

---

## Scalability Considerations
- **Horizontal Scaling**: Deploy multiple instances of the WebSocket service behind a load balancer.
- **Database Optimization**: Use indexing and caching for frequently accessed chat history.
- **Static File Delivery**: Serve frontend files via a CDN for faster access.

---

## Implementation Plan
1. **Environment Setup**:
   - Configure dependencies using [`pyproject.toml`] and [`requirements.txt`]
   - Set up Docker containers using [`docker-compose.yaml`]

2. **Backend Development**:
   - Implement WebSocket logic in [`services/websocket.py`]Mini-Test-Chat/services/websocket.py.
   - Develop chat history and user management modules ([`services/chat_history.py`]Mini-Test-Chat/services/chat_history.py"), [`services/user.py`]

3. **Frontend Design**:
   - Create user interfaces ([`static/chat.html`]
   Mini-Test-Chat/static/chat.html"), [`static/login.html`]
   Mini-Test-Chat/static/login.html"), [`static/signup.html`]
   - Add WebSocket client logic in [`static/chatUtils.js`]

4. **Testing**:
   - Write unit tests [`tests/services/test_websocket.py`]
   - Validate WebSocket connection and disconnection handling.

5. **Deployment**:
   - Deploy the application using Docker.
   - Monitor system performance and scale as needed.

---

## Additional Notes
For detailed instructions on running the application, refer to the [Getting Started](#getting-started) section.

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

## Getting Started

Follow the steps below to set up and run the application locally.

### 1. Clone the Repository
```bash
git clone https://github.com/elena-beauty/Mini-Test-Chat.git
cd Mini-Test-Chat
```

2. **Run in local**:
    ```bash
    Run docker with: 
    $ docker-compose up 
    to start Database postgres
    ```

3. **Create table in database**
```bash
-- Create the users table
CREATE TABLE users (
   id SERIAL PRIMARY KEY,
   name VARCHAR NOT NULL,
   email VARCHAR UNIQUE NOT NULL,
   gender VARCHAR NOT NULL,
   password VARCHAR NOT NULL
);

-- Create the chat_histories table
CREATE TABLE chat_histories (
   id SERIAL PRIMARY KEY,
   user_id VARCHAR NOT NULL,
   message_type VARCHAR NOT NULL,
   content VARCHAR NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   is_bot VARCHAR DEFAULT 'False'
);
```

4, **Run in terminal to start server**
   ```bash
   pip3 install -r requirements.txt

   uvicorn main:app --reload

   kill -9 $(lsof -ti :8000)
   ```
