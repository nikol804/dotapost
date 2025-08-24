from django.contrib import admin
from .models import Post, Comment, Like


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'status', 'published_at', 'created_at')
    list_filter = ('status', 'published_at', 'created_at')
    search_fields = ('title', 'summary', 'slug')
    date_hierarchy = 'published_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('body',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    search_fields = ('user__username', 'post__title')
