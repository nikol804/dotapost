from __future__ import annotations

from django import forms

from .models import Post, Comment, ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_PROTOCOLS
import bleach


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'summary', 'body', 'cover', 'status']

    def clean_body(self):
        data = self.cleaned_data.get('body', '')
        return bleach.clean(
            data,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

    def clean_body(self):
        data = self.cleaned_data.get('body', '')
        data = data.strip()
        if not (1 <= len(data) <= 2000):
            raise forms.ValidationError('Комментарий должен быть длиной от 1 до 2000 символов.')
        return bleach.clean(
            data,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
        )
