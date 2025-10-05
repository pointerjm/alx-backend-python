# file: messaging/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Notification
from rest_framework.test import APIClient


class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username='user1', password='testpass123'
        )
        self.user2 = get_user_model().objects.create_user(
            username='user2', password='testpass123'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)
        self.client = APIClient()

    def test_message_notification_signal(self):
        """
        Test that a notification is created when a new message is sent.
        """
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            receiver=self.user2,
            message_body="Hello, user2!"
        )
        
        # Check if a notification was created for the receiver
        notification = Notification.objects.filter(
            user=self.user2,
            message=message
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.read)

    def test_unread_messages_manager(self):
        """
        Test the UnreadMessagesManager for filtering unread messages.
        """
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            receiver=self.user2,
            message_body="Unread message",
            read=False
        )
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            receiver=self.user2,
            message_body="Read message",
            read=True
        )
        
        unread_messages = Message.unread.unread_for_user(self.user2)
        self.assertEqual(unread_messages.count(), 1)
        self.assertEqual(unread_messages.first().message_body, "Unread message")