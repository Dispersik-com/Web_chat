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

![Global_room](https://github.com/Dispersik-com/Web_chat/assets/126075849/3d99fb5e-d328-47b3-9ee6-70d080606a4f)

![Chat_room](https://github.com/Dispersik-com/Web_chat/assets/126075849/31e9a288-b0a5-4dec-9549-b1b6d8df2656)

## How to run:

bash
```
git clone
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
