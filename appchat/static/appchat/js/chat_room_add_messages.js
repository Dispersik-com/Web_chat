document.addEventListener('DOMContentLoaded', function() {
    var messageForm = document.getElementById('message-form');
    var messageInput = document.getElementById('message');
    var chatContainer = document.querySelector('.chat');
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    messageForm.addEventListener('submit', function(event) {
      event.preventDefault();
      var message = messageInput.value.trim();
      if (message !== '') {
        // Отправка нового сообщения на сервер
        var xhr = new XMLHttpRequest();
        xhr.open('POST', window.location.href);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.onload = function() {
          if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            var messageData = response.message;

            // Создание нового элемента для сообщения
            var messageBubble = document.createElement('div');
            messageBubble.className = 'message-bubble';
            if (messageData.sender.username === '{{ user.username }}') {
              messageBubble.style.float = 'right';
            } else {
              messageBubble.style.float = 'left';
            }

            // Создание HTML-разметки для нового сообщения
            var messageInfo = document.createElement('div');
            messageInfo.className = 'message-info';
            var userName = document.createElement('span');
            userName.className = 'user-name';
            if (messageData.sender.username === '{{ user.username }}') {
              userName.style.color = 'red';
            } else {
              userName.style.color = 'green';
            }
            userName.textContent = messageData.sender.username;

            var messageText = document.createElement('p');
            messageText.textContent = messageData.message;

            // Добавление элементов в иерархию
            messageInfo.appendChild(userName);
            messageBubble.appendChild(messageInfo);
            messageBubble.appendChild(messageText);

            // Добавление нового сообщения в контейнер
            chatContainer.appendChild(messageBubble);

            // Очистка поля ввода сообщения
            messageInput.value = '';
          }
        };
        xhr.send('message=' + encodeURIComponent(message));
      }
    });
  });