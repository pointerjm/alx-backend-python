# file: messaging/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .managers import UnreadMessagesManager


class Conversation(models.Model):
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
    Message model with edit tracking, threaded conversation support, and unread tracking.
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
    message_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ✅ Edit tracking - BOOLEAN FIELD for tracking if edited
    is_edited = models.BooleanField(default=False)
    
    # ✅ Edit tracking
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="edited_messages",
    )

    # ✅ Threaded conversations: self-referential FK
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )

    # ✅ Unread tracking - BOOLEAN FIELD for tracking if message is read
    read = models.BooleanField(default=False)

    # ✅ Custom manager for unread messages
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    def mark_as_edited(self, user):
        """Helper method to update edit fields when a message is modified."""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save(update_fields=["is_edited", "edited_at", "edited_by"])

    def __str__(self):
        return f"Message {self.id} in Conversation {self.conversation.id}"


# ✅ Signal for logging message edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Log old content to MessageHistory before saving an edited message.
    """
    if instance.pk:  # Existing message
        try:
            old_message = sender.objects.get(pk=instance.pk)
            # Check if this is an edit (message_body changed)
            if old_message.message_body != instance.message_body:
                # Create history record
                MessageHistory.objects.create(
                    original_message=instance,
                    old_content=old_message.message_body,
                    edited_by=old_message.edited_by or old_message.sender
                )
        except sender.DoesNotExist:
            pass


# ✅ Signal for deleting user-related data
@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up all messages, notifications, and message histories when user is deleted.
    """
    # Delete all messages sent/received by the user
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all message history related to the user
    MessageHistory.objects.filter(
        edited_by=instance
    ).delete()
    
    # Delete conversation participation
    instance.conversations.clear()