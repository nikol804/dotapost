import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from news.models import Post, Comment, Like


@pytest.mark.django_db
def test_like_toggle(client):
    user = User.objects.create_user(username='u', password='p')
    client.login(username='u', password='p')
    post = Post.objects.create(title='A', body='<p>ok</p>', author=user, status=Post.Status.PUBLISHED)
    url = reverse('post_like_toggle', kwargs={'year': post.published_at.year, 'month': post.published_at.month, 'slug': post.slug})
    # like
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert Like.objects.filter(post=post, user=user).exists()
    # unlike
    resp = client.post(url, follow=True)
    assert resp.status_code == 200
    assert not Like.objects.filter(post=post, user=user).exists()


@pytest.mark.django_db
def test_comment_create_and_delete_own(client):
    user = User.objects.create_user(username='u2', password='p')
    client.login(username='u2', password='p')
    post = Post.objects.create(title='B', body='<p>ok</p>', author=user, status=Post.Status.PUBLISHED)

    create_url = reverse('comment_create', kwargs={'year': post.published_at.year, 'month': post.published_at.month, 'slug': post.slug})
    resp = client.post(create_url, data={'body': '<p>Hello</p>'}, follow=True)
    assert resp.status_code == 200
    c = Comment.objects.get(post=post, author=user)

    delete_url = reverse('comment_delete', kwargs={'pk': c.pk})
    resp = client.post(delete_url, follow=True)
    assert resp.status_code == 200
    assert not Comment.objects.filter(pk=c.pk).exists()


@pytest.mark.django_db
def test_comment_rate_limit(client):
    user = User.objects.create_user(username='u3', password='p')
    client.login(username='u3', password='p')
    post = Post.objects.create(title='C', body='<p>ok</p>', author=user, status=Post.Status.PUBLISHED)

    url = reverse('comment_create', kwargs={'year': post.published_at.year, 'month': post.published_at.month, 'slug': post.slug})
    r1 = client.post(url, data={'body': 'first'}, follow=True)
    assert r1.status_code == 200
    r2 = client.post(url, data={'body': 'second'}, follow=True)
    # second should be blocked by rate limit; still 200 redirect but only one comment created
    assert Comment.objects.filter(post=post, author=user).count() == 1
