function addMessageToChat(sender, message) {
    const chatContainer = document.querySelector('.chat');

    // Створення елементів повідомлення
    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble');
    messageBubble.classList.add(sender === '{{ user.username }}' ? 'right' : 'left');

    const messageInfo = document.createElement('div');
    messageInfo.classList.add('message-info');

    const userName = document.createElement('span');
    userName.classList.add('user-name');
    userName.style.color = sender === '{{ user.username }}' ? 'red' : 'green';
    userName.textContent = sender;

    const messageContent = document.createElement('p');
    messageContent.textContent = message;

    // Додавання елементів до ієрархії DOM
    messageInfo.appendChild(userName);
    messageBubble.appendChild(messageInfo);
    messageBubble.appendChild(messageContent);
    chatContainer.appendChild(messageBubble);
}

// Створення WebSocket з'єднання
var chatRoomSlug = '{{ chat_room.slug }}' + '/';
var socketURL = 'ws://' + window.location.host + '/ws/chat_room/' + chatRoomSlug;
const socket = new WebSocket(socketURL);

// Обробник відкриття з'єднання
socket.onopen = function(event) {
    console.log('WebSocket з'єднання відкрито');
};

// Обробник закриття з'єднання
socket.onclose = function(event) {
    console.log('WebSocket з'єднання закрито');
};

// Обробник отримання повідомлення від сервера
socket.onmessage = function(event) {
    const response = JSON.parse(event.data);
    const message = JSON.parse(event.data).message;
    const sender = JSON.parse(event.data).sender;
    console.log('Отримано повідомлення від сервера:', message);
    addMessageToChat(sender, message);
};

// Функція відправки повідомлення на сервер
function sendMessage() {
    const messageInput = document.getElementById('message');
    const message = messageInput.value;

    // Перевірка, що повідомлення не порожнє
    if (message.trim() !== '') {
        const data = {
            type: 'chat_message',
            sender: '{{ user.username }}',
            message: message
        };

        // Відправка повідомлення на сервер у форматі JSON
        socket.send(JSON.stringify(data));

        // Очищення поля введення повідомлення
        messageInput.value = '';
    }
}

// Призначення обробника події натискання на кнопку "Send"
const sendButton = document.querySelector('.send-button');
sendButton.addEventListener('click', sendMessage);
