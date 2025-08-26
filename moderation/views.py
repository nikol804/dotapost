from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, View

from news.models import Post, Comment


class ModeratorsOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        # Доступ к модерации — только для администратора сайта (superuser)
        return user.is_superuser

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


class PostApproveView(LoginRequiredMixin, ModeratorsOnlyMixin, View):
    def post(self, request, pk: int) -> HttpResponseRedirect:
        post = get_object_or_404(Post, pk=pk)
        if post.status != Post.Status.PUBLISHED:
            post.status = Post.Status.PUBLISHED
            post.save(update_fields=['status', 'updated_at'])
        from .models import ModerationAction
        ModerationAction.objects.create(
            target_type=ModerationAction.TargetType.POST,
            target_id=post.pk,
            action=ModerationAction.Action.APPROVE,
            reason=request.POST.get('reason', '')[:255],
            moderator=request.user,
        )
        messages.success(request, 'Пост опубликован.')
        return redirect('moderation_posts')


class PostRejectView(LoginRequiredMixin, ModeratorsOnlyMixin, View):
    def post(self, request, pk: int) -> HttpResponseRedirect:
        post = get_object_or_404(Post, pk=pk)
        # В текущей модели нет статуса pending_review; оставляем draft, просто логируем.
        from .models import ModerationAction
        ModerationAction.objects.create(
            target_type=ModerationAction.TargetType.POST,
            target_id=post.pk,
            action=ModerationAction.Action.REJECT,
            reason=request.POST.get('reason', '')[:255],
            moderator=request.user,
        )
        messages.info(request, 'Решение по посту зафиксировано (отклонён).')
        return redirect('moderation_posts')


class CommentHideView(LoginRequiredMixin, ModeratorsOnlyMixin, View):
    def post(self, request, pk: int) -> HttpResponseRedirect:
        comment = get_object_or_404(Comment, pk=pk)
        if comment.status != Comment.Status.HIDDEN:
            comment.status = Comment.Status.HIDDEN
            comment.save(update_fields=['status', 'updated_at'])
        from .models import ModerationAction
        ModerationAction.objects.create(
            target_type=ModerationAction.TargetType.COMMENT,
            target_id=comment.pk,
            action=ModerationAction.Action.HIDE,
            reason=request.POST.get('reason', '')[:255],
            moderator=request.user,
        )
        messages.info(request, 'Комментарий скрыт.')
        return redirect('moderation_comments')


class CommentUnhideView(LoginRequiredMixin, ModeratorsOnlyMixin, View):
    def post(self, request, pk: int) -> HttpResponseRedirect:
        comment = get_object_or_404(Comment, pk=pk)
        if comment.status != Comment.Status.VISIBLE:
            comment.status = Comment.Status.VISIBLE
            comment.save(update_fields=['status', 'updated_at'])
        from .models import ModerationAction
        ModerationAction.objects.create(
            target_type=ModerationAction.TargetType.COMMENT,
            target_id=comment.pk,
            action=ModerationAction.Action.UNHIDE,
            reason=request.POST.get('reason', '')[:255],
            moderator=request.user,
        )
        messages.success(request, 'Комментарий восстановлен.')
        return redirect('moderation_comments')


