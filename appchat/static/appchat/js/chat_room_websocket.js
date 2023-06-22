const socket = new WebSocket(`ws://${window.location.host}/ws/chat/`);

socket.onopen = () => {
  console.log('WebSocket connection established.');
  alert('WebSocket connection established.');

  // Получаем ссылки на элементы DOM по их идентификаторам
  const messageInput = document.getElementById('message');
  const sendButton = document.getElementById('send-button');

  // Создаем функцию-обработчик события нажатия на кнопку
  function sendMessage() {
    // Получаем текст из текстового поля
    const message = messageInput.value;

    // Выполняем необходимые действия с сообщением
    console.log('Отправляем сообщение:', message);

    // Очищаем текстовое поле
    messageInput.value = '';
  }

  // Добавляем слушатель события нажатия на кнопку
  sendButton.addEventListener('click', sendMessage);
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data).message;
  console.log('Received message from server:', message);

  // Отображение ответа на странице
  const responseElement = document.getElementById('response');
  responseElement.value = message;
};

socket.onclose = (event) => {
  console.log('WebSocket connection closed:', event);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
