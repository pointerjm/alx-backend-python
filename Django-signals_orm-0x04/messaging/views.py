# file: messaging/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Prefetch

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Handles listing and creating conversations.
    Optimized with prefetch_related to reduce queries.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related(
                Prefetch(
                    "messages",
                    queryset=Message.objects.select_related("sender", "edited_by").order_by("-created_at"),
                )
            )
            .distinct()
        )

    def perform_create(self, serializer):
        conversation = serializer.save(participants=[self.request.user])
        return Response(
            {"conversation_id": conversation.id},
            status=status.HTTP_201_CREATED,
        )


class MessageViewSet(viewsets.ModelViewSet):
    """
    Handles sending messages and threaded replies.
    Uses select_related for sender/receiver, and supports recursive replies.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimized query:
        - select_related: sender and receiver (FKs)
        - prefetch_related: threaded replies
        """
        return (
            Message.objects.filter(conversation__participants=self.request.user)
            .select_related("sender", "edited_by", "conversation")
            .prefetch_related(
                Prefetch("replies", queryset=Message.objects.select_related("sender"))
            )
        )

    def perform_create(self, serializer):
        """
        Create a message or reply.
        If a reply_to is provided, link this message as a threaded reply.
        """
        conversation = serializer.validated_data.get("conversation")
        if self.request.user not in conversation.participants.all():
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        message = serializer.save(sender=self.request.user)

        return Response(
            {
                "conversation_id": message.conversation.id,
                "message_id": message.id,
                "reply_to": message.reply_to.id if message.reply_to else None,
            },
            status=status.HTTP_201_CREATED,
        )