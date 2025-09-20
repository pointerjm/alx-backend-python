#!/usr/bin/env python3
"""URL routing for the chats app using rest_framework.routers.DefaultRouter()."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Initialize DefaultRouter for standard routes
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Initialize NestedDefaultRouter for nested routes
messages_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
messages_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(messages_router.urls)),
]