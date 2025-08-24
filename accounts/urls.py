from django.urls import path, include
from allauth.account import views as allauth_views
from django.contrib.auth.views import LogoutView

from .views import ProfileEditView, PublicProfileView, UserPostsView

urlpatterns = [
    # allauth views with our URLs for backward compatibility
    path('accounts/login/', allauth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/register/', allauth_views.SignupView.as_view(template_name='accounts/register.html'), name='register'),

    # profiles
    path('accounts/profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('u/<str:username>/', PublicProfileView.as_view(), name='profile_public'),
    path('u/<str:username>/posts/', UserPostsView.as_view(), name='user_posts'),

    # include the rest of allauth endpoints (password reset, etc.)
    path('accounts/', include('allauth.urls')),
]
