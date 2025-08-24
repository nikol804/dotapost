from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView

from news.models import Post, Comment


class ModeratorsOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_staff or user.is_superuser

    def handle_no_permission(self):
        # скрываем факт существования
        from django.http import Http404
        raise Http404


class ModerationDashboardView(LoginRequiredMixin, ModeratorsOnlyMixin, TemplateView):
    template_name = 'moderation/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_posts'] = Post.objects.filter(status=Post.Status.DRAFT).count()
        context['hidden_comments'] = Comment.objects.filter(status=Comment.Status.HIDDEN).count()
        return context


class PostQueueView(LoginRequiredMixin, ModeratorsOnlyMixin, ListView):
    template_name = 'moderation/posts_queue.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.filter(status=Post.Status.DRAFT).select_related('author').order_by('-created_at')


class CommentQueueView(LoginRequiredMixin, ModeratorsOnlyMixin, ListView):
    template_name = 'moderation/comments_queue.html'
    context_object_name = 'comments'
    paginate_by = 20

    def get_queryset(self):
        return Comment.objects.filter(status=Comment.Status.HIDDEN).select_related('author', 'post').order_by('-created_at')


