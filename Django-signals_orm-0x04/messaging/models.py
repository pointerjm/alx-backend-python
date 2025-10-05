# file: messaging/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from .managers import UnreadMessagesManager


class Conversation(models.Model):
    """
    Represents a conversation between multiple participants.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


class MessageHistory(models.Model):
    """
    Stores historical versions of edited messages.
    """
    original_message = models.ForeignKey(
        'Message', 
        related_name='history', 
        on_delete=models.CASCADE
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edit_history'
    )

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"Edit {self.id} for Message {self.original_message.id}"


class Message(models.Model):
    """
    Message model with fields for sender, receiver, content, timestamp, edit tracking,
    threaded conversations, and unread tracking.
    """
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name="sent_messages", 
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name="received_messages", 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    message_body = models.TextField()  # Content field (Step 0)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp field (Step 0)
    
    # Edit tracking - BOOLEAN FIELD for tracking if edited (Step 1)
    is_edited = models.BooleanField(default=False)
    
    # Edit tracking fields (Step 1)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_messages",
    )

    # Threaded conversations: self-referential FK (Step 3)
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )

    # Unread tracking - BOOLEAN FIELD for tracking if message is read (Step 4)
    read = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages (Step 4)

    def mark_as_edited(self, user):
        """Helper method to update edit fields when a message is modified."""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save(update_fields=["is_edited", "edited_at", "edited_by"])

    def __str__(self):
        return f"Message {self.id} in Conversation {self.conversation.id}"


class Notification(models.Model):
    """
    Stores notifications for users, linked to a message and user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        'Message',
        related_name="notifications",
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for User {self.user.id} on Message {self.message.id}"