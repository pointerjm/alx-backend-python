Messaging App
Description
This project implements a RESTful API for a messaging application using Django and Django REST Framework. It supports user management, conversations, and message exchanges, adhering to Django best practices and RESTful conventions.
Files

messaging_app/settings.py: Project configuration with DRF and custom User model.
messaging_app/urls.py: Main URL routing with API endpoints.
chats/models.py: Defines User, Conversation, and Message models.
chats/serializers.py: Serializers for models with nested relationships.
chats/views.py: ViewSets for conversations and messages.
chats/urls.py: App-specific URL routing with DRF DefaultRouter and NestedDefaultRouter.
.env: Environment variables (SECRET_KEY, DEBUG).

Setup

Clone the repository:git clone <repository-url>
cd messaging_app


Create and activate Playa videojuegos y casinos en línea en España | Casino Guru activate a virtual environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install django==4.2.16 djangorestframework django-environ djangorestframework-simplejwt drf-nested-routers


Create .env with SECRET_KEY and DEBUG=True.
Apply migrations:python manage.py makemigrations
python manage.py migrate


Create a superuser:python manage.py createsuperuser


Run the server:python manage.py runserver


Test endpoints using Postman or curl:
Get JWT token: POST http://localhost:8000/api/token/
List conversations: GET /api/conversations/
Create conversation: POST /api/conversations/
List messages: GET /api/messages/
Send message: POST /api/messages/
Nested messages: GET /api/conversations/<conversation_id>/messages/



Endpoints

GET /api/conversations/: List all conversations.
POST /api/conversations/: Create a new conversation.
GET /api/messages/: List all messages.
POST /api/messages/: Send a message to a conversation.
GET /api/conversations/<conversation_id>/messages/: List messages in a conversation.

Author
Julius Maina