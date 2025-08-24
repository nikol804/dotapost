import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from news.models import Post


@pytest.mark.django_db
def test_post_publish_sets_published_at_and_url_unique_per_month():
    user = User.objects.create_user(username='u', password='p')
    p1 = Post.objects.create(title='Hello World', body='<p>ok</p>', author=user, status=Post.Status.PUBLISHED)
    assert p1.published_at is not None
    url1 = p1.get_absolute_url()

    # same title same month -> slug unique suffix
    p2 = Post.objects.create(title='Hello World', body='<p>ok</p>', author=user, status=Post.Status.PUBLISHED)
    assert p2.slug != p1.slug
    assert p2.get_absolute_url() != url1


@pytest.mark.django_db
def test_post_body_sanitized():
    user = User.objects.create_user(username='u2', password='p')
    p = Post.objects.create(title='X', body='<script>alert(1)</script><p><a href="https://example.com" onclick="x">link</a></p>', author=user, status=Post.Status.PUBLISHED)
    assert '<script>' not in p.body
    assert 'onclick' not in p.body
    assert '<a href="https://example.com"' in p.body
