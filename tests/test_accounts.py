import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import Profile
from news.models import Post


@pytest.mark.django_db
def test_registration_creates_profile(client):
    resp = client.post(reverse('register'), data={
        'username': 'newuser',
        'password1': 'Passw0rd!Passw0rd!',
        'password2': 'Passw0rd!Passw0rd!',
        'email': 'u@example.com'
    }, follow=True)
    assert resp.status_code == 200
    u = User.objects.get(username='newuser')
    assert Profile.objects.filter(user=u).exists()


@pytest.mark.django_db
def test_user_posts_list(client):
    author = User.objects.create_user(username='author', password='p')
    p = Post.objects.create(title='Visible', body='<p>ok</p>', author=author, status=Post.Status.PUBLISHED)
    url = reverse('user_posts', kwargs={'username': 'author'})
    resp = client.get(url)
    assert resp.status_code == 200
    assert b'Visible' in resp.content
