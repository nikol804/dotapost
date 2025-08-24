from __future__ import annotations

from django.conf import settings
from django.db import models


class ModerationAction(models.Model):
    class TargetType(models.TextChoices):
        POST = 'post', 'Post'
        COMMENT = 'comment', 'Comment'

    class Action(models.TextChoices):
        APPROVE = 'approve', 'Approve'
        REJECT = 'reject', 'Reject'
        HIDE = 'hide', 'Hide'
        UNHIDE = 'unhide', 'Unhide'

    target_type = models.CharField(max_length=10, choices=TargetType.choices, db_index=True)
    target_id = models.PositiveIntegerField(db_index=True)
    action = models.CharField(max_length=10, choices=Action.choices, db_index=True)
    reason = models.CharField(max_length=255, blank=True)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='moderation_actions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['target_type', 'target_id']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.moderator} {self.action} {self.target_type}:{self.target_id}"


