from django.urls import path

from . import views


urlpatterns = [
    path('', views.ModerationDashboardView.as_view(), name='moderation_dashboard'),
    path('posts/', views.PostQueueView.as_view(), name='moderation_posts'),
    path('comments/', views.CommentQueueView.as_view(), name='moderation_comments'),
    path('posts/<int:pk>/approve/', views.PostApproveView.as_view(), name='moderation_post_approve'),
    path('posts/<int:pk>/reject/', views.PostRejectView.as_view(), name='moderation_post_reject'),
    path('comments/<int:pk>/hide/', views.CommentHideView.as_view(), name='moderation_comment_hide'),
    path('comments/<int:pk>/unhide/', views.CommentUnhideView.as_view(), name='moderation_comment_unhide'),
]


