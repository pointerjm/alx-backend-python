#!/usr/bin/env python3
"""Serializers for the chats app."""

from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']

    def validate_message_body(self, value):
        """Validate message body is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    participants = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']

    def get_participants(self, obj):
        """Return serialized participants."""
        return UserSerializer(obj.participants.all(), many=True).data

    def validate(self, data):
        """Ensure at least one participant is provided on creation."""
        if self.context['request'].method == 'POST' and not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Authenticated user required to create a conversation.")
        return data