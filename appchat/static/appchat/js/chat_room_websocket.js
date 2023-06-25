
function addMessageToChat(sender, message) {
    const chatContainer = document.querySelector('.chat');

    // Создание элементов сообщения
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

    // Добавление элементов в иерархию DOM
    messageInfo.appendChild(userName);
    messageBubble.appendChild(messageInfo);
    messageBubble.appendChild(messageContent);
    chatContainer.appendChild(messageBubble);
}

// Создание WebSocket соединения
var chatRoomSlug = '{{ chat_room.slug }}' + '/';
var socketURL = 'ws://' + window.location.host + '/ws/chat_room/' + chatRoomSlug;
const socket = new WebSocket(socketURL);


  // Обработчик открытия соединения
  socket.onopen = function(event) {
    console.log('WebSocket connection opened');
  };

  // Обработчик закрытия соединения
  socket.onclose = function(event) {
    console.log('WebSocket connection closed');
  };

  // Обработчик получения сообщения от сервера
  socket.onmessage = function(event) {
    const response = JSON.parse(event.data);
    const message = JSON.parse(event.data).message;
    const sender = JSON.parse(event.data).sender;
    console.log('Received message from server:', message);
    addMessageToChat(sender, message);
  };

  // Функция отправки сообщения на сервер
  function sendMessage() {
    const messageInput = document.getElementById('message');
    const message = messageInput.value;

    // Проверка, что сообщение не пустое
    if (message.trim() !== '') {
      const data = {
        type: 'chat_message',
        sender: '{{ user.username }}',
        message: message
      };

      // Отправка сообщения на сервер в формате JSON
      socket.send(JSON.stringify(data));

      // Очистка поля ввода сообщения
      messageInput.value = '';
    }
  }

    // Назначение обработчика события нажатия на кнопку "Send"
    const sendButton = document.querySelector('.send-button');
    sendButton.addEventListener('click', sendMessage);
