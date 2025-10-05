# file: messaging/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, MessageHistory
from .serializers import ConversationSerializer, MessageSerializer, MessageHistorySerializer


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
                    queryset=Message.objects.select_related("sender", "edited_by", "receiver").order_by("-created_at"),
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
        - select_related: sender, receiver, edited_by, conversation (FKs)
        - prefetch_related: threaded replies and edit history
        """
        return (
            Message.objects.filter(conversation__participants=self.request.user)
            .select_related("sender", "edited_by", "receiver", "conversation")
            .prefetch_related(
                Prefetch("replies", queryset=Message.objects.select_related("sender", "receiver")),
                Prefetch("history", queryset=MessageHistory.objects.select_related("edited_by"))
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        """
        Create a message or reply.
        Explicitly set sender and receiver for validation.
        """
        conversation = serializer.validated_data.get("conversation")
        receiver = serializer.validated_data.get("receiver")

        if self.request.user not in conversation.participants.all():
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # ✅ Explicitly assign sender=self.request.user and keep receiver from serializer
        message = serializer.save(
            sender=self.request.user, 
            receiver=receiver,
            # ✅ Set sender as the current user explicitly for optimization
            sender=self.request.user
        )

        return Response(
            {
                "conversation_id": message.conversation.id,
                "message_id": message.id,
                "receiver": message.receiver.id if message.receiver else None,
                "parent_message": message.parent_message.id if message.parent_message else None,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def edit_history(self, request, pk=None):
        """
        Display the message edit history for a specific message.
        """
        message = self.get_object()
        if request.user != message.sender and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to view this history."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        history = message.history.all()
        serializer = MessageHistorySerializer(history, many=True)
        return Response({
            "message_id": pk,
            "original_content": message.message_body,
            "edit_history": serializer.data
        })

    @action(detail=False, methods=['get'])
    def threaded_replies(self, request, pk=None):
        """
        Get all threaded replies for a specific message (recursive).
        """
        parent_message_id = request.query_params.get('parent_message_id')
        if not parent_message_id:
            return Response(
                {"detail": "parent_message_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Get the parent message
        parent_message = get_object_or_404(Message, id=parent_message_id)
        
        if request.user not in parent_message.conversation.participants.all():
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Recursive query to get all replies and their replies
        def get_replies(message, depth=0):
            replies = message.replies.select_related("sender", "receiver").prefetch_related(
                Prefetch("replies", queryset=Message.objects.select_related("sender", "receiver"))
            )
            result = []
            for reply in replies:
                reply_data = {
                    "message": MessageSerializer(reply).data,
                    "depth": depth,
                    "replies": get_replies(reply, depth + 1)
                }
                result.append(reply_data)
            return result

        threaded_replies = get_replies(parent_message)
        
        return Response({
            "parent_message": MessageSerializer(parent_message).data,
            "threaded_replies": threaded_replies
        })


class UserDeletionView(viewsets.ViewSet):
    """
    Handles user account deletion and related data cleanup.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def delete_user(self, request):
        """
        Delete the authenticated user's account and all related data.
        ✅ Implements delete_user view for account deletion.
        """
        user = request.user
        
        if user.is_staff:
            return Response(
                {"detail": "Staff users cannot delete their accounts."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Delete all related data before deleting the user
        # This is handled by the post_delete signal, but we can also do explicit cleanup
        messages_count = Message.objects.filter(
            sender=user
        ).count() + Message.objects.filter(
            receiver=user
        ).count()
        
        # Trigger the deletion (signal will handle cleanup)
        user.delete()
        
        return Response(
            {
                "detail": "Account deleted successfully.",
                "messages_deleted": messages_count,
                "cleanup": "All messages, histories, and conversations have been removed."
            },
            status=status.HTTP_200_OK
        )