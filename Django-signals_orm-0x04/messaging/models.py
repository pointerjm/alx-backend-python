# file: messaging/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE
    )
    message_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Edit tracking fields
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_messages",
    )

    def mark_as_edited(self, user):
        """Helper method to update edit fields when a message is modified."""
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save(update_fields=["edited_at", "edited_by"])

    def __str__(self):
        return f"Message {self.id} in Conversation {self.conversation.id}"
