# file: messaging/admin.py

from django.contrib import admin
from .models import Conversation, Message, MessageHistory, Notification


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'participant_list']
    list_filter = ['created_at']
    search_fields = ['participants__username']

    def participant_list(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    participant_list.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'receiver', 'message_body', 'created_at', 'is_edited', 'read']
    list_filter = ['created_at', 'is_edited', 'read']
    search_fields = ['message_body', 'sender__username', 'receiver__username']


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_message', 'old_content', 'edited_at', 'edited_by']
    list_filter = ['edited_at']
    search_fields = ['old_content']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'created_at', 'read']
    list_filter = ['created_at', 'read']
    search_fields = ['user__username', 'message__message_body']