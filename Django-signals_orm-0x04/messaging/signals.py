# file: messaging/signals.py

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Message, MessageHistory, Notification


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Log old content to MessageHistory before saving an edited message (Step 1).
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


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up all messages, notifications, and message histories when user is deleted (Step 2).
    """
    # Delete all messages sent/received by the user
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all message history related to the user
    MessageHistory.objects.filter(edited_by=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Delete conversation participation
    instance.conversations.clear()


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Create a notification for the receiver when a new message is created (Step 0).
    """
    if created and instance.receiver:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )