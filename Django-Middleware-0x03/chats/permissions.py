from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only participants in a conversation to send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        conversation = getattr(obj, "conversation", None)
        if not conversation:
            return False

        # Only participants can access
        if request.user not in conversation.participants.all():
            return False

        # Allow safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Explicitly allow PUT, PATCH, DELETE for participants only
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return True

        # Allow POST for participants
        if request.method == "POST":
            return True

        return False
