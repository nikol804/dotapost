from __future__ import annotations

from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Count, Q, Prefetch
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.utils import timezone

from .forms import PostForm, CommentForm
from .models import Post, Comment, Like


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'news/post_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related('author')
            .annotate(comments_count=Count('comments', filter=Q(comments__status=Comment.Status.VISIBLE)))
            .annotate(likes_count=Count('likes'))
            .order_by('-published_at')
        )
        return qs


class InterestingPostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'news/post_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related('author')
            .annotate(
                comments_count=Count(
                    'comments',
                    filter=Q(comments__status=Comment.Status.VISIBLE),
                )
            )
            .annotate(likes_count=Count('likes'))
            .order_by('-likes_count', '-published_at')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Интересные посты'
        return context


class TopWeekPostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'news/post_list.html'
    paginate_by = 10

    def get_queryset(self):
        start_dt = timezone.now() - timedelta(days=7)
        queryset = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related('author')
            .annotate(
                comments_count=Count(
                    'comments',
                    filter=Q(comments__status=Comment.Status.VISIBLE),
                )
            )
            .annotate(likes_count=Count('likes', filter=Q(likes__created_at__gte=start_dt)))
            .order_by('-likes_count', '-published_at')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Топ за неделю'
        return context


class TopMonthPostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'news/post_list.html'
    paginate_by = 10

    def get_queryset(self):
        start_dt = timezone.now() - timedelta(days=30)
        queryset = (
            Post.objects.filter(status=Post.Status.PUBLISHED)
            .select_related('author')
            .annotate(
                comments_count=Count(
                    'comments',
                    filter=Q(comments__status=Comment.Status.VISIBLE),
                )
            )
            .annotate(likes_count=Count('likes', filter=Q(likes__created_at__gte=start_dt)))
            .order_by('-likes_count', '-published_at')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Топ за месяц'
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        year = self.kwargs['year']
        month = self.kwargs['month']
        slug = self.kwargs['slug']
        post = get_object_or_404(
            Post,
            Q(published_at__year=year, published_at__month=month) | Q(created_at__year=year, created_at__month=month),
            slug=slug,
        )
        if post.status != Post.Status.PUBLISHED and self.request.user != post.author:
            raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']
        comments = (
            post.comments.filter(status=Comment.Status.VISIBLE, parent__isnull=True)
            .select_related('author')
            .prefetch_related(
                Prefetch(
                    'replies',
                    queryset=Comment.objects.filter(status=Comment.Status.VISIBLE)
                    .select_related('author')
                    .order_by('created_at'),
                )
            )
        )
        context['comments'] = comments
        context['comment_form'] = CommentForm()
        context['likes_count'] = post.likes.count()
        context['user_liked'] = self.request.user.is_authenticated and Like.objects.filter(post=post, user=self.request.user).exists()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Пост сохранён.')
        return response


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_form.html'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise Http404
        return super().handle_no_permission()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Пост обновлён.')
        return response


class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, year: int, month: int, slug: str) -> HttpResponse:
        post = get_object_or_404(Post, slug=slug, published_at__year=year, published_at__month=month)
        like = Like.objects.filter(post=post, user=request.user).first()
        if like:
            like.delete()
            messages.info(request, 'Лайк удалён.')
        else:
            Like.objects.create(post=post, user=request.user)
            messages.success(request, 'Пост лайкнут.')
        return redirect(post.get_absolute_url())


class CommentCreateView(LoginRequiredMixin, View):
    RATE_SECONDS = 10

    def post(self, request: HttpRequest, year: int, month: int, slug: str) -> HttpResponse:
        post = get_object_or_404(Post, slug=slug, published_at__year=year, published_at__month=month)

        session_key = request.session.session_key or 'nosession'
        cache_key = f"comment_rate_limit:{request.user.id}:{session_key}"
        if cache.get(cache_key):
            messages.error(request, 'Слишком часто. Попробуйте через несколько секунд.')
            return redirect(post.get_absolute_url())

        form = CommentForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Ошибка в комментарии.')
            return redirect(post.get_absolute_url())

        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        parent_id = request.POST.get('parent')
        if parent_id:
            try:
                parent_pk = int(parent_id)
            except (TypeError, ValueError):
                messages.error(request, 'Некорректная ссылка на родительский комментарий.')
                return redirect(post.get_absolute_url())
            parent_comment = Comment.objects.filter(pk=parent_pk, post=post, status=Comment.Status.VISIBLE).first()
            if not parent_comment:
                messages.error(request, 'Родительский комментарий не найден.')
                return redirect(post.get_absolute_url())
            # ограничиваем глубину до 1 уровня
            if parent_comment.parent_id is not None:
                messages.error(request, 'Нельзя отвечать на ответ. Максимум один уровень вложенности.')
                return redirect(post.get_absolute_url())
            comment.parent = parent_comment
        comment.save()

        cache.set(cache_key, True, timeout=self.RATE_SECONDS)
        messages.success(request, 'Комментарий добавлен.')
        return redirect(post.get_absolute_url())


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author != request.user:
            raise Http404
        comment.delete()
        messages.info(request, 'Комментарий удалён.')
        # redirect to post detail
        return redirect(comment.post.get_absolute_url())
