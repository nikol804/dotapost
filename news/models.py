from __future__ import annotations

from typing import Optional

import bleach
from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone


ALLOWED_TAGS = [
    'a', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'code', 'pre', 'img', 'blockquote', 'br', 'h2', 'h3', 'h4'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title']
}
ALLOWED_PROTOCOLS = ['http', 'https']


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=200)
    slug = models.SlugField()
    summary = models.TextField(blank=True)
    body = models.TextField()
    cover = models.ImageField(upload_to='news/covers/%Y/%m/', blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, db_index=True)
    published_at = models.DateTimeField(blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['published_at']),
            models.Index(fields=['author']),
        ]
        ordering = ['-published_at', '-created_at']

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        if not self.published_at:
            year = self.created_at.year
            month = self.created_at.month
        else:
            year = self.published_at.year
            month = self.published_at.month
        return reverse('post_detail', kwargs={'year': year, 'month': month, 'slug': self.slug})

    def _ensure_unique_slug_in_month(self) -> None:
        # Ensure uniqueness of slug within the publication month.
        ref_dt = self.published_at or self.created_at or timezone.now()
        year = ref_dt.year
        month = ref_dt.month
        base_slug = self.slug or slugify(self.title)
        candidate = base_slug
        suffix = 2
        while Post.objects.filter(
            slug=candidate,
            published_at__year=year,
            published_at__month=month,
        ).exclude(pk=self.pk).exists():
            candidate = f"{base_slug}-{suffix}"
            suffix += 1
        self.slug = candidate

    def clean(self):
        # sanitize body
        self.body = bleach.clean(
            self.body or '',
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
        )
        # generate slug if empty
        if not self.slug:
            self.slug = slugify(self.title)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        is_publishing = self.status == Post.Status.PUBLISHED and not self.published_at
        if is_publishing:
            self.published_at = timezone.now()
        # sanitize and slug before first save
        self.clean()
        super().save(*args, **kwargs)
        # After initial save we may need to adjust slug for uniqueness in month
        old_slug = self.slug
        self._ensure_unique_slug_in_month()
        if self.slug != old_slug:
            super().save(update_fields=['slug'])


class Comment(models.Model):
    class Status(models.TextChoices):
        VISIBLE = 'visible', 'Visible'
        HIDDEN = 'hidden', 'Hidden'

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', db_index=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        db_index=True,
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', db_index=True)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.VISIBLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]
        ordering = ['created_at']

    def clean(self):
        self.body = bleach.clean(
            self.body or '',
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
        )

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.post}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'user'], name='unique_like_per_user_post')
        ]

    def __str__(self) -> str:
        return f"Like by {self.user} on {self.post}"
