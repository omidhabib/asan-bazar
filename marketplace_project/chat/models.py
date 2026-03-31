from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """Chat conversation between a buyer and a seller about a specific ad."""
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation #{self.pk} about '{self.ad}'"

    def other_participant(self, user):
        """Get the other participant in the conversation."""
        return self.participants.exclude(pk=user.pk).first()


class Message(models.Model):
    """A single message within a conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
