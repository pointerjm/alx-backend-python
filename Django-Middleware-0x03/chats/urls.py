#!/usr/bin/env python3
"""URL routing for the chats app using rest_framework.routers.DefaultRouter()."""

from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet

# Initialize DefaultRouter for standard routes
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Initialize NestedDefaultRouter for nested routes
messages_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
messages_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(messages_router.urls)),
]
