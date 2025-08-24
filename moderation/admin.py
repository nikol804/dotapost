from django.contrib import admin

from .models import ModerationAction


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'target_type', 'target_id', 'action', 'moderator', 'created_at')
    list_filter = ('target_type', 'action', 'created_at')
    search_fields = ('reason', 'moderator__username')


