# file: messaging/managers.py

from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    """
    def unread_for_user(self, user):
        """
        Returns unread messages where the user is the receiver and read=False.
        """
        return self.filter(
            receiver=user,
            read=False
        )