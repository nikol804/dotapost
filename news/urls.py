from django.urls import path

from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    LikeToggleView,
    CommentCreateView,
    CommentDeleteView,
    InterestingPostListView,
    TopWeekPostListView,
    TopMonthPostListView,
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('interesting/', InterestingPostListView.as_view(), name='post_interesting'),
    path('top/week/', TopWeekPostListView.as_view(), name='post_top_week'),
    path('top/month/', TopMonthPostListView.as_view(), name='post_top_month'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('<int:year>/<int:month>/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('<int:year>/<int:month>/<slug:slug>/like/', LikeToggleView.as_view(), name='post_like_toggle'),
    path('<int:year>/<int:month>/<slug:slug>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]
