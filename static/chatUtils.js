export async function fetchChatHistory(limit, offset, accessToken, chatHistory, appendToTop) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/messages/?limit=${limit}&offset=${offset}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch chat history');
        }

        const data = await response.json();
        const messages = data.messages;

        if (messages.length === 0) {
            return false; // No messages fetched
        }

        messages.reverse().forEach((message) => {
            const messageElement = document.createElement('p');
            messageElement.className = message.is_bot ? 'received' : 'sent';
            messageElement.textContent = message.content;

            if (appendToTop) {
                chatHistory.prepend(messageElement);
            } else {
                chatHistory.appendChild(messageElement);
            }
        });

        if (!appendToTop) {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        return true; // Messages fetched successfully
    } catch (error) {
        console.error('Error fetching chat history:', error);
        return false; // Treat as no messages fetched
    }
}

export async function fetchUserName(accessToken) {
    try {
        const response = await fetch(`/me?token=${accessToken}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user name');
        }

        const data = await response.json();
        return data.name;
    } catch (error) {
        console.error('Error fetching user name:', error);
        return null;
    }
}