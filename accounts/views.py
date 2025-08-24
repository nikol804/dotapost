from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from .forms import UserRegistrationForm, ProfileForm
from .models import Profile
from news.models import Post


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        login(self.request, user)
        messages.success(self.request, 'Регистрация успешна.')
        return response


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_edit.html'
    form_class = ProfileForm
    success_url = reverse_lazy('profile_edit')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Профиль обновлён.')
        return super().form_valid(form)


class PublicProfileView(DetailView):
    template_name = 'accounts/profile_public.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        return get_object_or_404(User, username=username)


class UserPostsView(ListView):
    template_name = 'accounts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return (
            Post.objects.filter(author=user, status=Post.Status.PUBLISHED)
            .select_related('author')
            .order_by('-published_at')
        )
