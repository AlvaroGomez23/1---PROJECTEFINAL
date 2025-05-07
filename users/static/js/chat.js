document.addEventListener("DOMContentLoaded", function () {
    const conversationId = window.chatConfig.conversationId;
    const username = window.chatConfig.username;

    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${wsProtocol}://${window.location.host}/ws/chat/${conversationId}/`);

    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.messages) {
            chatContainer.innerHTML = '';
            data.messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', msg.sender === username ? 'sent' : 'received');
                messageDiv.textContent = msg.content;
                chatContainer.appendChild(messageDiv);
            });
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        if (data.message) {
            if (data.sender === username) return;
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', 'received');
            messageDiv.textContent = data.message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    };

    ws.onclose = function () {
        console.warn("⚠️ WebSocket cerrado.");
    };

    window.sendMessage = function () {
        const message = messageInput.value.trim();
        if (message === "") return;

        const messageId = Date.now();
        ws.send(JSON.stringify({
            'message': message,
            'sender': username,
            'id': messageId
        }));

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'sent');
        messageDiv.textContent = message;
        messageDiv.dataset.id = messageId;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        messageInput.value = '';
    };
});
