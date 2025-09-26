#!/usr/bin/env python3
"""Views for the chats app."""

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating conversations."""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ["participants__email"]

    def get_queryset(self):
        """Return only conversations where the user is a participant."""
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """Add authenticated user to participants on create."""
        serializer.save(participants=[self.request.user])


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating messages."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["message_body"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return messages only from conversations where the user is a participant."""
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        """Set sender to authenticated user on create."""
        serializer.save(sender=self.request.user)
