# Web_chat


This is a project aimed at learning Django framework. The project implements basic development methods of web-applications. However, the project also can function fully.

The project includes:
* Working with templates;
* Forms;
* ORM models;
* Authorization, authentication, tokens;
* Django REST Framework (Serializers, View, ViewSets, Routers);
* Asgi (Django Channels WebSocket).

This project implements a simple chat, where users can communicate with each other. Users can create the rooms (public or private) and add each other to friends.

Here are a few screenshots of the website pages.

**The view of Chat room:**

![Chat_room](https://github.com/Dispersik-com/Web_chat/assets/126075849/31e9a288-b0a5-4dec-9549-b1b6d8df2656)

**The view of profile page:**

![profile](https://github.com/Dispersik-com/Web_chat/assets/126075849/74615adf-ccb4-478a-9bfc-8821e52d87e3)


## How to run:

bash
```
git clone https://github.com/Dispersik-com/Web_chat.git
cd Web_chat
python3 -m venv venv
source venv/bin/activate
python manage.py migrate
```

To run the project with WebSockets, use the Daphne server.

```
daphne -b 127.0.0.1 -p 8000 MustHaveChat.asgi:application
```

### P.S.

This project may be helpful not only to me.

Over time, comments will also be duplicated in English.
