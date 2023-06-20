const socket = new WebSocket(`ws://${window.location.host}/ws/chat/`);

    socket.onopen = () => {
      console.log('WebSocket connection established.');
      alert('WebSocket connection established.');
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

    function sendMessage() {
      const inputElement = document.getElementById('message-input');
      const message = inputElement.value;

      socket.send(JSON.stringify({ 'message': message }));

      inputElement.value = '';
    }