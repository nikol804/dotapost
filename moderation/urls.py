from django.urls import path

from . import views


urlpatterns = [
    path('', views.ModerationDashboardView.as_view(), name='moderation_dashboard'),
    path('posts/', views.PostQueueView.as_view(), name='moderation_posts'),
    path('comments/', views.CommentQueueView.as_view(), name='moderation_comments'),
]


