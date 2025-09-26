from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access and modify its messages.
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant of the conversation.
        Assuming Message model has a foreign key to Conversation
        and Conversation has a ManyToManyField participants.
        """
        conversation = getattr(obj, "conversation", None)
        if conversation:
            return request.user in conversation.participants.all()
        return False
