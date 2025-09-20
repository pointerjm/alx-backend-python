#!/usr/bin/env python3
"""Views for the chats app."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating conversations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Add authenticated user to participants on create."""
        serializer.save(participants=[self.request.user])


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating messages."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Set sender to authenticated user on create."""
        serializer.save(sender=self.request.user)